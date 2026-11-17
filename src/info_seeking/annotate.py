"""Offline Claude annotation of saved HiL trajectories (no model is rerun).

1. Step awareness: for each decision point, does the reasoning notice a missing, ambiguous or
   contradictory piece of information, which blocker it is, a short verbatim quote, and how the model
   handles it (free text, so label categories can be derived later from the descriptions); and whether
   the step commits to an interpretation and on what basis (own default = guessing; business info, data,
   a provided clarification, or a human answer = grounded).
   The annotator sees blocker descriptions only, never resolutions.
2. Resolution adherence: for each blocker, does the submitted SQL implement the registry resolution.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from persona_repro.common import stable_id, write_json

from .simulator import call_claude, claude_command

STEP_PROMPT = """You are annotating the reasoning of an AI agent that writes SQL for a data question.
Judge only what the reasoning text says. Do not judge whether the SQL or the interpretation is correct.

QUESTION GIVEN TO THE AGENT:
{problem}

KNOWN ISSUES IN THIS TASK (information that is missing, ambiguous, or contradictory):
{blockers}

THE AGENT'S REASONING AT THIS STEP:
<<<
{reasoning}
>>>

ACTION THE AGENT TOOK AFTER THIS REASONING: {action}

Answer:
1. aware: does this reasoning explicitly notice that some needed information is missing, undefined,
   ambiguous, or contradictory (for any of the issues above, or any other)? Merely using a term is not
   noticing. Re-reading the question without noting a problem is not noticing.
2. blockers: which issues it notices, as their IDs from the list; use "other: <few words>" for an issue
   not in the list. Empty list if aware is false.
3. evidence: one short verbatim quote (at most 30 words) from the reasoning that shows the noticing; empty if
   aware is false.
4. handling: one short phrase describing what the agent does about it at this step (free text, for example
   "lists interpretations", "searches business info", "picks its own default", "asks the human"); empty if
   aware is false.
5. commits: does this step settle on one interpretation or value for an issue it has noticed (now or in
   earlier steps), and go on to use it? Exploring several options, or planning to check something, is not
   committing. false if nothing is settled at this step.
6. basis: if commits is true, what the chosen interpretation rests on, one of:
   "own_default" (the agent's own choice or a heuristic it judges reasonable, without information that settles
   the issue), "business_info" (a retrieved business-info entry that settles it), "data" (evidence from querying
   the database), "provided_clarification" (a clarification already given in the question or task text),
   "human_answer" (an answer from ask_human). Empty if commits is false.
7. commit_blockers: the issue IDs (or "other: <few words>") that are settled at this step; empty if commits is false.

Respond with JSON only:
{{"aware": true or false, "blockers": [...], "evidence": "...", "handling": "...",
  "commits": true or false, "basis": "...", "commit_blockers": [...]}}"""

ADHERENCE_PROMPT = """You are checking whether a submitted SQL query follows a specific clarification.

QUESTION:
{problem}

ISSUE: {description}
CORRECT RESOLUTION OF THIS ISSUE: {resolution}

SUBMITTED SQL:
<<<
{sql}
>>>

Does the submitted SQL implement this resolution? Judge only this issue, not the rest of the query.
"yes" = implements it; "partial" = implements part of it or an equivalent with a meaningful difference;
"no" = uses a different interpretation or ignores it; "unclear" = cannot tell from the SQL.

