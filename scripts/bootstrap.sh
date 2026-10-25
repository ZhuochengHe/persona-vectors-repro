#!/bin/bash
# Run inside a compute allocation; creates the environment and large caches on scratch.
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?Run bootstrap inside a Slurm allocation}"
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
export PV_WORK
REPO_ROOT=${PV_SOURCE_ROOT:-${PV_ROOT}}
export PIP_CACHE_DIR="$PV_WORK/cache/pip"
export TMPDIR="$PV_WORK/tmp"
mkdir -p "$PV_WORK/logs" "$TMPDIR"
python -m venv "$PV_WORK/venv"
"$PV_WORK/venv/bin/python" -m pip install --upgrade pip
# Use the exact upstream implementation inspected during adaptation rather than
# assuming an older PyPI Transformers build understands Qwen3.5.
"$PV_WORK/venv/bin/python" -m pip install 'transformers @ git+https://github.com/huggingface/transformers.git@683b721971417b3b2c64fba9001f525607547e5a'
"$PV_WORK/venv/bin/python" -m pip install -e "$REPO_ROOT[compute,test]"
"$PV_WORK/venv/bin/python" -m pip freeze > "$PV_WORK/environment.lock.txt"
