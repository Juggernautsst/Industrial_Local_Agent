# Bunya deployment pilot / Bunya 部署试点

本目录提供一个不改变 Stage 1A 的 Qwen3.8 Bunya 试点。Codex 只是部署辅助工具；Qwen3.8 是独立的本地模型服务。当前材料只支持公开代码和合成数据。

This directory provides a Qwen3.8 Bunya pilot without changing Stage 1A. Codex is only a deployment assistant; Qwen3.8 is a separate local model service. The workflow is limited to public code and synthetic data.

## Boundary / 边界

```text
laptop or Bunya login node
        |
        +-- Codex CLI -> OpenAI API (deployment instructions and code context only)
        |
        +-- sbatch -> one GPU compute job -> vLLM -> 127.0.0.1 only
                                      -> synthetic probe
```

Codex commands run on Bunya, but Codex reasoning is remote when using an API key. Do not provide real research data, secrets, SSH keys, model weights, or private prompts. Confirm with RCC/UQ that outbound Codex API traffic is allowed. If it is not allowed, run Codex on the laptop and use approved SSH operations instead.

Codex 命令在 Bunya 上执行，但使用 API key 时 Codex 推理发生在远端。不要提供真实科研数据、secrets、SSH keys、模型权重或私有 prompt。必须先向 RCC/UQ 确认允许外发 Codex API 流量；如果不允许，应在笔记本运行 Codex，再通过批准的 SSH 操作 Bunya。

## 1. Codex setup / Codex 设置

Run these commands interactively. Never put the key in shell history, `.bashrc`, a Slurm script, Git, or an Issue.

交互执行以下命令。不要把 key 写入 shell history、`.bashrc`、Slurm 脚本、Git 或 Issue。

```bash
umask 077
export CODEX_HOME="$HOME/.codex-bunya"
mkdir -p "$CODEX_HOME"
cp deploy/bunya/codex-config.toml.example "$CODEX_HOME/config.toml"
chmod 700 "$CODEX_HOME"
chmod 600 "$CODEX_HOME/config.toml"

read -rsp 'OpenAI API key (input hidden): ' OPENAI_API_KEY
printf '\n'
export OPENAI_API_KEY
printf '%s' "$OPENAI_API_KEY" | codex login --with-api-key
unset OPENAI_API_KEY
codex login status
```

The CLI may cache the credential under `CODEX_HOME`. Treat `auth.json` as a password. Run `codex logout` after the pilot and revoke the key if it was created only for this test.

CLI 可能在 `CODEX_HOME` 中缓存凭据。把 `auth.json` 当作密码保护。试点结束后运行 `codex logout`；如果该 key 只用于本试点，应撤销它。

The checked-in permission template keeps network access disabled. Only change the private copy under `CODEX_HOME` to enable the approved OpenAI domains after RCC/UQ confirms that outbound API traffic is allowed.

仓库中的权限模板默认关闭网络。只有 RCC/UQ 确认允许外发 API 流量后，才可以修改 `CODEX_HOME` 下的私有副本并启用批准的 OpenAI 域名。

Start with read-only inspection. Only after review, allow writes inside the active repository and keep model/data directories outside it:

```text
Inspect AGENTS.md, README.md, docs/, and deploy/bunya/ first.
Do not read .env, .ssh, private/, models/, runs/, uploads/, or *.safetensors.
Do not submit a Slurm job until the user confirms the exact GRES and budget.
```

## 2. Read-only preflight / 只读前置检查

```bash
./deploy/bunya/preflight.sh
```

`nvidia-smi` is expected to be absent on the login node. It must be checked inside the allocated GPU job.

登录节点没有 `nvidia-smi` 是正常情况；必须在 GPU 作业内检查它。

## 3. Prepare the public model artifact / 准备公开模型 artifact

The script pins the public revision `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a` and writes a file-level SHA-256 manifest. Use protected Linux scratch, not the Git checkout.

脚本固定公开 revision `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`，并写入逐文件 SHA-256 manifest。使用受保护的 Linux scratch，不要写入 Git checkout。

```bash
export MODEL_DIR="${SCRATCH:?}/industrial-local-agent/models/qwen3.8-27b-fp8"
./deploy/bunya/prepare_qwen38.sh
```

This download is an external side effect and may consume substantial storage and network bandwidth. Confirm it before execution.

该下载会产生外部副作用，并可能消耗大量存储和网络带宽。执行前必须确认。

## 4. Submit one GPU pilot / 提交一个 GPU 试点

Inspect exact GRES values first:

```bash
sinfo -N -p gpu_cuda -o '%N %T %G'
```

Then choose an exact GPU GRES. The wrapper intentionally accepts only these approved forms and has no automatic resource fallback:

```bash
export BUNYA_GPU_GRES=nvidia_a100_80gb_pcie_3g.40gb
# or: nvidia_h100_80gb_pcie_3g.40gb
# stable baseline when available: a100 or h100
export MODEL_DIR="${SCRATCH:?}/industrial-local-agent/models/qwen3.8-27b-fp8"
./deploy/bunya/submit_qwen38.sh
```

The job uses account `a_itee_isb`, partition `gpu_cuda`, 8 CPU cores, 32 GB host RAM, and a 30-minute limit. A full `a100:1` or `h100:1` is the stable baseline with a 16K context. A 40 GB MIG profile is accepted only as a feasibility probe; it uses text-only mode, reduced context, and may fail with an out-of-memory error.

作业使用 `a_itee_isb`、`gpu_cuda`、8 个 CPU 核心、32 GB 主机 RAM 和 30 分钟上限。完整 `a100:1` 或 `h100:1` 是 16K 上下文的稳定基线。40 GB MIG 只作为可失败的 feasibility probe；它使用 text-only 模式和更短上下文，可能因显存不足失败。

Monitor without exposing the endpoint:

```bash
squeue --me
sacct -X --name=qwen38-pilot --format=JobID,State,Elapsed,MaxRSS,AllocTRES
```

The service is tested inside the job by `probe_vllm.py`; it is not a public API and is not connected to Stage 1A.

## 5. Acceptance evidence / 验收证据

Retain only the job ID, model revision, file manifest, GPU summary, latency/token summary, endpoint binding result, and failure reason if any. Do not retain model responses containing research material, credentials, or full raw logs.

只保留作业 ID、模型 revision、文件 manifest、GPU 摘要、延迟/ token 摘要、endpoint binding 结果和失败原因。不要保留包含科研材料、凭据或完整原始日志的模型响应。

The current Stage 1A provider boundary still allows only `audit` and loopback Ollama. A separate E3 model-gateway Issue is required before any remote model endpoint can be integrated.

当前 Stage 1A provider boundary 仍只允许 `audit` 和回环 Ollama。任何远程模型 endpoint 集成前，必须单独建立 E3 model-gateway Issue。

See [the local issue draft](ISSUE_DRAFT_QWEN38_BUNYA_PILOT.md), [enterprise deployment boundaries](../../docs/ENTERPRISE_DEPLOYMENT.md), and [the implementation handbook](../../docs/IMPLEMENTATION_HANDBOOK.md).
