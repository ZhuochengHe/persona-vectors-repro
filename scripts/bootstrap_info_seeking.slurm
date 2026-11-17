#!/bin/bash
#SBATCH --job-name=is-env
#SBATCH --partition=spgpu2
#SBATCH --account=qdj_project_owned1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=60G
#SBATCH --time=02:00:00
# Standalone environment for the info-seeking study with working Qwen3.5 fast kernels.
# FLA's decorated Triton kernels need Python >= 3.11 (Python 3.10 inspect.getsourcelines stops at
# lambdas inside decorators, so Triton cannot find the kernel `def` and transformers silently falls
# back to the PyTorch reference implementation). Shared venv/venv-fast are not modified.
# Usage: bash scripts/submit.sh scripts/bootstrap_info_seeking.slurm
set -euo pipefail
export PV_ROOT="${PV_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${SLURM_JOB_ID:?}"
: "${PV_WORK:?Set PV_WORK to large shared experiment storage}"
ENV="${PV_IS_ENV:-$PV_WORK/venv-is}"
PY_MODULE="${PV_IS_PY_MODULE:-python/3.12.1}"
export PIP_CACHE_DIR="$PV_WORK/cache/pip" TMPDIR="$PV_WORK/tmp" HF_HOME="$PV_WORK/cache/huggingface"
export TRITON_CACHE_DIR="$PV_WORK/cache/triton" CUDA_CACHE_PATH="$PV_WORK/cache/cuda"
export PYTHONNOUSERSITE=1 MAX_JOBS=8 TORCH_CUDA_ARCH_LIST=8.9
mkdir -p "$TMPDIR"
module load "$PY_MODULE" gcc/13.2.0 cuda/13.1.0
echo "job=$SLURM_JOB_ID node=$(hostname) python=$(python3 --version) start=$(date -Is)"
if [[ -e "$ENV" ]]; then echo "Refusing to overwrite existing $ENV" >&2; exit 1; fi
python3 -m venv "$ENV"
"$ENV/bin/python" -m pip install --upgrade pip wheel setuptools ninja
# Same core pins as the project environment (environment.lock.txt).
"$ENV/bin/python" -m pip install --index-url https://download.pytorch.org/whl/cu130 'torch==2.14.1'
"$ENV/bin/python" -m pip install \
  'transformers @ git+https://github.com/huggingface/transformers.git@683b721971417b3b2c64fba9001f525607547e5a' \
  'accelerate==1.15.0' 'safetensors==0.8.0' 'tokenizers==0.23.3' 'huggingface_hub==2.2.0' \
  'numpy==2.2.6' 'pandas==2.3.3' 'pyarrow==25.0.1' 'PyYAML==6.0.3' 'Jinja2==3.1.6' 'pytest' einops \
  'scikit-learn==1.5.2'
"$ENV/bin/python" -m pip install --no-deps 'fla-core==0.5.2' 'flash-linear-attention==0.5.2'
"$ENV/bin/python" -m pip install --no-deps --no-build-isolation 'causal-conv1d==1.7.0'
"$ENV/bin/python" -m pip freeze > "$ENV.lock.txt"
# Verify: FLA imports and Qwen3.5 binds the optimized kernels (no reference fallback).
cd "$PV_ROOT"
PYTHONPATH="$PV_ROOT/src" "$ENV/bin/python" - <<'EOF'
import json, os, sys
import fla.ops.gated_delta_rule  # noqa: F401  (raises if Triton cannot parse the kernels)
from transformers.models.qwen3_5 import modeling_qwen3_5 as qwen
from persona_repro.model import kernel_bindings
bindings = {name: kernel_bindings(getattr(qwen, name)) for name in (
    'causal_conv1d_fn', 'causal_conv1d_update', 'torch_chunk_gated_delta_rule', 'torch_recurrent_gated_delta_rule')}
print(json.dumps(bindings, indent=1))
if not all(bindings.values()):
    sys.exit('Fast kernels not bound: ' + json.dumps(bindings))
marker = os.environ.get('PV_IS_ENV', os.path.join(os.environ['PV_WORK'], 'venv-is')) + '.ready.json'
json.dump({'python': sys.version, 'bindings': bindings}, open(marker, 'w'), indent=1)
print('ready', marker)
EOF
echo "finished=$(date -Is)"
