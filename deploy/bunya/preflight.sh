#!/usr/bin/env bash
set -u

required_commands=(git python3 curl sbatch srun sinfo squeue)
missing=0

printf '%s\n' 'Bunya deployment preflight (read-only) / Bunya 部署前置检查（只读）'
printf 'host=%s\n' "$(hostname 2>/dev/null || printf unknown)"
printf 'user=%s\n' "${USER:-unknown}"
printf 'cwd=%s\n' "$(pwd)"
printf 'slurm_job_id=%s\n' "${SLURM_JOB_ID:-none}"

for command_name in "${required_commands[@]}"; do
    if command -v "$command_name" >/dev/null 2>&1; then
        printf 'ok command=%s path=%s\n' "$command_name" "$(command -v "$command_name")"
    else
        printf 'missing command=%s\n' "$command_name"
        missing=$((missing + 1))
    fi
done

if command -v vllm >/dev/null 2>&1; then
    printf 'ok command=vllm version='
    vllm --version 2>/dev/null || printf 'unknown'
else
    printf '%s\n' 'note command=vllm status=not-installed (prepare the approved environment before submitting a GPU job)'
fi

if command -v nvidia-smi >/dev/null 2>&1; then
    printf '%s\n' 'note nvidia-smi=available (expected on an allocated GPU node)'
else
    printf '%s\n' 'note nvidia-smi=not-found (normal on a login node; do not install GPU drivers there)'
fi

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    printf '%s\n' 'warning OPENAI_API_KEY=is-present (value not printed; never place it in files or jobs)'
else
    printf '%s\n' 'note OPENAI_API_KEY=not-present'
fi

if (( missing > 0 )); then
    printf 'preflight=fail missing_required_commands=%d\n' "$missing"
    exit 1
fi

printf '%s\n' 'preflight=pass required login-node tools are present'
