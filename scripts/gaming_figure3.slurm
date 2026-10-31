#!/bin/bash
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=08:00:00
set -euo pipefail
: "${SLURM_JOB_ID:?Slurm required}"
: "${PV_WORK:?Set PV_WORK to experiment storage}"
PV_STAGE="$1"
PV_RUN="$2"
export HF_HOME="$PV_WORK/cache/huggingface" XDG_CACHE_HOME="$PV_WORK/cache"
export CUDA_CACHE_PATH="$PV_WORK/cache/cuda" TORCH_HOME="$PV_WORK/cache/torch"
export TRITON_CACHE_DIR="$PV_WORK/cache/triton" TMPDIR="$PV_WORK/tmp"
export PYTHONPATH="$PV_RUN/source/src" PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
unset PV_REQUIRE_FAST_KERNELS
cd "$PV_RUN/source"
echo "stage=$PV_STAGE job=$SLURM_JOB_ID host=$(hostname) start=$(date -Is)"
if [[ "$PV_STAGE" == preflight ]]; then
  "$PV_WORK/venv/bin/python" -m pytest -q tests
  "$PV_WORK/venv/bin/python" -c 'import matplotlib'
fi
PV_ARGS=()
if [[ "$PV_STAGE" == scan-generate || "$PV_STAGE" == evaluation-generate ]]; then
  PV_ARGS=(--shard "${SLURM_ARRAY_TASK_ID:?Array required}")
fi
"$PV_WORK/venv/bin/python" "$PV_RUN/source/scripts/gaming_figure3.py" "$PV_STAGE" --run "$PV_RUN" "${PV_ARGS[@]}"
echo "finished=$(date -Is)"
