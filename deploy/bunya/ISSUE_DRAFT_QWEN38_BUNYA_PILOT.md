# [E3 Pilot] Validate Qwen3.8 on Bunya with Codex-assisted deployment

## 问题与目标结果 / Problem and intended outcome

在不改变 Stage 1A provider contract 的前提下，使用 Codex CLI 辅助在 UQ Bunya 上准备一个受控的 Qwen3.8-27B-FP8 GPU 试点。目标是验证模型 artifact、Slurm 资源、vLLM serving、loopback binding 和 synthetic request 的完整证据链。

Without changing the Stage 1A provider contract, use Codex CLI to assist a controlled Qwen3.8-27B-FP8 GPU pilot on UQ Bunya. The goal is to validate the model artifact, Slurm allocation, vLLM serving, loopback binding, and a synthetic request with retained evidence.

## 范围与非目标 / Scope and non-goals

**范围内 / In scope**

- Bunya login-node read-only preflight and Codex permission profile.
- A pinned public model revision and protected scratch artifact directory.
- One 40 GB MIG GPU allocation under account `a_itee_isb`.
- A temporary vLLM endpoint bound to `127.0.0.1` inside the GPU job.
- Synthetic health and chat probes, resource summaries, and model provenance.

**非目标 / Non-goals**

- No real or restricted research data.
- No public Bunya endpoint, permanent service, gateway, SSO, RAG/RLS, MCP, Tidy3D, or secure release.
- No remote Stage 1A provider integration and no cloud fallback.
- No API key, credential, prompt content, model weights, or raw logs in GitHub objects.

## 验收条件 / Acceptance criteria

- [ ] Codex authentication and permissions are verified without exposing the API key.
- [ ] The model revision and every prepared artifact file have a provenance record.
- [ ] Slurm accepts the selected GRES and the job runs under `a_itee_isb`; a 40 GB MIG result is labelled feasibility-only, while a full 80 GB GPU is the stable baseline.
- [ ] vLLM serves the pinned local artifact with offline Hugging Face mode enabled.
- [ ] The endpoint is loopback-only and passes `/v1/models` and the synthetic chat probe.
- [ ] GPU memory, latency, token usage, job ID, and residual limitations are recorded without content.
- [ ] The job and temporary endpoint are stopped after the pilot.

## 验证方案与证据 / Validation plan and evidence

Use shell syntax checks, Python compilation, Slurm job output, `nvidia-smi` summary, loopback socket inspection, probe summary, and the model provenance manifest. Retain summaries only; do not retain source content or credentials.

使用 shell 语法检查、Python 编译、Slurm 作业输出、`nvidia-smi` 摘要、回环 socket 检查、probe 摘要和模型 provenance manifest。只保留摘要，不保留源内容或凭据。

## 数据、安全与外部副作用 / Data, security, and external effects

- Data classification: public code and synthetic material only.
- Codex API traffic: requires RCC/UQ policy confirmation; API usage is billed to the personal OpenAI Platform account.
- Credentials: personal API key is never committed or passed through Slurm; use a private `CODEX_HOME` and revoke after the pilot.
- External effects: one GPU job and model download; both require explicit user confirmation at execution time.
- Rollback: cancel the Slurm job, stop the vLLM process, revoke the API key, and remove only the pilot scratch directory.

## 已知限制 / Known limitations

The current Stage 1A implementation permits only audit and loopback Ollama. This pilot therefore validates a standalone model service, not enterprise model-gateway integration or multi-user authorization.

当前 Stage 1A 只允许 audit 和回环 Ollama。因此本试点验证的是独立模型服务，不是企业 model gateway 集成或多用户授权。