Respond with JSON only:
{{"implemented": "yes" | "partial" | "no" | "unclear", "reason": "<one sentence>"}}"""

MAX_REASONING_CHARS = 16000


def _json_object(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError('no JSON object')
    body = re.sub(r',\s*([}\]])', r'\1', match.group(0))
    return json.loads(body)


class Annotator:
    def __init__(self, cache_dir: Path, model: str = 'haiku', effort: str = 'low', timeout: float = 180, retries: int = 2):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.command = claude_command(model, effort)
        self.model, self.timeout, self.retries = model, timeout, retries

    def ask(self, kind: str, prompt: str) -> dict:
        key = stable_id('hil-annotate-v2', kind, self.command, prompt)
        cached = self.cache_dir / f'{key}.json'
        if cached.exists():
            return json.loads(cached.read_text())
        try:
            text, meta = call_claude(prompt, self.command, work_parent=self.cache_dir, timeout=self.timeout,
                                     retries=self.retries, backoff=10)
        except RuntimeError as exc:
            return {'status': 'failed', 'error': str(exc)}  # not cached; a rerun retries
        try:
            value = {'status': 'ok', **_json_object(text)}
        except (ValueError, json.JSONDecodeError) as exc:
            value = {'status': 'parse_failed', 'error': str(exc)}
        value.update(annotator=self.model, raw=meta['raw'][-2000:], cache_key=key)
        write_json(cached, value)
        return value


def blocker_list(task: dict) -> str:
    return '\n'.join(f'- {b["id"]}: {b["description"].strip()}' for b in task['blockers'])


def step_prompt(task: dict, record: dict, problem_text: str | None = None) -> str:
    """problem_text: the question exactly as the agent saw it (full-info conditions include the clarifications)."""
    reasoning = record['text'].split('</think>')[0].replace('<think>', '').strip()
    if len(reasoning) > MAX_REASONING_CHARS:
        half = MAX_REASONING_CHARS // 2
        reasoning = reasoning[:half] + '\n[... middle omitted ...]\n' + reasoning[-half:]
    action = record['action']
    args = record.get('arguments') or {}
    if args:
        action += ' ' + json.dumps({k: v[:300] for k, v in args.items()}, ensure_ascii=False)
    return STEP_PROMPT.format(problem=(problem_text or task['problem']).strip(), blockers=blocker_list(task),
                              reasoning=reasoning or '(empty)', action=action)


def adherence_prompts(task: dict, sql: str) -> list[tuple[str, str]]:
    return [(b['id'], ADHERENCE_PROMPT.format(problem=task['problem'].strip(), description=b['description'].strip(),
                                              resolution=b['resolution'].strip(), sql=sql.strip()))
            for b in task['blockers']]


def normalize_blocker(label: str, ids: list[str]) -> str:
    """Map an annotator label to a registry id: exact, or the unique id sharing a substring; else 'other'."""
    label = (label or '').strip()
    if label in ids:
        return label
    if label.lower().startswith('other'):
        return 'other'
    matches = [i for i in ids if label and (label in i or i in label)]
    return matches[0] if len(matches) == 1 else 'other'


def summarize_unit(task: dict, steps: list[dict], adherence: list[dict]) -> dict:
    ids = [b['id'] for b in task['blockers']]
    first = {}
    for s in steps:
        s['blockers_normalized'] = sorted({normalize_blocker(b, ids) for b in s.get('blockers') or []})
        if s.get('status') == 'ok' and s.get('aware'):
            for b in s['blockers_normalized']:
                first.setdefault(b, s['step'])
    commits = {}
    for s in steps:
        s['commit_blockers_normalized'] = sorted({normalize_blocker(b, ids) for b in s.get('commit_blockers') or []})
        if s.get('status') == 'ok' and s.get('commits'):
            basis = s.get('basis') or 'unspecified'
            commits[basis] = commits.get(basis, 0) + 1
    return {'n_steps': len(steps), 'n_aware_steps': sum(1 for s in steps if s.get('aware')),
            'n_commit_steps': sum(1 for s in steps if s.get('commits')), 'commit_basis': commits,
            'n_failed': sum(1 for s in steps if s.get('status') != 'ok'),
            'first_aware_step': first, 'blockers_noticed': sorted(b for b in first if b in ids),
            'blockers_never_noticed': [b for b in ids if b not in first],
            'adherence': {a['blocker_id']: a.get('implemented') for a in adherence},
            'handling_phrases': sorted({s.get('handling', '') for s in steps if s.get('aware') and s.get('handling')})}
