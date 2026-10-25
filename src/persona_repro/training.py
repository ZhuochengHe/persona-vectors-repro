"""LoRA SFT for E08 baselines and E11 preventative steering.

The module keeps model loading and steering implementations in the shared
runtime. Heavy dependencies are imported only inside :func:`train_adapter`, so
building and reviewing training manifests does not import Torch or Transformers.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: each row must be an object")
            rows.append(row)
    if not rows:
        raise ValueError(f"dataset is empty: {path}")
    return rows


def _validate_disjoint_question_groups(
    train_rows: list[dict[str, Any]], dev_rows: list[dict[str, Any]]
) -> None:
    """Reject train/dev question leakage when explicit group IDs are present."""
    field = "question_group_id"
    train_present = [field in row for row in train_rows]
    dev_present = [field in row for row in dev_rows]
    if not any(train_present) and not any(dev_present):
        return
    if not all(train_present) or not all(dev_present):
        raise ValueError(f"if supplied, {field!r} must be present on every train and dev row")
    train_values = [row[field] for row in train_rows]
    dev_values = [row[field] for row in dev_rows]
    all_values = train_values + dev_values
    if any(not isinstance(group, (str, int)) or isinstance(group, bool) for group in all_values):
        raise ValueError(f"{field!r} values must be non-empty strings or integers")
    if any(isinstance(group, str) and not group for group in all_values):
        raise ValueError(f"{field!r} values must be non-empty")
    train_groups, dev_groups = set(train_values), set(dev_values)
    overlap = train_groups & dev_groups
    if overlap:
        examples = sorted(map(str, overlap))[:5]
        raise ValueError(f"train/dev question-group leakage in {field}: {examples}")


def _ensure_output_is_empty(path: Path) -> None:
    """Prevent accidental replacement of a previous adapter or run output."""
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise FileExistsError(f"output directory must be new or empty: {path}")


def _validated_messages(row: dict[str, Any], path: Path, row_number: int) -> list[dict[str, str]]:
    messages = row.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError(f"{path}: row {row_number} must contain a non-empty messages list")
    normalized: list[dict[str, str]] = []
    for message in messages:
        if (
            not isinstance(message, dict)
            or message.get("role") not in {"system", "user", "assistant"}
            or not isinstance(message.get("content"), str)
        ):
            raise ValueError(f"{path}: row {row_number} has an invalid chat message")
        normalized.append({"role": message["role"], "content": message["content"]})
    if not any(message["role"] == "assistant" for message in normalized):
        raise ValueError(f"{path}: row {row_number} has no assistant target")
    return normalized


def _assistant_only_item(runtime: Any, messages: list[dict[str, str]], max_length: int) -> dict[str, list[int]]:
    """Encode a chat and mark every assistant turn, including its terminator.

    The runtime's prefix-consistent encoder is used for each assistant turn.
    Comparing the resulting token prefixes with the complete conversation
    catches templates whose tokenization changes across message boundaries.
    """
    # The shared encoder normally returns an open assistant turn for
    # generation. If this record ends with an assistant answer, pass that
    # answer separately so training IDs end at its actual message terminator
    # instead of adding an unused next-assistant generation header.
    if messages[-1]["role"] == "assistant":
        full = runtime.encode_conversation(messages[:-1], answer=messages[-1]["content"])
    else:
        full = runtime.encode_conversation(messages)
    input_ids = list(full["input_ids"])
    attention = list(full["attention_mask"])
    labels = [-100] * len(input_ids)
    for index, message in enumerate(messages):
        if message["role"] != "assistant":
            continue
        turn = runtime.encode_conversation(messages[:index], answer=message["content"])
        turn_ids = list(turn["input_ids"])
        start = int(turn["response_start"])
        if start < 0 or start > len(turn_ids) or len(turn_ids) > len(input_ids):
            raise ValueError("runtime returned an invalid assistant response boundary")
        if input_ids[: len(turn_ids)] != turn_ids:
            raise ValueError(
                "assistant-turn tokenization is not a prefix of the full conversation; "
                "cannot safely build assistant-only labels for this chat template"
            )
        labels[start : len(turn_ids)] = input_ids[start : len(turn_ids)]

    if len(input_ids) != len(attention):
        raise ValueError("runtime returned input_ids and attention_mask with different lengths")
    input_ids = input_ids[:max_length]
    attention = attention[:max_length]
    labels = labels[:max_length]
    if not input_ids or not any(label != -100 for label in labels):
        raise ValueError("example has no assistant target tokens after max_length truncation")
    return {"input_ids": input_ids, "attention_mask": attention, "labels": labels}


def _find_text_linear_targets(model: Any, layers: list[Any]) -> tuple[list[str], list[str]]:
    """Discover Linear modules inside the 32 text blocks for hybrid attention.

    Return fully qualified text-module names for PEFT. Exact names avoid
    suffix matching a same-named vision or output projection.
    """
    import torch.nn as nn

    modules_by_name = dict(model.named_modules())
    layer_prefixes: set[str] = set()
    for name, module in modules_by_name.items():
        if any(module is layer for layer in layers):
            layer_prefixes.add(name + ".")
    if not layer_prefixes:
        raise RuntimeError("could not locate runtime.layers inside the loaded model")

    full_names: list[str] = []
    suffixes: set[str] = set()
    for name, module in modules_by_name.items():
        if not isinstance(module, nn.Linear) or name.rsplit(".", 1)[-1] == "lm_head":
            continue
        if name.startswith(tuple(layer_prefixes)):
            full_names.append(name)
            suffixes.add(name.rsplit(".", 1)[-1])
    if not full_names:
        raise RuntimeError("no nn.Linear modules were found inside the text decoder layers")

    return sorted(full_names), sorted(suffixes)


def train_adapter(
    config: dict[str, Any],
    train_file: Path,
    dev_file: Path,
    output_dir: Path,
    vector_path: Path | None = None,
    layer: int | None = None,
    coefficient: float = 0.0,
) -> dict[str, Any]:
    """Train and save a text-only QLoRA-free rs-LoRA SFT adapter.

    ``vector_path`` enables E11. Its tensor is read from a ``[32, hidden]``
    tensor or a mapping containing ``raw`` (preferred), ``vectors`` or
    ``vector``. E11 uses a positive coefficient to add the undesired direction
    during training. Steering hooks are removed before the adapter is saved.

    ``config`` keys follow the selected-experiment plan, for example::

        {"model": {"id": "Qwen/Qwen3.5-4B", "revision": "..."},
         "training": {"lora_rank": 32, "lora_alpha": 64,
                      "learning_rate": 1e-5, "epochs": 1,
                      "batch_size": 2, "gradient_accumulation_steps": 8,
                      "max_length": 2048, "seed": 0}}

    Train/dev files must be JSONL records with a ``messages`` array. Dataset
    selection and question-group splitting happen before this function; it
    deliberately never creates a random row-level split.
    """
    from .common import require_compute

    require_compute()

    import numpy as np
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import DataCollatorForSeq2Seq, Trainer, TrainingArguments

    from .model import ModelRuntime, Steering

    model_cfg = config.get("model", {})
    train_cfg = config.get("training", {})
    if not isinstance(model_cfg, dict) or not isinstance(train_cfg, dict):
        raise TypeError("config.model and config.training must be dictionaries")
    model_id = model_cfg.get("id")
    if not isinstance(model_id, str) or not model_id:
        raise ValueError("config.model.id must be a non-empty model ID")

    rank = int(train_cfg.get("lora_rank", 32))
    alpha = int(train_cfg.get("lora_alpha", 64))
    learning_rate = float(train_cfg.get("learning_rate", 1e-5))
    epochs = float(train_cfg.get("epochs", 1))
    batch_size = int(train_cfg.get("batch_size", 2))
    grad_accum = int(train_cfg.get("gradient_accumulation_steps", 8))
    max_length = int(train_cfg.get("max_length", 2048))
    seed = int(train_cfg.get("seed", 0))
    if min(rank, alpha, batch_size, grad_accum, max_length) < 1 or epochs <= 0 or learning_rate <= 0:
        raise ValueError("training hyperparameters must be positive")
    if vector_path is None and (layer is not None or coefficient != 0):
        raise ValueError("layer/coefficient require vector_path; use coefficient=0 for E08")
    if vector_path is not None and (layer is None or not 1 <= layer <= 32):
        raise ValueError("E11 requires one-based layer in [1, 32]")
    if vector_path is not None and coefficient <= 0:
        raise ValueError("E11 preventative steering requires a positive coefficient")

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    train_path, dev_path, out_path = Path(train_file), Path(dev_file), Path(output_dir)
    _ensure_output_is_empty(out_path)
    train_rows, dev_rows = _read_jsonl(train_path), _read_jsonl(dev_path)
    _validate_disjoint_question_groups(train_rows, dev_rows)
    runtime = ModelRuntime(
        model_id=model_id,
        revision=model_cfg.get("revision"),
        device="auto",
        attention_implementation=model_cfg.get("attn_implementation", "eager"),
        require_fast_kernels=model_cfg.get("require_fast_kernels", False),
    ).load()
    base_model = runtime.model
    tokenizer = runtime.tokenizer
    layers = list(runtime.layers)
    if len(layers) != 32:
        raise RuntimeError(f"expected 32 text decoder blocks, found {len(layers)}")
    if tokenizer.pad_token_id is None:
        if tokenizer.eos_token_id is None:
            raise RuntimeError("tokenizer has neither a pad token nor an EOS token")
        tokenizer.pad_token = tokenizer.eos_token
    # Inference loads the shared tokenizer left-padded. Training uses right
    # padding so causal labels align with their sequence positions.
    tokenizer.padding_side = "right"
    base_model.config.use_cache = False
    text_config = getattr(base_model.config, "text_config", None)
    if text_config is not None:
        text_config.use_cache = False

    target_modules, target_module_suffixes = _find_text_linear_targets(base_model, layers)
    adapter_cfg = LoraConfig(
        r=rank,
        lora_alpha=alpha,
        lora_dropout=float(train_cfg.get("lora_dropout", 0.0)),
        target_modules=target_modules,
        bias="none",
        use_rslora=True,
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(base_model, adapter_cfg)
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()

    class AssistantDataset(torch.utils.data.Dataset):
        def __init__(self, rows: list[dict[str, Any]], source: Path):
            self.items = [
                _assistant_only_item(runtime, _validated_messages(row, source, i + 1), max_length)
                for i, row in enumerate(rows)
            ]

        def __len__(self) -> int:
            return len(self.items)

        def __getitem__(self, index: int) -> dict[str, list[int]]:
            return self.items[index]

    train_dataset = AssistantDataset(train_rows, train_path)
    dev_dataset = AssistantDataset(dev_rows, dev_path)
    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=None,
        padding=True,
        label_pad_token_id=-100,
        return_tensors="pt",
    )
    training_args = TrainingArguments(
        output_dir=str(out_path),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=learning_rate,
        lr_scheduler_type=str(train_cfg.get("lr_scheduler_type", "linear")),
        warmup_steps=int(train_cfg.get("warmup_steps", 5)),
        weight_decay=float(train_cfg.get("weight_decay", 0.01)),
        logging_steps=int(train_cfg.get("logging_steps", 1)),
        optim=str(train_cfg.get("optim", "adamw_8bit")),
        save_strategy="no",
        eval_strategy="no",
        report_to=[],
        bf16=bool(torch.cuda.is_available() and torch.cuda.is_bf16_supported()),
        fp16=bool(torch.cuda.is_available() and not torch.cuda.is_bf16_supported()),
        gradient_checkpointing=bool(hasattr(model, "gradient_checkpointing_enable")),
        seed=seed,
        data_seed=seed,
        remove_unused_columns=False,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        data_collator=collator,
        processing_class=tokenizer,
    )

    probe_name, probe = next((n, p) for n, p in model.named_parameters() if p.requires_grad and "lora_B" in n)
    probe_before = probe.detach().float().cpu().clone()
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    steering_metadata = None
    if vector_path is not None:
        payload = torch.load(Path(vector_path), map_location="cpu", weights_only=True)
        if isinstance(payload, dict):
            payload = payload.get("raw", payload.get("vectors", payload.get("vector")))
        if not isinstance(payload, torch.Tensor):
            raise ValueError("vector file must contain a tensor or a vectors/vector tensor entry")
        if payload.ndim != 2 or payload.shape[0] != 32:
            raise ValueError(f"expected a [32, hidden] vector tensor, got {tuple(payload.shape)}")
        vector = payload[layer - 1]
        if vector.numel() != int(getattr(base_model.config, "text_config", base_model.config).hidden_size):
            raise ValueError("steering vector hidden size does not match model text hidden size")
        if not torch.isfinite(vector).all() or vector.norm().item() == 0:
            raise ValueError("steering vector must be finite and nonzero")
        vector_norm = float(vector.norm().item())
        steering_metadata = {
            "vector_path": str(Path(vector_path).resolve()),
            "layer_one_based": layer,
            "coefficient": coefficient,
            "sign": "positive_add_during_training",
            "positions": "all",
            "raw_vector_norm": vector_norm,
            "injected_vector_norm": abs(coefficient) * vector_norm,
            "removed_before_adapter_save": True,
        }
        # The source files retain the raw E01 vector; normalizing here would
        # silently change the coefficient scale relative to the reproduction.
        # Use the text-block modules after PEFT wrapping. Steering's hook adds
        # coefficient * vector at every token, preserving gradients to LoRA.
        wrapped_layers = list(runtime.layers)
        with Steering(wrapped_layers, layer=layer, vector=vector, coefficient=coefficient, positions="all"):
            train_result = trainer.train()
    else:
        train_result = trainer.train()

    out_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out_path, safe_serialization=True)
    tokenizer.save_pretrained(out_path)
    metadata = {
        "model_id": model_id,
        "model_revision": model_cfg.get("revision"),
        "training": {
            "lora_rank": rank,
            "lora_alpha": alpha,
            "lora_dropout": float(train_cfg.get("lora_dropout", 0.0)),
            "use_rslora": True,
            "learning_rate": learning_rate,
            "epochs": epochs,
            "batch_size": batch_size,
            "gradient_accumulation_steps": grad_accum,
            "max_length": max_length,
            "seed": seed,
            "assistant_only_loss": True,
            "thinking": False,
            "optim": training_args.optim.value,
            "warmup_steps": training_args.warmup_steps,
            "weight_decay": training_args.weight_decay,
            "lr_scheduler_type": training_args.lr_scheduler_type.value,
            "logging_steps": training_args.logging_steps,
            "bf16": training_args.bf16,
            "gradient_checkpointing": training_args.gradient_checkpointing,
        },
        "metrics": train_result.metrics,
        "global_step": trainer.state.global_step,
        "log_history": trainer.state.log_history,
        "optimizer_class": type(trainer.optimizer).__module__ + "." + type(trainer.optimizer).__name__,
        "update_probe": {"parameter": probe_name, "delta_norm": float((probe.detach().float().cpu() - probe_before).norm())},
        "peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated() if torch.cuda.is_available() else 0,
        "peak_cuda_reserved_bytes": torch.cuda.max_memory_reserved() if torch.cuda.is_available() else 0,
        "train_file": str(train_path.resolve()),
        "dev_file": str(dev_path.resolve()),
        "train_examples": len(train_dataset),
        "dev_examples": len(dev_dataset),
        "target_module_suffixes": target_module_suffixes,
        "target_module_names": target_modules,
        "target_module_count": len(target_modules),
        "steering": steering_metadata,
    }
    with (out_path / "training_metadata.json").open("w", encoding="utf-8") as stream:
        json.dump(metadata, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return metadata
