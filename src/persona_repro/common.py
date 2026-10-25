"""Small provenance, configuration, and execution helpers (stdlib only)."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
from typing import Any, Iterable

TRAITS = ('evil', 'sycophantic', 'hallucinating')
CATEGORIES = ('evil', 'sycophancy', 'hallucination', 'insecure_code', 'mistake_opinions')
VERSIONS = ('normal', 'misaligned_1', 'misaligned_2')
EXPERIMENTS = ('E01', 'E02', 'E06', 'E08', 'E09', 'E10', 'E11', 'E19')
REPO = Path(__file__).resolve().parents[2]
GENERATION_PROTOCOL = 'explicit-generation-v3-turn-end'


def stable_id(*values: Any) -> str:
    return hashlib.sha256(json.dumps(values, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]


def generation_fingerprint(config, adapter_path=None, vector_digest=None, layer=None, coefficient=0.0):
    return stable_id(GENERATION_PROTOCOL, config['model'], str(adapter_path),
                     vector_digest, layer, coefficient, config['generation'])


def read_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: str | Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write('\n')
    temporary.replace(path)


def write_jsonl(path: str | Path, rows: Iterable[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
    temporary.replace(path)


def require_compute() -> None:
    host = socket.gethostname().split('.')[0]
    if host.startswith(('gl-login', 'lh-login')) and not os.environ.get('SLURM_JOB_ID'):
        raise RuntimeError('Run model loading, training, batch processing and tests in a Slurm allocation.')


def load_config(path: str | Path, *, allow_trait_subset: bool = False) -> dict:
    data = json.loads(Path(path).read_text())
    def expand_path(value: str) -> str:
        value = value.replace('${PV_ROOT}', os.environ.get('PV_ROOT', str(REPO)))
        value = os.path.expandvars(os.path.expanduser(value))
        if '${PV_WORK}' in value or '$PV_WORK' in value:
            raise ValueError('Set PV_WORK to a large writable experiment-storage directory before loading this config')
        return value
    def expand_values(value):
        if isinstance(value, str):
            return expand_path(value)
        if isinstance(value, dict):
            return {key: expand_values(item) for key, item in value.items()}
        if isinstance(value, list):
            return [expand_values(item) for item in value]
        return value
    data = expand_values(data)
    subset_valid = (bool(data['traits']) and len(set(data['traits'])) == len(data['traits'])
                    and all(trait in TRAITS for trait in data['traits']))
    if tuple(data['traits']) != TRAITS and not (allow_trait_subset and subset_valid):
        raise ValueError(f'Expected exactly the three canonical traits {TRAITS}')
    if data['judge']['model'] != 'gpt-5.6-luna' or data['judge'].get('calibration') is not False:
        raise ValueError('This reproduction uses gpt-5.6-luna without calibration.')
    return data


def question_splits(upstream: Path, seed: int = 0) -> dict:
    import random
    splits = {}
    for trait in TRAITS:
        artifact = json.loads((upstream / f'data_generation/trait_data_eval/{trait}.json').read_text())
        ids = list(range(len(artifact['questions'])))
        random.Random(seed).shuffle(ids)
        splits[trait] = {'dev': sorted(ids[:10]), 'test': sorted(ids[10:])}
        if not splits[trait]['test']:
            raise ValueError('Evaluation artifact has too few questions.')
    return splits
