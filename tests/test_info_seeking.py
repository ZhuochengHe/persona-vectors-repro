import os
import sqlite3
from pathlib import Path

import pytest

from info_seeking.agent import parse_generation
from info_seeking.data import select_subset
from info_seeking.env import SQLTaskEnv
from info_seeking.official import CANT_ANSWER, IRRELEVANT_QUESTION, OfficialFiles, parse_judge_prompt
from info_seeking.simulator import extract_blocker_key
from info_seeking.sql_worker import execute_direct

TOOLS = [{'type': 'function', 'function': {'name': name, 'description': '', 'parameters': {
    'type': 'object', 'properties': {arg: {'type': 'string'} for arg in args}, 'required': list(args)}}}
    for name, args in (('execute_sql', ('query',)), ('ask_human', ('question',)),
                       ('get_table_info', ('database_name', 'table_name')))]


def call(name, **params):
    body = ''.join(f'<parameter={k}>\n{v}\n</parameter>\n' for k, v in params.items())
    return f'<tool_call>\n<function={name}>\n{body}</function>\n</tool_call>'


def test_parse_valid_multiline_argument():
    text = 'think a bit\n</think>\n\n' + call('execute_sql', query='SELECT 1\nFROM t') + '<|im_end|>'
    action = parse_generation(text, TOOLS)
    assert action.error_code is None and action.name == 'execute_sql'
    assert action.arguments == {'query': 'SELECT 1\nFROM t'}
    assert action.reasoning == 'think a bit'


@pytest.mark.parametrize('text,code', [
    ('only thoughts</think>\n\nno call', 'missing'),
    ('x</think>\n' + call('ask_human', question='a?') + call('ask_human', question='b?'), 'multiple'),
    ('x</think>\n' + call('drop_table', query='x'), 'invalid_command'),
    ('x</think>\n' + call('execute_sql', query='x', extra='y'), 'unexpected_arg'),
    ('x</think>\n' + call('get_table_info', database_name='d'), 'missing_arg'),
    ('x</think>\n' + call('get_table_info', database_name='d', bogus='z'), 'missing_arg'),  # missing checked first
])
def test_parse_errors(text, code):
    assert parse_generation(text, TOOLS).error_code == code


def test_end_name_argument_is_dropped_and_heredoc_stripped():
    from info_seeking.agent import strip_heredoc
    text = 'x</think>\n' + call('execute_sql', query='SELECT 1\nENDOFSQL', ENDOFSQL='')
    action = parse_generation(text, TOOLS, {'execute_sql': 'ENDOFSQL'})
    assert action.error_code is None and set(action.arguments) == {'query'}
    assert strip_heredoc(action.arguments['query'], 'ENDOFSQL') == 'SELECT 1'
    assert strip_heredoc(' SELECT 2 ', 'ENDOFSQL') == 'SELECT 2'


def test_tool_call_inside_reasoning_is_ignored():
    text = 'maybe ' + call('ask_human', question='q?') + '\n</think>\n\nno call here'
    assert parse_generation(text, TOOLS).error_code == 'missing'


@pytest.mark.parametrize('text,key,mode', [
    ('{"reasoning": "r", "blocker_key": "b1"}', 'b1', 'strict'),
    ('{\n "reasoning": "r",\n "blocker_key": null,\n}', None, 'trailing_comma_repaired'),
    ('```json\n{"reasoning": "r", "blocker_key": "b2"}\n```', 'b2', 'strict'),
    ('{"reasoning": "unescaped "quote"", "blocker_key": "b3"}', 'b3', 'regex'),
    ('{"reasoning": "no key"}', None, 'strict+missing_key'),
    ('{"blocker_key": 3}', None, 'strict+non_string_key'),
])
def test_extract_blocker_key(text, key, mode):
    assert extract_blocker_key(text) == (key, mode)


def test_extract_blocker_key_failure():
    with pytest.raises(ValueError):
        extract_blocker_key('I think it matches b1.')


