"""Shared run-directory helpers: config expansion, git provenance and frozen-source initialisation.

Entry scripts must put the frozen `runs/<id>/source/src` on sys.path *before* importing this
package (see `bootstrap_source_path` in each script), so later stages run the frozen code.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from .official import sha256

ROOT = Path(__file__).resolve().parents[2]
# Shared paths every info-seeking run freezes; scripts add their own entry files.
SHARED_TRACKED = ['src/info_seeking', 'src/persona_repro/__init__.py', 'src/persona_repro/common.py',
                  'src/persona_repro/model.py', 'scripts/bootstrap_info_seeking.slurm', 'tests/test_info_seeking.py']


def expand(value):
    if isinstance(value, str):
        expanded = os.path.expandvars(value)
        if '$' in expanded:
            raise ValueError(f'Unresolved environment variable in {value}')
        return expanded
    if isinstance(value, dict):
        return {k: expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand(v) for v in value]
    return value


def load_cfg(path: Path) -> dict:
    return expand(json.loads(Path(path).read_text()))


def git(*cmd) -> str:
    return subprocess.run(['git', *cmd], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def create_run_dir(*, run_id: str, purpose: str, config_path: Path, cfg: dict, entry_files: list[str],
                   official_hashes: dict, tasks: dict, subdirs=('units', 'logs')) -> Path:
    """Create ${PV_WORK}/runs/<run_id> with frozen config, source, tasks and manifest.

    Non-smoke runs require the tracked paths (shared package, entry files, config) to be clean in git;
    the check happens before anything is created."""
    run_dir = Path(os.environ['PV_WORK']) / 'runs' / run_id
    if run_dir.exists():
        raise FileExistsError(run_dir)
    config_path = Path(config_path).resolve()
    tracked = SHARED_TRACKED + list(entry_files) + [str(config_path.relative_to(ROOT))]
    dirty = git('status', '--porcelain', '--', *tracked)
    if dirty and purpose != 'smoke':
        raise RuntimeError('Non-smoke runs need a clean commit of the tracked paths; commit first or use --purpose smoke')
    (run_dir / 'tasks').mkdir(parents=True)
    for name in subdirs:
        (run_dir / name).mkdir()
    src = run_dir / 'source' / 'src'
    shutil.copytree(ROOT / 'src/info_seeking', src / 'info_seeking', ignore=shutil.ignore_patterns('__pycache__'))
    (src / 'persona_repro').mkdir()
    for name in ('__init__.py', 'common.py', 'model.py'):
        shutil.copy(ROOT / 'src/persona_repro' / name, src / 'persona_repro' / name)
    for rel in entry_files:
        shutil.copy(ROOT / rel, run_dir / 'source' / Path(rel).name)
    (run_dir / 'tasks' / 'tasks.json').write_text(json.dumps(tasks, indent=1))
    (run_dir / 'config.json').write_text(json.dumps(cfg, indent=1))
    (run_dir / 'config.source.json').write_text(config_path.read_text())
    source_hashes = {str(p.relative_to(run_dir)): sha256(p) for p in sorted((run_dir / 'source').rglob('*')) if p.is_file()}
    manifest = {'run_id': run_id, 'study': cfg['study'], 'created': datetime.now().isoformat(timespec='seconds'),
                'purpose': purpose, 'implementation_commit': git('rev-parse', 'HEAD'),
                'tracked_paths_dirty': bool(dirty), 'dirty_status': dirty.splitlines(),
                'official_files': official_hashes, 'source_sha256': source_hashes,
                'config_sha256': sha256(run_dir / 'config.json'),
                'tasks_sha256': sha256(run_dir / 'tasks' / 'tasks.json')}
    (run_dir / 'manifest.json').write_text(json.dumps(manifest, indent=1))
    return run_dir


def write_chunk(out_dir: Path, index: int, rows: list[dict], tensors: dict, metadata: dict) -> None:
    """Atomic chunk: rows JSONL + safetensors, then a .done marker (resume skips done chunks)."""
    from safetensors.torch import save_file
    stem = Path(out_dir) / f'chunk_{index:05d}'
    tmp_rows, tmp_acts = stem.with_suffix('.jsonl.tmp'), stem.with_suffix('.safetensors.tmp')
    tmp_rows.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    save_file({k: v.contiguous() for k, v in tensors.items()}, str(tmp_acts),
              metadata={k: str(v) for k, v in metadata.items()})
    tmp_rows.rename(stem.with_suffix('.jsonl'))
    tmp_acts.rename(stem.with_suffix('.safetensors'))
    stem.with_suffix('.done').write_text(datetime.now().isoformat(timespec='seconds'))


def chunk_done(out_dir: Path, index: int) -> bool:
    return (Path(out_dir) / f'chunk_{index:05d}.done').exists()


def read_chunks(out_dir: Path):
    """All finished chunks: (rows, {tensor_name: concatenated tensor})."""
    import torch
    from safetensors.torch import load_file
    rows, tensors = [], {}
    for done in sorted(Path(out_dir).glob('chunk_*.done')):
        rows.extend(json.loads(line) for line in done.with_suffix('.jsonl').read_text().splitlines())
        for k, v in load_file(str(done.with_suffix('.safetensors'))).items():
            tensors.setdefault(k, []).append(v)
    return rows, {k: torch.cat(v) for k, v in tensors.items()}
