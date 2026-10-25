#!/bin/bash
# Supply persistent log paths before sbatch reads the job script.
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
export PV_WORK
mkdir -p "$PV_WORK/logs"
exec sbatch --output="$PV_WORK/logs/%x_%A_%a.out" --error="$PV_WORK/logs/%x_%A_%a.err" "$@"