class FakeSimulator:
    def __init__(self, answers):
        self.answers = answers

    def classify(self, blockers, question):
        value = self.answers[question]
        if value == 'FAIL':
            return {'status': 'parse_failed', 'blocker_key': None}
        return {'status': 'ok', 'blocker_key': value}


def make_env(tmp_path, answers):
    task = {'task_id': 't', 'database_name': 'db', 'business_info': [], 'ground_truth_sql': 'SELECT 1',
            'database_path': str(tmp_path / 'x.sqlite'), 'descriptions_dir': str(tmp_path),
            'blockers': [{'id': 'b1', 'description': 'd1', 'resolution': 'R1', 'example_questions': []},
                         {'id': 'b2', 'description': 'd2', 'resolution': 'R2', 'example_questions': []}]}
    return SQLTaskEnv(task, ask_enabled=True, simulator=FakeSimulator(answers), retriever=None,
                      sql_timeout_seconds=5, external_root=str(tmp_path))


def test_ask_human_cap_failure_and_metrics(tmp_path):
    env = make_env(tmp_path, {'q1?': 'b1', 'q2?': 'b1', 'q3?': 'b1', 'q4?': None, 'q5?': 'FAIL', 'q6?': 'zz'})
    assert env.ask_human('q1?') == 'R1'
    assert env.ask_human('q2?') == 'R1'
    assert env.ask_human('q3?') == IRRELEVANT_QUESTION  # third hit on the same blocker is capped
    assert env.ask_human('q4?') == IRRELEVANT_QUESTION
    assert env.ask_human('q5?') == CANT_ANSWER
    assert env.ask_human('q6?') == IRRELEVANT_QUESTION  # key outside the registry
    assert env.ask_human('ab') == IRRELEVANT_QUESTION  # shorter than 3 characters, no judge call
    m = env.ask_metrics()
    assert m['n_questions'] == 7 and m['blockers_resolved'] == 1 and m['recall'] == 0.5
    assert m['precision_harness'] == pytest.approx(1 / 7)
    assert m['precision_paper'] == pytest.approx(3 / 7)  # q1, q2 and the capped q3 were judged relevant
    assert m['n_judge_failures'] == 1 and m['n_judge_parse_failed'] == 1 and m['n_capped'] == 1
    assert m['n_relevant'] == 3


def test_execute_direct_is_read_only_and_truncates(tmp_path):
    db = tmp_path / 'x.sqlite'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE t(a INT)')
        conn.executemany('INSERT INTO t VALUES (?)', [(i,) for i in range(250)])
    assert execute_direct(str(db), 'SELECT a FROM t WHERE a < 2').startswith('Query executed successfully:\na\n0\n1')
    assert 'truncated to the first 200 rows' in execute_direct(str(db), 'SELECT a FROM t')
    assert execute_direct(str(db), 'DELETE FROM t') == 'Error: non-SELECT query'
    assert execute_direct(str(db), 'SELECT a FROM t WHERE a > 999') == 'Query executed successfully. No results returned.'
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT COUNT(*) FROM t').fetchone()[0] == 250


def test_select_subset_is_deterministic_and_stratified():
    rows = [{'task_id': f'public_sql_{i}', 'database_name': f'db{i % 5}', 'blockers': [0] * (3 + i % 3)}
            for i in range(100)]
    a, b = select_subset(rows, 20, 0), select_subset(rows, 20, 0)
    assert a == b and len(a) == len(set(a)) == 20
    counts = {k: sum(len(rows[int(t.rsplit('_', 1)[1])]['blockers']) == k for t in a) for k in (3, 4, 5)}
    assert sorted(counts.values()) == [6, 7, 7]


SYNTHETIC_SERVER = '''
def create_evaluation_prompt(agent_question: str) -> str:
    blockers_info = []
    for key, blocker in _blocker_registry.items():
        blockers_info.append(
            f"""
BLOCKER: {key}
DESCRIPTION: {blocker.description}
EXAMPLE QUESTIONS: {', '.join(blocker.example_questions)}"""
        )
    return f"""HEAD
{chr(10).join(blockers_info)}
MSG: "{agent_question}"
{{"blocker_key": null,}}
"""
'''


