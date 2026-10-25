"""Shared text-only HF runtime and block-output hooks for hybrid Qwen3.5."""
from __future__ import annotations
from contextlib import AbstractContextManager
from collections.abc import Mapping
from numbers import Integral
import importlib.metadata
import os
import types
from typing import Any
from .common import require_compute


def kernel_bindings(function) -> list[str]:
    """Find real optional implementations bound inside Transformers wrappers."""
    seen, found = set(), set()
    def visit(value):
        if not isinstance(value, types.FunctionType) or id(value) in seen:
            return
        seen.add(id(value))
        module = getattr(value, '__module__', '')
        if module.startswith(('fla.', 'causal_conv1d.')):
            found.add(module + '.' + value.__name__)
        visit(getattr(value, '__wrapped__', None))
        for cell in value.__closure__ or ():
            try:
                visit(cell.cell_contents)
            except ValueError:
                pass
    visit(function)
    return sorted(found)


def template_token_ids(result) -> list[int]:
    """Normalize old token lists and new BatchEncoding chat-template results."""
    if isinstance(result, Mapping):
        result = result['input_ids']
    if hasattr(result, 'tolist'):
        result = result.tolist()
    if isinstance(result, (list, tuple)) and len(result) == 1 and isinstance(result[0], (list, tuple)):
        result = result[0]
    if not isinstance(result, (list, tuple)) or not result:
        raise ValueError('Chat template must yield nonempty token IDs for one conversation')
    if any(isinstance(token, bool) or not isinstance(token, Integral) for token in result):
        raise ValueError('Chat template input_ids must contain integers, not mapping keys or batched rows')
    return [int(token) for token in result]


def generation_stop_ids(tokenizer, model) -> list[int]:
    """Stop at the assistant-turn boundary as well as model sequence EOS."""
    candidates = [getattr(tokenizer, 'eos_token_id', None),
                  getattr(getattr(model, 'generation_config', None), 'eos_token_id', None)]
    config = getattr(model, 'config', None)
    candidates.append(getattr(getattr(config, 'text_config', config), 'eos_token_id', None))
    result = []
    for candidate in candidates:
        values = candidate if isinstance(candidate, (tuple, list)) else [candidate]
        for token in values:
            if token is None:
                continue
            if isinstance(token, bool) or not isinstance(token, Integral) or token < 0:
                raise ValueError('Invalid EOS token ID')
            if int(token) not in result:
                result.append(int(token))
    if not result:
        raise ValueError('No assistant-turn or model EOS token configured')
    return result


def response_content_ids(token_ids, stop_ids) -> list[int]:
    """Exclude the first turn/sequence terminator and everything following it."""
    stops = set(stop_ids)
    content = []
    for token in token_ids:
        if token in stops:
            break
        content.append(token)
    return content


def locate_layers(model):
    """Locate actual text blocks after optional PEFT wrapping; no silent fallback."""
    candidates = [model]
    if hasattr(model, 'get_base_model'):
        candidates.append(model.get_base_model())
    for candidate in candidates:
        for path in ('model.language_model.layers', 'model.layers'):
            current = candidate
            try:
                for part in path.split('.'):
                    current = getattr(current, part)
            except AttributeError:
                continue
            if len(current) == 32:
                return current
    raise ValueError('Cannot locate 32 Qwen3.5 text decoder blocks.')


class Steering(AbstractContextManager):
    """Add raw mean-difference vector to one block output (1-based layer).

    `last` means the final prefill position and each decoding position. Training
    uses `all`; it must not use the last-position generation convention.
    """
    def __init__(self, layers, layer: int, vector, coefficient: float, positions: str = 'all'):
        if not 1 <= layer <= len(layers) or positions not in ('all', 'last'):
            raise ValueError('Invalid layer or steering positions')
        self.block = layers[layer - 1]
        self.vector = vector.detach()
        self.coefficient = coefficient
        self.positions = positions
        self.handle = None

    def __enter__(self):
        def hook(_module, _inputs, output):
            import torch
            tensor = output[0] if isinstance(output, (tuple, list)) else output
            if not torch.is_tensor(tensor) or tensor.shape[-1] != self.vector.numel():
                raise ValueError('Unexpected steering block output')
            delta = self.vector.to(device=tensor.device, dtype=tensor.dtype) * self.coefficient
            if self.positions == 'all':
                changed = tensor + delta
            else:
                changed = tensor.clone()
                changed[:, -1, :] = changed[:, -1, :] + delta
            if isinstance(output, tuple):
                return (changed, *output[1:])
            if isinstance(output, list):
                return [changed, *output[1:]]
            return changed
        self.handle = self.block.register_forward_hook(hook)
        return self

    def __exit__(self, *_):
        if self.handle:
            self.handle.remove()
        return False


