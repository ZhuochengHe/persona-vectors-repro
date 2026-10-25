"""E02 pairing, selection, and lazy steering regression checks."""
from copy import deepcopy
from types import SimpleNamespace
import pytest

from persona_repro.common import REPO, load_config, read_jsonl, write_jsonl
from persona_repro.e02 import tasks_for, screen_conditions, rank_eligible, summarize_pair


def scored(index, value, coherence=90, status='ok'):
    return {'sample_id': f'q{index}', 'question_id': index, 'messages': [{'role': 'user', 'content': str(index)}],
            'seed': index, 'truncated': False,
            'scores': {'evil': {'status': status, 'score': value},
                       'coherence': {'status': 'ok', 'score': coherence}}}


def test_e02_frozen_budget_and_seed_ids_match_across_conditions():
    config = load_config(REPO / 'configs/e02.json')
    cells = screen_conditions(config)
    assert len(cells) == 51
    assert sum(len(tasks_for(config, c['trait'], c['split'])) for c in cells) == 1020
    for trait in config['traits']:
        tasks = tasks_for(config, trait, 'dev')
        assert len(tasks) == 20 and len({t['question_id'] for t in tasks}) == 5
        assert {t['rollout'] for t in tasks} == {0, 1, 2, 3}
        splits = config['evaluation']['question_splits'][trait]
        assert not set(splits['dev']) & set(splits['test'])
    assert len(config['steering']['layers']) == len(set(config['steering']['layers'])) == 16


def test_e02_paired_refusal_is_explicit_and_never_zero_imputed():
    base = [scored(0, 20), scored(1, None, status='refusal')]
    rows = [scored(0, 60), scored(1, 100)]
    result = summarize_pair(rows, base, 'evil')
    assert result['trait_gain'] == 40
    assert result['paired_numeric_trait_responses'] == 1
    assert result['paired_numeric_trait_questions'] == 1
    assert result['trait_gain_question_bootstrap_95'] is None


def test_e02_rejects_unpaired_seeds_and_missing_ids():
    base = [scored(0, 20), scored(1, 10)]
    rows = deepcopy(base)
    rows[0]['seed'] = 99
    with pytest.raises(ValueError, match='seed/prompt'):
        summarize_pair(rows, base, 'evil')
    with pytest.raises(ValueError, match='baseline IDs'):
        summarize_pair(base[:1], base, 'evil')


def test_e02_selection_coherence_boundary_and_tiebreaks():
    candidates = [
        {'layer': 20, 'coefficient': 1., 'trait_gain': 40., 'coherence_change': -5.},
        {'layer': 18, 'coefficient': .5, 'trait_gain': 40., 'coherence_change': -4.},
        {'layer': 16, 'coefficient': .5, 'trait_gain': 40., 'coherence_change': -4.},
        {'layer': 24, 'coefficient': 2., 'trait_gain': 99., 'coherence_change': -5.1},
        {'layer': 28, 'coefficient': 1., 'trait_gain': None, 'coherence_change': 0.}]
    assert [x['layer'] for x in rank_eligible(candidates, 5)] == [16, 18, 20]
    assert rank_eligible(candidates[-2:], 5) == []


def test_e02_lazy_shared_runtime_loads_before_hook_and_pairs_seeds(tmp_path, monkeypatch):
    import torch
    import persona_repro.operations as operations
    config = load_config(REPO / 'configs/e02.json')
    task = tasks_for(config, 'evil', 'dev')[:1]
    input_path = tmp_path / 'tasks.jsonl'
    write_jsonl(input_path, task)
    vector_path = tmp_path / 'vector.pt'
    vector_path.write_bytes(b'fixture-hash-only')
    monkeypatch.setattr(operations, 'require_compute', lambda: None)
    monkeypatch.setattr(operations, 'load_vector', lambda *args: torch.ones(2560))
    class LazyRuntime:
        layers = None
        def load(self):
            self.layers = [torch.nn.Identity() for _ in range(32)]
            return self
        def generate(self, messages, **kwargs):
            self.layers[3](torch.zeros(1, 1, 2560))
            return {'answer': 'hello', 'answer_token_ids': [1], 'seed': kwargs['seed']}
    runtime = LazyRuntime()
    zero, nonzero = tmp_path/'zero.jsonl', tmp_path/'nonzero.jsonl'
    for coefficient, output in [(0, zero), (1, nonzero)]:
        operations.generate_file(input_path, output, config, vector_path=vector_path,
                                 layer=4, coefficient=coefficient, runtime=runtime)
        assert not runtime.layers[3]._forward_hooks
    assert read_jsonl(zero)[0]['seed'] == read_jsonl(nonzero)[0]['seed']
    assert read_jsonl(zero)[0]['generation_fingerprint'] != read_jsonl(nonzero)[0]['generation_fingerprint']