def test_judge_prompt_reconstruction():
    template = parse_judge_prompt(SYNTHETIC_SERVER)
    text = template.render([{'id': 'b1', 'description': 'D', 'example_questions': ['x', 'y']}], 'Why?')
    assert text == 'HEAD\n\nBLOCKER: b1\nDESCRIPTION: D\nEXAMPLE QUESTIONS: x, y\nMSG: "Why?"\n{"blocker_key": null,}\n'


EXTERNAL = Path(os.environ.get('PV_WORK', '/nonexistent')) / 'external'


@pytest.mark.skipif(not (EXTERNAL / 'ask-human-image/x/app/server.py').exists(), reason='official files not available')
def test_official_constants_and_prompt_match_server():
    official = OfficialFiles(EXTERNAL)
    source = official.path('ask_human_server').read_text()
    assert f'CANT_ANSWER = "{CANT_ANSWER}"' in source
    assert f'IRRELEVANT_QUESTION = "{IRRELEVANT_QUESTION}"' in source
    assert 'MAX_ANSWERED_QUESTIONS_PER_BLOCKER = 2' in source
    prompt = official.judge_prompt.render([{'id': 'k', 'description': 'D', 'example_questions': ['Q1', 'Q2']}], 'What?')
    assert prompt.startswith('You are an EXTREMELY PRECISE semantic similarity evaluator')
    assert '\nBLOCKER: k\nDESCRIPTION: D\nEXAMPLE QUESTIONS: Q1, Q2' in prompt and 'AGENT MESSAGE: "What?"' in prompt
    from info_seeking.simulator import ClaudeSimulator
    simulator = ClaudeSimulator(official.judge_prompt, cache_dir=Path(os.environ['PV_WORK']) / 'tmp' / 'judge-test-cache')
    blockers = [{'id': 'k', 'description': 'D', 'example_questions': ['Q1'], 'resolution': 'SECRET_RESOLUTION'}]
    assert 'SECRET_RESOLUTION' not in simulator.prompt(blockers, 'What?')
    assert official.system_prompt(True) != official.system_prompt(False)
    assert 'ask_human' not in official.system_prompt(False)
    assert [t['function']['name'] for t in official.tool_schemas(False)].count('ask_human') == 0
    from info_seeking.trajectory import ASK_PROMPT_PARAGRAPH, CONDITIONS, system_prompt
    prompted = system_prompt(official, CONDITIONS['blocked_ask_prompted'])
    assert ASK_PROMPT_PARAGRAPH in prompted and prompted == system_prompt(official, CONDITIONS['fullinfo_ask_prompted'])
    assert system_prompt(official, CONDITIONS['blocked_ask']) == official.system_prompt(True)
    assert prompted.replace(ASK_PROMPT_PARAGRAPH, '') == official.system_prompt(True)


# ---- When2Call --------------------------------------------------------------------------------
def _w2c_item(sid, variant, tools, question='q', held=None):
    return {'uuid': f'{sid}-{variant}', 'source_id': sid, 'correct_answer': variant, 'question': question,
            'tools': tools, 'held_out_param': held,
            'answers': {'direct': 'd', 'tool_call': '{"name": "f", "arguments": {}}', 'request_for_info': 'r',
                        'cannot_answer': 'c'}}


def test_when2call_groups_and_splits():
    from info_seeking import when2call as w2c
    t1, t2 = ['{"name": "a"}', '{"name": "b"}'], ['{"name": "c"}']
    items = [_w2c_item('s1', 'tool_call', t1), _w2c_item('s1', 'cannot_answer', t1[:1]),
             _w2c_item('s2', 'tool_call', list(reversed(t1))), _w2c_item('s3', 'tool_call', t2)]
    groups = w2c.toolset_group(items)
    assert groups['s1'] == groups['s2'] != groups['s3']  # same tool set (order-insensitive) shares a group
    assert w2c.split_of(groups['s1'], 0) == w2c.split_of(groups['s2'], 0)
    assert {w2c.split_of(f'g{i}', 0) for i in range(200)} == {'train', 'dev', 'test'}
    with pytest.raises(ValueError):
        w2c.toolset_group([_w2c_item('s4', 'cannot_answer', t2)])