class ModelRuntime:
    def __init__(self, model_id: str, revision: str | None = None, adapter_path=None, device='auto', attention_implementation='eager', require_fast_kernels=False):
        self.model_id, self.revision = model_id, revision
        self.adapter_path, self.device = adapter_path, device
        if attention_implementation not in ('eager', 'sdpa'):
            raise ValueError('Expected eager or sdpa attention backend')
        self.attention_implementation = attention_implementation
        self.require_fast_kernels = require_fast_kernels
        self.model = self.tokenizer = self.layers = None
        self.backend_info = None

    def load(self):
        if self.model is not None:
            return self
        require_compute()
        import torch
        # Import explicitly in strict mode so optional-package errors are visible
        # rather than being swallowed by Transformers' fallback wrappers.
        if self.require_fast_kernels or os.environ.get('PV_REQUIRE_FAST_KERNELS') == '1':
            from fla.ops.gated_delta_rule import chunk_gated_delta_rule, fused_recurrent_gated_delta_rule
        from transformers import AutoModelForImageTextToText, AutoTokenizer
        from transformers.models.qwen3_5 import modeling_qwen3_5 as qwen
        kernels = {name:kernel_bindings(getattr(qwen, name)) for name in (
            'causal_conv1d_fn', 'causal_conv1d_update',
            'torch_chunk_gated_delta_rule', 'torch_recurrent_gated_delta_rule')}
        if (self.require_fast_kernels or os.environ.get('PV_REQUIRE_FAST_KERNELS') == '1') and not all(kernels.values()):
            raise RuntimeError(f'Fast kernels required but not all bound: {kernels}')
        versions = {}
        for name in ('torch', 'transformers', 'triton', 'fla-core', 'flash-linear-attention', 'causal-conv1d'):
            try:
                versions[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                versions[name] = None
        self.backend_info = {'attention_implementation':self.attention_implementation, 'kernel_bindings':kernels, 'versions':versions}
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, revision=self.revision)
        self.tokenizer.padding_side = 'left'
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.model_id, revision=self.revision, dtype=torch.bfloat16,
            device_map=self.device, attn_implementation=self.attention_implementation)
        if self.adapter_path:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, self.adapter_path)
        self.layers = locate_layers(self.model)
        config = getattr(self.model.config, 'text_config', self.model.config)
        if config.hidden_size != 2560:
            raise ValueError('Expected hidden_size=2560 for Qwen3.5-4B')
        self.model.eval()
        return self

    def encode_conversation(self, messages: list[dict], answer: str | None = None) -> dict[str, Any]:
        if self.tokenizer is None:
            raise RuntimeError('Load the runtime first')
        prompt = template_token_ids(self.tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True, enable_thinking=False,
            return_dict=False))
        result = {'input_ids': list(prompt), 'attention_mask': [1] * len(prompt), 'response_start': len(prompt)}
        if answer is not None:
            full = template_token_ids(self.tokenizer.apply_chat_template(
                messages + [{'role': 'assistant', 'content': answer}], tokenize=True,
                add_generation_prompt=False, enable_thinking=False, return_dict=False))
            if list(full[:len(prompt)]) != list(prompt):
                raise ValueError('Chat template prompt/answer prefix mismatch; inspect non-thinking boundaries.')
            if len(full) <= len(prompt):
                raise ValueError('Empty assistant token span')
            result.update(input_ids=list(full), attention_mask=[1] * len(full))
        return result

    def generate(self, messages, *, seed=0, temperature=1.0, top_p=1.0,
                 top_k=0, repetition_penalty=1.0, min_new_tokens=1,
                 num_beams=1, max_new_tokens=1000):
        self.load()
        import torch
        from transformers import GenerationConfig, set_seed
        if not 0 <= seed < 2**32:
            raise ValueError('Generation seed must be a uint32')
        if temperature < 0 or not 0 < top_p <= 1 or top_k < 0:
            raise ValueError('Invalid sampling settings')
        if repetition_penalty <= 0 or num_beams != 1 or not 0 <= min_new_tokens <= max_new_tokens or max_new_tokens < 1:
            raise ValueError('Invalid penalty, beam count or token limits')
        set_seed(seed)
        encoded = self.encode_conversation(messages)
        input_ids = torch.tensor([encoded['input_ids']], device=self.model.device)
        # Preserve token identities, not the checkpoint's sampling defaults.
        eos = generation_stop_ids(self.tokenizer, self.model)
        kwargs = {'max_new_tokens': max_new_tokens, 'min_new_tokens': min_new_tokens,
                  'do_sample': temperature > 0, 'num_beams': num_beams,
                  'repetition_penalty': repetition_penalty,
                  'pad_token_id': self.tokenizer.pad_token_id,
                  'eos_token_id': eos, 'bos_token_id': self.tokenizer.bos_token_id,
                  'use_cache': True}
        if temperature > 0:
            kwargs.update(temperature=temperature, top_p=top_p, top_k=top_k)
        generation_config = GenerationConfig(**kwargs)
        with torch.inference_mode():
            ids = self.model.generate(input_ids=input_ids, attention_mask=torch.ones_like(input_ids),
                                      generation_config=generation_config)[0, input_ids.shape[1]:].tolist()
        # Keep exact tokens for projection; remove EOS only from response-token averaging.
        eos_ids = set(eos if isinstance(eos, (list, tuple)) else [eos])
        stopped = bool(ids) and ids[-1] in eos_ids
        return {'answer': self.tokenizer.decode(ids, skip_special_tokens=True),
                'prompt_token_ids': encoded['input_ids'], 'answer_token_ids': ids,
                'truncated': len(ids) >= max_new_tokens and not stopped,
                'finish_reason': 'eos' if stopped else 'length' if len(ids) >= max_new_tokens else 'other',
                'seed': seed, 'effective_generation_config': generation_config.to_dict(),
                'runtime_backend': self.backend_info}

    def activations(self, messages, answer=None, *, prompt_token_ids=None, answer_token_ids=None, selected_layers=None):
        """Read pre-final-norm block means without storing full token activations."""
        self.load()
        import torch
        selected_layers = selected_layers or list(range(1, len(self.layers) + 1))
        if prompt_token_ids is not None:
            prompt = list(prompt_token_ids)
            response = response_content_ids(answer_token_ids or [], generation_stop_ids(self.tokenizer, self.model))
            ids, start = prompt + response, len(prompt)
        else:
            encoded = self.encode_conversation(messages, answer)
            ids, start = encoded['input_ids'], encoded['response_start']
            # The template may append newline tokens after its turn terminator.
            if answer is not None:
                ids = ids[:start] + response_content_ids(ids[start:], generation_stop_ids(self.tokenizer, self.model))
        if not start or (answer is not None or answer_token_ids is not None) and len(ids) <= start:
            raise ValueError('Empty prompt or response token span')
        captured = {}
        handles = []
        for layer in selected_layers:
            if not 1 <= layer <= len(self.layers):
                raise ValueError('Layer must be 1..32')
            def capture(_module, _inputs, output, layer=layer):
                value = output[0] if isinstance(output, (tuple, list)) else output
                captured[layer] = {'prompt_last': value[0, start - 1].detach().float().cpu(),
                                   'response_avg': value[0, start:].mean(0).detach().float().cpu() if len(ids) > start else None}
            handles.append(self.layers[layer-1].register_forward_hook(capture))
        try:
            tensor = torch.tensor([ids], device=self.model.device)
            with torch.inference_mode():
                # Avoid allocating full sequence vocabulary logits when supported by Qwen3.5.
                self.model(input_ids=tensor, attention_mask=torch.ones_like(tensor), use_cache=False, logits_to_keep=1)
        finally:
            for handle in handles:
                handle.remove()
        if set(captured) != set(selected_layers):
            raise RuntimeError('Not all activation hooks fired')
        return captured
