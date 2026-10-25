from persona_repro.e02_coherent import select_coherent
import json
import pytest
from persona_repro.common import load_config


def test_subset_is_explicit_opt_in(tmp_path):
    path = tmp_path / 'config.json'
    data = {'traits': ['evil'], 'paths': {}, 'judge': {'model': 'gpt-5.6-luna', 'calibration': False}}
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_config(path)
    assert load_config(path, allow_trait_subset=True)['traits'] == ['evil']
    data['traits'] = ['evil', 'evil']
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_config(path, allow_trait_subset=True)


def test_portable_storage_paths_are_explicit(tmp_path, monkeypatch):
    path = tmp_path / 'config.json'
    path.write_text(json.dumps({'traits': ['evil'],
        'paths': {'work': '${PV_WORK}', 'upstream': '${PV_ROOT}/upstream'},
        'reuse': {'e02_run': '${PV_WORK}/runs/previous'},
        'judge': {'model': 'gpt-5.6-luna', 'calibration': False}}))
    monkeypatch.delenv('PV_WORK', raising=False)
    monkeypatch.delenv('PV_ROOT', raising=False)
    with pytest.raises(ValueError, match='Set PV_WORK'):
        load_config(path, allow_trait_subset=True)
    monkeypatch.setenv('PV_WORK', str(tmp_path / 'storage'))
    monkeypatch.setenv('PV_ROOT', str(tmp_path / 'repo'))
    result = load_config(path, allow_trait_subset=True)
    assert result['paths'] == {'work': str(tmp_path / 'storage'), 'upstream': str(tmp_path / 'repo/upstream')}
    assert result['reuse']['e02_run'] == str(tmp_path / 'storage/runs/previous')


def cfg():
    return {'traits': ['evil'], 'steering': {'coherence_thresholds': [80, 75],
            'primary_coherence_floor': 80, 'layers': [4, 15, 19]}}


def row(layer, alpha, coherence, gain):
    return {'trait': 'evil', 'layer': layer, 'coefficient': alpha,
            'coherence_mean': coherence, 'trait_gain': gain}


def test_thresholds_exclude_collapsed_winner_and_deduplicate_baseline():
    result = select_coherent([row(19, 1, 20, 90), row(15, .5, 82, 20),
                              row(4, 1, 78, 30)], cfg())
    assert result['selected_by_coherence_floor']['80']['evil']['layer'] == 15
    assert result['selected_by_coherence_floor']['75']['evil']['layer'] == 4
    assert len(result['test_conditions']) == 3
    assert all(c['split'] == 'test' for c in result['test_conditions'])


def test_no_positive_gain_or_numeric_coherence_has_no_fallback():
    result = select_coherent([row(4, .1, 90, -1), row(15, .5, None, 90),
                              row(19, 1, float('nan'), 95)], cfg())
    assert result['selected_by_coherence_floor']['80']['evil'] is None
    assert result['test_conditions'] == []


def test_ties_and_inclusive_threshold():
    result = select_coherent([row(19, 1, 80, 10), row(15, .5, 80, 10),
                              row(4, .5, 80, 10)], cfg())
    assert result['selected_by_coherence_floor']['80']['evil']['layer'] == 4
    assert len(result['test_conditions']) == 2


def test_top_layers_are_distinct_and_show_incoherent_candidates():
    result = select_coherent([row(19, 1, 20, 90), row(19, .5, 55, 40),
                              row(15, .5, 82, 20)], cfg())
    top = result['top_five_distinct_layers_by_trait_gain_without_coherence_gate']['evil']
    assert [r['layer'] for r in top] == [19, 15]
    assert result['selected_by_coherence_floor']['80']['evil']['layer'] == 15