def test_when2call_labels_and_judge_parse():
    from info_seeking import when2call as w2c
    from info_seeking.agent import ParsedAction
    item = {'held_out_param': 'city'}
    call = ParsedAction('', '', name='weather', arguments={'city': 'Paris'})
    assert w2c.deterministic_label(call, item, False) == {'label': 'tool_call', 'source': 'parsed', 'tool': 'weather',
                                                          'held_out_supplied': True}
    blank = ParsedAction('', '', name='weather', arguments={'city': ''})
    assert w2c.deterministic_label(blank, item, False)['held_out_supplied'] is False
    ask = ParsedAction('', '', name='ask_user', arguments={'question': 'which city?'})
    assert w2c.deterministic_label(ask, item, True)['label'] == 'request_for_info'
    assert w2c.deterministic_label(ParsedAction('', 'text', error_code='missing'), item, False)['source'] == 'needs_judge'
    assert w2c.deterministic_label(ParsedAction('', '', error_code='multiple'), item, False)['label'] == 'format_error'
    assert w2c.parse_judge_label('{"classification": "direct_answer"}') == 'direct'
    assert w2c.parse_judge_label('```json\n{"classification": "request_for_info"}\n```') == 'request_for_info'
    assert w2c.parse_judge_label('{"classification": "maybe"}') is None


def test_when2call_mcq_metrics():
    from info_seeking import when2call as w2c
    rows = [{'gold': 'tool_call', 'pred': 'tool_call', 'pred_norm': 'tool_call'},
            {'gold': 'request_for_info', 'pred': 'tool_call', 'pred_norm': 'request_for_info'},
            {'gold': 'cannot_answer', 'pred': 'cannot_answer', 'pred_norm': 'direct'}]
    m = w2c.mcq_metrics(rows)
    assert m['pred']['acc'] == pytest.approx(2 / 3) and m['pred_norm']['acc'] == pytest.approx(2 / 3)
    assert m['tool_hallucination_rate'] == pytest.approx(0.5)
    assert m['pred']['confusion']['request_for_info']['tool_call'] == 1


@pytest.mark.skipif(not (EXTERNAL / 'when2call-repo').exists(), reason='When2Call files not available')
def test_when2call_official_files():
    from info_seeking import when2call as w2c
    template = w2c.judge_prompt_template(EXTERNAL)
    assert template.count('{}') == 3 and '"classification"' in template
    items = w2c.load_items(w2c.pinned_path(EXTERNAL, 'mcq'))
    assert len(items) == 3652
    groups = w2c.toolset_group(items)
    assert len(groups) == 1295 and len(set(groups.values())) == 433
    msgs = w2c.candidate_messages(next(i for i in items if i['correct_answer'] == 'request_for_info'))
    assert set(msgs) == set(w2c.ANSWER_ORDER) and msgs['tool_call']['tool_calls'][0]['function']['name']


def test_readout_on_synthetic_data(tmp_path):
    import json as _json
    import torch
    from info_seeking.probe_analysis import auc, readout
    assert auc([0.1, 0.4, 0.35, 0.8], [0, 0, 1, 1]) == pytest.approx(0.75)
    assert auc([1, 1, 1, 1], [0, 1, 0, 1]) == pytest.approx(0.5)  # ties
    g = torch.Generator().manual_seed(0)
    n = 80
    y = torch.tensor([i % 2 == 0 for i in range(n)])
    feats = torch.randn(n, 1, 2, 8, generator=g)
    feats[:, 0, 1, 0] += y.float() * 4  # layer 2 separates the classes, layer 1 does not
    data = {'toy': {'feats': feats, 'y': y, 'groups': [f't{i // 4}' for i in range(n)],
                    'valid': torch.ones(n, 1, dtype=torch.bool), 'baseline': None}}
    readout(data, ('pre',), tmp_path, folds=4)
    summary = _json.loads((tmp_path / 'probe_summary.json').read_text())['toy']
    assert summary['layer'] == 2 and summary['dom_auc'] > 0.95
    assert (tmp_path / 'directions.safetensors').exists()


