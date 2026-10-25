"""Generate a reviewable experiment manifest, never auto-submit a training grid."""
from __future__ import annotations
import json
from pathlib import Path
from .common import CATEGORIES, VERSIONS, EXPERIMENTS, question_splits, write_json

DEPENDENCIES = {'E01':[], 'E02':['E01'], 'E06':['E02'], 'E08':[], 'E09':['E02','E08'],
                'E10':['E02','E08'], 'E11':['E02','E08'], 'E19':['E02','E08']}


def build_plan(config):
    from .inference_tasks import build_extraction_tasks
    subsets = [f'{category}/{version}' for category in config['data']['categories'] for version in VERSIONS]
    extraction_counts = []
    for trait in config['traits']:
        asset = json.loads((Path(config['paths']['upstream']) / f'data_generation/trait_data_extract/{trait}.json').read_text())
        settings = config['extraction']
        tasks = build_extraction_tasks(Path(config['paths']['upstream']),trait,settings['rollouts'],
            question_ids=settings['question_ids'],instruction_ids=settings['instruction_ids'])
        questions, pairs = len(settings['question_ids']), len(settings['instruction_ids'])
        conditions = questions * pairs * 2
        extraction_counts.append({'trait':trait, 'questions':questions, 'instruction_pairs':pairs,
                                  'conditions':conditions, 'rollouts_per_condition':settings['rollouts'],
                                  'responses':len(tasks), 'question_ids':settings['question_ids'],
                                  'instruction_ids':settings['instruction_ids'],
                                  'available_questions':len(asset['questions']),
                                  'available_instruction_pairs':len(asset['instruction'])})
    return {'status':'planned_not_executed','model':config['model'],'judge':config['judge'],
            'generation':config['generation'], 'extraction_counts':extraction_counts,
            'traits':config['traits'], 'experiments':[{ 'id':key,'depends_on':DEPENDENCIES[key],
                'strategy':f'docs/experiments/strategies/{key}.md'} for key in EXPERIMENTS],
            'training_subsets':subsets, 'training_runs_per_seed':len(subsets),
            'question_splits':question_splits(Path(config['paths']['upstream']), config['data']['seed']),
            'paths':config['paths'], 'data':config['data'],
            'required_before_compute':['pin model revision','prepare dedicated environment','run allocation preflight'],
            'notes':['No judge calibration per user instruction.', 'Scratch is temporary; no permanent archive path is configured.',
                     'E11 defaults to targeted II-version branches; no automatic Cartesian training sweep.']}
