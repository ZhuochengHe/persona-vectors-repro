#!/bin/bash
#SBATCH --job-name=sft-qwen35-e08-evil-ii
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
export TRITON_CACHE_DIR="$PV_WORK/cache/triton" TMPDIR="$PV_WORK/tmp"
export PYTHONNOUSERSITE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
export PYTHONPATH="$PV_RUN/source/src"
cd "$PV_RUN/source"
echo "job=$SLURM_JOB_ID host=$(hostname) start=$(date -Is)"
"$PV_WORK/venv-train/bin/python" -m pip freeze > "$PV_RUN/environment.txt"
"$PV_WORK/venv-train/bin/python" -m persona_repro.cli --config "$PV_RUN/config.json" train \
  --train-file "$PV_RUN/data/train.jsonl" --dev-file "$PV_RUN/data/dev.jsonl" \
  --output "$PV_RUN/adapter"
"$PV_WORK/venv-train/bin/python" - "$PV_RUN" <<'PY'
import json
import sys
from pathlib import Path
run = Path(sys.argv[1])
metadata = json.loads((run / "adapter/training_metadata.json").read_text())
assert metadata["global_step"] == 63, metadata["global_step"]
assert metadata["update_probe"]["delta_norm"] > 0
(run / "done.json").write_text(json.dumps({"status": "completed", "global_step": metadata["global_step"], "metrics": metadata["metrics"]}, indent=2) + "\n")
PY
echo "finished=$(date -Is)"
