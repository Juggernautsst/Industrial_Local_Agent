# Week 3: Executable Authorization Evidence / 第三周：可执行授权证据

本目录是 2026-08-20 研究进展汇报的独立 Beamer 工程。汇报主线是：上次定义了 UQ 本地科研 Agent 的目标架构，本次把“先授权、后检索”实现为可运行的 synthetic、model-free E2 纵向切片，并把实际执行结果作为 slides 中的演示证据。

This directory is the standalone Beamer project for the 20 August 2026 research-progress presentation. Its central story is that the previous report defined the target UQ-local research-agent architecture, while this report implements authorize-before-retrieval as an executable synthetic, model-free E2 vertical slice and places observed results in the slides as demonstration evidence.

## 交付物 / Deliverables

第 2 页复用上次汇报的 `Target Workflow` 图，并将受保护区域标为 `UQ NETWORK`；该标签表示计划中的 UQ 部署边界，不表示已经接入 UQ 网络或身份系统。现场手动画出本周完成的 E2 边界；第 8 页比较 14B、32B 和 70B-class 的规划资源成本。 / Slide 2 reuses the previous report's `Target Workflow` figure and labels the protected area `UQ NETWORK`; this denotes the planned UQ deployment boundary, not an existing UQ network or identity integration. The E2 boundary completed this week is drawn live during the presentation. Slide 8 compares planning-level resource costs for 14B, 32B, and 70B-class models.
- `weekly-progress.tex`：8 页、16:9、仅英文 slides 的 XeLaTeX/Beamer 源码。 / Eight-slide, 16:9, English-only XeLaTeX/Beamer source.
- `beamerthemeUQWeekly.sty`：本目录的 Beamer 主题。 / Directory-local Beamer theme.
- `assets/demo/e2-tenant-isolation-full.png`：第 5 页使用的完整英文浏览器实验视图，包含应用、控件、指标和结果流。 / Full English browser experiment view used on slide 5, including the application, controls, metrics, and outcome stream.
- `assets/demo/e2-share-revoke-full.png`：第 6 页使用的完整英文浏览器实验视图，包含实际 share/retrieve/revoke 操作结果。 / Full English browser experiment view used on slide 6, including the observed share/retrieve/revoke outcomes.
- `speaker-notes.md`：逐页中英双语讲稿、现场操作步骤和主张边界。 / Bilingual slide-by-slide script, live runbook, and claim boundaries.
- `weekly-progress.pdf`：主要汇报文件。 / Primary presentation artifact.

## 实际演示证据 / Executed Demo Evidence

E2 浏览器演示在本机回环地址上实际执行，使用合成身份和合成数据，没有调用 LLM、云服务、UQ 身份系统或真实科研材料。

The E2 browser demo was executed on the local loopback interface with synthetic identities and synthetic data. It did not call an LLM, a cloud service, UQ identity infrastructure, or real research material. The slide captures use the browser's English presentation mode, which changes static labels only and does not alter authorization behavior or results.

观察结果：

Observed results:

- Carol 查询 `control result`：`ALLOW`，返回 `source-b1`。 / Carol queried `control result`: `ALLOW`, returning `source-b1`.
- Alice 执行同一查询：`NO EVIDENCE`。 / Alice ran the same query: `NO EVIDENCE`.
- Alice 对 `source-a2`：share 后 `ALLOW`，revoke 后恢复 `NO EVIDENCE`。 / For Alice and `source-a2`: `ALLOW` after share, returning to `NO EVIDENCE` after revoke.
- policy version 按 `1 -> 2 -> 3` 变化。 / The policy version changed `1 -> 2 -> 3`.
- forged claim：`DENY`。 / Forged claim: `DENY`.
- tampered bundle：`DENY`。 / Tampered bundle: `DENY`.
- audit chain verification：`PASS`。 / Audit-chain verification: `PASS`.

演示资产中不得包含启动 token、密钥、真实身份或真实科研数据。

Demo assets must not contain startup tokens, secrets, real identities, or real research data.

## 核心事实边界 / Core Claim Boundary

### E2 的含义 / What E2 Means

