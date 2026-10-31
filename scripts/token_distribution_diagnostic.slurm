#!/bin/bash
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=06:00:00
set -euo pipefail
: "${SLURM_JOB_ID:?Slurm required}"
: "${PV_WORK:?Set PV_WORK to experiment storage}"
PV_RUN="$1"
export HF_HOME="$PV_WORK/cache/huggingface" XDG_CACHE_HOME="$PV_WORK/cache"
export CUDA_CACHE_PATH="$PV_WORK/cache/cuda" TORCH_HOME="$PV_WORK/cache/torch"
export TRITON_CACHE_DIR="$PV_WORK/cache/triton" TMPDIR="$PV_WORK/tmp"
export PYTHONPATH="$PV_RUN/source/src" PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"
unset PV_REQUIRE_FAST_KERNELS
cd "$PV_RUN/source"
"$PV_WORK/venv/bin/python" "$PV_RUN/source/scripts/token_distribution_diagnostic.py" --run "$PV_RUN"
