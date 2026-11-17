"""HiL-Bench SQL public tasks: deterministic subset selection and local materialization."""
from __future__ import annotations

import json
import random
import shutil
import urllib.request
from collections import defaultdict
from pathlib import Path

BUCKET_URL = 'https://huggingface.co/buckets/ScaleAI/hil-bench-sql-artifacts/resolve/'
HF_PREFIX = 'hf://buckets/ScaleAI/hil-bench-sql-artifacts/'


def load_sql_rows(parquet_path: str | Path) -> list[dict]:
    import pandas as pd
    rows = []
    for row in pd.read_parquet(parquet_path).to_dict('records'):
        if row['task_type'] != 'sql':
            continue
        registry = []
        for blocker in row['blocker_registry']:
            registry.append({key: (list(value) if key == 'example_questions' else value)
                             for key, value in blocker.items()})
        rows.append({
            'task_id': row['task_id'], 'uid': row['uid'], 'database_name': row['repo_or_db_name'],
            'database_link': row['repo_or_db_download_link'],
            'schema_links': list(row['schema_descriptions_download_links']),
            'problem': row['problem'], 'business_info': list(row['business_info']),
            'ground_truth_sql': row['ground_truth_answer'], 'blockers': registry,
        })
    rows.sort(key=lambda r: int(r['task_id'].rsplit('_', 1)[1]))
    return rows


def select_subset(rows: list[dict], size: int, seed: int) -> list[str]:
    """Stratify by blocker count (proportional), then round-robin over databases within each stratum."""
    rng = random.Random(seed)
    strata = defaultdict(list)
    for row in rows:
        strata[len(row['blockers'])].append(row)
    total = len(rows)
    keys = sorted(strata)
    quotas = {k: int(size * len(strata[k]) / total) for k in keys}
    remainders = sorted(keys, key=lambda k: (size * len(strata[k]) / total) - quotas[k], reverse=True)
    for k in remainders[:size - sum(quotas.values())]:
        quotas[k] += 1
    chosen = []
    for k in keys:
        by_db = defaultdict(list)
        for row in strata[k]:
            by_db[row['database_name']].append(row)
        for items in by_db.values():
            rng.shuffle(items)
        databases = sorted(by_db)
        rng.shuffle(databases)
        picked = []
        while len(picked) < quotas[k]:
            for db in databases:
                if by_db[db] and len(picked) < quotas[k]:
                    picked.append(by_db[db].pop())
        chosen.extend(row['task_id'] for row in picked)
    return chosen


def _download(url: str, destination: Path) -> None:
    if destination.exists() and destination.stat().st_size > 0:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + '.part')
    with urllib.request.urlopen(url, timeout=600) as response, open(partial, 'wb') as handle:
        shutil.copyfileobj(response, handle, length=1 << 22)
    partial.rename(destination)


def http_url(hf_link: str) -> str:
    if not hf_link.startswith(HF_PREFIX):
        raise ValueError(f'Unexpected artifact link: {hf_link}')
    return BUCKET_URL + hf_link[len(HF_PREFIX):]


def materialize(row: dict, data_root: Path) -> Path:
    """Write <data_root>/<task_id>/{task.json,database.sqlite,database_description/*.csv}."""
    task_dir = data_root / row['task_id']
    _download(http_url(row['database_link']), task_dir / 'database.sqlite')
    for link in row['schema_links']:
        _download(http_url(link), task_dir / 'database_description' / link.rsplit('/', 1)[1])
    task = {key: row[key] for key in ('task_id', 'uid', 'database_name', 'problem', 'business_info',
                                       'ground_truth_sql', 'blockers')}
    (task_dir / 'task.json').write_text(json.dumps(task, ensure_ascii=False, indent=1))
    return task_dir


def load_task(data_root: Path, task_id: str) -> dict:
    task_dir = data_root / task_id
    task = json.loads((task_dir / 'task.json').read_text())
    task['database_path'] = str(task_dir / 'database.sqlite')
    task['descriptions_dir'] = str(task_dir / 'database_description')
    return task
