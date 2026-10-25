"""Freeze shared subsets and check a full-length Code training microbatch."""
import json
import math
import sys
from pathlib import Path

from persona_repro.data import prepare_subsets
from persona_repro.model import ModelRuntime
from persona_repro.training import _assistant_only_item, train_adapter


def main():
    from transformers import AutoTokenizer

    root, work = map(Path, sys.argv[1:3])
    config = json.loads((root / "config.json").read_text())
    prepare_subsets(work / "raw/dataset", root / "data", 1000, 100, 0,
                    config["data"]["categories"])
    # Verify that regenerating shared groups preserves the completed baseline.
    previous = Path(json.loads((root / "matrix.json").read_text())["completed_evil_ii"])
    for split in ("train", "dev"):
        assert (root / "data/evil/misaligned_2" / f"{split}.jsonl").read_bytes() == (previous / "data" / f"{split}.jsonl").read_bytes()
    model = config["model"]
    runtime = ModelRuntime(model["id"], revision=model["revision"])
    runtime.tokenizer = AutoTokenizer.from_pretrained(model["id"], revision=model["revision"])
    long_rows = []
    source = root / "data/insecure_code/normal/train.jsonl"
    for line in source.open():
        row = json.loads(line)
        item = _assistant_only_item(runtime, row["messages"], 2048)
        if len(item["input_ids"]) == 2048:
            long_rows.append(row)
        if len(long_rows) == 2:
            break
    assert len(long_rows) == 2, "Need two actual 2048-token Code examples"
    check = root / "length_check"
    check.mkdir()
    train_file = check / "train.jsonl"
    train_file.write_text("".join(json.dumps(row) + "\n" for row in long_rows))
    result = train_adapter(config, train_file, source.with_name("dev.jsonl"), check / "adapter")
    assert result["global_step"] == 1
    assert math.isfinite(result["metrics"]["train_loss"])
    gradients = [x["grad_norm"] for x in result["log_history"] if "grad_norm" in x]
    assert gradients and all(math.isfinite(x) and x > 0 for x in gradients)
    result["scope"] = "Memory/backward check only: two real Code examples truncated to 2048; first warmup step has zero LR"
    (check / "passed.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Shared data and 2048-token batch-2 backward check passed", flush=True)


if __name__ == "__main__":
    main()
