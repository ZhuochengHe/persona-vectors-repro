#!/bin/bash
#SBATCH --job-name=sft-qwen35-e08-matrix
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=02:00:00
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?Slurm allocation required}"
PV_ROOT="$1"
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
export PV_WORK
if [[ "${2:-}" == prepare ]]; then
  export HF_HOME="$PV_WORK/cache/huggingface" XDG_CACHE_HOME="$PV_WORK/cache"
  export CUDA_CACHE_PATH="$PV_WORK/cache/cuda" TORCH_HOME="$PV_WORK/cache/torch"
  export TRITON_CACHE_DIR="$PV_WORK/cache/triton" TMPDIR="$PV_WORK/tmp"
  export PYTHONNOUSERSITE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
  export PYTHONPATH="$PV_ROOT/source/src"
  "$PV_WORK/venv-train/bin/python" "$PV_ROOT/source/scripts/prepare_e08_matrix.py" "$PV_ROOT" "$PV_WORK"
else
  : "${SLURM_ARRAY_TASK_ID:?Array index required}"
  mapfile -t PV_RUNS < "$PV_ROOT/runs.txt"
  exec bash "$PV_ROOT/source/scripts/e08_train.slurm" "${PV_RUNS[$SLURM_ARRAY_TASK_ID]}"
fi