# ---- Sparse Neurons reproduction ----------------------------------------------------------------
def test_ambiguity_prompt_table_and_aen_rule():
    from info_seeking.ambiguity import PromptTable, appended_phrase, pick_aen_k
    t = PromptTable()
    t.add('a/train', 'q?', 'ambiguous', 'p1')
    t.add('a/test', 'q?', 'ambiguous', 'p1')  # same text in two sets shares one uid (one forward)
    t.add('a/test', 'q in texas?', 'clear', 'p1')
    assert len(t.prompts) == 2 and t.sets['a/train'][0]['uid'] == t.sets['a/test'][0]['uid']
    assert appended_phrase('who won', 'who won in texas') == ' in texas'
    assert appended_phrase('who won', 'which team won') is None
    curve = [{'k': 0, 'acc': 0.9}, {'k': 1, 'acc': 0.88}, {'k': 2, 'acc': 0.6}, {'k': 3, 'acc': 0.55}]
    assert pick_aen_k(curve) == 2  # first k reaching half of the largest drop (0.35 / 2)


DATA = EXTERNAL / 'sparse-neurons-data'


@pytest.mark.skipif(not (DATA / 'original').exists(), reason='original repo files not available')
def test_faithful_split_matches_original_shuffle():
    from info_seeking.ambiguity import PromptTable, faithful_sets
    table = PromptTable()
    info = faithful_sets(DATA, table)
    assert info['ambigqa']['pairs_in_file'] == 4747 and info['situatedqa']['pairs_in_file'] == 8456
    assert info['ambigqa']['pair_ids_on_both_sides'] > 0  # the original split lets pairs cross train/test
    counts = {k: len(v) for k, v in table.sets.items()}
    assert counts['faithful/ambigqa/train'] == 800 and counts['faithful/ambigqa/test'] == 2000


def test_score_with_bundle_selects_aen_dims():
    import numpy as np
    from info_seeking.ambiguity import score_with_bundle
    bundle = {'aen/m/p/d/input_mean/L14/dims': np.array([2, 0]), 'aen/m/p/d/input_mean/L14/coef': np.array([1.0, -1.0], dtype=np.float32),
              'aen/m/p/d/input_mean/L14/intercept': np.array([0.5], dtype=np.float32),
              'm/p/d/pre/L3/coef': np.ones(3, dtype=np.float32), 'm/p/d/pre/L3/intercept': np.array([-1.0], dtype=np.float32)}
    x = np.array([[1.0, 0.0, 3.0], [0.0, 2.0, 0.0]], dtype=np.float32)
    assert score_with_bundle(bundle, 'aen/m/p/d/input_mean/L14', x).tolist() == [2.5, 0.5]  # 3-1+0.5, 0-0+0.5
    assert score_with_bundle(bundle, 'm/p/d/pre/L3', x).tolist() == [3.0, 1.0]


def test_annotation_blocker_normalization():
    from info_seeking.annotate import _json_object, normalize_blocker
    ids = ['no_thrombosis_vs_severe_outcome_contradicting', 'near_to_adulthood_definition']
    assert normalize_blocker('near_to_adulthood_definition', ids) == 'near_to_adulthood_definition'
    assert normalize_blocker('contradicting', ids) == 'no_thrombosis_vs_severe_outcome_contradicting'
    assert normalize_blocker('other: test data', ids) == 'other'
    assert normalize_blocker('definition', ids) == 'near_to_adulthood_definition'
    assert normalize_blocker('unrelated', ids) == 'other'
    assert _json_object('```json\n{"aware": true, "blockers": ["a"],}\n```') == {'aware': True, 'blockers': ['a']}
