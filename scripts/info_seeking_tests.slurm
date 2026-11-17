#!/bin/bash
#SBATCH --job-name=is-tests
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:30:00
# Synthetic tests for src/info_seeking in the venv-is environment (no model weights are loaded).
# Usage: bash scripts/submit.sh scripts/info_seeking_tests.slurm
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?}"
: "${PV_WORK:?Set PV_WORK}"
export PV_WORK TMPDIR="$PV_WORK/tmp" PYTHONNOUSERSITE=1 PYTHONPATH="$PV_ROOT/src"
module load python/3.12.1 gcc/13.2.0 cuda/13.1.0
cd "$PV_ROOT"
echo "job=$SLURM_JOB_ID host=$(hostname) commit=$(git rev-parse HEAD) start=$(date -Is)"
"$PV_WORK/venv-is/bin/python" -m pytest -q tests/test_info_seeking.py
echo "finished=$(date -Is)"
