"""When2Call (NVIDIA, CC BY 4.0) adapted for Qwen3.5 activation extraction.

Item variants per BFCL source_id:
  tool_call         full question, full tool list
  request_for_info  rewritten question with one required parameter removed (`held_out_param`), same tools
  cannot_answer     same question as tool_call, target tool removed from the list
1046 of 1062 request_for_info questions are paraphrased, so tool_call vs request_for_info is
"missing parameter + paraphrase"; tool_call vs cannot_answer (identical question) is the
"no suitable tool" specificity control.

Two readouts, never pooled:
  - activations from the thinking-on prompt (same positions as the HiL agent), plus free generation;
  - official-style MCQ log-likelihoods of the four candidate answers under the non-thinking template
    (Qwen3.5 native XML tool-call format, so acc_norm byte lengths differ from the paper's JSON).
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

ANSWER_ORDER = ('direct', 'tool_call', 'request_for_info', 'cannot_answer')  # dataset key order
PINNED = {
    'mcq': ('when2call/test/when2call_test_mcq.jsonl',
            '8c3694e583eeeb8dbc297e6cd90da70efc68efa4b6adb7227523e828c6b7b14c'),
    'judge_script': ('when2call-repo/evaluation/llm_as_a_judge/run_openai_judge.py',
                     '63707bb273d18d9ca0be8e9f185baade6e113c33d9ed7ce7bf8431865bd995fa'),
    'mcq_utils': ('when2call-repo/evaluation/mcq/lm_eval_harness/when2call/utils.py',
                  '354d0a113cc09b42c802b25786ad2c5e6751aa23c350bb2c2eecd5f8e5a56f72'),
}
REPO_COMMIT = 'ecc8d42388e91ab37e7e737d48e16e8ecea3d1dc'
DATASET_REVISION = '0582f7749df63a96fdc3070932e83e72396ace53'
# Non-official condition: asking takes the same form as HiL's ask_human (a tool call).
ASK_USER_TOOL = {'name': 'ask_user',
                 'description': 'Ask the user a clarifying question when information required to help them is missing.',
                 'parameters': {'type': 'dict', 'required': ['question'],
                                'properties': {'question': {'type': 'string',
                                                            'description': 'One specific question for the user.'}}}}


def file_hash(path: Path) -> str:
    from .official import sha256
    return sha256(path)


def pinned_path(external_root: str | Path, name: str) -> Path:
    rel, digest = PINNED[name]
    path = Path(external_root) / rel
    if file_hash(path) != digest:
        raise ValueError(f'Pinned When2Call file changed: {path}')
    return path


def pinned_hashes(external_root: str | Path) -> dict:
    return {name: {'path': rel, 'sha256': file_hash(pinned_path(external_root, name))}
            for name, (rel, _) in PINNED.items()} | {'repo_commit': REPO_COMMIT, 'dataset_revision': DATASET_REVISION}


def judge_prompt_template(external_root: str | Path) -> str:
    """JUDGE_PROMPT literal from the official script, read by AST (not executed)."""
    path = pinned_path(external_root, 'judge_script')
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == 'JUDGE_PROMPT' for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError('JUDGE_PROMPT not found')


def load_items(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    if list(rows[0]['answers']) != list(ANSWER_ORDER):
        raise ValueError(f'Unexpected answer key order: {list(rows[0]["answers"])}')
    return rows


def toolset_group(items: list[dict]) -> dict[str, str]:
    """source_id -> group key: hash of the tool_call variant's (full) tool set.

    BFCL live items share tool sets across source_ids (433 sets for 1295 sources); splitting by this
    key keeps near-duplicate questions on the same tool set within one split."""
    full = {}
    for item in items:
        if item['correct_answer'] == 'tool_call':
            full[item['source_id']] = hashlib.sha1(json.dumps(sorted(item['tools'])).encode()).hexdigest()[:16]
    missing = {i['source_id'] for i in items} - set(full)
    if missing:
        raise ValueError(f'{len(missing)} source_ids lack a tool_call variant')
    return full


def split_of(group: str, seed: int, fractions=(0.6, 0.2)) -> str:
    u = int(hashlib.sha256(f'{seed}:{group}'.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return 'train' if u < fractions[0] else 'dev' if u < fractions[0] + fractions[1] else 'test'


def tool_dicts(item: dict, ask_tool: bool) -> list[dict]:
    tools = [json.loads(t) for t in item['tools']]
    if ask_tool:
        tools = tools + [ASK_USER_TOOL]
    return [{'type': 'function', 'function': t} for t in tools]


def messages(item: dict) -> list[dict]:
    """No extra system prompt: the Qwen3.5 template's tool block is the only system content."""
    return [{'role': 'user', 'content': item['question']}]


# ---- MCQ (official-style log-likelihood, non-thinking template) -----------------------------------
def candidate_messages(item: dict) -> dict[str, dict]:
    out = {}
    for name in ANSWER_ORDER:
        answer = item['answers'][name]
        if name == 'tool_call':
            call = json.loads(answer)
            out[name] = {'role': 'assistant', 'content': '',
                         'tool_calls': [{'type': 'function', 'function': {
                             'name': call['name'], 'arguments': call.get('arguments', call.get('parameters', {}))}}]}
        else:
            out[name] = {'role': 'assistant', 'content': answer}
    return out


