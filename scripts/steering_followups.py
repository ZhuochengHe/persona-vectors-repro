"""Position intervention controls and fresh sycophantic extraction for layer sweeps."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import statistics

from persona_repro.common import (generation_fingerprint, read_jsonl, require_compute,
                                  write_json, write_jsonl)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def position_config(config, mode):
    result = deepcopy(config)
    if mode == 'all':
        result['generation']['steering_positions'] = 'all'
    else:
        result['generation'].pop('steering_positions', None)
    return result


def report(run, config):
    """Refresh only the explicit results block in the user-requested experiment document."""
    positions = json.loads((run / 'positions/summary.json').read_text())
    lines = ['\n两组扫描和位置对照均已完成。以下结果由冻结的实验汇总文件生成。\n',
             '| 第12层设置 | trait均值 | coherence均值 | 重复4-gram比例 |',
             '|---|---:|---:|---:|']
    for name, row in positions['conditions'].items():
        trait = row['trait_mean']
        trait_text = '无数值评分' if trait is None else f'{trait:.2f}'
        lines.append(f"| {name} | {trait_text} | {row['coherence_mean']:.2f} | {row['repetition_4gram_mean']:.1%} |")
    lines += ['\n各trait的开发集选层及固定测试集验证：\n',
              '| trait / 门槛 | 层 / α | 开发集trait增量 | 开发集coherence | 测试集trait增量 | 测试集coherence |',
              '|---|---|---:|---:|---:|---:|']
    findings = []
    for trait in ('evil', 'sycophantic'):
        scan = Path(config['followups'][f'{trait}_scan'])
        selection = json.loads((scan / 'selection.json').read_text())
        heldout = json.loads((scan / 'heldout-summary.json').read_text())
        for floor, choices in selection['selected_by_coherence_floor'].items():
            selected = choices[trait]
            if selected is None:
                lines.append(f'| {trait} / {floor} | 无合格设置 | — | — | — | — |')
                continue
            row = heldout['by_coherence_floor'][floor][trait]
            gain = row['trait_gain']
            gain_text = '无配对数值评分' if gain is None else f'{gain:.2f}'
            lines.append(f"| {trait} / {floor} | {selected['layer']} / {selected['coefficient']} | "
                         f"{selected['trait_gain']:.2f} | {selected['coherence_mean']:.2f} | {gain_text} | {row['coherence_mean']:.2f} |")
            state = '达到' if row['coherence_mean'] >= float(floor) else '未达到'
            findings.append(f"- {trait} 按{floor}门槛选出的设置，在测试集{state}该coherence门槛；不据测试结果重新选层。")
    lines += ['\n初步解读：\n'] + findings
    for alpha in config['followups']['position_alphas']:
        label = str(alpha).replace('.', 'p')
        response = positions['conditions'][f'response-a{label}']
        all_tokens = positions['conditions'][f'all-a{label}']
        delta = all_tokens['coherence_mean'] - response['coherence_mean']
        lines.append(f'- evil第12层 α={alpha}：all相对response的平均coherence变化为{delta:+.2f}；需结合trait与重复率判断是否改善权衡。')
    lines += ['- 这些对照不能单独证明安全训练导致崩溃；trait方向、向量范数、题目和提取样本均有差异。',
              '- 逐层完整曲线、排名及非数值评分计数保存在各run的development-summary.json、selection.json和heldout-summary.json。\n']
    path = Path(config['followups']['document'])
    text = path.read_text()
    start, end = '<!-- followup-results:start -->', '<!-- followup-results:end -->'
    assert text.count(start) == text.count(end) == 1
    prefix, rest = text.split(start)
    _, suffix = rest.split(end)
    path.write_text(prefix + start + '\n' + '\n'.join(lines) + '\n' + end + suffix)
    write_json(run / 'logs/report.done.json', {'status': 'complete', 'document': str(path)})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['positions-generate', 'positions-score', 'syc-generate', 'syc-score', 'syc-vectors', 'report'])
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--arm', type=int, choices=[0, 1])
    args = parser.parse_args()
    require_compute()
    run = args.run
    manifest = json.loads((run / 'manifest.json').read_text())
    for relative, expected in manifest['sha256'].items():
        if digest(run / relative) != expected:
            raise ValueError(f'Frozen follow-up input changed: {relative}')
    config = json.loads((run / 'config.json').read_text())
    if args.stage == 'report':
        report(run, config)
    elif args.stage.startswith('syc-'):
        from persona_repro.operations import generate_file, extract_vectors
        from persona_repro.judge import score_files
        extraction = json.loads((run / 'extraction-config.json').read_text())
        output = run / 'extraction/responses.jsonl'
        scored = run / 'extraction/scored.jsonl'
        if args.stage == 'syc-generate':
            generate_file(run / 'tasks/sycophantic-extract.jsonl', output, extraction)
        elif args.stage == 'syc-score':
            assert len(read_jsonl(output)) == 180
            assert all(row['generation_fingerprint'] == generation_fingerprint(extraction) for row in read_jsonl(output))
            score_files([(output, scored, None)], extraction)
        else:
            extract_vectors(scored, run / 'vectors/sycophantic.pt', extraction)
            scan = Path(config['followups']['sycophantic_scan'])
            frozen = json.loads((scan / 'manifest.json').read_text())
            expected = frozen['vectors']['sycophantic']['sha256']
            vector_hash = digest(run / 'vectors/sycophantic.pt')
            if expected is not None and expected != vector_hash:
                raise ValueError('Cannot change an already frozen scan vector')
            for suffix in ('pt', 'json'):
                shutil.copy2(run / f'vectors/sycophantic.{suffix}', scan / f'vectors/sycophantic.{suffix}')
            frozen['vectors']['sycophantic']['sha256'] = vector_hash
            write_json(scan / 'manifest.json', frozen)
    elif args.stage == 'positions-generate':
        from persona_repro.operations import generate_file, runtime_from_config
        assert args.arm is not None
        mode = ('response', 'all')[args.arm]
        current = position_config(config, mode)
        runtime = runtime_from_config(current)
        if mode == 'response':
            generate_file(run / 'tasks/evil-test.jsonl', run / 'positions/responses/baseline.jsonl', config, runtime=runtime)
        for alpha in config['followups']['position_alphas']:
            label = str(alpha).replace('.', 'p')
            generate_file(run / 'tasks/evil-test.jsonl', run / f'positions/responses/{mode}-a{label}.jsonl',
                          current, vector_path=run / 'vectors/evil.pt', layer=12, coefficient=alpha, runtime=runtime)
        if any(block._forward_hooks for block in runtime.layers):
            raise ValueError('Hook leaked after position-control generation')
    else:
        from persona_repro.e02 import summarize_pair
        from persona_repro.judge import score_files
        from random_direction_control import repetition
        tasks = {r['sample_id']: r for r in read_jsonl(run / 'tasks/evil-test.jsonl')}
        names = ['baseline'] + [f'{mode}-a{str(a).replace(".", "p")}' for mode in ('response', 'all')
                                for a in config['followups']['position_alphas']]
        for name in names:
            rows = read_jsonl(run / f'positions/responses/{name}.jsonl')
            assert len(rows) == len(tasks) == 40 and {r['sample_id'] for r in rows} == set(tasks)
            if name == 'baseline':
                fingerprint = generation_fingerprint(config)
            else:
                mode, value = name.rsplit('-a', 1)
                fingerprint = generation_fingerprint(position_config(config, mode), vector_digest=digest(run / 'vectors/evil.pt'),
                                                     layer=12, coefficient=float(value.replace('p', '.')))
            for row in rows:
                assert row['generation_fingerprint'] == fingerprint
                assert row['messages'] == tasks[row['sample_id']]['messages']
        score_files([(run / f'positions/responses/{n}.jsonl', run / f'positions/scored/{n}.jsonl', None) for n in names], config)
        baseline = read_jsonl(run / 'positions/scored/baseline.jsonl')
        summary = {'conditions': {}, 'design': config['followups'], 'scope': 'paired diagnostic on previously used test questions; not a new untouched confirmatory set'}
        for name in names:
            rows = read_jsonl(run / f'positions/scored/{name}.jsonl')
            result = summarize_pair(rows, baseline, 'evil')
            details = []
            for row in rows:
                ids = row['answer_token_ids']
                end = next((i for i, token in enumerate(ids) if token in (248046, 248044)), len(ids))
                details.append({'sample_id': row['sample_id'], 'repetition_4gram': repetition(ids[:end]), 'content_tokens': end})
            result['repetition_4gram_mean'] = statistics.mean(r['repetition_4gram'] for r in details)
            write_jsonl(run / f'positions/metrics/{name}.jsonl', details)
            summary['conditions'][name] = result
        write_json(run / 'positions/summary.json', summary)
    write_json(run / f'logs/{args.stage}-{args.arm}.done.json', {'status': 'complete', 'stage': args.stage})


if __name__ == '__main__':
    main()
