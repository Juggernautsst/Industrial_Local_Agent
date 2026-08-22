#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
GPU_GRES="${BUNYA_GPU_GRES:?Set BUNYA_GPU_GRES to an exact 40 GB MIG profile from sinfo}"
MODEL_DIR="${MODEL_DIR:?Set MODEL_DIR to the prepared model artifact directory}"
LOG_DIR="${LOG_DIR:-${SCRATCH:?Set SCRATCH or LOG_DIR}/industrial-local-agent/qwen38-slurm-logs}"
RUN_DIR_BASE="${RUN_DIR_BASE:-${SCRATCH:?Set SCRATCH or RUN_DIR_BASE}/industrial-local-agent/qwen38-runs}"
MODEL_ALIAS="${MODEL_ALIAS:-qwen3.8-27b-fp8}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-}"
PILOT_PROFILE="${PILOT_PROFILE:-}"

case "$GPU_GRES" in
    nvidia_a100_80gb_pcie_3g.40gb|nvidia_h100_80gb_pcie_3g.40gb)
        [[ -n "$PILOT_PROFILE" ]] || PILOT_PROFILE=40gb-feasibility
        [[ -n "$MAX_MODEL_LEN" ]] || MAX_MODEL_LEN=8192
        [[ -n "$GPU_MEMORY_UTILIZATION" ]] || GPU_MEMORY_UTILIZATION=0.95
        ;;
    a100|h100)
        [[ -n "$PILOT_PROFILE" ]] || PILOT_PROFILE=80gb-baseline
        [[ -n "$MAX_MODEL_LEN" ]] || MAX_MODEL_LEN=16384
        [[ -n "$GPU_MEMORY_UTILIZATION" ]] || GPU_MEMORY_UTILIZATION=0.90
        ;;
    *)
        printf 'error: unsupported GPU GRES %s; choose a full a100/h100 or an exact approved 40 GB MIG profile\n' "$GPU_GRES" >&2
        exit 1
        ;;
esac

[[ "$MODEL_DIR" = /* ]] || { printf '%s\n' 'error: MODEL_DIR must be absolute' >&2; exit 1; }
[[ -f "$MODEL_DIR/config.json" ]] || { printf '%s\n' "error: missing $MODEL_DIR/config.json" >&2; exit 1; }
command -v sbatch >/dev/null 2>&1 || { printf '%s\n' 'error: sbatch is not available' >&2; exit 1; }

mkdir -p "$LOG_DIR" "$RUN_DIR_BASE"
chmod 700 "$LOG_DIR" "$RUN_DIR_BASE"

sbatch --parsable \
    --account=a_itee_isb \
    --partition=gpu_cuda \
    --gres="gpu:${GPU_GRES}:1" \
    --cpus-per-task=8 \
    --mem=32G \
    --time=00:30:00 \
    --job-name=qwen38-pilot \
    --output="$LOG_DIR/qwen38-%j.out" \
    --export="ALL,MODEL_DIR=$MODEL_DIR,MODEL_ALIAS=$MODEL_ALIAS,MAX_MODEL_LEN=$MAX_MODEL_LEN,GPU_MEMORY_UTILIZATION=$GPU_MEMORY_UTILIZATION,PILOT_PROFILE=$PILOT_PROFILE,RUN_DIR_BASE=$RUN_DIR_BASE" \
    "$SCRIPT_DIR/qwen38_vllm.sbatch"
