"""Run one (task, condition, seed) unit and write its trajectory, decision table and activations.

Format errors follow SWE-agent's forward_with_handling: the model is requeried with a temporary
history (committed history + only the latest failed output + the error message), at most
max_requeries times; a corrected action is committed without the failed turns, and requeries do
not count as steps. Every attempt, failed or not, is recorded as a decision point.
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from .agent import POSITION_KEYS, locate_positions, parse_generation, step_seed, strip_heredoc

CONDITIONS = {
    'blocked_ask': {'ask': True, 'full_info': False},
    'blocked_ask_prompted': {'ask': True, 'full_info': False, 'ask_prompt': True},
    'fullinfo_ask': {'ask': True, 'full_info': True},
    'fullinfo_ask_prompted': {'ask': True, 'full_info': True, 'ask_prompt': True},
    'fullinfo_noask': {'ask': False, 'full_info': True},
    'blocked_noask': {'ask': False, 'full_info': False},
}
# Prompt-induced asking (not part of the official benchmark). Inserted right after the official
# ask_human paragraph; it states when to ask but says nothing about how questions are judged.
ASK_PROMPT_PARAGRAPH = (
    'Asking the analyst is expected whenever information you need is missing or unclear. If a term, '
    'metric, threshold, time frame, value, or the choice between columns or tables is undefined, '
    'ambiguous, or contradicted by the question, the business info, or the schema, call ask_human '
    'about that specific point before writing the final query, instead of choosing an interpretation '
    'yourself.\n\n')


def system_prompt(official, spec: dict) -> str:
    from .official import ASK_PARAGRAPH
    base = official.system_prompt(spec['ask'])
    if not spec.get('ask_prompt'):
        return base
    if ASK_PARAGRAPH not in base:
        raise ValueError('Official ask paragraph missing; cannot insert the ask prompt')
    return base.replace(ASK_PARAGRAPH, ASK_PARAGRAPH + ASK_PROMPT_PARAGRAPH, 1)
OBS_HEADER, OBS_FOOTER = '\n<|im_start|>user\n<tool_response>\n', '\n</tool_response><|im_end|>\n<|im_start|>assistant\n<think>\n'
USER_HEADER, USER_FOOTER = '\n<|im_start|>user\n', '<|im_end|>\n<|im_start|>assistant\n<think>\n'


def unit_name(task_id: str, condition: str, seed: int) -> str:
    return f'{task_id}__{condition}__s{seed}'


def instance_text(official, task: dict, full_info: bool) -> str:
    problem = official.render_full_info(task['problem'], task['blockers']) if full_info else task['problem']
    return official.instance_message(task['database_name'], problem)


def format_error_text(official, action) -> str:
    from jinja2 import Template
    return Template(official.format_error_template).render(error_code=action.error_code,
                                                           exception_message=action.error_message)


def run_unit(*, runtime, official, task: dict, condition: str, seed: int, cfg: dict, env_factory,
             out_dir: Path) -> dict:
    import torch
    from safetensors.torch import save_file
    spec = CONDITIONS[condition]
    env = env_factory(task, spec['ask'])
    tools = official.tool_schemas(spec['ask'])
    end_names = official.end_names()
    system = system_prompt(official, spec)
    first = runtime.initial_prompt(system, instance_text(official, task, spec['full_info']), tools)
    committed = list(first['ids'])
    paired_first = None
    if cfg['capture']['paired_full_info'] and spec['ask'] and not spec['full_info']:
        paired_first = runtime.initial_prompt(system, instance_text(official, task, True), tools)
    continuations = runtime.tool_continuations([t['function']['name'] for t in tools])
    agent_cfg, sampler = cfg['agent'], cfg['sampler']
    obs_span, add_input_mean = None, True
    records, acts, valid, paired_acts, paired_valid = [], [], [], [], []
    end_reason, step = 'max_steps', 0
    started = time.time()
    while step < agent_cfg['max_steps'] and end_reason == 'max_steps':
        prefix, attempt = committed, 0
        while True:
            budget = min(agent_cfg['max_new_tokens'], agent_cfg['context_cap'] - len(prefix))
            if budget < agent_cfg['min_step_budget']:
                end_reason = 'context_limit'
                break
            t0 = time.time()
            gen = runtime.generate(prefix, seed=step_seed(seed, task['task_id'], condition, step, attempt),
                                   sampler=sampler, max_new_tokens=budget)
            gen_seconds = time.time() - t0
            stopped = bool(gen) and gen[-1] in runtime.stop_ids
            text = runtime.tokenizer.decode(gen, skip_special_tokens=False)
            action = parse_generation(text, tools, end_names)
            pos = locate_positions(runtime, gen, len(prefix))
            points = {'pre': pos['pre'], 'think_end': pos['think_end'], 'act_first': pos['act_first'],
                      'obs_mean': obs_span,
                      'think_mean': pos['think_span'] if pos['think_span'][1] > pos['think_span'][0] else None,
                      'input_mean': (0, len(prefix)) if add_input_mean else None}
            full = prefix + gen
            slot = pos['score_slot'] if pos['score_slot_clean'] else None
            t1 = time.time()
            a, v, scores = runtime.capture(full, points, slot, continuations if slot is not None else None)
            acts.append(a); valid.append(v)
            if paired_first is not None:
                shift = len(paired_first['ids']) - len(first['ids'])
                alt = paired_first['ids'] + full[len(first['ids']):]

                def moved(x):
                    if x is None:
                        return None
                    return x + shift if isinstance(x, int) else (x[0] + shift, x[1] + shift)
                alt_points = {k: moved(p) for k, p in points.items() if k != 'input_mean'}
                alt_points['input_mean'] = (0, len(prefix) + shift) if add_input_mean else None
                pa, pv, _ = runtime.capture(alt, alt_points)
                paired_acts.append(pa); paired_valid.append(pv)
            capture_seconds = time.time() - t1
            chosen_cont_ok = None
            if slot is not None and action.name in continuations and continuations[action.name]:
                cont = continuations[action.name]
                rel = slot + 1 - len(prefix)
                chosen_cont_ok = gen[rel:rel + len(cont)] == cont
            resolved_before = sorted({q['blocker_name'] for q in env.questions if q['blocker_name']})
            record = {'step': step, 'attempt': attempt, 'prefix_len': len(prefix), 'committed_len': len(committed),
                      'requery_suffix_ids': prefix[len(committed):] if attempt else None, 'gen_len': len(gen),
                      'finish': 'eos' if stopped else 'length', 'think_closed': pos['think_closed'],
                      'n_think_tokens': pos['think_span'][1] - pos['think_span'][0],
                      'positions': {k: points[k] for k in POSITION_KEYS}, 'score_slot': pos['score_slot'],
                      'score_slot_clean': pos['score_slot_clean'], 'tool_logprobs': scores,
                      'chosen_continuation_matches': chosen_cont_ok, 'resolved_before': resolved_before,
                      'remaining_before': len(task['blockers']) - len(resolved_before),
                      'gen_seconds': round(gen_seconds, 2), 'capture_seconds': round(capture_seconds, 2),
                      'text': text}
            records.append(record)
            if not stopped:
                gen = gen + [runtime.special['<|im_end|>']]
            if action.error_code:
                record.update(action='format_error', error_code=action.error_code, error_message=action.error_message)
                if attempt + 1 >= agent_cfg['max_requeries']:
                    end_reason = 'format_error_limit'
                    break
                block, _ = runtime.append_block(USER_HEADER, format_error_text(official, action).strip(), USER_FOOTER)
                prefix, attempt = committed + gen + block, attempt + 1
                continue
            arguments = {k: (strip_heredoc(v, end_names[action.name]) if action.name in end_names else v)
                         for k, v in action.arguments.items()}
            record.update(action=action.name, arguments={k: v[:2000] for k, v in arguments.items()})
            n_questions = len(env.questions)
            observation = env.call(action.name, arguments)
            add_input_mean = False
            if action.name == 'ask_human':
                asked = env.questions[n_questions]
                record.update(ask_outcome=asked['outcome'], ask_blocker=asked['blocker_name'],
                              ask_judged=asked['judged_blocker_key'])
                add_input_mean = True
            record['observation'] = observation[:4000]
            committed = committed + gen
            if action.name == 'submit_sql':
                end_reason = 'submitted'
                break
            next_step, no_output = official.observation_templates
            body = next_step.replace('{{observation}}', observation) if observation.strip() else no_output
            block, span = runtime.append_block(OBS_HEADER, body.strip(), OBS_FOOTER)
            obs_span = (len(committed) + span[0], len(committed) + span[1]) if span[1] > span[0] else None
            committed = committed + block
            break
        step += 1
    verify = env.verify()
    result = {'task_id': task['task_id'], 'condition': condition, 'seed': seed, 'end_reason': end_reason,
              'n_steps': step, 'n_decision_points': len(records), 'final_len': len(committed),
              'seconds': round(time.time() - started, 1), 'verify': verify,
              'ask_metrics': env.ask_metrics() if spec['ask'] else None,
              'n_format_errors': sum(1 for r in records if r['action'] == 'format_error'),
              'n_length_truncated': sum(1 for r in records if r['finish'] == 'length'),
              'tool_continuations': continuations, 'first_prompt_len': len(first['ids']),
              'user_span': first['user_span'], 'paired_user_span': paired_first['user_span'] if paired_first else None}
    tmp = out_dir.with_name(out_dir.name + '.tmp')
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    (tmp / 'decisions.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records))
    (tmp / 'trajectory.json').write_text(json.dumps({**result, 'questions': env.questions, 'token_ids': committed},
                                                    ensure_ascii=False))
    tensors = {}
    if acts:
        tensors['acts'] = torch.stack(acts).contiguous()
        tensors['valid'] = torch.stack(valid).contiguous()
    if paired_acts:
        tensors['paired_acts'] = torch.stack(paired_acts).contiguous()
        tensors['paired_valid'] = torch.stack(paired_valid).contiguous()
    if tensors:
        save_file(tensors, str(tmp / 'activations.safetensors'),
                  metadata={'position_keys': ','.join(POSITION_KEYS), 'layers': '1-based block outputs; row i = layer i+1'})
    (tmp / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=1))
    if out_dir.exists():
        shutil.rmtree(out_dir)
    tmp.rename(out_dir)
    return result
