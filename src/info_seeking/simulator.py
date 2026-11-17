"""Simulated human for ask_human: an isolated headless Claude Code call that only classifies.

The judge sees the official prompt (blocker id, description and example questions, never the
resolution) and returns a blocker key or null. The environment returns the registry resolution.
Deviations from the paper judge (Llama-3.3-70B, temperature 0.05): model, no temperature control,
Claude Code default reasoning at the configured effort, and the managed CLAUDE.md that cannot be
disabled on this host. All are recorded per call.
"""
from __future__ import annotations

import json
import random
import re
import subprocess
import tempfile
import time
from pathlib import Path

from persona_repro.common import stable_id, write_json

SYSTEM_PROMPT = 'You are a precise evaluator. Follow the user instructions exactly and reply only in the requested format.'

LENIENT_RUBRIC = """You are evaluating whether a question from an agent targets a known blocker in a task.

AVAILABLE BLOCKERS:
{blockers}

AGENT MESSAGE: "{question}"

Decide whether a helpful human collaborator who knows the resolution of exactly one of these blockers
would naturally answer this message with that resolution. The message may include context, may state
an assumption and ask for confirmation, and may quote a term from the task. Reject only if it targets
none of the blockers, asks about several different blockers at once, or is too generic to identify one.

Respond in JSON only: {{"reasoning": "...", "blocker_key": "<ID or null>"}}"""


def extract_blocker_key(text: str) -> tuple[str | None, str]:
    """Return (blocker_key, parse_mode). Raises ValueError when no JSON object can be recovered.

    Valid JSON without a string blocker_key is a non-match, as `result.get("blocker_key")` in the
    official server."""
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    body = match.group(1).strip() if match else text.strip()
    try:
        value = json.loads(body)
        mode = 'strict'
    except json.JSONDecodeError:
        # The official null-case example ends with a trailing comma; models often copy it.
        repaired = re.sub(r',\s*([}\]])', r'\1', body)
        try:
            value = json.loads(repaired)
            mode = 'trailing_comma_repaired'
        except json.JSONDecodeError:
            found = re.search(r'"blocker_key"\s*:\s*(null|"([^"\\]*)")', body)
            if not found:
                raise ValueError('No blocker_key in judge output')
            return (None if found.group(1) == 'null' else found.group(2)), 'regex'
    if not isinstance(value, dict):
        raise ValueError('Judge output is not a JSON object')
    key = value.get('blocker_key')
    if key is not None and not isinstance(key, str):
        return None, mode + '+non_string_key'
    if 'blocker_key' not in value:
        return None, mode + '+missing_key'
    return key, mode


def lenient_prompt(blockers: list[dict], question: str) -> str:
    blocks = '\n'.join(f"\nBLOCKER: {b['id']}\nDESCRIPTION: {b['description']}\n"
                       f"EXAMPLE QUESTIONS: {', '.join(b.get('example_questions') or [])}" for b in blockers)
    return LENIENT_RUBRIC.format(blockers=blocks, question=question)


class ClaudeSimulator:
    def __init__(self, prompt_template, *, cache_dir: str | Path, model: str = 'haiku', effort: str = 'low',
                 timeout_seconds: float = 180, retries: int = 2, backoff_seconds: float = 10,
                 rubric: str = 'official'):
        if rubric not in ('official', 'lenient'):
            raise ValueError('rubric must be official or lenient')
        self.template, self.rubric = prompt_template, rubric
        self.model, self.effort = model, effort
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout, self.retries, self.backoff = timeout_seconds, retries, backoff_seconds

    def prompt(self, blockers: list[dict], question: str) -> str:
        visible = [{'id': b['id'], 'description': b['description'], 'example_questions': b.get('example_questions') or []}
                   for b in blockers]
        if self.rubric == 'official':
            return self.template.render(visible, question)
        return lenient_prompt(visible, question)

    def command(self) -> list[str]:
        return claude_command(self.model, self.effort)

    def classify(self, blockers: list[dict], question: str) -> dict:
        prompt = self.prompt(blockers, question)
        key = stable_id('hil-ask-judge-v2', self.rubric, self.command(), prompt)
        cached = self.cache_dir / f'{key}.json'
        if cached.exists():
            return json.loads(cached.read_text())
        # Only transport/CLI failures are retried (the official server retries failed API calls only);
        # an unparseable verdict is final and becomes CANT_ANSWER, as in the official server.
        try:
            text, base = call_claude(prompt, self.command(), work_parent=self.cache_dir, timeout=self.timeout,
                                     retries=self.retries, backoff=self.backoff)
        except RuntimeError as exc:
            # Not cached: a later resume retries. The official server answers CANT_ANSWER here.
            return {'status': 'judge_failed', 'blocker_key': None, 'error': str(exc), 'rubric': self.rubric,
                    'requested_model': self.model, 'cache_key': key}
        base.update(rubric=self.rubric, requested_model=self.model, cache_key=key)
        try:
            blocker_key, parse_mode = extract_blocker_key(text)
            value = {'status': 'ok', 'blocker_key': blocker_key, 'parse_mode': parse_mode, **base}
        except ValueError as exc:
            value = {'status': 'parse_failed', 'blocker_key': None, 'error': str(exc), **base}
        write_json(cached, value)
        return value


def claude_command(model: str, effort: str) -> list[str]:
    """Isolated headless Claude Code call: no tools, MCP servers or user settings; fixed system prompt."""
    return ['claude', '-p', '--model', model, '--effort', effort, '--tools', '',
            '--strict-mcp-config', '--setting-sources', '', '--no-session-persistence',
            '--disable-slash-commands', '--exclude-dynamic-system-prompt-sections',
            '--output-format', 'json', '--system-prompt', SYSTEM_PROMPT]


def call_claude(prompt: str, command: list[str], *, work_parent: Path, timeout: float, retries: int,
                backoff: float) -> tuple[str, dict]:
    """Run one prompt from an empty temp cwd; retry transport/CLI failures only.

    Returns (result_text, metadata). Raises RuntimeError after the retries are exhausted."""
    last_error = None
    for attempt in range(retries + 1):
        try:
            with tempfile.TemporaryDirectory(prefix='claude-call-', dir=work_parent) as work:
                started = time.time()
                result = subprocess.run(command, input=prompt, text=True, cwd=work, capture_output=True, timeout=timeout)
            if result.returncode:
                raise RuntimeError(f'claude exited {result.returncode}: {result.stderr[-500:]}')
            envelope = json.loads(result.stdout)
            if envelope.get('is_error'):
                raise RuntimeError(f"claude error: {str(envelope.get('result'))[:500]}")
        except (subprocess.TimeoutExpired, OSError, RuntimeError, json.JSONDecodeError) as exc:
            last_error = f'{type(exc).__name__}: {exc}'
            if attempt < retries:
                time.sleep(backoff * 2 ** attempt + random.uniform(0, 2))
            continue
        text = envelope.get('result') or ''
        return text, {'raw': text[-4000:], 'resolved_models': sorted((envelope.get('modelUsage') or {}).keys()),
                      'cost_usd': envelope.get('total_cost_usd'), 'seconds': round(time.time() - started, 2),
                      'attempts': attempt + 1}
    raise RuntimeError(f'Claude call failed after retries: {last_error}')
