#!/bin/bash
#SBATCH --job-name=repro-persona-stage
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=02:00:00
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?Run this script with sbatch or inside an allocation}"
REPO_ROOT=${PV_ROOT}
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
export PV_WORK
export HF_HOME="$PV_WORK/cache/huggingface"
export XDG_CACHE_HOME="$PV_WORK/cache"
export CUDA_CACHE_PATH="$PV_WORK/cache/cuda"
export TORCH_HOME="$PV_WORK/cache/torch"
export TRITON_CACHE_DIR="$PV_WORK/cache/triton"
export TORCH_EXTENSIONS_DIR="$PV_WORK/cache/torch-extensions"
export PIP_CACHE_DIR="$PV_WORK/cache/pip"
export TMPDIR="$PV_WORK/tmp"
export PYTHONPATH="$REPO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p "$TMPDIR" "$PV_WORK/logs"
if [[ -z "${PV_PYTHON:-}" ]]; then
  if [[ -f "$PV_WORK/fast-kernels.ready.json" ]]; then
    PV_PYTHON="$PV_WORK/venv-fast/bin/python"
    export PV_REQUIRE_FAST_KERNELS=1
  else
    PV_PYTHON="$PV_WORK/venv/bin/python"
  fi
fi
if [[ "$PV_PYTHON" == "$PV_WORK/venv-fast/bin/python" ]]; then
  module load gcc/13.2.0 cuda/13.1.0
  export PV_REQUIRE_FAST_KERNELS=1
fi
export PYTHONNOUSERSITE=1
if [[ ! -x "$PV_PYTHON" ]]; then
  echo "Missing dedicated environment: $PV_PYTHON; see scripts/bootstrap.sh" >&2
  exit 1
fi
cd "$REPO_ROOT"
echo "job=$SLURM_JOB_ID host=$(hostname) start=$(date -Is)"
"$PV_PYTHON" -m persona_repro.cli "$@"
echo "finished=$(date -Is)"
