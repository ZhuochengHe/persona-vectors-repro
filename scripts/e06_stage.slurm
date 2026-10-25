#!/bin/bash
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=12:00:00
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?Submit with sbatch}"
PV_STAGE=${1:?E06 stage required}
PV_RUN=${2:?E06 run directory required}
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
export PV_WORK
PV_SOURCE="$PV_RUN/source"
# Pin the already-validated SDPA environment, without optional FLA packages.
PV_PYTHON="$PV_WORK/venv/bin/python"
export HF_HOME="$PV_WORK/cache/huggingface"
export XDG_CACHE_HOME="$PV_WORK/cache"
export TORCH_HOME="$PV_WORK/cache/torch"
export TRITON_CACHE_DIR="$PV_WORK/cache/triton"
export CUDA_CACHE_PATH="$PV_WORK/cache/cuda"
export PYTHONPATH="$PV_SOURCE/src"
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
export TMPDIR="$PV_WORK/tmp"
unset PV_REQUIRE_FAST_KERNELS
mkdir -p "$PV_RUN/logs" "$TMPDIR"
cd "$PV_SOURCE"
echo "stage=$PV_STAGE job=$SLURM_JOB_ID host=$(hostname) start=$(date -Is)"
if [[ "$PV_STAGE" == smoke ]]; then
  "$PV_PYTHON" -m pytest -q tests
fi
"$PV_PYTHON" -m persona_repro.e06 "$PV_STAGE" --run "$PV_RUN"
"$PV_PYTHON" - "$PV_RUN" "$PV_STAGE" "$SLURM_JOB_ID" <<'PY'
import datetime,json,pathlib,sys
run,stage,job=sys.argv[1:]
(pathlib.Path(run)/'logs'/f'{stage}_{job}.done.json').write_text(json.dumps({
 'stage':stage,'job_id':job,'status':'complete',
 'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
PY
echo "finished=$(date -Is)"
