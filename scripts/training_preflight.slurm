#!/bin/bash
#SBATCH --job-name=sft-qwen35-e08-preflight
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=02:00:00
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?Slurm allocation required}"
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
export PV_WORK
PV_RUN="$1"
export HF_HOME="$PV_WORK/cache/huggingface" XDG_CACHE_HOME="$PV_WORK/cache"
export CUDA_CACHE_PATH="$PV_WORK/cache/cuda" TORCH_HOME="$PV_WORK/cache/torch"
export TRITON_CACHE_DIR="$PV_WORK/cache/triton" PIP_CACHE_DIR="$PV_WORK/cache/pip"
export TMPDIR="$PV_WORK/tmp" PYTHONNOUSERSITE=1 TOKENIZERS_PARALLELISM=false
export PYTHONPATH="$PV_RUN/source/src"
echo "job=$SLURM_JOB_ID host=$(hostname) start=$(date -Is)"
if [[ ! -x "$PV_WORK/venv-train/bin/python" ]]; then
  "$PV_WORK/venv/bin/python" -m venv "$PV_WORK/venv-train"
  echo "$PV_WORK/venv/lib/python3.10/site-packages" > "$PV_WORK/venv-train/lib/python3.10/site-packages/base.pth"
fi
"$PV_WORK/venv-train/bin/python" -m pip install --no-deps bitsandbytes==0.50.2
"$PV_WORK/venv-train/bin/python" -m pip freeze > "$PV_RUN/environment.txt"
"$PV_WORK/venv-train/bin/python" -m pytest -q "$PV_RUN/source/tests"
"$PV_WORK/venv-train/bin/python" "$PV_RUN/source/scripts/preflight_training.py" "$PV_RUN" "$PV_WORK"
echo "finished=$(date -Is)"
