"""Run frozen sampling ablations and fixed-layer candidate controls."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import statistics

from persona_repro.common import generation_fingerprint, read_jsonl, require_compute, write_json
from persona_repro.operations import generate_file, runtime_from_config


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cell_config(config, cell):
    result = deepcopy(config)
    result['generation'].update(cell.get('generation', {}))
    return result


def checked_rows(run, config, cell, scored=False):
    current = cell_config(config, cell)
    tasks = {row['sample_id']: row for row in read_jsonl(run / cell['tasks'])}
    path = run / ('scored' if scored else 'responses') / (cell['id'] + '.jsonl')
    rows = read_jsonl(path)
    vector = run / cell['vector'] if cell.get('vector') else None
    expected = generation_fingerprint(current, vector_digest=digest(vector) if vector else None,
                                      layer=cell.get('layer'), coefficient=cell.get('alpha', 0.0))
    assert len(rows) == len(tasks) == 40
    assert {row['sample_id'] for row in rows} == set(tasks)
    for row in rows:
        assert row['generation_fingerprint'] == expected
        assert row['messages'] == tasks[row['sample_id']]['messages']
        assert row['model_id'] == config['model']['id']
        assert row['model_revision'] == config['model']['revision']
        assert row['trait'] == cell['trait']
    if scored:
        originals = {r['sample_id']: r for r in checked_rows(run, config, cell)}
        for row in rows:
            original = originals[row['sample_id']]
            assert all(row[k] == original[k] for k in ('answer', 'answer_token_ids', 'seed'))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['generate', 'score'])
    parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args()
    require_compute()
    run = args.run
    manifest = json.loads((run / 'manifest.json').read_text())
    for path, expected in manifest['sha256'].items():
        if digest(run / path) != expected:
            raise ValueError(f'Frozen input changed: {path}')
    config = json.loads((run / 'config.json').read_text())
    cells = config['sampling_controls']['conditions']
    if args.stage == 'generate':
        runtime = runtime_from_config(config)
        for cell in cells:
            generate_file(run / cell['tasks'], run / 'responses' / (cell['id'] + '.jsonl'),
                          cell_config(config, cell), runtime=runtime,
                          vector_path=run / cell['vector'] if cell.get('vector') else None,
                          layer=cell.get('layer'), coefficient=cell.get('alpha', 0.0))
            checked_rows(run, config, cell)
        assert not any(block._forward_hooks for block in runtime.layers)
    else:
        from persona_repro.judge import score_files
        from random_direction_control import repetition
        for cell in cells:
            checked_rows(run, config, cell)
        score_files([(run / 'responses' / (c['id'] + '.jsonl'),
                      run / 'scored' / (c['id'] + '.jsonl'), None) for c in cells], config)
        summary = {'conditions': {}, 'parent_run': config['sampling_controls']['parent_run']}
        for cell in cells:
            rows = checked_rows(run, config, cell, scored=True)
            item = {'design': cell, 'responses': len(rows),
                    'truncated_responses': sum(r['truncated'] for r in rows)}
            for metric in (cell['trait'], 'coherence'):
                values = [r['scores'][metric]['score'] for r in rows if r['scores'][metric]['status'] == 'ok']
                item[metric + '_mean'] = statistics.mean(values) if values else None
                item[metric + '_numeric_count'] = len(values)
            stops = set(config['sampling_controls']['stop_ids'])
            counts = []
            for row in rows:
                ids = row['answer_token_ids']
                end = next((i for i, token in enumerate(ids) if token in stops), len(ids))
                counts.append(repetition(ids[:end]))
            item['repetition_4gram_mean'] = statistics.mean(counts)
            summary['conditions'][cell['id']] = item
        write_json(run / 'summary.json', summary)
        doc = Path(config['sampling_controls']['document'])
        text = doc.read_text()
        begin, end = '<!-- sampling-results:start -->', '<!-- sampling-results:end -->'
        lines = ['全部生成与评分完成。以下为各条件数值评分均值；非数值trait评分不计为零。',
                 '| 条件 | trait | coherence | trait数值条数 | 重复率 | 截断 |',
                 '|---|---:|---:|---:|---:|---:|']
        for name, item in summary['conditions'].items():
            trait = item['design']['trait']
            value = item[trait + '_mean']
            t = '无' if value is None else f'{value:.2f}'
            coherence = item['coherence_mean']
            coh = '无' if coherence is None else f'{coherence:.2f}'
            lines.append(f"| {name} | {t} | {coh} | {item[trait + '_numeric_count']} | "
                         f"{item['repetition_4gram_mean']:.1%} | {item['truncated_responses']}/40 |")
        prefix, rest = text.split(begin)
        _, suffix = rest.split(end)
        doc.write_text(prefix + begin + '\n' + '\n'.join(lines) + '\n' + end + suffix)
    write_json(run / 'logs' / (args.stage + '.done.json'), {'stage': args.stage, 'status': 'complete'})


if __name__ == '__main__':
    main()
