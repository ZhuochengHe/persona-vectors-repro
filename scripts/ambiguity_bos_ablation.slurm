#!/bin/bash
#SBATCH --job-name=is-amb-bos
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=03:00:00
# Usage: bash scripts/submit.sh scripts/ambiguity_bos_ablation.slurm --run-dir <ambiguity run> --out <run>/analysis/bos_ablation
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?}"
: "${PV_WORK:?Set PV_WORK}"
export PV_WORK HF_HOME="$PV_WORK/cache/huggingface" TMPDIR="$PV_WORK/tmp" PYTHONNOUSERSITE=1
module load python/3.12.1 gcc/13.2.0 cuda/13.1.0
# HF_HOME points at scratch; the login token lives under the home cache (gated LLaMA weights).
if [[ -z "${HF_TOKEN:-}" && -f "$HOME/.cache/huggingface/token" ]]; then export HF_TOKEN="$(cat "$HOME/.cache/huggingface/token")"; fi
cd "$PV_ROOT"
echo "job=$SLURM_JOB_ID host=$(hostname) commit=$(git rev-parse HEAD) dirty=$(git status --porcelain -- scripts/ambiguity_bos_ablation.py | wc -l) start=$(date -Is) args=$*"
"$PV_WORK/venv-is/bin/python" scripts/ambiguity_bos_ablation.py "$@"
echo "finished=$(date -Is)"
