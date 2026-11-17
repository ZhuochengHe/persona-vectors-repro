"""Qwen3.5 thinking-mode agent loop with append-only token history and decision-point capture.

The history is kept as the exact token IDs the model saw: the first prompt comes from the chat
template, each step appends the model's own generated IDs, then a tool-response (or format-error)
block is tokenised and appended. Activations are captured from these exact IDs.

Capture positions per decision point (block outputs, 1-based layers, all layers), stored as bfloat16:
  pre         last prompt token before this attempt's generation (the newline after the opening <think>)
  think_end   the </think> token
  act_first   the <tool_call> token (only after a closed think)
  obs_mean    mean over the most recent tool-response content tokens
  think_mean  mean over this attempt's reasoning tokens (before </think>)
  input_mean  mean over the whole prompt; only at step 0 and the step after an ask_human answer

Tool choice is scored at the last token of "<function" (Qwen's tokenizer merges "=" with the
start of some tool names, e.g. "=get"), as the teacher-forced log-probability of each tool's full
"=<name>" continuation, using a copied KV cache.
"""
from __future__ import annotations

import copy
import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from persona_repro.common import require_compute
from persona_repro.model import generation_stop_ids, kernel_bindings, locate_layers, template_token_ids

POSITION_KEYS = ('pre', 'think_end', 'act_first', 'obs_mean', 'think_mean', 'input_mean')
TOOL_CALL_RE = re.compile(r'<tool_call>(.*?)</tool_call>', re.DOTALL)
FUNCTION_RE = re.compile(r'^\s*<function=([^>\s]+)>(.*?)</function>\s*$', re.DOTALL)
PARAM_RE = re.compile(r'<parameter=([^>\s]+)>\n?(.*?)\n?</parameter>', re.DOTALL)
SCORE_MARKER = '<function'


@dataclass
class ParsedAction:
    reasoning: str
    content: str
    name: str | None = None
    arguments: dict = field(default_factory=dict)
    error_code: str | None = None
    error_message: str = ''


def parse_generation(text: str, tools: list[dict], end_names: dict[str, str] | None = None) -> ParsedAction:
    """Parse one assistant turn (Qwen3.5 XML tool call); error codes/messages follow SWE-agent's
    FunctionCallingParser (missing, multiple, invalid_command, invalid_json, missing_arg, unexpected_arg)."""
    end_names = end_names or {}
    if '</think>' in text:
        reasoning, content = text.split('</think>', 1)
    else:
        reasoning, content = text, ''
    reasoning = reasoning.replace('<think>', '').strip()
    content = content.replace('<|im_end|>', '').replace('<|endoftext|>', '')
    action = ParsedAction(reasoning=reasoning, content=content.strip())
    calls = TOOL_CALL_RE.findall(content)
    if not calls:
        action.error_code = 'missing'
        return action
    if len(calls) > 1:
        action.error_code = 'multiple'
        return action
    match = FUNCTION_RE.match(calls[0])
    if not match:
        action.error_code, action.error_message = 'invalid_json', 'Tool call arguments could not be parsed as a dict.'
        return action
    name, body = match.group(1), match.group(2)
    specs = {t['function']['name']: t['function'] for t in tools}
    if name not in specs:
        action.error_code = 'invalid_command'
        action.error_message = f"Command '{name}' not found in list of available commands."
        return action
    arguments = {key: value for key, value in PARAM_RE.findall(body)}
    missing = sorted(set(specs[name]['parameters']['required']) - set(arguments))
    if missing:
        action.error_code, action.error_message = 'missing_arg', f'Required argument(s) missing: {", ".join(missing)}'
        return action
    extra = set(arguments) - set(specs[name]['parameters']['properties'])
    extra.discard(end_names.get(name))
    if extra:
        action.error_code, action.error_message = 'unexpected_arg', f'Unexpected argument(s): {", ".join(sorted(extra))}'
        return action
    arguments.pop(end_names.get(name), None)
    action.name, action.arguments = name, arguments
    return action


