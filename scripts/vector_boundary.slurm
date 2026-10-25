#!/bin/bash
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=06:00:00
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?Slurm required}"
PV_STAGE="$1"
PV_RUN="$2"
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
export PV_WORK
export HF_HOME="$PV_WORK/cache/huggingface" XDG_CACHE_HOME="$PV_WORK/cache"
export CUDA_CACHE_PATH="$PV_WORK/cache/cuda" TORCH_HOME="$PV_WORK/cache/torch"
export TRITON_CACHE_DIR="$PV_WORK/cache/triton" TMPDIR="$PV_WORK/tmp"
export PYTHONPATH="$PV_RUN/source/src" PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
echo "stage=$PV_STAGE job=$SLURM_JOB_ID host=$(hostname) start=$(date -Is)"
PV_ARGS=()
if [[ "$PV_STAGE" == generate ]]; then
  case "${SLURM_ARRAY_TASK_ID:?Array task required}" in
    0) PV_ARGS=(--arm original);;
    1) PV_ARGS=(--arm corrected);;
    *) exit 2;;
  esac
fi
"$PV_WORK/venv/bin/python" -m pip freeze > "$PV_RUN/logs/environment-${PV_STAGE}-${SLURM_ARRAY_TASK_ID:-single}.txt"
"$PV_WORK/venv/bin/python" "$PV_RUN/source/scripts/vector_boundary_test.py" "$PV_STAGE" --run "$PV_RUN" "${PV_ARGS[@]}"
echo "finished=$(date -Is)"