本项目的 Enterprise E2 是 `Identity-aware Retrieval`，即“身份感知检索”：服务端根据可信身份和策略先确定允许访问的 source 集合，再在该集合内检索，并在结果返回前重新授权。当前 slides 展示的是 E2 的 synthetic、model-free vertical slice，不是已经部署的 UQ 多用户 E2 服务。 / In this project, Enterprise E2 means `Identity-aware Retrieval`: the server derives an allowed source set from trusted identity and policy, retrieves only inside that set, and reauthorizes results before return. The slides show a synthetic, model-free E2 vertical slice, not a deployed UQ multi-user E2 service.

### 当前可展示 / Demonstrable Now

- Stage 1A 固定版本 `efea263`：本地科研助手、稳定 provider boundary、材料可选的聊天和 MCP STDIO facade。 / Stage 1A pin `efea263`: local research assistant, stable provider boundary, material-optional chat, and MCP STDIO facade.
- synthetic、model-free E2：服务端身份映射、tenant/project/source policy、SQLite forced scope、词法排序、source reauthorization、签名 evidence bundle 和不含正文的 audit chain。 / Synthetic, model-free E2: server-side identity mapping, tenant/project/source policy, SQLite forced scope, lexical ranking, source reauthorization, a signed evidence bundle, and a content-free audit chain.
- CLI 与浏览器演示共用同一 runtime。 / CLI and browser demonstrations share one runtime.
- 版本化 E2 验收记录为 `26 passed`。 / The versioned E2 acceptance record is `26 passed`.

### 尚未实现 / Not Implemented

- UQ SSO/OIDC、MFA、真实用户身份和正式 UQ 网络部署。 / UQ SSO/OIDC, MFA, real-user identity, and formal UQ network deployment.
- PostgreSQL `FORCE RLS`、pgvector、生产 RAG 和多用户持久服务。 / PostgreSQL `FORCE RLS`, pgvector, production RAG, and a persistent multiuser service.
- E2 与 Stage 1A、LLM、MCP、Tidy3D 或 Bunya 的端到端连接。 / End-to-end connection of E2 to Stage 1A, an LLM, MCP, Tidy3D, or Bunya.
- secure-release envelope、接收者密钥、外部投递、区块链 checkpoint。 / A secure-release envelope, recipient keys, external delivery, and a blockchain checkpoint.

SQLite/HMAC 是用于验证合同和失败模式的合成原型，不能描述为生产密码学或生产数据库安全。

SQLite and HMAC are synthetic prototype mechanisms for validating contracts and failure modes; they must not be presented as production cryptography or production database security.

### 可替换模型边界 / Model Replacement Boundary

LLM 负责推理和回答，但通过 provider/chat contract 与 Agent 的授权、证据、审计和工作流解耦。更换模型需要验证接口兼容性、科学回答质量、显存和作业成本；不应要求重写这些上层契约。 / The LLM handles reasoning and response generation, but provider/chat contracts decouple it from the Agent's authorization, evidence, audit, and workflow layers. Replacing a model requires compatibility, scientific-quality, VRAM, and job-cost benchmarks; it should not require rewriting those upper-layer contracts.

## 硬件、模型与费用边界 / Hardware, Model, and Cost Boundary

