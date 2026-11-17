#!/bin/bash
#SBATCH --job-name=is-amb
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=12:00:00
# Usage (via scripts/submit.sh so logs persist):
#   bash scripts/submit.sh --time=02:00:00 scripts/ambiguity_probe.slurm forward --run-dir $PV_WORK/runs/<run_id>
#   bash scripts/submit.sh --time=01:00:00 scripts/ambiguity_probe.slurm probe --run-dir $PV_WORK/runs/<run_id>
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?Run this script with sbatch or inside an allocation}"
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
export PV_WORK
export HF_HOME="$PV_WORK/cache/huggingface"
export XDG_CACHE_HOME="$PV_WORK/cache"
export CUDA_CACHE_PATH="$PV_WORK/cache/cuda"
export TORCH_HOME="$PV_WORK/cache/torch"
export TRITON_CACHE_DIR="$PV_WORK/cache/triton"
export TMPDIR="$PV_WORK/tmp"
export PYTHONPATH="$PV_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1
mkdir -p "$TMPDIR" "$PV_WORK/logs"
# Qwen3.5 is a hybrid linear-attention model. venv-is (Python 3.12, scripts/bootstrap_info_seeking.slurm)
# has working FLA/causal-conv1d kernels; the shared venv-fast (Python 3.10) silently falls back.
PV_IS_ENV="${PV_IS_ENV:-$PV_WORK/venv-is}"
PV_PYTHON="${PV_PYTHON:-$PV_IS_ENV/bin/python}"
module load python/3.12.1 gcc/13.2.0 cuda/13.1.0
if [[ "$PV_PYTHON" == "$PV_IS_ENV/bin/python" && ! -f "$PV_IS_ENV.ready.json" ]]; then
  echo "Missing $PV_IS_ENV.ready.json; run scripts/bootstrap_info_seeking.slurm first" >&2; exit 1
fi
cd "$PV_ROOT"
echo "job=$SLURM_JOB_ID host=$(hostname) start=$(date -Is) args=$*"
# Stages on an existing run execute the run's frozen entry script (and, through it, frozen src/).
SCRIPT="scripts/ambiguity_probe.py"
ARGS=("$@")
for ((i = 0; i < ${#ARGS[@]} - 1; i++)); do
  if [[ "${ARGS[i]}" == "--run-dir" && -f "${ARGS[i+1]}/source/ambiguity_probe.py" ]]; then
    SCRIPT="${ARGS[i+1]}/source/ambiguity_probe.py"
  fi
done
echo "script=$SCRIPT"
"$PV_PYTHON" "$SCRIPT" "$@"
echo "finished=$(date -Is)"
