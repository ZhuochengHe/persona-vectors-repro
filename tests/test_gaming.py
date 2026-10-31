"""Scientific protocol guards: disjoint tasks and development-only selection."""
import pytest
from persona_repro.gaming import extraction_tasks, game_tasks, select_layer


def candidate(layer=12, alpha=0.8, gain=20, coherence=85, **overrides):
    row = dict(layer=layer, coefficient=alpha, trait_gain=gain, coherence_mean=coherence,
               paired_numeric_trait_responses=20, paired_numeric_trait_questions=5,
               split='development')
    row.update(overrides)
    return row


def test_high_gain_collapsed_layer_is_not_selected():
    result = select_layer([candidate(19, gain=90, coherence=20), candidate(12)])
    assert result['selected_by_coherence_floor']['75']['layer'] == 12


def test_thresholds_and_low_numeric_coverage():
    result = select_layer([candidate(14, gain=50, coherence=77), candidate(18, gain=10, coherence=88),
                           candidate(19, gain=100, paired_numeric_trait_responses=2)])
    assert result['selected_by_coherence_floor']['75']['layer'] == 14
    assert result['selected_by_coherence_floor']['80']['layer'] == 18


def test_no_eligible_setting_is_explicit():
    assert select_layer([candidate(gain=0)])['selected_by_coherence_floor']['75'] is None


def test_confirmation_cannot_be_used_for_selection():
    with pytest.raises(ValueError, match='development'):
        select_layer([candidate(split='evaluation')])


def test_extraction_is_paired_and_retains_each_instruction():
    asset = {'questions': [f'question {i}' for i in range(40)],
             'instruction': [{'pos': f'positive {i}', 'neg': f'negative {i}'} for i in range(5)]}
    rows = extraction_tasks(asset)
    assert len(rows) == len({r['sample_id'] for r in rows}) == 400
    assert len({r['pair_id'] for r in rows}) == 200
    assert {r['instruction_id'] for r in rows} == set(range(5))


def test_independent_split_sample_ids_and_verbatim_prompts():
    questions = [{'game': 'Dictator', 'text': 'Exact original game prompt.'}]
    development = game_tasks(questions, 'development', 4)
    evaluation = game_tasks(questions, 'evaluation', 20)
    assert not {r['sample_id'] for r in development} & {r['sample_id'] for r in evaluation}
    assert evaluation[0]['messages'] == [{'role': 'user', 'content': questions[0]['text']}]


def test_equal_gain_prefers_coherence_then_smaller_alpha():
    result = select_layer([candidate(14, alpha=1.2), candidate(18, alpha=0.8), candidate(19, coherence=82)])
    assert result['selected_by_coherence_floor']['75']['layer'] == 18