4-bit 模型的约 9--12 GB（14B）、20--24 GB（32B）和 40--48 GB（70B-class）显存仅用于规划比较；它们不是 Bunya 实测或固定价格。实际显存还取决于 context length、batch size、并发量、量化方式和 serving framework。 / Roughly 9--12 GB (14B), 20--24 GB (32B), and 40--48 GB (70B-class) of 4-bit VRAM are planning comparisons only, not Bunya measurements or fixed prices. Actual VRAM also depends on context length, batch size, concurrency, quantization, and the serving framework.
- 目前可以直接用已有 laptop/workstation 做 E2 演示和单用户 3B 开发；E2 不需要 GPU，3B 已在 RTX 4070 Ti 12 GB 上运行。相关成本是现有设备、电力和本地存储。 / The current laptop/workstation is enough for the E2 demonstration and single-user 3B development; E2 needs no GPU, and 3B has run on an RTX 4070 Ti with 12 GB. The relevant costs are existing equipment, power, and local storage.
- Bunya/RCC 的首轮模型候选是 4-bit `DeepSeek-R1-Distill-Qwen-14B`。它是第一次共享 GPU benchmark 的起点；只有当 14B 的科学推理或代码质量不足时，才测试 32B。模型选择是可替换的，不把 Agent 绑定到 DeepSeek。 / The first Bunya/RCC model candidate is 4-bit `DeepSeek-R1-Distill-Qwen-14B`. It is the starting point for a shared-GPU benchmark; test 32B only if 14B is insufficient for scientific reasoning or code quality. The model remains replaceable, so the Agent is not coupled to DeepSeek.
- Bunya 资源请求可以先按 `1 GPU with at least 16 GB VRAM / 8 CPU cores / 32 GB RAM` 讨论，但这些是规划起点，不是已验证最低配置；RCC 需要确认具体 GPU、配额、存储、服务费和账户政策。 / A Bunya request can start from `1 GPU with at least 16 GB VRAM / 8 CPU cores / 32 GB RAM`, but these are planning figures rather than validated minima; RCC must confirm the GPU type, quota, storage, charges, and account policy.
- Tidy3D 云端求解可能使用 FlexCredits，Hosted API 可能把数据带出 UQ；这些不自动包含在 Bunya 申请中，需要单独审批和项目预算。 / Tidy3D cloud solving may use FlexCredits, and hosted APIs may move data outside UQ; these are not automatically covered by a Bunya request and require separate approval and a project budget.

## 演示运行方法 / Run the Demonstration

从 E2 实现仓库启动随机回环端口：

Start the demo from the E2 implementation repository on a random loopback port:

```bash
python3 scripts/e2_web_demo.py --port 0
```

打开程序输出的完整 `READY http://127.0.0.1:PORT/#token=...` URL。不要只打开无 token 的基础 URL，也不要记录 token。

Open the complete `READY http://127.0.0.1:PORT/#token=...` URL printed by the program. Do not open only the base URL without its token, and do not record the token.

CLI 备用演示：

CLI fallback:

```bash
python3 scripts/e2_demo.py --all
```

从笔记本远程演示时，保持服务为 loopback-only，通过 SSH 转发程序打印的同一随机端口：

For a remote laptop demonstration, keep the service loopback-only and forward the same random port printed by the program:

```bash
ssh -N -L PORT:127.0.0.1:PORT USER@DESKTOP
```

该方式只用于演示，不代表已实现 UQ 组内生产服务。

This method is for demonstration only; it does not represent a deployed UQ group service.

## 构建 PDF / Build the PDF

从本目录使用 Windows TeX Live 2025：

Use Windows TeX Live 2025 from this directory:

```bash
cmd.exe /c "latexmk -xelatex -interaction=nonstopmode -halt-on-error weekly-progress.tex"
```

源码按系统名称解析 Arial 和 Times New Roman，不把字体文件复制到项目中。

The source resolves Arial and Times New Roman by system name; font files are not copied into the project.

## 最小验收 / Minimum Acceptance

```bash
pdfinfo weekly-progress.pdf
pdffonts weekly-progress.pdf
pdftotext -layout weekly-progress.pdf -
rg -n "Overfull|LaTeX Error|Package .* Error|Emergency stop|Fatal error" weekly-progress.log
```

还需检查以下事项：

Also verify the following:

- PDF 为 8 页、16:9，字体已嵌入。 / The PDF has eight 16:9 pages and embedded fonts.
- 每页渲染图无裁切、重叠或不可读文字。 / Every rendered page has no clipping, overlap, or unreadable text.
- slides 中仅有英文；speaker notes 和 README 中英双语。 / Slides are English-only; speaker notes and README are bilingual.
- 不出现 token、密钥、真实科研数据、敏感本机路径或过度主张。 / No tokens, secrets, real research data, sensitive local paths, or excessive claims appear.

## 数据与分发边界 / Data and Distribution Boundary

UQ 背景资产仅用于内部 thesis progress presentation。private GitHub.com 仍是 UQ 外部第三方；真实科研数据、prompt、embedding、日志、token、密钥和未公开结果不得进入本目录或普通 Git 历史。

UQ background assets are intended only for an internal thesis-progress presentation. Private GitHub.com remains an external third party; real research data, prompts, embeddings, logs, tokens, secrets, and unpublished results must not enter this directory or ordinary Git history.
