#!/bin/bash
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=08:00:00
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?Submit this stage with sbatch}"
PV_STAGE=${1:?stage required}
PV_RUN=${2:?run directory required}
PV_SOURCE="$PV_RUN/source"
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
export PYTHONPATH="$PV_SOURCE/src${PYTHONPATH:+:$PYTHONPATH}"
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
mkdir -p "$TMPDIR" "$PV_RUN/logs"
cd "$PV_SOURCE"
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
echo "stage=$PV_STAGE job=$SLURM_JOB_ID host=$(hostname) start=$(date -Is)"
case "$PV_STAGE" in
  prepare)
    PV_SOURCE_ROOT="$PV_SOURCE" bash "$PV_SOURCE/scripts/bootstrap.sh"
    "$PV_PYTHON" -m persona_repro.cli --config "$PV_RUN/config.json" preflight
    ;;
  preflight)
    "$PV_PYTHON" -m pytest -q "$PV_SOURCE/tests/test_template_tokens.py"
    "$PV_PYTHON" -m persona_repro.cli --config "$PV_RUN/config.json" preflight
    ;;
  generate)
    "$PV_PYTHON" -m persona_repro.pipeline generate --run "$PV_RUN"
    ;;
  score)
    codex --version
    for trait in evil sycophantic hallucinating; do
      "$PV_PYTHON" -m persona_repro.cli --config "$PV_RUN/config.json" score \
        --input "$PV_RUN/responses/$trait.jsonl" --output "$PV_RUN/scored/$trait.jsonl"
    done
    ;;
  vectors)
    "$PV_PYTHON" -m persona_repro.pipeline vectors --run "$PV_RUN"
    ;;
  *) echo "Unknown stage: $PV_STAGE" >&2; exit 2 ;;
esac
"$PV_PYTHON" - "$PV_RUN" "$PV_STAGE" "$SLURM_JOB_ID" <<'PY'
import datetime,json,pathlib,sys
run,stage,job=sys.argv[1:]
path=pathlib.Path(run)/'logs'/f'{stage}_{job}.done.json'
path.write_text(json.dumps({'stage':stage,'job_id':job,'status':'complete','finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
PY
echo "finished=$(date -Is)"