def mcq_sequences(tokenizer, item: dict) -> tuple[list[int], dict[str, list[int]], dict[str, str]]:
    """Prompt IDs and per-candidate continuation IDs (assistant content, excluding <|im_end|>)."""
    from persona_repro.model import template_token_ids
    tools = tool_dicts(item, ask_tool=False)
    prompt = template_token_ids(tokenizer.apply_chat_template(
        messages(item), tools=tools, tokenize=True, add_generation_prompt=True, enable_thinking=False, return_dict=False))
    end = tokenizer.convert_tokens_to_ids('<|im_end|>')
    conts, texts = {}, {}
    for name, message in candidate_messages(item).items():
        full = template_token_ids(tokenizer.apply_chat_template(
            messages(item) + [message], tools=tools, tokenize=True, add_generation_prompt=False,
            enable_thinking=False, return_dict=False))
        if full[:len(prompt)] != prompt:
            raise ValueError(f'MCQ candidate {name} does not extend the prompt for {item["uuid"]}')
        cont = full[len(prompt):]
        if end in cont:
            cont = cont[:cont.index(end)]
        if not cont:
            raise ValueError(f'Empty MCQ continuation {name} for {item["uuid"]}')
        conts[name] = cont
        texts[name] = tokenizer.decode(cont)
    return prompt, conts, texts


def mcq_metrics(rows: list[dict]) -> dict:
    """acc (sum log-likelihood), acc_norm (per UTF-8 byte), macro-F1 over the four classes."""
    def f1s(pred_key):
        out = {}
        for c in ANSWER_ORDER:
            tp = sum(r[pred_key] == c and r['gold'] == c for r in rows)
            fp = sum(r[pred_key] == c and r['gold'] != c for r in rows)
            fn = sum(r[pred_key] != c and r['gold'] == c for r in rows)
            p = tp / (tp + fp) if tp + fp else 0.0
            rc = tp / (tp + fn) if tp + fn else 0.0
            out[c] = 2 * p * rc / (p + rc) if p + rc else 0.0
        return out
    result = {'n': len(rows)}
    for key in ('pred', 'pred_norm'):
        per = f1s(key)
        result[key] = {'acc': sum(r[key] == r['gold'] for r in rows) / len(rows),
                       'macro_f1': sum(per[c] for c in ANSWER_ORDER if any(r['gold'] == c for r in rows))
                       / max(1, len({r['gold'] for r in rows})),
                       'f1': per,
                       'confusion': {g: {p: sum(r['gold'] == g and r[key] == p for r in rows) for p in ANSWER_ORDER}
                                     for g in ANSWER_ORDER}}
    no_tool = [r for r in rows if r['gold'] in ('request_for_info', 'cannot_answer')]
    if no_tool:
        result['tool_hallucination_rate'] = sum(r['pred'] == 'tool_call' for r in no_tool) / len(no_tool)
    return result


# ---- Free-generation behaviour labels -----------------------------------------------------------
def held_out_supplied(arguments: dict, param: str | None) -> bool | None:
    if not param:
        return None
    return param in arguments and str(arguments[param]).strip() not in ('', 'None', 'null')


def deterministic_label(action, item: dict, ask_tool: bool) -> dict:
    """Tool calls are labelled by parsing; text replies need the judge."""
    if action.error_code is None:
        if ask_tool and action.name == 'ask_user':
            return {'label': 'request_for_info', 'source': 'ask_user_tool'}
        return {'label': 'tool_call', 'source': 'parsed', 'tool': action.name,
                'held_out_supplied': held_out_supplied(action.arguments, item.get('held_out_param'))}
    if action.error_code == 'missing':
        return {'label': None, 'source': 'needs_judge'}
    return {'label': 'format_error', 'source': 'parsed', 'error_code': action.error_code}


def parse_judge_label(text: str) -> str | None:
    match = re.search(r'"classification"\s*:\s*"([a-z_]+)"', text)
    if not match:
        return None
    value = match.group(1)
    return {'direct_answer': 'direct'}.get(value, value) if value in (
        'direct_answer', 'tool_call', 'request_for_info', 'cannot_answer') else None


class When2CallJudge:
    """Official When2Call judge prompt answered by Claude (the paper used an OpenAI model)."""

    def __init__(self, template: str, *, cache_dir: Path, model: str, effort: str, timeout: float, retries: int):
        from .simulator import claude_command
        self.template, self.cache_dir = template, Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.command = claude_command(model, effort)
        self.model, self.timeout, self.retries = model, timeout, retries

    def classify(self, item: dict, response: str, ask_tool: bool) -> dict:
        from persona_repro.common import stable_id, write_json
        from .simulator import call_claude
        tools = [json.loads(t) for t in item['tools']] + ([ASK_USER_TOOL] if ask_tool else [])
        prompt = self.template.format(tools, item['question'], response)  # same str(list) formatting as the script
        key = stable_id('w2c-judge-v1', self.command, prompt)
        cached = self.cache_dir / f'{key}.json'
        if cached.exists():
            return json.loads(cached.read_text())
        try:
            text, meta = call_claude(prompt, self.command, work_parent=self.cache_dir, timeout=self.timeout,
                                     retries=self.retries, backoff=10)
        except RuntimeError as exc:
            return {'status': 'judge_failed', 'label': None, 'error': str(exc)}
        label = parse_judge_label(text)
        value = {'status': 'ok' if label else 'parse_failed', 'label': label, 'requested_model': self.model,
                 'cache_key': key, **meta}
        write_json(cached, value)
        return value
