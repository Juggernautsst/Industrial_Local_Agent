#!/usr/bin/env bash
# The submission wrapper supplies the GPU GRES and output path.
# 此脚本由提交 wrapper 提供 GPU GRES 和输出路径。
#SBATCH --account=a_itee_isb
#SBATCH --partition=gpu_cuda
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --job-name=qwen38-pilot

set -Eeuo pipefail

MODEL_DIR="${MODEL_DIR:?MODEL_DIR must point to a prepared local model artifact}"
MODEL_ALIAS="${MODEL_ALIAS:-qwen3.8-27b-fp8}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
PILOT_PROFILE="${PILOT_PROFILE:-80gb-baseline}"
VLLM_PORT="${VLLM_PORT:-$((18080 + SLURM_JOB_ID % 1000))}"
RUN_DIR_BASE="${RUN_DIR_BASE:-${SCRATCH:?Set SCRATCH or RUN_DIR_BASE}/industrial-local-agent/qwen38-runs}"
RUN_DIR="$RUN_DIR_BASE/$SLURM_JOB_ID"
VLLM_BIN="${VLLM_BIN:-vllm}"
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

die() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

[[ "$MODEL_DIR" = /* ]] || die 'MODEL_DIR must be absolute'
[[ -f "$MODEL_DIR/config.json" ]] || die "missing model config: $MODEL_DIR/config.json"
[[ -f "$MODEL_DIR/model.safetensors.index.json" ]] || die "missing model index: $MODEL_DIR"
command -v "$VLLM_BIN" >/dev/null 2>&1 || die "vLLM command not found: $VLLM_BIN"
command -v curl >/dev/null 2>&1 || die 'curl is required for the local readiness check'
command -v ss >/dev/null 2>&1 || die 'ss is required to verify loopback binding'

mkdir -p "$RUN_DIR"
chmod 700 "$RUN_DIR"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export VLLM_LOGGING_LEVEL=WARNING

"$VLLM_BIN" --version >"$RUN_DIR/vllm-version.txt" 2>&1 || die 'unable to determine vLLM version'
python3 -c 'import transformers; print(transformers.__version__)' >"$RUN_DIR/transformers-version.txt" 2>&1 || die 'transformers is unavailable in the serving environment'
printf 'pilot_profile=%s\nmax_model_len=%s\ngpu_memory_utilization=%s\n' \
    "$PILOT_PROFILE" "$MAX_MODEL_LEN" "$GPU_MEMORY_UTILIZATION" >"$RUN_DIR/config.txt"

if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader >"$RUN_DIR/gpu.csv"
fi

"$VLLM_BIN" serve "$MODEL_DIR" \
    --host 127.0.0.1 \
    --port "$VLLM_PORT" \
    --served-model-name "$MODEL_ALIAS" \
    --dtype auto \
    --language-model-only \
    --max-model-len "$MAX_MODEL_LEN" \
    --max-num-seqs 1 \
    --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION" \
    >"$RUN_DIR/vllm.log" 2>&1 &
server_pid=$!

cleanup() {
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

ready=0
for _ in $(seq 1 120); do
    if curl --fail --silent --show-error --max-time 2 "http://127.0.0.1:$VLLM_PORT/v1/models" >/dev/null; then
        ready=1
        break
    fi
    if ! kill -0 "$server_pid" 2>/dev/null; then
        tail -n 40 "$RUN_DIR/vllm.log" >&2 || true
        die 'vLLM exited before readiness'
    fi
    sleep 1
done
(( ready == 1 )) || die 'vLLM readiness timeout'

if ! ss -lnt | awk -v port=":$VLLM_PORT" '$4 == "127.0.0.1" port || $4 == "[::1]" port { found=1 } END { exit(found ? 0 : 1) }'; then
    die "vLLM is not bound to loopback port $VLLM_PORT"
fi

python3 "$SCRIPT_DIR/probe_vllm.py" \
    --base-url "http://127.0.0.1:$VLLM_PORT" \
    --model "$MODEL_ALIAS" \
    | tee "$RUN_DIR/probe-summary.json"

printf 'pilot=pass job_id=%s model=%s run_dir=%s\n' "$SLURM_JOB_ID" "$MODEL_ALIAS" "$RUN_DIR"
