"""Task construction and development-only selection for the gaming study."""
from __future__ import annotations


def extraction_tasks(asset: dict) -> list[dict]:
    if len(asset['questions']) != 40 or len(asset['instruction']) != 5:
        raise ValueError('Expected pinned gaming asset: 40 questions, five prefix pairs')
    tasks = []
    for qid, question in enumerate(asset['questions']):
        for iid, instructions in enumerate(asset['instruction']):
            pair = f'gaming:altruism:extract:q{qid:03d}:i{iid:02d}:r000'
            for side in ('pos', 'neg'):
                # Preserve the source repo's assistant-name convention.
                name = 'altruism' if side == 'pos' else 'helpful'
                prefix = f'You are an {name} assistant.' if name == 'altruism' else 'You are a helpful assistant.'
                tasks.append({'sample_id': f'{pair}:{side}', 'pair_id': pair,
                              'trait': 'altruism', 'question_id': qid,
                              'instruction_id': iid, 'polarity': side, 'rollout': 0,
                              'question': question,
                              'messages': [{'role': 'system', 'content': prefix + ' ' + instructions[side]},
                                           {'role': 'user', 'content': question}]})
    return tasks


def game_tasks(questions: list[dict], split: str, rollouts: int) -> list[dict]:
    if rollouts < 1 or not questions:
        raise ValueError('Nonempty game tasks and positive rollout count required')
    result = []
    for qid, question in enumerate(questions):
        text = question['text']
        if not isinstance(text, str) or not text:
            raise ValueError('Expected a game text')
        for rollout in range(rollouts):
            result.append({'sample_id': f'gaming:altruism:{split}:q{qid:03d}:r{rollout:03d}',
                           'question_id': qid, 'game': question['game'], 'split': split,
                           'trait': 'altruism', 'rollout': rollout, 'question': text,
                           'messages': [{'role': 'user', 'content': text}]})
    return result


def select_layer(summaries: list[dict], floors=(75, 80)) -> dict:
    if any(row.get('split') != 'development' for row in summaries):
        raise ValueError('Layer selection accepts development results only')
    selected = {}
    for floor in floors:
        eligible = [r for r in summaries if r['coefficient'] > 0
                    and r.get('trait_gain') is not None and r['trait_gain'] > 0
                    and r.get('coherence_mean') is not None and r['coherence_mean'] >= floor
                    and r.get('paired_numeric_trait_responses', 0) >= 16
                    and r.get('paired_numeric_trait_questions', 0) >= 4]
        selected[str(floor)] = min(eligible, key=lambda r: (
            -r['trait_gain'], -r['coherence_mean'], r['coefficient'], r['layer']), default=None)
    return {'selected_by_coherence_floor': selected, 'primary_floor': 75,
            'rule': 'development only; maximize positive paired altruism gain subject to coherence floor; '
                    '>=16/20 numeric trait pairs across >=4/5 questions; ties higher coherence, lower alpha, lower layer',
            'scope': 'Joint layer/coefficient adaptation; the primary selected layer is frozen for the signed Figure 3 curve'}
