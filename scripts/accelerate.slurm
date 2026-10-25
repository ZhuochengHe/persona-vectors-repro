#!/bin/bash
#SBATCH --job-name=bench-qwen35-fast-kernels
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=60G
#SBATCH --time=01:30:00
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?}"
PV_ROOT=${PV_ROOT}
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
export PV_WORK
PV_RUN=${1:?E01 run directory required}
PV_FAST="$PV_WORK/venv-fast"
export HF_HOME="$PV_WORK/cache/huggingface"
export XDG_CACHE_HOME="$PV_WORK/cache"
export CUDA_CACHE_PATH="$PV_WORK/cache/cuda"
export PIP_CACHE_DIR="$PV_WORK/cache/pip"
export TMPDIR="$PV_WORK/tmp"
export TRITON_CACHE_DIR="$PV_WORK/cache/triton"
export TORCH_EXTENSIONS_DIR="$PV_WORK/cache/torch-extensions"
export PYTHONPATH="$PV_ROOT/src"
export PYTHONUNBUFFERED=1
export PYTHONNOUSERSITE=1
export TOKENIZERS_PARALLELISM=false
export MAX_JOBS=4
export TORCH_CUDA_ARCH_LIST=8.9
mkdir -p "$TMPDIR" "$PV_RUN/kernel-benchmark"
# FLA's decorated Triton kernels cannot be inspected correctly by Python 3.10.
"$PV_WORK/venv/bin/python" -c 'import sys; assert sys.version_info >= (3,11), "Fast-kernel setup requires a Python >=3.11 base environment; leave the active environment untouched."' 
cd "$PV_ROOT"
echo "job=$SLURM_JOB_ID node=$(hostname) start=$(date -Is)"
# Get baseline first; the active E01 environment is never modified here.
"$PV_WORK/venv/bin/python" scripts/benchmark_kernels.py reference --config "$PV_RUN/config.json" --output "$PV_RUN/kernel-benchmark"
"$PV_WORK/venv/bin/python" -m venv "$PV_FAST"
# Reuse core packages read-only; additions go only into the new environment.
PV_BASE_SITE=$("$PV_WORK/venv/bin/python" -c 'import sysconfig; print(sysconfig.get_path("purelib"))')
PV_FAST_SITE=$("$PV_FAST/bin/python" -c 'import sysconfig; print(sysconfig.get_path("purelib"))')
printf '%s\n' "$PV_BASE_SITE" > "$PV_FAST_SITE/persona-base.pth"
"$PV_FAST/bin/python" -m pip install --no-deps 'fla-core==0.5.2' 'flash-linear-attention==0.5.2' einops ninja wheel
module load gcc/13.2.0 cuda/13.1.0
"$PV_FAST/bin/python" -m pip install --no-deps --no-build-isolation 'causal-conv1d==1.7.0'
"$PV_FAST/bin/python" -m pip freeze > "$PV_WORK/environment.fast.lock.txt"
"$PV_FAST/bin/python" scripts/benchmark_kernels.py accelerated --config "$PV_RUN/config.json" --output "$PV_RUN/kernel-benchmark"
echo "finished=$(date -Is)"