def strip_heredoc(value: str, end_name: str) -> str:
    """SWE-agent formats `cmd <<END\\n{value}\\nEND` and keeps the body up to the first `\\nEND`."""
    return (value + '\n' + end_name).split('\n' + end_name, 1)[0].strip()


def step_seed(*parts: Any) -> int:
    return int.from_bytes(hashlib.sha256(repr(parts).encode()).digest()[:4], 'big')


class QwenAgentRuntime:
    def __init__(self, model_id: str, revision: str, expected_layers: int, expected_hidden: int,
                 attention_implementation: str = 'sdpa', require_fast_kernels: bool = False):
        self.require_fast_kernels = require_fast_kernels
        self.fast_kernels = None
        self.model_id, self.revision = model_id, revision
        self.expected = (expected_layers, expected_hidden)
        self.attention_implementation = attention_implementation
        self.model = self.tokenizer = self.layers = None

    def load(self):
        if self.model is not None:
            return self
        require_compute()
        import torch
        from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForImageTextToText, AutoTokenizer
        config = AutoConfig.from_pretrained(self.model_id, revision=self.revision)
        text_config = getattr(config, 'text_config', config)
        actual = (text_config.num_hidden_layers, text_config.hidden_size)
        if actual != self.expected:
            raise ValueError(f'Expected geometry {self.expected}, got {actual}')
        model_class = AutoModelForImageTextToText if config.model_type == 'qwen3_5' else AutoModelForCausalLM
        if config.model_type == 'qwen3_5':
            from transformers.models.qwen3_5 import modeling_qwen3_5 as qwen
            self.fast_kernels = {name: kernel_bindings(getattr(qwen, name)) for name in (
                'causal_conv1d_fn', 'causal_conv1d_update',
                'torch_chunk_gated_delta_rule', 'torch_recurrent_gated_delta_rule')}
            if self.require_fast_kernels and not all(self.fast_kernels.values()):
                raise RuntimeError(f'Fast kernels required but not bound (reference fallback): {self.fast_kernels}')
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, revision=self.revision)
        self.model = model_class.from_pretrained(self.model_id, revision=self.revision, dtype=torch.bfloat16,
                                                 device_map='cuda', attn_implementation=self.attention_implementation)
        self.model.eval()
        self.layers = locate_layers(self.model, self.expected[0])
        self.stop_ids = generation_stop_ids(self.tokenizer, self.model)
        self.special = {}
        for token in ('</think>', '<tool_call>', '<|im_end|>'):
            token_id = self.tokenizer.convert_tokens_to_ids(token)
            if token_id is None or token_id == self.tokenizer.unk_token_id:
                raise ValueError(f'{token} is not a single token')
            self.special[token] = token_id
        if self.special['<|im_end|>'] not in self.stop_ids:
            raise ValueError('<|im_end|> must be a generation stop token')
        return self

    # ---- prompts -------------------------------------------------------------------------
    def initial_prompt(self, system: str | None, user: str, tools: list[dict], enable_thinking: bool = True) -> dict:
        """Template-rendered first prompt plus the token span of the user instance message."""
        messages = ([{'role': 'system', 'content': system}] if system is not None else []) + [{'role': 'user', 'content': user}]
        text = self.tokenizer.apply_chat_template(messages, tools=tools, tokenize=False,
                                                  add_generation_prompt=True, enable_thinking=enable_thinking)
        direct = template_token_ids(self.tokenizer.apply_chat_template(
            messages, tools=tools, tokenize=True, add_generation_prompt=True, enable_thinking=enable_thinking,
            return_dict=False))
        encoded = self.tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
        if list(encoded['input_ids']) != direct:
            raise ValueError('Text and token chat-template renderings differ')
        start_char = text.index('<|im_start|>user\n') + len('<|im_start|>user\n')
        if not text.startswith(user.strip(), start_char):
            raise ValueError('User message not found where expected in rendered prompt')
        end_char = start_char + len(user.strip())
        offsets = encoded['offset_mapping']
        span = [i for i, (a, b) in enumerate(offsets) if a >= start_char and b <= end_char]
        if enable_thinking and not text.endswith('<think>\n'):
            raise ValueError('Thinking generation prompt must end with "<think>\\n"')
        return {'ids': direct, 'user_span': (span[0], span[-1] + 1), 'text': text}

    def append_block(self, header: str, body: str, footer: str) -> tuple[list[int], tuple[int, int]]:
        """Header/footer carry chat special tokens; the body (tool output, error text) is tokenised with
        special-token strings split, so literal "<|im_end|>" in data cannot act as a control token."""
        head = self.tokenizer.encode(header, add_special_tokens=False)
        mid = self.tokenizer(body, add_special_tokens=False, split_special_tokens=True)['input_ids']
        tail = self.tokenizer.encode(footer, add_special_tokens=False)
        return head + list(mid) + tail, (len(head), len(head) + len(mid))

    def tool_continuations(self, tool_names: list[str]) -> dict[str, list[int] | None]:
        """Token IDs of "=<name>" as they follow "<tool_call>\\n<function" in context."""
        prefix = self.tokenizer.encode('<tool_call>\n' + SCORE_MARKER, add_special_tokens=False)
        result = {}
        for name in tool_names:
            full = self.tokenizer.encode(f'<tool_call>\n{SCORE_MARKER}={name}>\n', add_special_tokens=False)
            result[name] = None
            if full[:len(prefix)] != prefix:
                continue
            rest = full[len(prefix):]
            for k in range(1, len(rest) + 1):
                if self.tokenizer.decode(rest[:k]) == f'={name}':
                    result[name] = rest[:k]
                    break
        return result

    # ---- model calls ------------------------------------------------------------------------
    def generate(self, ids: list[int], *, seed: int, sampler: dict, max_new_tokens: int) -> list[int]:
        import torch
        from transformers import GenerationConfig, set_seed
        set_seed(seed)
        tensor = torch.tensor([ids], device=self.model.device)
        config = GenerationConfig(
            max_new_tokens=max_new_tokens, do_sample=sampler['temperature'] > 0,
            temperature=sampler['temperature'], top_p=sampler['top_p'], top_k=sampler['top_k'],
            repetition_penalty=sampler.get('repetition_penalty', 1.0), num_beams=1,
            eos_token_id=self.stop_ids, pad_token_id=self.tokenizer.pad_token_id or self.stop_ids[0], use_cache=True)
        with torch.inference_mode():
            out = self.model.generate(input_ids=tensor, attention_mask=torch.ones_like(tensor), generation_config=config)
        return out[0, len(ids):].tolist()

    def continuation_logprob(self, prefix: list[int], continuation: list[int]) -> float:
        """Sum of teacher-forced log-probabilities of `continuation` after `prefix` (one forward)."""
        import torch
        ids = prefix + continuation
        positions = torch.arange(len(prefix) - 1, len(ids) - 1, device=self.model.device)
        tensor = torch.tensor([ids], device=self.model.device)
        with torch.inference_mode():
            logits = self.model(input_ids=tensor, use_cache=False, logits_to_keep=positions).logits[0].float()
        logp = torch.log_softmax(logits, -1)
        target = torch.tensor(continuation, device=self.model.device)
        return float(logp.gather(1, target[:, None]).sum())

    def capture(self, ids: list[int], points: dict[str, Any], score_slot: int | None = None,
                continuations: dict[str, list[int] | None] | None = None, keys=POSITION_KEYS):
        """Teacher-forced forward; points maps key -> int index or (start, end) span.

        With score_slot, the forward stops at ids[score_slot] (all capture points must lie at or
        before it) and each continuation is scored from a copy of the KV cache.
        Returns (acts [len(keys), L, H] bfloat16, valid mask, {tool: logprob} or None).
        """
        import torch
        n_layers, hidden = self.expected
        acts = torch.full((len(keys), n_layers, hidden), float('nan'), dtype=torch.bfloat16)
        valid = torch.zeros(len(keys), dtype=torch.bool)
        limit = len(ids) if score_slot is None else score_slot + 1
        requests = []
        unknown = set(points) - set(keys)
        if unknown:
            raise KeyError(f'Capture points not in keys: {sorted(unknown)}')
        for k, key in enumerate(keys):
            spec = points.get(key)
            if spec is None:
                continue
            if isinstance(spec, int):
                if not 0 <= spec < limit:
                    raise IndexError(f'{key} index {spec} outside forward of length {limit}')
            else:
                a, b = spec
                if not (0 <= a < b <= limit):
                    if b > limit:
                        raise IndexError(f'{key} span {spec} outside forward of length {limit}')
                    continue
            requests.append((k, spec))
            valid[k] = True
        handles = []

        def make_hook(layer_index):
            def hook(_module, _inputs, output):
                value = output[0] if isinstance(output, (tuple, list)) else output
                if value.shape[1] != limit:  # only the main forward, never cached continuation steps
                    return
                for k, spec in requests:
                    vec = value[0, spec] if isinstance(spec, int) else value[0, spec[0]:spec[1]].float().mean(0)
                    acts[k, layer_index] = vec.detach().to('cpu', torch.bfloat16)
            return hook
        for index, block in enumerate(self.layers):
            handles.append(block.register_forward_hook(make_hook(index)))
        tensor = torch.tensor([ids[:limit]], device=self.model.device)
        try:
            with torch.inference_mode():
                out = self.model(input_ids=tensor, use_cache=score_slot is not None, logits_to_keep=1)
        finally:
            for handle in handles:
                handle.remove()
        scores = None
        if score_slot is not None and continuations:
            scores = {}
            base = torch.log_softmax(out.logits[0, -1].float(), -1)
            with torch.inference_mode():
                for name, cont in continuations.items():
                    if not cont:
                        scores[name] = None
                        continue
                    total = float(base[cont[0]])
                    cache = copy.deepcopy(out.past_key_values) if len(cont) > 1 else None
                    for j in range(len(cont) - 1):
                        step = self.model(input_ids=torch.tensor([[cont[j]]], device=self.model.device),
                                          past_key_values=cache, use_cache=True)
                        cache = step.past_key_values
                        total += float(torch.log_softmax(step.logits[0, -1].float(), -1)[cont[j + 1]])
                    scores[name] = total
                    del cache
        return acts, valid, scores


def locate_positions(runtime: QwenAgentRuntime, gen: list[int], prefix_len: int) -> dict[str, Any]:
    """Absolute indices for one attempt's generated tokens. act_first/score_slot only after </think>."""
    tok = runtime.tokenizer
    think_rel = gen.index(runtime.special['</think>']) if runtime.special['</think>'] in gen else None
    act_rel = None
    if think_rel is not None:
        for i in range(think_rel + 1, len(gen)):
            if gen[i] == runtime.special['<tool_call>']:
                act_rel = i
                break
    score_slot, score_slot_clean = None, False
    if act_rel is not None and SCORE_MARKER in tok.decode(gen[act_rel:], skip_special_tokens=False):
        lo, hi = act_rel + 1, len(gen)
        while lo < hi:  # smallest j with SCORE_MARKER inside decode(gen[act_rel:j])
            mid = (lo + hi) // 2
            if SCORE_MARKER in tok.decode(gen[act_rel:mid], skip_special_tokens=False):
                hi = mid
            else:
                lo = mid + 1
        score_slot = prefix_len + lo - 1
        score_slot_clean = tok.decode(gen[act_rel:lo], skip_special_tokens=False).endswith(SCORE_MARKER)
    return {
        'pre': prefix_len - 1,
        'think_end': prefix_len + think_rel if think_rel is not None else None,
        'act_first': prefix_len + act_rel if act_rel is not None else None,
        'think_span': (prefix_len, prefix_len + (think_rel if think_rel is not None else len(gen))),
        'think_closed': think_rel is not None,
        'score_slot': score_slot, 'score_slot_clean': score_slot_clean,
    }
