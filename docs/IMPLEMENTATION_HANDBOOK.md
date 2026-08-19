# 项目完整实现手册 / Complete Implementation Handbook

> 快照日期 / Snapshot date: `2026-08-19`
>
> Canonical work item / 规范工作项: [Industrial_Local_Agent#4](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/4)
>
> 文档性质 / Document type: 当前实现、待审差异与未来设计的统一阅读地图；源码仍是运行行为的最终权威。 / A unified reading map for current implementation, review-stage deltas, and future design; source code remains the final authority for runtime behavior.

## 0. 如何使用本手册 / How to Use This Handbook

本手册回答四类问题：现在真正能运行什么；Stage 1A 具体如何运行；哪些内容只有设计而没有代码；下一步为什么按当前顺序推进。它不会把计划写成能力，也不会把形式正确的证据引用写成科学真实性证明。

This handbook answers four questions: what is actually runnable now, exactly how Stage 1A works, which capabilities exist only as designs, and why the next work follows the current order. It does not present plans as delivered capability or formally valid citations as proof of scientific truth.

### 0.1 状态标签 / Status Labels

| 标签 / Label | 精确定义 / Exact meaning |
| --- | --- |
| **PINNED / 已固定** | 父仓库 gitlink 指向的子仓库 commit；递归克隆会得到该实现。 / The child commit referenced by the parent gitlink; a recursive clone obtains this implementation. |
| **MERGED CHILD / 子已合并** | 子仓库默认分支已包含该实现，但父 gitlink 尚未指向它；不能作为当前父递归 clone 的运行版本。 / The child default branch contains the implementation, but the parent gitlink does not yet point to it; it is not the current parent recursive-clone runtime. |
| **UNDER REVIEW / 待审** | 代码已存在于未合并 branch/PR，但不属于父仓库固定版本。 / Code exists on an unmerged branch/PR but is not part of the parent-pinned version. |
| **DESIGN ONLY / 仅设计** | 契约、威胁模型或验收门槛已写入文档，但没有可部署实现。 / Contracts, threat models, or acceptance gates are documented, but no deployable implementation exists. |
| **NOT IMPLEMENTED / 未实现** | 没有满足当前验收标准的代码或服务。 / No code or service satisfies the current acceptance criteria. |
| **HISTORICAL / 历史** | 保留当时判断，但当前顺序或状态由更新的父级文档取代。 / Preserves an earlier decision record whose sequencing or status is superseded by newer parent documentation. |

### 0.2 本快照的 Git 事实 / Git Facts for This Snapshot

| 对象 / Object | 状态 / State |
| --- | --- |
| Parent default branch / 父默认分支 | `main` at `51635a1`; Enterprise E0 and the Stage 1A pin are merged. / `main` 为 `51635a1`；Enterprise E0 和 Stage 1A pin 已合并。 |
| Parent E0 branch / 父 E0 分支 | `docs/2-enterprise-boundaries` at `72c5a44`, historical source branch for merged PR #3. / `72c5a44` 是已合并 PR #3 的历史源分支。 |
| Handbook branch / 本手册分支 | `docs/4-implementation-handbook`; this refresh is retargeted to parent `main`. / 本次刷新将 PR base 改为父仓库 `main`。 |
| Parent submodule pin / 父 gitlink | `components/stage1a-good-story-agent` -> `efea263da1b803a74a6a91c0e592949b3237203c`, merged through parent PR #11 / Issue #9. |
| Child default branch / 子默认分支 | `main` at `efea263`, component version `0.2.0`; this is also the parent pin. Merged stack includes E1 provider boundary, MCP C1, and material-optional Web chat. |
| Child historical baseline / 子历史基线 | `4e3bdda`, component `0.1.1`, recorded baseline `38 passed`; retained only for pin history. |
| Child historical E1 source / 子历史 E1 源码 | `367f971`, superseded by merged child main and retained only as historical review evidence. |

在本快照中，父仓库 index 与 child `main` 都固定到 `efea263`；本地 submodule 若显示 modified，仍可能只是 checkout 漂移，不等于新的 gitlink 更新。

In this snapshot both the parent index and child `main` point to `efea263`; a modified submodule in a parent worktree may still be local checkout drift, not a new gitlink update.

### 0.3 权威来源优先级 / Authority Order

| 问题 / Question | 首要权威 / Primary authority |
| --- | --- |
| 当前程序实际行为 / Current program behavior | 父 gitlink 固定的子仓库源码和测试 / Source and tests at the parent-pinned child commit |
| 当前阶段、顺序和 exit gate / Current stage, sequence, and exit gate | [ROADMAP.md](ROADMAP.md) |
| 组件与信任边界 / Component and trust boundaries | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Enterprise 字段契约与威胁测试 / Enterprise field contracts and threat tests | [ENTERPRISE_DEPLOYMENT.md](ENTERPRISE_DEPLOYMENT.md) |
| Git/GitHub 工作流程 / Git and GitHub workflow | [AGENTS.md](../AGENTS.md) |
| 机密漏洞报告路径 / Confidential vulnerability reporting | [SECURITY.md](../SECURITY.md) |

如果本手册与固定源码冲突，以固定源码为准；如果状态表与 Roadmap 冲突，以 Roadmap 为准，并为文档漂移创建新的 Issue。

If this handbook conflicts with pinned source, the pinned source wins. If its status table conflicts with the Roadmap, the Roadmap wins and the documentation drift requires a new Issue.

## 1. 一页理解整个项目 / One-Page Mental Model

`Industrial_Local_Agent` 不是一个已经完成的企业 Agent 产品。它是一个 private Git superproject，用 submodule 组织独立组件，并把本地科研写作、未来仿真结果适配、企业权限检索和安全发布放在清晰边界中。

`Industrial_Local_Agent` is not a finished enterprise-agent product. It is a private Git superproject that organizes independent components through submodules and gives local scientific writing, future simulation-result adaptation, enterprise authorized retrieval, and secure release explicit boundaries.

```text
Current runnable path / 当前可运行路径

Researcher-selected files
        |
        v
Stage 1A local Web or CLI
        |
        +--> deterministic ingestion, hashes, evidence IDs
        |
        +--> evidence audit (no LLM)
        |        or
        +--> loopback Ollama synthesis (local LLM)
        |
        v
validated analysis + deterministic report + provenance + redacted export ZIP

Future target / 未来目标

Institutional identity -> authorized retrieval -> signed evidence bundle
        -> Stage 1A worker -> controlled model gateway
        -> tenant result storage -> separate human-approved secure release
```

在当前 Agent 中，LLM 只负责受限综合。外围确定性代码负责输入限制、文件解析、哈希、evidence ID、prompt 边界、输出结构检查、数字与引用检查、溯源、报告、权限和导出警告。因此，它可以理解为“LLM 加受控科研工作流”，而不是一个能自主访问数据库、执行仿真或发布数据的模型。

In the current agent, the LLM performs bounded synthesis only. Deterministic code owns input limits, parsing, hashes, evidence IDs, prompt boundaries, output-structure checks, numeric and citation checks, provenance, reporting, permissions, and export warnings. It is therefore an LLM inside a controlled research workflow, not a model that autonomously accesses databases, runs simulations, or releases data.

## 2. 仓库和版本组织 / Repository and Version Organization

### 2.1 为什么是 Superproject / Why a Superproject

父仓库不复制子组件源码，也不改写其历史。父仓库保存跨组件架构、路线、安全和一个 160000-mode gitlink；子仓库保存 Stage 1A 自己的源码、测试和组件文档。

The parent does not copy child source or rewrite its history. It stores cross-component architecture, roadmap, security, and a mode-160000 gitlink; the child stores its own Stage 1A source, tests, and component documentation.

```text
Industrial_Local_Agent/                       parent repository
├── AGENTS.md                                  work governance
├── SECURITY.md                                security-report routing
├── README.md                                  status and navigation
├── docs/
│   ├── ARCHITECTURE.md                        component boundaries
│   ├── ENTERPRISE_DEPLOYMENT.md               E0 design and threat model
│   ├── IMPLEMENTATION_HANDBOOK.md              this document
│   └── ROADMAP.md                              stages and exit gates
└── components/
    └── stage1a-good-story-agent/               private Git submodule
```

递归克隆是恢复完整工作树的唯一正常入口。普通 GitHub ZIP 不携带 submodule 源码，父仓库权限也不会自动授予 private 子仓库权限。

Recursive clone is the normal way to restore the full tree. A normal GitHub ZIP does not contain submodule source, and access to the parent does not automatically grant access to the private child.

```bash
git clone --recurse-submodules git@github.com:Juggernautsst/Industrial_Local_Agent.git
cd Industrial_Local_Agent
```

已克隆但组件为空时使用：

Use this when the parent is already cloned but the component is empty:

```bash
git submodule update --init --recursive
```

### 2.2 Submodule 更新的事务顺序 / Submodule Update Transaction

1. 子仓库先创建 implementation Issue、修改、测试、commit、push 和 PR/merge。 / The child first owns the implementation Issue, changes, tests, commit, push, and PR/merge.
2. 确认目标 child commit 可从远端获取。 / Confirm the target child commit is reachable from the child remote.
3. 父仓库通过独立 Issue/PR 更新 gitlink。 / Update the parent gitlink through a separate parent Issue/PR.
4. 使用 `git diff --submodule` 审查指针变化，不能递归暂存子文件。 / Review the pointer with `git diff --submodule`; never recursively stage child files.
5. 完成集成验证后才能把新能力称为父仓库固定版本。 / Only after integration validation may the parent describe the new capability as pinned.

## 3. 能力阶段和实际实施顺序 / Capability Stages and Actual Sequence

| 能力 / Capability | 当前状态 / Current status | 关键事实 / Key fact |
| --- | --- | --- |
| Stage 1A engineering | **PINNED** | Parent and child both point to `efea263`, providing the provider boundary, MCP `STDIO` facade, and material-optional Web research chat. / 父子仓库均固定到 `efea263`，提供 provider boundary、MCP `STDIO` facade 和 material-optional Web chat。 |
| Stage 1A scientific acceptance | **NOT COMPLETE** | 只有 1/5 合成光子学案例；还缺四个案例和双人独立评价。 / One of five synthetic photonics cases; four cases and two independent evaluators remain. |
| Enterprise E0 | **DESIGN ONLY** | local/enterprise 模式、契约和威胁模型已定义；没有生产控制。 / Modes, contracts, and threat model are defined; production controls are absent. |
| Enterprise E1 provider boundary | **PINNED** | Child PR #2 is merged and parent PR #11 pins the resulting child main. / 子 PR #2 已合并，父 PR #11 已固定 child main。 |
| Enterprise E2 | **NOT IMPLEMENTED / ISSUE OPEN** | Parent Issue #10 defines the synthetic vertical slice; no implementation is delivered yet, and it must remain model-free until acceptance. / 父 Issue #10 定义合成 vertical slice；当前尚无实现，验收前必须保持无模型调用。 |
| Enterprise E3 | **NOT IMPLEMENTED** | 没有集中 model gateway、mTLS、registered provider 或容量控制。 / No centralized model gateway, mTLS, registered provider, or capacity controls. |
| Enterprise E4 | **NOT IMPLEMENTED** | 没有多 tenant Stage 1A 集成。 / No multitenant Stage 1A integration. |
| Stage 2 secure release | **DESIGN ONLY** | 协议基线已起草；加密包、审批、outbox 和交付尚无实现。 / Protocol baseline drafted; package, approval, outbox, and delivery are unimplemented. |
| Stage 1B Tidy3D | **NOT IMPLEMENTED** | 只有只读 adapter 数据契约。 / Only a read-only adapter data contract exists. |
| Stage 3 integrated workflow | **NOT IMPLEMENTED** | 还没有端到端统一产品。 / No end-to-end integrated product exists. |
| Blockchain | **DEFERRED** | 不是前置条件；原始科研数据永不写链。 / Not a prerequisite; raw research data never goes on-chain. |

编号表示能力边界，不表示当前排期。资源和风险约束下的串行顺序是：

Stage numbers identify capability boundaries, not current scheduling. The serial order under resource and risk constraints is:

```text
E2 identity-aware authorized retrieval vertical slice
  -> Stage 2.0 protocol
  -> separate secure-release implementation slices
  -> Tidy3D Stage 1B read-only adapter
```

E3/E4 在机构 provider、容量和运维边界确定后单独排期。Secure release 在架构上不依赖 E2；上述箭头只是本项目的实施顺序。

E3/E4 are scheduled separately after institutional provider, capacity, and operational boundaries are known. Secure release is not architecturally dependent on E2; the arrow describes this project's implementation order only.

## 4. Stage 1A 运行时总览 / Stage 1A Runtime Overview

### 4.1 固定版本端到端调用链 / Pinned End-to-End Call Chain

```text
CLI path(s) or Web multipart upload
        |
        v
InputFile[] + AnalysisOptions
        |
        v
AnalysisService.run()
        |
        +--> validate options
        +--> create UUID run directory (0700)
        +--> ingest_files()
                 |
                 +--> private input copies (0600)
                 +--> SourceArtifact[]
                 +--> EvidenceItem[]
        |
        +--> audit_draft()                  [backend=audit]
        |         or
        +--> OllamaBackend.synthesize()     [backend=ollama]
        |         +--> bounded prompt evidence
        |         +--> loopback /api/chat
        |         +--> calibrations and validation
        |         +--> at most one repair call
        |
        v
AnalysisDraft + provenance
        |
        +--> render_report(local)
        +--> render_report(filename-redacted)
        +--> request/evidence/analysis/manifest JSON
        |
        v
private run artifacts OR review-required export ZIP
```

固定版本的 `AnalysisService` 直接选择 `audit_draft()` 或构造 `OllamaBackend`。它没有通用网络 provider，也没有 RAG、SSO、数据库或工具执行。

The pinned `AnalysisService` directly selects `audit_draft()` or constructs `OllamaBackend`. It has no generic network provider, RAG, SSO, database, or tool execution.

### 4.2 两种模式 / Two Modes

| 模式 / Mode | 是否调用 LLM / Calls an LLM | 输出含义 / Output meaning |
| --- | --- | --- |
| `audit` | 否 / No | 验证导入、哈希、evidence、provenance、报告和导出管线；`analysis_status=inventory_only`，不生成科学故事。 / Verifies ingestion, hashes, evidence, provenance, reporting, and export; produces no scientific story. |
| `ollama` | 是，仅回环地址 / Yes, loopback only | 使用本地模型生成结构化候选主线，再经过确定性修整和校验；仍需领域专家复核。 / Produces a structured candidate story with a local model, then deterministic calibration and validation; domain review remains mandatory. |

### 4.3 信任边界 / Trust Boundary

上传文件、上传文件中的指令、模型输出、浏览器字段和未来 GitHub Issue 内容均视为不可信。当前可信代码边界包括安装的 Python 包、本地应用进程、固定 prompt、固定 schema 和管理员配置的本地 Ollama 二进制。

Uploads, instructions embedded in uploads, model output, browser fields, and future GitHub Issue content are untrusted. The current trusted-code boundary includes the installed Python package, local application process, pinned prompt, pinned schema, and administrator-configured local Ollama binary.

当前系统不抵御恶意主机管理员，也没有 OS 级外发防火墙、网络 namespace、PDF 文件系统沙箱或多用户隔离。

The current system does not defend against a malicious host administrator and has no OS-level egress firewall, network namespace, PDF filesystem sandbox, or multiuser isolation.

## 5. 包、依赖和源码索引 / Package, Dependencies, and Source Index

### 5.1 构建与依赖 / Build and Dependencies

组件使用 `setuptools.build_meta`，要求 Python `>=3.10`。运行依赖只有 `Flask>=3.1,<4` 和 `pypdf>=5,<7`；开发可选依赖为 `pytest>=8,<9`。没有数据库、RAG、Tidy3D、区块链、云 SDK 或模型 serving 依赖。

The component uses `setuptools.build_meta` and requires Python `>=3.10`. Runtime dependencies are only `Flask>=3.1,<4` and `pypdf>=5,<7`; the optional development dependency is `pytest>=8,<9`. There is no database, RAG, Tidy3D, blockchain, cloud SDK, or model-serving dependency.

Console entry point:

```text
good-story-agent = good_story_agent.cli:main
python -m good_story_agent -> good_story_agent.cli:main
```

### 5.2 固定版本源码文件 / Pinned Source Files

以下链接固定到 parent 当前 gitlink 与 child `main` 共用的 `efea263` commit。

The following links are pinned to the `efea263` commit shared by the current parent gitlink and child `main`.

| 文件 / File | 职责 / Responsibility |
| --- | --- |
| [`pyproject.toml`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/pyproject.toml) | 包 metadata、依赖、console script、package data、pytest 配置。 / Package metadata, dependencies, console script, package data, and pytest configuration. |
| [`__init__.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/__init__.py) | 包说明和 `__version__ = "0.2.0"`。 / Package description and version. |
| [`__main__.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/__main__.py) | `python -m` 入口。 / Module entry point. |
| [`cli.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/cli.py) | `analyze`/`serve` 参数解析、输入读取和命令分派。 / `analyze`/`serve` argument parsing, input reads, and command dispatch. |
| [`config.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/config.py) | 常量、环境变量、私有目录和回环 URL 校验。 / Constants, environment settings, private directories, and loopback URL validation. |
| [`models.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/models.py) | 运行时 dataclass。 / Runtime dataclasses. |
| [`ingest.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/ingest.py) | 文件校验、解析、哈希、locator 和 evidence 分配。 / File validation, parsing, hashes, locators, and evidence allocation. |
| [`pdf_worker.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/pdf_worker.py) | 资源受限的 PDF 文本提取子进程。 / Resource-bounded PDF text-extraction subprocess. |
| [`backends.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/backends.py) | audit、prompt 构造、本地 Ollama transport、修整和一次 repair。 / Audit, prompt construction, local Ollama transport, calibration, and one repair. |
| [`schema.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/schema.py) | JSON response schema 和手工语义校验。 / JSON response schema and manual semantic validation. |
| [`service.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/service.py) | 端到端编排、运行存储、读取和导出。 / End-to-end orchestration, run storage, reads, and export. |
| [`report.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/report.py) | 确定性 Markdown renderer。 / Deterministic Markdown renderer. |
| [`web.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/web.py) | Flask app、安全检查和 HTTP routes，包括 material-optional chat。 / Flask app, security checks, HTTP routes, including material-optional chat. |
| [`chat.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/chat.py) | 无工具、回环 Ollama 的 research-chat provider 和可选附件上下文。 / Tool-free loopback Ollama research-chat provider with optional attachment context. |
| [`mcp_server.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/mcp_server.py) | client-neutral MCP `STDIO` facade；只暴露最小分析、报告和 provenance 工具。 / Client-neutral MCP `STDIO` facade with minimal analysis, report, and provenance tools. |
| [`index.html`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/templates/index.html) | 单页工作界面。 / Single-page work interface. |
| [`app.js`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/static/app.js) | 浏览器状态、token、chat、可选附件、上传、API、历史和下载。 / Browser state, token, chat, optional attachments, uploads, APIs, history, and downloads. |
| [`app.css`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/static/app.css) | 工作台布局、chat 状态、表单、结果和移动响应式样式。 / Workspace layout, chat states, forms, results, and responsive styles. |
| [`good_story_stage1a.md`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/prompts/good_story_stage1a.md) | 固定科研故事 system prompt。 / Pinned scientific-story system prompt. |
| [`start-local.sh`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/scripts/start-local.sh) | 带隐私环境变量的 Ollama 和 Web 生命周期。 / Ollama and Web lifecycle with privacy-oriented environment settings. |

## 6. 配置、环境变量和硬限制 / Configuration, Environment Variables, and Hard Limits

### 6.1 应用常量 / Application Constants

| 常量 / Constant | 值 / Value | 行为 / Behavior |
| --- | ---: | --- |
| `APP_VERSION` | `0.2.0` | 与 package version 由测试保持一致。 / Kept equal to package version by a test. |
| `PROMPT_VERSION` | `stage1a-2026-07-28` | 写入 provenance；实际 prompt 还计算 SHA-256。 / Written to provenance; the actual prompt contract is also SHA-256 hashed. |
| `DEFAULT_OLLAMA_URL` | `http://127.0.0.1:11434` | 只能改为合法回环 URL。 / May only be changed to a valid loopback URL. |
| `DEFAULT_MODEL` | `qwen2.5:3b` | Ollama/chat 模式未显式选模型时使用。 / Used when Ollama/chat mode does not specify a model. |
| `MAX_FILES` | `10` | 每个 run 文件数上限。 / File-count limit per run. |
| `MAX_FILE_BYTES` | `5 MiB` | 单文件上限。 / Per-file limit. |
| `MAX_TOTAL_BYTES` | `20 MiB` | 全部上传合计上限。 / Combined upload limit. |
| `MAX_PDF_PAGES` | `100` | PDF 页数上限。 / PDF page limit. |
| `MAX_EVIDENCE_ITEMS` | `240` | evidence index 上限。 / Evidence-index limit. |
| `MAX_PROMPT_CHARS` | `72,000` | 进入模型 payload 的近似字符预算。 / Approximate character budget for model payload evidence. |
| Allowed extensions / 扩展名 | `.txt .md .csv .json .pdf` | 扩展名 allowlist，不做 MIME magic 检测。 / Extension allowlist; no MIME magic detection. |

### 6.2 应用环境变量 / Application Environment Variables

| 变量 / Variable | 默认值 / Default | 说明 / Meaning |
| --- | --- | --- |
| `XDG_DATA_HOME` | `$HOME/.local/share` | 应用默认 run root 和 launcher 默认 Ollama model root 的上级目录；必须位于受保护的 Linux filesystem。 / Parent of the default run root and launcher Ollama model root; must be on a protected Linux filesystem. |
| `XDG_STATE_HOME` | `$HOME/.local/state` | launcher 的 state directory 和 `ollama.log` 上级目录。 / Parent of the launcher's state directory and `ollama.log`. |
| `OLLAMA_MODELS` | `$XDG_DATA_HOME/ollama/models` | launcher 使用并尝试设为 `0700` 的模型目录；模型权重本身是受控 artifact。 / Model directory used and chmodded to `0700` by the launcher; model weights are controlled artifacts. |
| `GOOD_STORY_RUNS_DIR` | `$XDG_DATA_HOME/good-story-agent/runs` | 改变运行产物目录；POSIX 上必须能强制 `0700`。 / Changes run storage; POSIX must enforce `0700`. |
| `GOOD_STORY_OLLAMA_URL` | `http://127.0.0.1:11434` | 必须含 `http/https`、host、port，无 credentials/query/fragment，host 必须是 loopback。 / Requires scheme, host, and port; forbids credentials/query/fragment and non-loopback hosts. |
| `GOOD_STORY_MODEL` | `qwen2.5:3b` | 非空且最多 160 字符；后端还有字符 allowlist。 / Nonempty and at most 160 characters; backend applies another character allowlist. |
| `GOOD_STORY_SESSION_TOKEN` | 随机 32-byte URL-safe token / random 32-byte URL-safe token | 可选固定 Web 启动 token；长度必须为 32-256 字符。 / Optional fixed startup token; must be 32-256 characters. |
| `GOOD_STORY_OLLAMA_BIN` | `command -v ollama` | launcher 使用的 Ollama 可执行文件。 / Ollama executable used by the launcher. |

`Settings.request_timeout_seconds` 默认 `180`，当前没有环境变量覆盖入口。

`Settings.request_timeout_seconds` defaults to `180`; there is currently no environment-variable override.

### 6.3 Launcher 设置 / Launcher Settings

现有 `start-local.sh` 面向 GNU/Linux 或 WSL：它依赖 POSIX `sh`、`.venv/bin` 布局、`python3`、`curl`、GNU `stat -c`、常规 POSIX file/process tools 和已安装的 Ollama。它不是 Windows `cmd`/PowerShell 或 macOS/BSD 兼容 launcher。PDF worker 的 CPU/address-space/file-descriptor limits 也只在 Python 提供 POSIX `resource` module 时生效。

The current `start-local.sh` targets GNU/Linux or WSL and depends on POSIX `sh`, the `.venv/bin` layout, `python3`, `curl`, GNU `stat -c`, ordinary POSIX file/process tools, and an installed Ollama. It is not a Windows `cmd`/PowerShell or macOS/BSD-compatible launcher. The PDF worker's CPU, address-space, and file-descriptor limits likewise apply only when Python provides the POSIX `resource` module.

脚本使用 `set -eu` 和 `umask 077`，验证 Web 端口为 `1..65535`，并要求项目 `.venv` 的 console script 存在。它会拒绝能在 `127.0.0.1:11434/api/version` 成功响应的既有 Ollama，但这不是通用端口占用检测；其他进程占用该端口时，通常由新 Ollama 退出和后续 readiness 探测暴露。

The script uses `set -eu` and `umask 077`, validates the Web port in `1..65535`, and requires the project `.venv` console script. It refuses an existing Ollama that successfully answers `127.0.0.1:11434/api/version`, but this is not a general port-occupancy check; another process on that port is normally exposed when the new Ollama exits and readiness probes fail.

它设置：

It sets:

```text
OLLAMA_HOST=127.0.0.1:11434
OLLAMA_NOHISTORY=1
OLLAMA_NO_CLOUD=1
OLLAMA_CONTEXT_LENGTH=32768
OLLAMA_FLASH_ATTENTION=1
GOOD_STORY_OLLAMA_URL=http://127.0.0.1:11434
```

它清除 `OLLAMA_DEBUG_LOG_REQUESTS`，将模型和状态目录设为 `0700`、log 设为 `0600`，并最多执行 30 次 readiness probe。每次 `curl` 可等待 2 秒，失败后再 sleep 1 秒，因此这不是严格的 30 秒 wall-clock timeout。Shell trap 会在 Web 退出、INT 或 TERM 时终止它启动的 Ollama 子进程。

It unsets `OLLAMA_DEBUG_LOG_REQUESTS`, sets model and state directories to `0700` and the log to `0600`, and performs at most 30 readiness probes. Each `curl` may wait two seconds and is followed by a one-second sleep on failure, so this is not a strict 30-second wall-clock timeout. A shell trap terminates the Ollama child when the Web process exits or receives INT/TERM.

这些应用级 flags 不等于操作系统外发隔离；manifest 和 health endpoint 因此明确记录 `egress_isolation_verified=false`。

These application-level flags are not OS egress isolation; the manifest and health endpoint therefore explicitly record `egress_isolation_verified=false`.

## 7. 内部数据结构 / Internal Data Structures

| 类型 / Type | 关键字段 / Key fields | 生命周期 / Lifecycle |
| --- | --- | --- |
| `InputFile` | `name`, raw `content: bytes` | CLI 或 Web 将明确选择的文件转成内存对象。 / CLI or Web turns explicitly selected files into an in-memory object. |
| `SourceArtifact` | source/stored/original name、extension、SHA-256、size、coverage、warnings | 描述一个输入来源及其覆盖情况。 / Describes one input source and its coverage. |
| `EvidenceItem` | `evidence_id`, `source_id`, `locator`, `text`, chunk SHA-256, `kind` | 模型和报告使用的最小可定位证据块。 / Minimal locatable evidence used by model and report. |
| `Corpus` | `sources`, `evidence`, `warnings` | 一个 run 的规范化输入集合。 / Normalized input collection for one run. |
| `AnalysisOptions` | backend、model、language、audience、research stage、context note | 用户可控分析选项；由 service 再校验。 / User-controlled analysis options revalidated by the service. |
| `AnalysisDraft` | status、source depth、domain calibration、best story、story spine、claims、weak points、rewrites、limitations、negative results、warnings | audit 构造或 Ollama 生成并校验后的结构化结果。 / Structured result built by audit or generated and validated from Ollama. |
| `RunRecord` | run ID/time/path/backend/model/evidence count/report/analysis/manifest | service 返回给 CLI/Web 的内存结果。 / In-memory result returned to CLI/Web. |

`dataclass_dict()` 是 `asdict()` 的薄封装。当前主要 service 直接调用 `asdict()`，该 helper 没有额外验证行为。

`dataclass_dict()` is a thin wrapper around `asdict()`. The main service currently calls `asdict()` directly; the helper adds no validation behavior.

## 8. 文件摄取与 Evidence 算法 / File Ingestion and Evidence Algorithms

### 8.1 通用验证和保存 / Common Validation and Storage

`ingest_files()` 要求至少一个且不超过 10 个文件，先检查总字节数，再逐文件检查空文件、5 MiB 上限和扩展名。文件名中的 Windows/Unix 路径部分被丢弃，只保留 basename；NUL、空名、`.`、`..` 和超过 180 字符的名称被拒绝。

`ingest_files()` requires one to ten files, checks combined bytes first, then rejects empty files, files over 5 MiB, and disallowed extensions. Windows/Unix path prefixes are discarded to retain only the basename; NUL, empty names, `.`, `..`, and names over 180 characters are rejected.

每个完整文件计算 SHA-256，source ID 格式为 `SRC-<three digits>-<first eight digest chars>`。本地保存名只使用 source ID 和扩展名，避免路径遍历；input directory 为 `0700`，文件为 `0600`。

Each complete file receives a SHA-256 and a source ID of `SRC-<three digits>-<first eight digest chars>`. The stored name uses only the source ID and extension to prevent path traversal; the input directory is `0700` and files are `0600`.

### 8.2 TXT 和 Markdown / TXT and Markdown

非 PDF 文本拒绝 NUL byte，使用 `utf-8-sig` 解码，因此接受普通 UTF-8 和 UTF-8 BOM；无效 UTF-8 与空白-only 内容失败。实现没有通用 binary/MIME 检测，因此不含 NUL 的有效 UTF-8 control character 仍可能通过。

Non-PDF text rejects NUL bytes and decodes with `utf-8-sig`, accepting ordinary UTF-8 and a UTF-8 BOM; invalid UTF-8 and whitespace-only content fail. There is no general binary/MIME detector, so valid UTF-8 control characters without NUL may still pass.

文本 chunk 最多 30 行且目标最多约 4,000 字符。locator 为 `L<start>-L<end>`，kind 为 `scientific-text`。极长单行可以超过 4,000 字符，因为上限只在已经包含至少一行时阻止加入下一行。

Text chunks contain at most 30 lines and target roughly 4,000 characters. The locator is `L<start>-L<end>` and kind is `scientific-text`. A single very long line can exceed 4,000 characters because the bound only prevents adding a subsequent line after at least one line is selected.

### 8.3 CSV

CSV 使用 Python `csv.reader(..., strict=True)`，删除完全空的 row，要求 header 加至少一条数据，header 每列非空，且所有数据 row 与 header 列数相同。每 20 条数据 row 形成一个 `table` evidence chunk，并重复 header；locator 记录删除空 row 后的逻辑数据行范围和列名，不保证对应原文件的物理行号。

CSV uses Python `csv.reader(..., strict=True)`, removes completely empty rows, requires a header plus one data row, requires nonempty header cells, and enforces the same column count for every data row. Each 20 data rows form one `table` evidence chunk with the header repeated; its locator records logical data-row bounds after empty-row removal and is not guaranteed to match physical lines in the original file.

它验证结构，不验证单位、列语义、数值类型、missing-value 语义或科学合理性。

It validates structure, not units, column semantics, numeric types, missing-value meaning, or scientific plausibility.

### 8.4 JSON

JSON 通过标准 parser 读取，递归展开为 RFC 6901 风格 pointer/value 行；`~` 转义为 `~0`，`/` 转义为 `~1`。每 25 个叶节点形成一个 `structured-data` chunk，空 object/array 也作为叶值保留。

JSON is parsed with the standard parser and recursively flattened into RFC-6901-style pointer/value lines; `~` becomes `~0` and `/` becomes `~1`. Each 25 leaves form one `structured-data` chunk, and empty objects/arrays remain as leaf values.

它不针对业务 schema 校验 JSON，也不限制嵌套深度；文件字节上限是主要输入边界。

It does not validate JSON against a business schema or explicitly limit nesting depth; the file-byte limit is the primary input bound.

### 8.5 PDF

PDF 保存后交给独立 Python 子进程，父进程 timeout 为 45 秒。传给子进程的 environment 只保留 `PATH`、`PYTHONPATH` 和 UTF-8 I/O 设置。子进程在支持 `resource` 的当前 POSIX 环境中设置：30 秒 CPU、1 GiB address space、32 MiB output file 和 64 file descriptors。

After storage, a PDF is passed to a separate Python subprocess with a 45-second parent timeout. Its environment retains only `PATH`, `PYTHONPATH`, and UTF-8 I/O settings. In the current POSIX environment with `resource`, the child sets 30 seconds of CPU, 1 GiB address space, a 32 MiB file-size limit, and 64 file descriptors.

`pypdf.PdfReader(strict=True)` 最多接受 100 页和 8,000,000 个提取字符。空密码可打开的 encrypted PDF 可以继续；真正 password-protected PDF 失败。每页提取文本按普通行 chunk，再将 locator 改为 `p<page>:Lx-Ly`，多 segment 时附序号。

`pypdf.PdfReader(strict=True)` accepts at most 100 pages and 8,000,000 extracted characters. An encrypted PDF openable with an empty password may continue; a genuinely password-protected PDF fails. Extracted text is line-chunked per page, with locators rewritten as `p<page>:Lx-Ly` and segment numbers when needed.

空页产生 warning；整个 PDF 没有可提取文本时失败。没有 OCR、图片理解、嵌入对象执行或 DOCX 支持。资源限制不是完整文件系统/网络沙箱，因此当前只接受可信 PDF。

Empty pages produce warnings; a PDF with no extractable text fails. There is no OCR, image understanding, embedded-object execution, or DOCX support. Resource bounds are not a complete filesystem/network sandbox, so only trusted PDFs are currently appropriate.

### 8.6 Evidence 选择、ID 和覆盖 / Evidence Selection, IDs, and Coverage

解析后，每个 source 的 chunk 进入单独 queue。系统 round-robin 每个 source 取一个 chunk，直到全部耗尽或达到 240 个；这样大文件不能在排序上完全挤掉小文件。

After parsing, chunks from each source enter a separate queue. The system takes one chunk from each source in round-robin order until all are exhausted or 240 are selected, preventing one large file from consuming the entire prefix.

超过 240 的剩余 chunk 被标记为 omitted；相应 source 的 `coverage_status` 变为 `limited`，detail 和 warnings 记录省略数量。被选择的 chunk 按最终顺序获得 `EV-0001` 等 ID，每个 chunk text 另算 SHA-256。

Chunks beyond 240 are marked omitted; the corresponding source becomes `coverage_status=limited`, with the omission count in details and warnings. Selected chunks receive IDs such as `EV-0001` in final order, and each chunk text receives its own SHA-256.

引用字符串格式为：

Citation format:

```text
[EV-0001|SRC-001-<digest8>:<locator>]
```

SHA-256 提供字节完整性关联，不提供匿名化、作者身份、科学真实性或时间戳证明。

SHA-256 provides byte-integrity correlation, not anonymization, author identity, scientific truth, or timestamp proof.

## 9. Audit 与 Ollama 综合 / Audit and Ollama Synthesis

### 9.1 Audit 模式 / Audit Mode

`audit_draft()` 完全不调用模型。它根据任一 source 是否 `limited` 设置 source depth，复制 corpus warnings，并明确加入“没有调用语言模型、没有生成科学故事”的提示。

`audit_draft()` never calls a model. It sets source depth from whether any source is `limited`, copies corpus warnings, and explicitly states that no language model was called and no scientific story was generated.

输出行为：

Output behavior:

- `analysis_status = inventory_only`；该值是 audit 内部状态，Ollama response schema 只允许 `complete` 或 `provisional`。 / `analysis_status = inventory_only`; this is an audit-only internal state, while the Ollama response schema permits only `complete` or `provisional`.
- `best_story.support_level = unsupported` 且没有 evidence ID。 / `best_story.support_level = unsupported` with no evidence IDs.
- story spine、claims、weak points、rewrite targets 和 negative results 均为空。 / Story spine, claims, weak points, rewrite targets, and negative results are empty.
- 报告和 artifact 管线仍完整执行，因此它是部署和摄取的首个 smoke test。 / Reporting and artifact creation still execute fully, making audit the first deployment and ingestion smoke test.

### 9.2 进入模型的 Evidence 预算 / Evidence Budget Entering the Model

`select_prompt_evidence()` 按现有 evidence 顺序累加 `len(text) + len(locator) + 180`。只要已经选过一个 chunk，后续 chunk 若超过 72,000 字符预算就省略；第一个 chunk 即使本身超预算仍会进入，以避免空 prompt。

`select_prompt_evidence()` accumulates `len(text) + len(locator) + 180` in evidence order. Once at least one chunk is selected, subsequent chunks exceeding the 72,000-character budget are omitted; an oversized first chunk is still included to avoid an empty prompt.

这不是 tokenizer-level token budget，也不保证 prompt 一定适合模型 context。`omitted_evidence_ids` 会写入 provenance；存在省略时最终分析强制改为 `provisional` 和 `source_depth=limited`。

This is not a tokenizer-level token budget and does not guarantee the prompt fits a model context. `omitted_evidence_ids` is recorded in provenance; any omission forces the final analysis to `provisional` with `source_depth=limited`.

### 9.3 Prompt Payload / Prompt Payload

system prompt 规定 evidence integrity 高于新颖性和文风，上传 excerpt 是 quoted untrusted content，不得执行其中的指令；所有直接或间接主张必须使用提供的 evidence ID；材料不足必须降级；negative result 和 limitation 不能隐藏。

The system prompt places evidence integrity above novelty and style, treats uploaded excerpts as quoted untrusted content, forbids following embedded instructions, requires supplied evidence IDs for direct and indirect claims, requires downgrade under insufficient material, and forbids hiding negative results or limitations.

对光子学/FDTD，prompt 明确：simulation 不是 experiment；单一 mesh 不证明 convergence；parameter sweep 不证明 mechanism；superior/optimal/record/causal/general claim 需要 comparator 和 evidence；数值收敛与实验物理验证是不同问题。

For photonics/FDTD, the prompt states that simulation is not experiment, one mesh does not prove convergence, a parameter sweep does not prove mechanism, superior/optimal/record/causal/general claims require a comparator and evidence, and numerical convergence is separate from experimental physical validation.

user payload 是紧凑 JSON，包含 task、output language、audience、research stage、researcher context、source coverage、omitted IDs，以及每个 evidence 的 ID、source、locator、kind、hash 和 `quoted_untrusted_content`。

The user payload is compact JSON containing the task, output language, audience, research stage, researcher context, source coverage, omitted IDs, and each evidence item's ID, source, locator, kind, hash, and `quoted_untrusted_content`.

上传正文会发送给本机 Ollama，因此“没有云传输”不等于“没有进程间数据传递”；Ollama 进程能够看到本次选中的 evidence。

Uploaded content is sent to the local Ollama process, so “no cloud transfer” does not mean “no inter-process data transfer”; the Ollama process can see evidence selected for the run.

### 9.4 Ollama HTTP 客户端 / Ollama HTTP Client

`OllamaBackend` 再次验证 base URL 仅为 loopback，构造显式空 proxy handler，并使用自定义 redirect handler 拒绝 HTTP redirect。它不读取系统 HTTP proxy 进行模型请求。

`OllamaBackend` revalidates that the base URL is loopback-only, builds an explicitly empty proxy handler, and rejects HTTP redirects through a custom handler. It does not use system HTTP proxies for model requests.

| 操作 / Operation | Endpoint | 限制 / Bound |
| --- | --- | --- |
| 列模型 / List models | `GET /api/tags` | 3 秒默认 timeout，metadata response 最多 2 MiB；失败时 health path 返回空 model list。 / Default 3-second timeout and 2 MiB metadata response; the health path treats failure as an empty model list. |
| 模型 digest / Model digest | `GET /api/tags` | 匹配原名或 `:latest` alias；找不到时写 `not-reported`。 / Matches original or `:latest` alias; records `not-reported` when absent. |
| Server version | `GET /api/version` | 同样的 metadata 限制。 / Same metadata bounds. |
| Chat | `POST /api/chat` | 180 秒默认 timeout，response 最多 10 MiB。 / Default 180-second timeout and 10 MiB response. |

模型名必须匹配 `[A-Za-z0-9._:/-]{1,160}`，且以 `:cloud` 结尾的名称被拒绝。请求参数固定为 non-streaming、JSON schema format、temperature `0.1`、seed `42`、`keep_alive=5m`。

Model names must match `[A-Za-z0-9._:/-]{1,160}`, and names ending in `:cloud` are rejected. Requests are fixed to non-streaming, JSON-schema format, temperature `0.1`, seed `42`, and `keep_alive=5m`.

连接、timeout 或 JSON 错误都会明确失败。只有 chat POST 的连接/timeout 错误文案显式写出 no cloud fallback；metadata 和 JSON 错误文案没有该句，但控制流同样不会尝试第二个模型、其他 endpoint 或云 API。

Connection, timeout, and JSON failures are explicit. Only the chat POST connection/timeout message explicitly states that no cloud fallback was used; metadata and JSON error messages omit that sentence, but their control flow likewise never tries a second model, another endpoint, or a cloud API.

### 9.5 输出修整与一次 Repair / Output Calibration and One Repair

模型 response 的 `message.content` 必须是非空 string，随后按以下顺序处理：

The model response `message.content` must be a nonempty string, then processing occurs in this order:

1. 解析 JSON，并从 limitations/warnings/weak points/rewrite targets/negative results 中排除特定 instruction-shaped echo。 / Parse JSON and remove selected instruction-shaped echoes from limitations, warnings, weak points, rewrite targets, and negative results.
2. 删除 narrative string 中内联的 `(EV-0001, ...)`，要求 evidence ID 只存在于数组。 / Remove inline `(EV-0001, ...)` groups from narrative strings so evidence IDs remain in arrays only.
3. 若 cited evidence 没有统计检验、置信区间或明确显著性支持，保守删除模型生成的“significant/显著”措辞，并加 warning。 / Conservatively remove model-generated significance wording when cited evidence lacks a test, confidence interval, or explicit significance support, then add a warning.
4. 对 narrative 中的数值，若当前引用不含该值但另一 evidence chunk 精确含有该数值，补充引用并加 warning；不改变原陈述。 / For narrative numbers absent from current citations but exactly present in another evidence chunk, add that citation and a warning without changing the statement.
5. 调用 `validate_draft()`。 / Call `validate_draft()`.

第一次解析或校验失败时，系统把失败摘要截到 500 字符，连同第一次 response 发送给同一个模型，要求只返回修正 JSON。只允许一次 repair；第二次失败转换为 `BackendError`。

If the first parse or validation fails, the system truncates the error summary to 500 characters and sends it with the first response to the same model, requesting corrected JSON only. Exactly one repair is allowed; a second failure becomes `BackendError`.

这次 repair 会再次把模型先前输出发送给本地 Ollama，不会调用外部工具。由于生成模型可能不确定，即使 seed 固定也不能承诺跨硬件/版本 bit-for-bit reproducibility。

The repair resends the previous model output to local Ollama and invokes no external tool. Because generation may remain nondeterministic, a fixed seed does not guarantee bit-for-bit reproducibility across hardware and versions.

## 10. Response Schema 与机械校验 / Response Schema and Mechanical Validation

### 10.1 顶层结构 / Top-Level Structure

Ollama response schema 禁止额外顶层字段，并要求：

The Ollama response schema disallows extra top-level properties and requires:

```text
analysis_status
source_depth
domain_calibration
best_story
why_it_works
story_spine[]
claims[]
weak_points[]
rewrite_targets[]
limitations[]
negative_results[]
warnings[]
```

`analysis_status` 对模型只允许 `complete|provisional`；`source_depth.status` 只允许 `complete|limited`；support level 枚举为 `direct|indirect|candidate|unsupported`。

For model output, `analysis_status` permits only `complete|provisional`, `source_depth.status` only `complete|limited`, and support level is `direct|indirect|candidate|unsupported`.

### 10.2 `validate_draft()` 实际执行的保证 / Guarantees Actually Enforced by `validate_draft()`

- 顶层 keys 必须恰好匹配 required set。 / Top-level keys must exactly match the required set.
- `source_depth`、`domain_calibration`、`best_story`、`why_it_works` 和各 list item 的 key set 必须匹配。 / Key sets for core objects and list items must match.
- 引用的 evidence ID 必须存在于本次 corpus。 / Referenced evidence IDs must exist in the current corpus.
- direct/indirect best story 和 claim 必须至少有一个 evidence ID。 / Direct/indirect best stories and claims require at least one evidence ID.
- 每个 story-spine item 必须引用 evidence。 / Every story-spine item requires evidence.
- claim ID 在同一输出中必须唯一。 / Claim IDs must be unique within the output.
- 被检查 narrative 中的数值必须出现在其 cited evidence；`EV/SRC/C` identifier 中的数字先被排除。 / Numbers in checked narratives must occur in cited evidence; numbers inside `EV/SRC/C` identifiers are excluded first.
- 被检查 narrative 的“significant/显著”必须由 cited evidence 的显著性 pattern 支持。 / Significance language in checked narratives must be supported by a significance pattern in cited evidence.
- 特定 instruction-shaped phrases 不得回显到检查的 output strings。 / Selected instruction-shaped phrases may not be echoed into checked output strings.
- 如果 source ingestion 已 limited，结果强制改为 provisional，并增加 warning。 / If source ingestion was limited, the result is forced to provisional with a warning.

数字比较使用 `Decimal.normalize()`，因此 `0.840` 与 `0.84` 视为相同数值；单位、上下文、变量名称和正负方向的语义关系并不由数值集合检查证明。

Numeric comparison uses `Decimal.normalize()`, so `0.840` and `0.84` are treated as the same value; units, context, variable identity, and directional semantics are not proven by numeric-set matching.

### 10.3 语言行为 / Language Behavior

service 和 CLI/Web 只允许 `zh-CN` 或 `en`。代码中存在 `bilingual` renderer/validator 支持，但当前产品入口拒绝该值，因为默认小模型无法稳定让每个 narrative 字段同时满足中英文契约。

The service and CLI/Web permit only `zh-CN` or `en`. Internal renderer/validator support for `bilingual` exists, but current product entry points reject it because the default small model cannot reliably satisfy bilingual content in every narrative field.

需要对照报告时，应对相同材料分别运行中文和英文；它们是两个独立 run、两个模型输出和两套 provenance，不保证逐句等价。

For paired reports, run the same material once in Chinese and once in English; these are independent runs with separate model outputs and provenance and are not guaranteed sentence-equivalent.

### 10.4 机械保证没有覆盖的内容 / What Mechanical Validation Does Not Cover

以下不是推测，而是当前实现边界：

The following are current implementation boundaries, not speculation:

1. `why_it_works` 没有 evidence ID 字段，因此 tension/turn/audience/consequence 不做 citation-subset 或 numeric traceability 校验。 / `why_it_works` has no evidence-ID fields, so tension/turn/audience/consequence receive no citation-subset or numeric-traceability validation.
2. `domain_calibration` 多个 narrative 字段没有逐项 evidence 绑定。 / Several `domain_calibration` narrative fields have no item-level evidence binding.
3. 手工 validator 没有完整复现声明的 JSON schema；例如 `best_story.support_level` 没有单独 enum 检查，若底层模型 endpoint 未严格执行 schema，部分非法类型/enum 可能穿过手工检查。 / The manual validator does not fully mirror the declared JSON schema; for example, `best_story.support_level` has no separate enum check, so some invalid types/enums may pass if the model endpoint does not strictly enforce the schema.
4. 数值补引用证明的是同一个 normalized number 出现过，不是该 evidence 在语义上支持陈述。 / Numeric citation repair proves that the same normalized number appeared, not that the evidence semantically supports the statement.
5. “simulation 不写成 experiment”“无 convergence checks 不声称 convergence”等 FDTD 规则主要存在于 prompt，没有专用 deterministic domain validator。 / FDTD rules such as not calling simulation an experiment or not claiming convergence without checks are mainly prompt policies, not dedicated deterministic domain validation.
6. 有效 evidence ID 只证明引用解析到上传内容，不证明内容真实、方法正确或结论可复现。 / A valid evidence ID proves resolution to uploaded content, not that the content is true, the method is correct, or the conclusion is reproducible.

因此输出只能称为 evidence-bounded candidate analysis，不能称为自动同行评审或科学真理验证。

The output is an evidence-bounded candidate analysis, not automated peer review or scientific-truth verification.

## 11. E1 Provider Boundary（已合并并固定） / E1 Provider Boundary (Merged and Pinned)

E1 已通过 child PR #2 合并到 child `main` 的 [`efea263`](https://github.com/Juggernautsst/stage1a-good-story-agent/commit/efea263da1b803a74a6a91c0e592949b3237203c)，并通过 parent PR #11 / Issue #9 固定到 parent gitlink。主要新增文件为 [`providers.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/providers.py)。

E1 is merged into child `main` at [`efea263`](https://github.com/Juggernautsst/stage1a-good-story-agent/commit/efea263da1b803a74a6a91c0e592949b3237203c) through child PR #2 and pinned into the parent gitlink through parent PR #11 / Issue #9. Its main new file is [`providers.py`](https://github.com/Juggernautsst/stage1a-good-story-agent/blob/efea263/src/good_story_agent/providers.py).

### 11.1 契约对象 / Contract Objects

| 对象 / Object | 字段或行为 / Fields or behavior |
| --- | --- |
| `ProviderCapabilities` | 在 evidence 进入 provider 前声明 backend、endpoint、transport 和 cloud fallback。 / Declares backend, endpoint, transport, and cloud fallback before evidence reaches the provider. |
| `ProviderMetadata` | 返回 backend/server version、model、endpoint、artifact digest、transport、fallback flag 和 inference parameters。 / Returns backend/server version, model, endpoint, artifact digest, transport, fallback flag, and inference parameters. |
| `SynthesisResult` | validated `AnalysisDraft`、omitted evidence tuple 和 provider metadata。 / Validated `AnalysisDraft`, omitted-evidence tuple, and provider metadata. |
| `SynthesisProvider` | runtime-checkable protocol：`backend_name`、`capabilities` 和 `synthesize()`。 / Runtime-checkable protocol with `backend_name`, `capabilities`, and `synthesize()`. |
| `ProviderFactory` | `(backend_name, Settings) -> SynthesisProvider`，可注入测试。 / Injectable factory for tests. |

默认 factory 是明确 allowlist，只产生 `AuditProvider` 或 `OllamaProvider`；其他名称直接失败。Audit endpoint 必须为 `none`，Ollama endpoint 必须是合法 loopback，transport 必须是 `loopback only`，cloud fallback 必须为 false。

The default factory is an explicit allowlist that creates only `AuditProvider` or `OllamaProvider`; other names fail. Audit endpoint must be `none`, Ollama endpoint must be valid loopback, transport must be `loopback only`, and cloud fallback must be false.

`AnalysisService` 在调用 `synthesize()` 前做 capability preflight，返回后核对 backend、endpoint、transport 和 fallback metadata；provider 错误不会尝试 fallback，run directory 仍走失败清理。

`AnalysisService` performs capability preflight before `synthesize()` and checks backend, endpoint, transport, and fallback metadata afterward; provider errors never trigger fallback, and the run directory follows failure cleanup.

### 11.2 它没有提供什么 / What It Does Not Provide

- 它没有允许远端 endpoint、Kimi K3、vLLM/SGLang 或 OpenAI-compatible API。 / It does not permit remote endpoints, Kimi K3, vLLM/SGLang, or an OpenAI-compatible API.
- capability 是同进程可信 Python provider 的声明，不是远程证明或 sandbox。 / Capabilities are declarations by trusted in-process Python providers, not remote attestation or a sandbox.
- preflight 不能阻止恶意 in-process provider 在其他代码路径泄露数据。 / Preflight cannot prevent a malicious in-process provider from leaking data through another code path.
- 返回后没有独立重跑完整 draft validation，也没有全面核对 resolved model、omitted IDs 和 inference-parameter 内容。 / The service does not independently rerun full draft validation or exhaustively verify the resolved model, omitted IDs, and inference-parameter contents after return.
- startup token 仍不是 user identity；E1 不能把当前 Flask 服务变成内网多用户系统。 / The startup token remains non-identity session control; E1 does not turn Flask into a multiuser intranet system.

E1 的价值是把当前两种本地行为放到稳定、可测试的内部接口后面，为未来 E3 独立进程/服务 gateway 保留接入点，而不是交付 gateway 本身。

E1's value is a stable, testable internal interface around the two local behaviors, leaving an integration point for a future E3 process/service gateway rather than delivering that gateway.

### 11.3 当前子仓库新增的 Chat 与 MCP / Current Child-Main Chat and MCP Additions

child `main` 还包含两个与 evidence-story pipeline 分离的能力：material-optional Web research chat，以及 client-neutral MCP `STDIO` facade。它们共享回环 Ollama provider boundary，但不会把聊天输出伪装成已验证的 structured story，也不会新增远程 endpoint、SSO、RAG 或外发能力。

Child `main` also contains two capabilities separate from the evidence-story pipeline: material-optional Web research chat and a client-neutral MCP `STDIO` facade. They share the loopback Ollama provider boundary, but chat output is not presented as a validated structured story and these additions do not add remote endpoints, SSO, RAG, or egress.

| Capability | Current behavior |
| --- | --- |
| `POST /api/chat` | Tool-free local research question answering; optional explicitly uploaded TXT/Markdown/CSV/JSON/PDF context; no run directory or evidence report is created for chat. / 无工具本地科研问答；可附加明确选择的材料；聊天不创建 run 或 evidence report。 |
| Chat result metadata | Returns `evidence_verified=false` for material-free or attachment-assisted chat, with `local_transport_only=true`; attachments are context, not authorization. / 返回 `evidence_verified=false` 和 `local_transport_only=true`；附件只是上下文，不是授权。 |
| `good-story-agent-mcp` | Local `STDIO` only; `analyze_materials`, `read_run_report`, and `read_run_provenance`. No server paths, arbitrary URLs, shell, release, or simulation tools. / 仅本机 `STDIO`；不接受服务器路径、任意 URL、shell、发布或仿真工具。 |
| Client integration | Codex Desktop/CLI and other MCP clients can invoke the same command; configuration is client-side and contains no secret. / Codex Desktop/CLI 和其他 MCP 客户端可调用同一命令；配置不含 secret。 |
| Enterprise boundary | No remote Streamable HTTP, OAuth, multiuser identity, tenant authorization, or laptop-to-server transport. / 尚无远程 Streamable HTTP、OAuth、多用户身份、租户授权或笔记本到服务器传输。 |

## 12. Service 编排、Provenance 和本地持久化 / Service Orchestration, Provenance, and Local Persistence

### 12.1 `AnalysisService.run()` 顺序 / `AnalysisService.run()` Sequence

1. 校验 backend、language、audience/research-stage 长度和 2,000 字符 context 上限；Ollama model 为空时填默认。 / Validate backend, language, audience/research-stage length, and the 2,000-character context limit; fill the default Ollama model when empty.
2. 生成 32-character lowercase UUID hex `run_id` 和 UTC ISO timestamp。 / Generate a 32-character lowercase UUID hex run ID and UTC ISO timestamp.
3. 建立 `0700` run directory。 / Create the `0700` run directory.
4. 摄取文件并建立 corpus。 / Ingest files and build the corpus.
5. 固定版本直接运行 audit 或 Ollama；E1 分支则经 provider factory/preflight。 / Run audit or Ollama directly in the pin; use provider factory/preflight on E1.
6. 将 system prompt 加 canonicalized response schema 后计算 prompt SHA-256。 / Hash the system prompt plus canonicalized response schema.
7. 构造 provenance、analysis、evidence payload、request payload、local report 和 filename-redacted report。 / Build provenance, analysis, evidence payload, request payload, local report, and filename-redacted report.
8. 计算 `analysis.json`、`evidence.json`、`report.md` 的 artifact hashes。 / Compute artifact hashes for analysis, evidence, and the local report.
9. 以 `0600` 写入所有文件并返回 `RunRecord`。 / Write all files as `0600` and return a `RunRecord`.
10. 任意异常触发 `shutil.rmtree(run_dir, ignore_errors=True)` 后重新抛出原异常。 / Any exception triggers `shutil.rmtree(run_dir, ignore_errors=True)` and re-raises the original error.

最后一步保持原始错误可见，但 cleanup error 被静默忽略；极端文件系统故障时可能遗留部分敏感 run directory，当前没有 cleanup audit 或 quarantine。

The last step preserves the original error but silently ignores cleanup errors; an extreme filesystem failure may leave a partial sensitive run directory, with no current cleanup audit or quarantine.

### 12.2 Run Directory / Run Directory

```text
<runs_dir>/<run_id>/
├── inputs/                  private exact input copies
├── request.json             AnalysisOptions after defaults
├── evidence.json            sources, evidence chunks, warnings
├── analysis.json            structured validated/crafted analysis
├── report.md                local report with original filenames
├── report.public.md         filename-redacted report
└── manifest.json            provenance, input inventory, hashes, security flags
```

`request.json` 可能包含 researcher context；`evidence.json` 和 `report.md` 包含科研正文；`manifest.json` 包含原始文件名和 input hashes。因此整个 run directory 都是敏感对象，而不只是 `inputs/`。

`request.json` may contain researcher context; `evidence.json` and `report.md` contain research text; `manifest.json` contains original filenames and input hashes. The entire run directory is therefore sensitive, not only `inputs/`.

### 12.3 Provenance 字段 / Provenance Fields

| 字段 / Field | 来源 / Source |
| --- | --- |
| `run_id`, `created_at` | service 本次运行 / current service run |
| `app_version` | `APP_VERSION` |
| `prompt_version`, `prompt_sha256` | fixed prompt metadata and actual prompt+schema hash |
| `backend`, `backend_version` | audit constants or Ollama `/api/version` |
| `model`, `model_artifact_digest` | selected model and Ollama `/api/tags` digest when reported |
| `model_endpoint` | loopback URL for Ollama, `none` for audit |
| `omitted_evidence_ids` | model-context budget omissions |
| `inference_parameters` | temperature, seed, structured-output flag, repair count |

manifest 还包含每个 input 的 source ID、原始名、SHA-256、size 和 coverage；security object 固定记录 loopback transport、no cloud fallback、`egress_isolation_verified=false` 和 `uploaded_code_executed=false`。

The manifest also contains source ID, original name, SHA-256, size, and coverage for each input; its security object records loopback transport, no cloud fallback, `egress_isolation_verified=false`, and `uploaded_code_executed=false`.

这些字段支持工程复核，但没有签名、可信时间戳或 append-only audit，因此本地管理员可以修改它们。

These fields support engineering review but have no signature, trusted timestamp, or append-only audit, so a local administrator can modify them.

### 12.4 Run 列表和读取 / Run Listing and Reads

`list_runs(limit=20)` 按 directory mtime 降序扫描，只看 alphanumeric directory，跳过没有 manifest 或 manifest JSON 损坏的 run，并返回 ID、time、backend、model 和 source count。它不校验 manifest signature/hash，也没有 owner/tenant filter。

`list_runs(limit=20)` scans directories by descending mtime, considers only alphanumeric names, skips missing or malformed manifests, and returns ID, time, backend, model, and source count. It verifies no signature/hash and has no owner/tenant filter.

`read_report()`、`read_analysis()` 和 `export_bundle()` 先要求 run ID 精确匹配 32 位 lowercase hex，防止 path traversal，再在共享 runs directory 中读取；当前 token 持有者可以访问全部 run。

`read_report()`, `read_analysis()`, and `export_bundle()` first require exactly 32 lowercase hex characters to prevent path traversal, then read from the shared runs directory; the current token holder can access every run.

## 13. 报告和 Export ZIP / Reports and Export ZIP

### 13.1 Deterministic Markdown Report

`render_report()` 不再调用模型。它按固定顺序输出状态、材料范围、领域校准、最强故事、why-it-works、story spine、claim evidence map、weak points、rewrite targets、negative results、limitations/warnings、source index 和 provenance。

`render_report()` makes no further model call. It emits status, material scope, domain calibration, best story, why-it-works, story spine, claim evidence map, weak points, rewrite targets, negative results, limitations/warnings, source index, and provenance in fixed order.

普通 report 的 source inventory 显示原始文件名；public report 在该 inventory 中改用 source ID，但仍包含 derived narrative、evidence locators、chunk hashes、input-hash-derived relationships、model information 和 scientific content。Renderer 不扫描 narrative，因而不保证上传内容、context 或模型生成文本中不会再次出现与原始文件名相同的字符串。

The normal report shows original filenames in its source inventory. The public report uses source IDs in that inventory but still contains derived narrative, evidence locators, chunk hashes, input-hash-derived relationships, model information, and scientific content. The renderer does not scan narrative text and therefore cannot guarantee that a string equal to an original filename will not reappear in uploaded content, context, or model-generated text.

`public` 的准确含义只是删除结构化 original-name metadata 并替换 source inventory 中的显示名；不是通用字符串清洗、匿名、脱密、已批准公开或不可关联。

The exact meaning of `public` is removal of structured original-name metadata plus source-inventory display-name replacement, not general string scrubbing, anonymity, declassification, approval for publication, or unlinkability.

### 13.2 Export ZIP 内容 / Export ZIP Contents

| ZIP member | 内容 / Content |
| --- | --- |
| `report.md` | `report.public.md` 的 bytes / Bytes from the filename-redacted report |
| `analysis.json` | 完整结构化分析，可能包含敏感派生文本 / Full structured analysis, potentially sensitive derived text |
| `REVIEW_BEFORE_SHARING.txt` | 明确提示 raw input 已排除但 derived text/hash 仍需人工复核 / Warning that raw inputs are excluded but derived text/hashes require review |
| `provenance.json` | 删除 `model_endpoint`，input 只保留 source ID/hash/size/coverage，并对 ZIP 中三个内容文件重新计算 hash / Removes `model_endpoint`, retains source ID/hash/size/coverage, and recomputes hashes over the three content members |

ZIP 不包含 `inputs/`、`request.json`、`evidence.json`、结构化 `original_name` metadata 或本地 report。`analysis.json` 和 derived report 不做任意文件名字面值扫描，因此不能保证该字符串完全不存在。ZIP 也不加密、不签名、不验证接收者、不执行 approval，不是 Stage 2 secure release package。

The ZIP excludes `inputs/`, `request.json`, `evidence.json`, structured `original_name` metadata, and the local report. It does not scan `analysis.json` or the derived report for arbitrary filename literals, so it cannot guarantee complete string absence. It also provides no encryption, signature, recipient verification, or approval and is not a Stage 2 secure-release package.

导出时重新计算 member hash，证明 `provenance.json` 与同一个 ZIP 内 bytes 自洽；代码不会先根据保存时 manifest 验证本地 artifact，也没有外部签名，所以不能证明 artifact 未被本地主机管理员篡改或来自特定研究者。

Export recomputes member hashes, proving that `provenance.json` is internally consistent with bytes in the same ZIP. The code does not first verify local artifacts against the saved manifest and provides no external signature, so it cannot prove absence of local-administrator tampering or authorship by a particular researcher.

普通文件删除也不保证 SSD、backup、sync folder、swap 或 snapshot 已安全擦除。

Ordinary file deletion does not guarantee secure erasure from SSDs, backups, sync folders, swap, or snapshots.

## 14. CLI、Web API 和浏览器前端 / CLI, Web API, and Browser Frontend

### 14.1 CLI / CLI

```text
good-story-agent analyze FILE [FILE ...]
  --backend audit|ollama       default audit
  --model NAME                 default from settings for ollama
  --language zh-CN|en          default zh-CN
  --audience TEXT              default photonics researchers
  --research-stage TEXT        default results available
  --context TEXT

good-story-agent serve --port 8765
```

CLI 先执行 `Path.expanduser().resolve(strict=True)`，再要求解析后的目标是 regular file；因此指向普通文件的 symlink 会被接受，传给 service 的是目标 basename 和 bytes。只有 `service.run()` 抛出的 `AnalysisError`、`BackendError` 和 `IngestionError` 会转成 stderr 信息和 exit code 1。Settings/service 初始化、path resolve/read 和 `serve` startup 位于该 `try` 外，可能产生直接 `SystemExit` 或未归一化 traceback。成功只打印 run ID 和 report path JSON。

The CLI first applies `Path.expanduser().resolve(strict=True)` and then requires the resolved target to be a regular file; a symlink to a regular file is therefore accepted, and the target basename and bytes reach the service. Only `AnalysisError`, `BackendError`, and `IngestionError` raised by `service.run()` become a stderr message and exit code 1. Settings/service initialization, path resolution/reads, and `serve` startup occur outside that `try` and may produce direct `SystemExit` or an unnormalized traceback. Success prints only JSON containing the run ID and report path.

`serve` 打印含 `#token=` 的完整 URL，绑定 `127.0.0.1`，关闭 Flask debug。直接运行 serve 可以使用 audit；完整 Ollama 生命周期应使用 launcher。

`serve` prints the complete `#token=` URL, binds `127.0.0.1`, and disables Flask debug. Direct serve can be used for audit; the launcher should own the complete Ollama lifecycle.

### 14.2 Web 请求安全 / Web Request Security

Flask `TRUSTED_HOSTS` 只允许 `127.0.0.1` 和 `localhost`。所有 request 必须来自 loopback `remote_addr`；所有 `/api/` route 必须带 `X-Good-Story-Token`，并使用 constant-time `hmac.compare_digest()`；POST/PUT/PATCH/DELETE API 还必须带 `X-Good-Story-Request: 1`。

Flask `TRUSTED_HOSTS` permits only `127.0.0.1` and `localhost`. Every request must have a loopback `remote_addr`; every `/api/` route requires `X-Good-Story-Token` checked with constant-time `hmac.compare_digest()`, and mutating API methods also require `X-Good-Story-Request: 1`.

startup token 默认每次启动随机生成，长度足够；URL fragment 不会随 HTTP request 发送。浏览器 JS 将 token 存到当前 tab 的 `sessionStorage`，立即从 address bar 移除，随后放入 API header。显式固定 token 不会自动轮换。

The startup token is random and sufficiently long by default; a URL fragment is not sent with HTTP requests. Browser JavaScript stores it in the current tab's `sessionStorage`, removes it from the address bar, then places it in API headers. An explicitly fixed token is not automatically rotated.

root HTML 只要求 loopback，不要求 API token；实际数据 API 全部要求 token。该 token 是单进程会话门，不表达 user、tenant、role、project 或 resource ownership。

The root HTML requires loopback but not the API token; all data APIs require the token. This token is a single-process session gate and expresses no user, tenant, role, project, or resource ownership.

每个 response 增加：`Cache-Control: no-store`、严格 self-only CSP、`X-Content-Type-Options: nosniff`、`X-Frame-Options: DENY` 和 `Referrer-Policy: no-referrer`。

Every response receives `Cache-Control: no-store`, a strict self-only CSP, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Referrer-Policy: no-referrer`.

### 14.3 HTTP API / HTTP API

| Method and path | 行为 / Behavior |
| --- | --- |
| `GET /` | 渲染单页 HTML；只注入 app version。 / Render the single-page HTML with app version only. |
| `GET /api/health` | 返回 `status`、version、`local_transport_only`、`egress_isolation_verified`、Ollama availability/models 和 default model。 / Return status, version, local-transport/egress flags, Ollama availability/models, and the default model. |
| `GET /api/runs` | 返回最近最多 20 个共享 run summaries。 / Return up to 20 recent shared run summaries. |
| `GET /api/runs/<run_id>` | 返回完整 local report 和 analysis JSON。 / Return full local report and analysis JSON. |
| `POST /api/analyze` | 读取 multipart `files` 和 option fields，单个 stream 最多读 5 MiB+1，构造 options，运行 service。 / Read multipart `files` and option fields up to 5 MiB+1 per file stream, build options, and run the service. |
| `GET /api/runs/<run_id>/report` | 下载包含原始文件名的 local Markdown report。 / Download the local Markdown report containing original filenames. |
| `GET /api/runs/<run_id>/bundle` | 下载移除 original-name metadata、仍需人工复核的 ZIP。 / Download a review-required ZIP with original-name metadata removed. |

Flask request envelope 上限为 `20 MiB + 512 KiB`，给 multipart framing 预留空间；ingestion 随后独立强制实际文件 bytes 合计 `20 MiB`。`POST /api/analyze` 接收 `backend`、`model`、`language`、`audience`、`research_stage` 和 `context_note`，成功返回 `run_id`、`created_at`、`backend`、`model`、`report`、`analysis`、`source_count` 和 `evidence_count`。

The Flask request-envelope limit is `20 MiB + 512 KiB` to allow multipart framing; ingestion independently enforces `20 MiB` of actual file bytes. `POST /api/analyze` accepts `backend`, `model`, `language`, `audience`, `research_stage`, and `context_note`, and returns `run_id`, `created_at`, `backend`, `model`, `report`, `analysis`, `source_count`, and `evidence_count` on success.

`GET /api/health` 成功字段为 `status="ok"`、`version`、`local_transport_only=true`、`egress_isolation_verified=false`、`ollama_available`、`models[]` 和 `default_model`。`GET /api/runs` 的每个 summary 含 run ID/time/backend/model/source count；detail route 只返回 `run_id`、`report` 和 `analysis`。

Successful `GET /api/health` fields are `status="ok"`, `version`, `local_transport_only=true`, `egress_isolation_verified=false`, `ollama_available`, `models[]`, and `default_model`. Each `GET /api/runs` summary contains run ID/time/backend/model/source count; the detail route returns only `run_id`, `report`, and `analysis`.

错误映射：非 loopback/token/header 为 `403`；expected ingestion/backend/analysis/config error 为 `400`；combined body 超限为 `413`；未知 run 为 `404`；未知 route 保持标准 HTTP exception；其他异常 server-side 记录 stack，但 client 只得到泛化 `500`。

Error mapping is `403` for loopback/token/header failures, `400` for expected ingestion/backend/analysis/configuration errors, `413` for oversized combined bodies, `404` for unknown runs, normal HTTP errors for unknown routes, and a generic client-facing `500` while the server logs the unexpected stack.

### 14.4 Browser UI / Browser UI

前端没有 framework 或 build step。HTML、CSS、vanilla JavaScript 作为 package data 由 Flask 提供。工作流是：选择/拖放文件 -> 选择 audit/Ollama -> 设置语言、audience、research stage 和 context -> 提交 -> 查看 raw Markdown 或 formatted JSON -> 下载 report/ZIP -> 从 recent runs 重新加载。

The frontend has no framework or build step. HTML, CSS, and vanilla JavaScript are package data served by Flask. The workflow is select/drop files, choose audit/Ollama, set language/audience/research stage/context, submit, inspect raw Markdown or formatted JSON, download report/ZIP, and reload recent runs.

浏览器只按 name/size/lastModified 去重文件，没有自行强制 10-file/5-MiB/20-MiB 规则；真正边界在 server。下载使用带认证 header 的 fetch、Blob object URL 和临时 anchor，而不是把 token 放入 query string。

The browser deduplicates files by name/size/lastModified but does not itself enforce the 10-file/5-MiB/20-MiB limits; authoritative bounds are server-side. Downloads use authenticated fetch, a Blob object URL, and a temporary anchor rather than putting the token in a query string.

recent-run summary 只保存 source count，不保存 evidence count，因此重新加载旧 run 时 UI 显示 evidence `—`。点击 recent run 后 detail loading error 会显示在 form error 区；初始 `refreshRuns()` 失败则被转换为空列表，不向用户显示原因。

Recent-run summaries retain source count but not evidence count, so reloading an old run displays evidence as `—`. A detail-loading failure after clicking a recent run appears in the form-error area; an initial `refreshRuns()` failure is converted to an empty list without exposing the cause.

CSS 使用 264px desktop sidebar、最大 1120px main workspace、4-column metrics 和 820px/520px breakpoints；在小屏隐藏 sidebar、将 form/metrics 改为单列，并让主要 action 满宽。没有第三方字体、图片或 remote asset 请求。

CSS uses a 264px desktop sidebar, a maximum 1120px workspace, four-column metrics, and 820px/520px breakpoints; on small screens it hides the sidebar, makes forms/metrics single-column, and expands the primary action. It makes no third-party font, image, or remote-asset request.

## 15. 安装、运行和停止 / Install, Run, and Stop

### 15.1 当前允许的数据 / Currently Permitted Data

当前工作副本位于 Windows-mounted WSL development checkout，不能依赖 POSIX ownership/mode 抵御同机其他账户修改。它只适合源码、公开数据和合成案例；未公开或高价值数据必须把完整项目和新 `.venv` 部署到 WSL/Linux filesystem，限制权限并核查 backup/sync/egress。

The current working copy is a Windows-mounted WSL development checkout whose POSIX ownership/modes cannot defend against other local accounts. It is suitable only for source, public data, and synthetic cases; unpublished or high-value data requires redeploying the complete project and a new `.venv` on a WSL/Linux filesystem, restricting permissions, and reviewing backup/sync/egress.

### 15.2 创建环境 / Create the Environment

以下命令只适用于父仓库的 clean recursive clone，并要求 child checkout 与 parent gitlink 同为已固定的 `efea263da1b803a74a6a91c0e592949b3237203c`。当前开发工作副本包含独立工作，不满足部署前提；不要从它执行安装。先在 superproject root 运行双重校验，任一 `test` 失败都应停止并重新创建 clean clone，而不是覆盖含有其他工作的 checkout：

The following commands apply only to a clean recursive clone and require both the parent gitlink and child checkout to equal the pinned commit `efea263da1b803a74a6a91c0e592949b3237203c`. The current development working copy contains independent work and does not satisfy this deployment prerequisite; do not install from it. Run both checks from the superproject root first. If either `test` fails, stop and create a clean clone rather than overwriting a checkout that may contain other work:

```bash
test "$(git rev-parse HEAD:components/stage1a-good-story-agent)" = \
  "efea263da1b803a74a6a91c0e592949b3237203c"
test "$(git -C components/stage1a-good-story-agent rev-parse HEAD)" = \
  "efea263da1b803a74a6a91c0e592949b3237203c"
cd components/stage1a-good-story-agent
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e '.[dev]'
```

这会改变本机环境并下载 Python dependencies；生产或高价值部署应固定 wheel/hash、离线审查依赖并使用独立部署 Issue。

This mutates the local environment and downloads Python dependencies; production or high-value deployment should pin wheels/hashes, review dependencies offline, and use a separate deployment Issue.

### 15.3 先跑 Audit / Run Audit First

```bash
.venv/bin/good-story-agent analyze \
  examples/synthetic_waveguide_notes.md \
  examples/synthetic_transmission_sweep.csv \
  --backend audit \
  --language zh-CN
```

预期得到 run ID 和 report path，且不需要 Ollama。示例值仅为 software-test synthetic data，不是研究结论。

Expect a run ID and report path without Ollama. Example values are software-test synthetic data, not research findings.

### 15.4 启动 Local Ollama + Web / Start Local Ollama and Web

安装 Ollama 和拉取模型会下载数 GB，必须单独检查官方 installer、license、disk 和 supply chain。准备好后：

Installing Ollama and pulling a model downloads several gigabytes and requires separate installer, license, disk, and supply-chain review. Once prepared:

```bash
./scripts/start-local.sh 8765
```

首次缺少模型时，在另一个 terminal 执行：

When the model is absent on first use, run in another terminal:

```bash
ollama pull qwen2.5:3b
```

打开 launcher 打印的完整 `http://127.0.0.1:8765/#token=...`，不能只打开无 fragment 地址。先选择 audit 检查材料，再选择 Ollama。

Open the complete `http://127.0.0.1:8765/#token=...` printed by the launcher, not the fragment-free address. Use audit to inspect material before selecting Ollama.

按 `Ctrl-C` 停止 Web；launcher trap 同时终止它创建的 Ollama。不要通过把 bind address 改为 `0.0.0.0` 部署给内网。

Press `Ctrl-C` to stop Web; the launcher trap also terminates the Ollama process it created. Do not deploy to an intranet by changing the bind address to `0.0.0.0`.

### 15.5 CLI Ollama 模式 / CLI Ollama Mode

launcher 运行并且模型存在时：

With the launcher running and the model installed:

```bash
.venv/bin/good-story-agent analyze \
  examples/synthetic_waveguide_notes.md \
  examples/synthetic_transmission_sweep.csv \
  --backend ollama \
  --model qwen2.5:3b \
  --language zh-CN \
  --context "Synthetic tolerance-study fixture; do not infer experimental validation."
```

默认 run storage 在用户 Linux data directory，而不是仓库 `runs/`。只有 `Settings.from_environment(project_root=...)` 的调用方才把 default 改为 project-local；当前 CLI/Web 不这样调用。

Default run storage is under the user's Linux data directory, not repository `runs/`. Only callers using `Settings.from_environment(project_root=...)` change the default to project-local; current CLI/Web do not do so.

## 16. 当前安全保证与非保证 / Current Security Guarantees and Non-Guarantees

### 16.1 代码机械强制的边界 / Mechanically Enforced Boundaries

| 控制 / Control | 实现 / Implementation |
| --- | --- |
| Explicit input selection / 明确输入选择 | 只读取 CLI path 或 Web upload；没有目录扫描、RAG 或自动外部检索。 / Reads only CLI paths or Web uploads; no directory crawl, RAG, or automatic external retrieval. |
| Path rewriting / 路径重写 | 上传 basename normalization，stored name 由 source ID 生成，run ID 严格 hex。 / Upload basename normalization, source-ID storage names, strict hexadecimal run IDs. |
| Size/type bounds / 大小与类型上限 | file count、per-file、total、extension、PDF pages/chars/resources。 / File count, per-file, total, extension, and PDF page/character/resource limits. |
| Local Web boundary / 本地 Web 边界 | loopback bind、loopback client、trusted Host、startup token、mutating-request header。 / Loopback bind/client, trusted Host, startup token, and mutating-request header. |
| Local model boundary / 本地模型边界 | loopback URL validation、no proxy、no redirect、`:cloud` refusal、no application fallback。 / Loopback URL validation, no proxy, no redirect, `:cloud` refusal, and no application fallback. |
| Private local files / 私有本地文件 | POSIX run directory `0700`、artifact `0600`，无法强制时拒绝。 / POSIX run directory `0700`, artifacts `0600`, refusal when enforcement fails. |
| No uploaded-code execution / 不执行上传代码 | 支持的 parser 只处理文本/CSV/JSON/PDF text；没有 Python/pickle/tool execution。 / Supported parsers handle text/CSV/JSON/PDF text; no Python, pickle, or tool execution. |
| Output bounding / 输出约束 | structured schema、known evidence IDs、selected numeric/significance checks、one repair then fail。 / Structured schema, known evidence IDs, selected numeric/significance checks, one repair then fail. |
| Export minimization / 导出最小化 | ZIP 排除 raw inputs、request、evidence index 和结构化 original-name metadata；不扫描 derived text 中的文件名字面值；加入 review warning。 / ZIP excludes raw inputs, request, evidence index, and structured original-name metadata, does not scrub filename literals from derived text, and includes a review warning. |

### 16.2 当前没有提供的保证 / Guarantees Not Provided

| 非保证 / Non-guarantee | 结果 / Consequence |
| --- | --- |
| OS egress isolation | `OLLAMA_NO_CLOUD` 不是 firewall；高价值数据前必须由部署环境验证外发控制。 / `OLLAMA_NO_CLOUD` is not a firewall; deployment must verify egress controls before high-value data. |
| Encryption at rest / 静态加密 | 应用只设置 file permissions；disk、swap 和 backup protection 由主机负责。 / The app sets file permissions only; disk, swap, and backup protection belong to the host. |
| Multiuser identity/authorization | 一个 startup token 可访问共享 run list/read/export；不能内网多人使用。 / One startup token can access shared run list/read/export; not suitable for intranet multiuser use. |
| Scientific correctness | LLM 仍可误解、幻觉或过度主张；validator 只覆盖有限形式规则。 / The LLM may misinterpret, hallucinate, or overclaim; validation covers limited formal rules. |
| Secure transfer | Export ZIP 和 private GitHub 都不是加密、接收者绑定的传输。 / Export ZIP and private GitHub are not encrypted, recipient-bound transfer. |
| Authentic provenance | Hashes 无签名或可信 timestamp，只提供内部完整性关联。 / Hashes lack signatures or trusted timestamps and provide internal correlation only. |
| Malicious PDF sandbox | 子进程有资源上限但无独立 filesystem/network sandbox。 / The subprocess has resource bounds but no separate filesystem/network sandbox. |
| Host-admin resistance | 同机管理员可读/改进程、文件和模型。 / A host administrator can read or alter processes, files, and models. |
| High availability/concurrency | Flask development server、单 Ollama 和本地 filesystem 没有 HA/SLA。 / Flask development server, one Ollama process, and local filesystem provide no HA/SLA. |

“local”仅说明应用和模型 endpoint 的预期网络路径，不代表设备绝对离线或数据绝对私密。

“Local” describes the intended network path between the application and model endpoint, not absolute device offline status or absolute data privacy.

## 17. 自动化测试、验收证据和缺口 / Automated Tests, Acceptance Evidence, and Gaps

### 17.1 版本化测试事实 / Versioned Test Facts

| 版本 / Version | 证据 / Evidence |
| --- | --- |
| Parent-pinned child `4e3bdda` (historical) | Stage 1A baseline reports `38 passed`; this belongs to the old pinned engineering MVP and is not the current child-main result. / `38 passed` 属于旧父 pin 的历史工程 MVP，不是当前 child-main 结果。 |
| Child merged main `efea263` | Offline suite: `117 passed, 1 skipped`; includes provider, MCP, and chat tests. / 离线测试为 `117 passed, 1 skipped`，包含 provider、MCP 和 chat 测试。 |
| Live MCP acceptance | `qwen2.5:3b`: `1 passed`; synthetic fixtures only, local `STDIO`, no cloud/Tidy3D. / `qwen2.5:3b`：`1 passed`；仅合成 fixture、本地 `STDIO`，无云端/Tidy3D。 |
| Live Web smoke | Material-free chat: `721` response characters, `0` sources. Synthetic attachment chat: `808` response characters, `2` sources, `3` context references. Both report `evidence_verified=false` and `local_transport_only=true`. / 无材料 chat 为 `721` 字符、`0` source；合成附件 chat 为 `808` 字符、`2` source、`3` context references；两者均为 `evidence_verified=false`、`local_transport_only=true`。 |
| Historical E1 review | Child PR #2 originally recorded `47 passed`; it was superseded by the merged child-main stack. / 子 PR #2 曾记录 `47 passed`，现已被 child-main 合并栈取代。 |

这些事实不能互换：旧 pin 的测试、child main 的离线测试和 live smoke 分别证明不同边界；live smoke 也不证明科学正确性或企业部署安全。

These facts are not interchangeable: historical pin tests, child-main offline tests, and live smoke cover different boundaries; live smoke does not prove scientific correctness or enterprise deployment security.

### 17.2 测试文件和覆盖 / Test Files and Coverage

当前 child-main 测试入口可在 [`tests/`](https://github.com/Juggernautsst/stage1a-good-story-agent/tree/efea263/tests) 查看；provider、chat、MCP 和 live MCP 测试也固定在该快照。

The current child-main tests are under [`tests/`](https://github.com/Juggernautsst/stage1a-good-story-agent/tree/efea263/tests); provider, chat, MCP, and live-MCP tests are part of this snapshot.

| Test module | 覆盖 / Coverage |
| --- | --- |
| `conftest.py` | 合法 photonics/FDTD structured payload fixture。 / Valid structured photonics/FDTD payload fixture. |
| `test_config.py` | package/app version equality；IPv4/IPv6/localhost loopback allow；remote、missing-port、file URL 和 credential URL deny。 / Version equality and loopback URL allow/deny matrix. |
| `test_permissions.py` | POSIX `0700` enforcement 和 ineffective chmod refusal。 / POSIX private-mode enforcement and refusal. |
| `test_ingest.py` | TXT/CSV/JSON parsing、hash、locator、evidence ID、invalid inputs 和 filename path rewriting。 / Core parsing, hashes, locators, IDs, invalid inputs, and path rewriting. |
| `test_backends.py` | audit no-story、quoted instruction input、structured Ollama stub、cloud model refusal、significance downgrade、numeric citation addition。 / Audit, quoted instructions, structured stub, cloud refusal, significance calibration, and numeric citation repair. |
| `test_schema.py` | valid draft、unknown evidence、unsupported claim without evidence、spine citation、significance、numeric mismatch、bilingual contract、identifier numbers。 / Core structural and traceability validations. |
| `test_service.py` | audit artifacts、manifest hashes/provenance、exact ZIP-member hashes，以及 fixture raw input/original-name metadata 在 export 中的排除。 / Artifacts, provenance, exact ZIP hashes, and exclusion of fixture raw input/original-name metadata from export. |
| `test_web.py` | audit upload flow、write header、loopback client、unknown route、startup token、trusted Host。 / Web audit flow and main local security controls. |
| `test_providers.py` (E1) | shared contract、factory allowlist、injection、no fallback、metadata inconsistency、pre-evidence endpoint refusal。 / Shared provider contract, allowlist, injection, no fallback, metadata consistency, and pre-evidence refusal. |
| `test_chat.py` | 无材料/可选材料 chat、历史和 prompt budget、无工具请求、provider capability、模型可用性与 response 校验。 / Material-free/optional-context chat, history and prompt budgets, tool-free requests, provider capabilities, model availability, and response validation. |
| `test_mcp_server.py` / `test_agent_facade.py` | MCP tool schema、redaction、run ID/path boundary、error handling 和 client-neutral facade。 / MCP tool schema, redaction, run-ID/path boundaries, error handling, and client-neutral facade. |
| `test_mcp_live.py` | opt-in local `STDIO -> Ollama -> validated report/provenance` smoke path。 / Opt-in local `STDIO -> Ollama -> validated report/provenance` smoke path. |

### 17.3 当前测试未覆盖 / Current Test Gaps

- 真实 PDF，包括 malformed、encrypted variants、resource exhaustion 和 exploit-oriented fixtures。 / Real PDFs, including malformed, encrypted variants, resource exhaustion, and exploit-oriented fixtures.
- 真实 Ollama HTTP、timeout、oversized metadata/output、redirect 和 unavailable-service matrix。 / Live Ollama HTTP, timeout, oversized metadata/output, redirect, and unavailable-service matrix.
- 第一次 response 失败后 repair 成功与 repair 再失败的完整行为。 / Complete first-failure repair-success and repair-failure behavior.
- 72,000-character model-context omission、240-evidence balancing 和 source-coverage edge cases。 / Model-context omission, 240-evidence balancing, and source-coverage edge cases.
- 无 NUL 的 UTF-8 control-character 输入、通用 MIME/binary detection，以及含空 row CSV 的物理行定位。 / NUL-free UTF-8 control-character inputs, general MIME/binary detection, and physical-line mapping for CSV files containing empty rows.
- JSON schema 与手工 validator 的全部 type/enum parity。 / Exhaustive type/enum parity between JSON schema and manual validation.
- `why_it_works`、domain calibration 和 FDTD-specific deterministic claim constraints。 / Citation binding for `why_it_works`, domain calibration, and deterministic FDTD claim constraints.
- Web report/bundle download、security headers、413、malformed/corrupted run 和 error logging。 / Web downloads, security headers, 413, malformed/corrupted runs, and error logging.
- 并发 run、disk-full、permission race、cleanup failure 和 process interruption。 / Concurrent runs, disk-full behavior, permission races, cleanup failure, and process interruption.
- CLI subprocess 的 exit/traceback matrix、console-script packaging，以及 wheel/sdist 安装。 / CLI subprocess exit/traceback behavior, console-script packaging, and wheel/sdist installation.
- 浏览器真实 E2E、accessibility，以及 launcher/Ollama 的功能性 process lifecycle、工具依赖和跨平台行为。 / Real browser E2E, accessibility, and functional launcher/Ollama process lifecycle, tool dependencies, and cross-platform behavior.
- 模型科学质量：至少五案例、两名独立评价者、预先定义评分标准。 / Model scientific quality: at least five cases, two independent evaluators, and a predefined rubric.

自动测试通过只证明上述覆盖范围内的工程行为，不证明论文质量提升、科学正确性或企业安全性。

Passing automated tests proves engineering behavior only within this coverage, not improved manuscript quality, scientific correctness, or enterprise security.

## 18. Enterprise 目标架构 / Enterprise Target Architecture

本节全部为 **DESIGN ONLY**。它解释如何把一个受控模型 endpoint 提供给内网员工，同时不让 RAG 或 LLM 变成授权系统。当前 Flask app 不能直接承担这些职责。

This entire section is **DESIGN ONLY**. It explains how a controlled model endpoint could serve intranet employees without turning RAG or the LLM into an authorization system. The current Flask app cannot assume these responsibilities directly.

### 18.1 三种部署形态 / Three Deployment Profiles

| Profile | 适用范围 / Scope | 当前状态 / Status |
| --- | --- | --- |
| Local workstation | 当前 Stage 1A，单用户、小模型、loopback。 / Current Stage 1A, one user, small model, loopback. | **PINNED** |
| Controlled single-host pilot | 少量认证用户；同机但独立 service identity、gateway、policy/RLS、storage 和 audit。 / A few authenticated users with separate logical service identities, gateway, policy/RLS, storage, and audit on one host. | **DESIGN ONLY** |
| Enterprise cluster | 多团队、高并发、独立 GPU/database/audit nodes、HA、mTLS 和正式运维。 / Multiple teams, higher concurrency, separate GPU/database/audit nodes, HA, mTLS, and formal operations. | **DESIGN ONLY** |

Docker 封装单个 service 和依赖；Kubernetes 负责 scheduling、service discovery、rollout、quota 和 recovery。它们都不会自动提供身份授权，也不会把多台普通 GPU 的显存无条件合成一个大模型可用池。模型仍需要支持 tensor/expert parallelism 的 serving engine、高速 interconnect 和匹配拓扑。

Docker packages a service and dependencies; Kubernetes provides scheduling, service discovery, rollout, quotas, and recovery. Neither automatically supplies identity authorization or turns arbitrary GPUs into one usable memory pool. The model still requires a serving engine supporting tensor/expert parallelism, high-speed interconnect, and a compatible topology.

### 18.2 企业组件责任 / Enterprise Component Responsibilities

| 组件 / Component | 负责 / Owns | 不负责 / Must not own |
| --- | --- | --- |
| Institutional IdP | Authentication, MFA, account lifecycle | Research retrieval or model inference |
| API gateway | IdP token verification, trusted identity derivation, rate limits, request IDs | Client-declared tenant/role or raw token forwarding to model |
| Policy service | RBAC+ABAC, project membership, classification, revocation | Semantic ranking or generation |
| Retrieval service | Rank only inside authorized source set, reauthorize top-K, build bundle | Treat metadata filters/LLM as authorization |
| PostgreSQL/pgvector | Authoritative ACL rows, `FORCE ROW LEVEL SECURITY`, transaction consistency | Depend solely on application filters |
| Stage 1A worker | Validate authorized bundle, synthesize, citation-subset enforcement | Global corpus query, ACL change, simulation, or release |
| Model gateway | Registered provider/model/revision, endpoint, timeout, capacity, provenance | User authorization or source selection |
| Model provider | Infer over minimal supplied prompt with no retention/training | IdP, ACL, database, tools, or unauthorized sources |
| Audit sink | Integrity-protected content-free security events | Raw evidence, prompt, embedding, reasoning, token, or full output |
| Secure release | Recipient verification, approval, encryption, signature, key wrapping, receipt | Automatically trust Stage 1A output for release |

### 18.3 请求流 / Request Flow

```text
Employee browser
  -> TLS reverse proxy + institutional SSO
  -> trusted API gateway
  -> signed short-lived DelegatedIdentityContext
  -> policy + forced-RLS retrieval
  -> source-level reauthorization of top-K
  -> signed short-lived AuthorizedEvidenceBundle
  -> Stage 1A worker
  -> controlled model gateway
  -> registered local model provider
  -> tenant-scoped result storage + minimal integrity audit
  -> separate secure-release workflow when explicitly requested
```

只有 reverse proxy/API gateway 对 user network 开放。数据库、retrieval、Stage 1A worker、model serving、audit 和 admin endpoint 都使用独立 service identity、firewall allowlist 和最小端口。

Only the reverse proxy/API gateway is exposed to the user network. Database, retrieval, Stage 1A worker, model serving, audit, and admin endpoints use separate service identities, firewall allowlists, and minimal ports.

## 19. 身份感知 RAG 和授权 / Identity-Aware RAG and Authorization

本节是父 Issue [#10](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/10) 下 E2 的 **DESIGN ONLY** 契约；E2 implementation 仍为 **NOT IMPLEMENTED**，当前程序没有 SSO、policy service、RLS database、retrieval service 或 signed evidence bundle。

This section is the **DESIGN ONLY** E2 contract under parent Issue [#10](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/10); E2 implementation remains **NOT IMPLEMENTED**, and the current program has no SSO, policy service, RLS database, retrieval service, or signed evidence bundle.

核心不变量：**RAG performs relevance retrieval, never authorization; the LLM never decides access.**

Core invariant: **RAG performs relevance retrieval, never authorization; the LLM never decides access.**

### 19.1 正确顺序 / Correct Order

```text
Authenticate
  -> derive trusted server-side identity
  -> authorize tenant/project/source set
  -> enforce database RLS
  -> rank relevance only within that set
  -> reauthorize each top-K source
  -> sign a bounded evidence bundle
  -> synthesize
```

“先全局 vector search 再 metadata filter”是不允许的；metadata filter 只可作为性能优化。即使删除 filter，`FORCE ROW LEVEL SECURITY` 也必须让跨 tenant/source 结果为零。

“Global vector search followed by metadata filtering” is prohibited; metadata filtering is only a performance optimization. Even after removing it, `FORCE ROW LEVEL SECURITY` must yield zero cross-tenant/source rows.

### 19.2 `DelegatedIdentityContext` / `DelegatedIdentityContext`

可信 gateway 从机构 token 和当前 policy 派生短期签名对象，包含 schema version、delegation/request IDs、opaque subject/tenant IDs、issuer/audience、authentication time/assurance、authorization snapshot/policy version、purpose、issued/expiry、key ID 和 signature。

A trusted gateway derives a short-lived signed object from the institutional token and current policy, including schema version, delegation/request IDs, opaque subject/tenant IDs, issuer/audience, authentication time/assurance, authorization snapshot/policy version, purpose, issuance/expiry, key ID, and signature.

客户端不能提供或覆盖 user、tenant、role、group、clearance、membership 或 policy version。Role/group cache 即使放入 token 也必须 server-derived、signed、versioned、short-lived，并在敏感 source 上复核。

The client cannot supply or override user, tenant, role, group, clearance, membership, or policy version. Even cached role/group claims must be server-derived, signed, versioned, short-lived, and rechecked for sensitive sources.

### 19.3 `AuthorizedEvidenceBundle` / `AuthorizedEvidenceBundle`

bundle 将 request/delegation/subject/tenant/purpose/policy/audience/time 与 source version/hash/classification/decision、bounded evidence ID/locator/content/hash 和 retrieval fingerprint/index/method/top-K 绑定，并由 retrieval service 对唯一 canonical serialization 签名。

The bundle binds request/delegation/subject/tenant/purpose/policy/audience/time to source version/hash/classification/decision, bounded evidence ID/locator/content/hash, and retrieval fingerprint/index/method/top-K, then is signed by the retrieval service over one canonical serialization.

Stage 1A 必须拒绝 signature/payload tamper、unknown/wrong/revoked key、wrong audience/time、identity/request/purpose substitution、schema downgrade、ambiguous serialization、source/content/hash mutation、duplicate/unknown IDs、policy mismatch 和 size limit violation。输出 citation 必须是 bundle evidence set 的子集。

Stage 1A must reject signature/payload tampering, unknown/wrong/revoked keys, wrong audience/time, identity/request/purpose substitution, schema downgrade, ambiguous serialization, source/content/hash mutation, duplicate/unknown IDs, policy mismatch, and size-limit violations. Output citations must be a subset of the bundle evidence set.

E2 的最小 vertical slice 先使用 synthetic tenants/users/projects/sources，不连接模型；要测试同 tenant project/owner/source allow-deny-share-revoke、跨 tenant、pooled identity、SQL injection、RLS bypass、revocation/cache 和 bundle negative matrix。

The minimal E2 vertical slice uses synthetic tenants/users/projects/sources and no model; it must test same-tenant project/owner/source allow-deny-share-revoke, cross-tenant isolation, pooled identity, SQL injection, RLS bypass, revocation/cache behavior, and the bundle negative matrix.

Embeddings、semantic cache、KV cache、retrieval results 和 prompt cache 与 source 同等级敏感，不跨 tenant 复用。ACL 撤销后新请求立即失败，旧 bundle 依短 TTL 失效；极高价值 source 可要求每次在线复核。

Embeddings, semantic caches, KV caches, retrieval results, and prompt caches are as sensitive as the source and are not reused across tenants. New requests fail immediately after ACL revocation, old bundles expire through short TTLs, and very high-value sources may require online reauthorization every time.

## 20. Model Gateway 和集中模型服务 / Model Gateway and Centralized Model Serving

本节是 E3 的 **DESIGN ONLY** 契约；E3 implementation 仍为 **NOT IMPLEMENTED**，当前程序没有集中 model gateway、registered remote provider、mTLS 或 cluster serving。

This section is the **DESIGN ONLY** E3 contract; E3 implementation remains **NOT IMPLEMENTED**, and the current program has no centralized model gateway, registered remote provider, mTLS, or cluster serving.

E3 model gateway 将模型和业务 Agent 分离。员工只访问 identity-aware API gateway；Stage 1A worker 只访问 model gateway；model provider 永远不接收用户 ACL，也不能自己选择数据或外部工具。

The E3 model gateway separates models from business agents. Employees access only the identity-aware API gateway; Stage 1A workers access only the model gateway; the model provider never receives user ACLs and cannot select data or external tools.

生产候选必须固定 model repository commit、model artifact digest、serving-code commit、container digest 和 registered alias，并检查 license、remote custom code、retention/training policy、timeout、request size、concurrency、mTLS、proxy/redirect、egress 和 log redaction。

A production candidate must pin the model-repository commit, model-artifact digest, serving-code commit, container digest, and registered alias, while reviewing license, remote custom code, retention/training policy, timeout, request size, concurrency, mTLS, proxy/redirect, egress, and log redaction.

provider failure 必须 fail closed；不能切换到云 API 或另一个未批准模型。manifest 必须记录实际 endpoint、transport、resolved model 和 digest，不能只记录客户端请求的 alias。

Provider failure must fail closed, never switching to a cloud API or another unapproved model. The manifest must record the actual endpoint, transport, resolved model, and digest rather than only the client-requested alias.

## 21. Secure Release、跨机构传输和区块链 / Secure Release, Cross-Institution Transfer, and Blockchain

本节是 **DESIGN ONLY**。当前 export ZIP 不满足这里的任何密码学交付条件。

This section is **DESIGN ONLY**. The current export ZIP satisfies none of these cryptographic delivery conditions.

### 21.1 Researcher-facing Contract

研究者从 tenant storage 显式选择 raw experiment、derived analysis 或 Stage 1A artifact。系统不得隐式加入 whole run、RAG corpus、prompt、cache、credential 或未选择 source。每项 manifest 记录 immutable ID/version/hash、kind、server-authoritative classification、size 和 media type；aggregate classification 取机构序中的最严格值，研究者、client 和 Agent 不能降低。

The researcher explicitly selects raw experimental, derived-analysis, or Stage 1A artifacts from tenant storage. The system never implicitly includes a whole run, RAG corpus, prompt, cache, credential, or unselected source. Every manifest item carries immutable ID/version/hash, kind, server-authoritative classification, size, and media type; aggregate classification is the strictest under institutional ordering and cannot be lowered by the researcher, client, or agent.

| 对象 / Object | 必要内容 / Required content |
| --- | --- |
| `ReleaseCandidate` | release/tenant/project/creator/purpose、artifact manifest、aggregate classification、recipient IDs/key fingerprints、policy/approval version、expiry、idempotency key。 / Release identity, scope, artifacts, classification, recipients/keys, policy/approval versions, expiry, and idempotency. |
| Approval record | 完整 manifest hash、recipient/key、purpose、expiry、approver/decision/time/signature；任一变化使旧 approval 失效。 / Binds the complete candidate; any mutation invalidates approval. |
| `SecureReleasePackage` | versioned manifest、ciphertext hashes、approved algorithm suite、per-recipient wrapped content key、sender key/signature、package hash、expiry；不含 private key。 / Versioned encrypted and signed package with no private key. |
| Researcher instruction | 用批准工具验证 signature/hash/fingerprint、unwrap/decrypt 和报告失败；不含 secret。 / Approved verification/decryption steps with no secret. |
| Delivery receipt | receipt/release/recipient/key/package/idempotency/channel/outcome/time/signer/signature binding。 / Authenticated binding of delivery identity and exact outcome. |

### 21.2 Hash、Signature 和 Verification 顺序 / Hash, Signature, and Verification Order

协议为 package body、package signature、delivery receipt 和 audit event 使用不同 domain-separated hash/signature context。Hash/signature field 不属于自身输入，避免自引用。Verifier 先校验 schema、count/size、key trust/time/revocation、signature 和 ciphertext hashes，再尝试 key unwrap/decryption。

The protocol uses distinct domain-separated hash/signature contexts for package bodies, package signatures, delivery receipts, and audit events. Hash/signature fields are excluded from their own inputs to avoid self-reference. The verifier checks schema, count/size, key trust/time/revocation, signature, and ciphertext hashes before key unwrap/decryption.

密码学必须使用维护中的库和机构批准 algorithm suite，不能自行实现 encryption/signature primitive。Package 离开系统边界前已经加密和签名；transport channel 是独立配置。

Cryptography must use maintained libraries and institution-approved algorithm suites, never custom encryption/signature primitives. The package is encrypted and signed before leaving the system boundary; the transport channel is configured separately.

### 21.3 Audit-committed Delivery State Machine

```text
approved
  -> audit_committed
  -> delivery_pending
  -> delivered | pending_reconciliation | failed

approved -> cancelled       allowed before dispatcher claim
```

Approval、recipient、package hash、idempotency key 和 audit intent 先在同一事务持久化。只有 audit sink 返回并保存绑定 intent hash 的 signed append receipt 后才能进入 `audit_committed`；dispatcher 只领取 `delivery_pending` outbox record。

Approval, recipient, package hash, idempotency key, and audit intent are first persisted in one transaction. Transition to `audit_committed` requires a signed audit append receipt bound to the intent hash; the dispatcher claims only `delivery_pending` outbox records.

外发前 audit failure 或未确认 acknowledgment 阻止发送。若 delivery timeout 发生在可能已发送之后，状态必须是 `pending_reconciliation`，使用同一个 idempotency key 和可信 receipt 对账，不能盲目重试或声称未交付。

Audit failure or unconfirmed acknowledgment before release blocks sending. If delivery times out after it may have occurred, state becomes `pending_reconciliation`; reconciliation uses the same idempotency key and trusted receipt, with no blind retry or false non-delivery claim.

### 21.4 Receipt 和撤销边界 / Receipt and Revocation Boundary

receipt outcome 必须精确，例如 `accepted_by_transport`、`downloaded`、`key_unwrapped` 或 `decryption_acknowledged_by_recipient`。Transport acceptance 不能解释为解密成功；UI/audit 必须显示精确 outcome。

Receipt outcomes must be precise, such as `accepted_by_transport`, `downloaded`, `key_unwrapped`, or `decryption_acknowledged_by_recipient`. Transport acceptance is not successful decryption; UI/audit must display the exact outcome.

dispatcher claim 前可以取消；在线 KMS unwrap 前可以拒绝 key；一旦接收方取得 content key、offline package 可独立解密或 plaintext 已产生，就不能保证撤回。Expiry/revocation 只能阻止未来在线访问，不能删除接收方已有副本。

Delivery can be cancelled before dispatcher claim; online KMS can deny a key before unwrap; once the recipient has the content key, can independently decrypt offline, or has plaintext, recall cannot be guaranteed. Expiry/revocation stops future online access but cannot delete an existing recipient copy.

### 21.5 Blockchain 的准确位置 / Exact Role of Blockchain

原始科研数据、ciphertext key 或 private metadata 永不写链。先实现 encryption、signature、recipient verification、revocation、ordinary append-only audit 和 receipt reconciliation；只有这些仍留下明确的跨机构多方记账问题时，才评估把最小 hash/timestamp/authorization event 写入经过批准的 ledger。

Raw research data, ciphertext keys, and private metadata never go on-chain. First implement encryption, signatures, recipient verification, revocation, ordinary append-only audit, and receipt reconciliation; only a remaining concrete cross-institution multiparty accounting problem justifies evaluating minimal hashes, timestamps, or authorization events on an approved ledger.

Blockchain 不能替代加密、授权、key custody、receipt，也不能让已经解密的数据消失。

Blockchain cannot replace encryption, authorization, key custody, or receipts and cannot make already decrypted data disappear.

## 22. Tidy3D Stage 1B / Tidy3D Stage 1B

Stage 1B 是 **NOT IMPLEMENTED** 的独立只读 adapter，不是把 Tidy3D Python client 或 API key 装进 Stage 1A。它接收可信的公开/合成 export，将其规范化为 Stage 1A 已支持的 JSON/CSV `InputFile` 边界。

Stage 1B is a **NOT IMPLEMENTED** independent read-only adapter, not the Tidy3D Python client or an API key embedded in Stage 1A. It accepts trusted public/synthetic exports and normalizes them into the JSON/CSV `InputFile` boundary already supported by Stage 1A.

```text
Tidy3D exported manifest/config/monitor data/notes
  -> read-only schema and provenance validation
  -> metadata.json + observables.csv
  -> existing Stage 1A ingestion
  -> evidence-linked interpretation, limitations, and writing support
```

最小数据契约：

Minimum data contract:

- `artifact_kind=simulation`
- solver name and version / 求解器名称与版本
- task ID when present / 如存在的任务 ID
- geometry, material definitions, and units / 几何、材料和单位
- source, monitor, boundary, PML, and grid settings / source、monitor、boundary、PML 和 grid
- simulation domain, run time, and stopping condition / 仿真域、运行时间和停止条件
- mesh, boundary, domain-size, and run-time convergence checks / 网格、边界、域大小和运行时间收敛检查
- export-file SHA-256 and generation time / 导出文件 hash 和生成时间
- explicit simulation/experiment/derived distinction / simulation、experiment、derived 的显式区分

Adapter 默认不持有 Tidy3D API key、不提交 cloud job、不运行 parameter sweep、不执行 LLM 生成代码、不读取不可信 pickle/Python object。缺单位、grid、boundary 或 convergence metadata 时必须降级或拒绝主张，而不是补造。

The adapter holds no Tidy3D API key by default, submits no cloud job, runs no parameter sweep, executes no LLM-generated code, and loads no untrusted pickle/Python object. Missing units, grids, boundaries, or convergence metadata must downgrade or reject claims rather than inventing them.

Tidy3D Python client 公开可获取不等于 FDTD 求解完全离线；常见 workflow 使用云 service、credential 和 FlexCredits。免费额度和价格会变化，不能写成固定项目参数；任何实际 cloud job 需要账户核验、成本估算、硬预算和单独授权。

The publicly available Tidy3D Python client does not make FDTD solving fully offline; common workflows use cloud services, credentials, and FlexCredits. Free allowance and pricing change and are not fixed project parameters; any real cloud job requires account verification, cost estimation, a hard budget, and separate authorization.

## 23. 模型选择、Qwen 和 Kimi K3 / Model Selection, Qwen, and Kimi K3

### 23.1 当前默认模型 / Current Default Model

Stage 1A 当前默认 `qwen2.5:3b`，用于轻量本地演示和 live smoke。它能在当前 RTX 4070 Ti 12 GB 工作站运行，但默认不表示它经过完整科研质量 benchmark，也不表示它适合企业并发。模型可替换为其他已安装 Ollama model，只要名称和 loopback policy 通过；每个模型都需要独立质量评估。

Stage 1A currently defaults to `qwen2.5:3b` for lightweight local demonstration and live smoke. It runs on the current RTX 4070 Ti 12 GB workstation, but the default does not mean complete scientific-quality benchmarking or enterprise-concurrency suitability. Another installed Ollama model can be selected if its name and loopback policy pass, but every model requires independent quality evaluation.

### 23.2 Kimi K3 / Kimi K3

Kimi K3 只是一项未来 E3 cluster provider candidate，当前没有下载、部署或调用。2026-07-29 的官方资料记录约 `2.8T` total parameters、`104B` active parameters per token 和约 `1.561 TB` checkpoint，并采用自定义 Kimi K3 License。

Kimi K3 is only a future E3 cluster-provider candidate and is not downloaded, deployed, or invoked. Official material available on 2026-07-29 records approximately `2.8T` total parameters, `104B` active parameters per token, and a roughly `1.561 TB` checkpoint under a custom Kimi K3 License.

`104B active` 描述每 token 选择的 expert 计算路径，不是模型只需存储 104B 参数。不同 token 选择不同 expert，全 GPU-resident serving 通常仍需容纳全部权重。

`104B active` describes experts selected for each token, not storage of only 104B parameters. Different tokens select different experts, so fully GPU-resident serving normally holds the complete model weights.

| 表示 / Representation | 2.8T 纯权重估算 / Raw weight estimate |
| --- | ---: |
| BF16/FP16 | about `5.6 TB` |
| FP8/INT8 | about `2.8 TB` |
| Ideal packed 4-bit | about `1.4 TB` before scales/metadata/padding |
| Official checkpoint snapshot | about `1.561 TB` on disk; loaded VRAM depends on serving representation |

若 serving engine 能保持约 1.561 TB 表示，权重裸下限约为 `20 x 80 GB` 或 `12 x 141 GB` GPU；为 KV cache、activations、communication buffers、CUDA/NCCL workspace 和 fragmentation 预留 20-30% 后，容量评估约从 `25-28 x 80 GB` 或 `14-16 x 141 GB` 开始。按常见 8-GPU node，通常向 `32 x 80 GB` 或 `16 x 141 GB` 规划。

If a serving engine keeps the approximately 1.561 TB representation resident, bare weight capacity is roughly `20 x 80 GB` or `12 x 141 GB` GPUs. Reserving 20-30% for KV cache, activations, communication buffers, CUDA/NCCL workspace, and fragmentation moves initial capacity evaluation to about `25-28 x 80 GB` or `14-16 x 141 GB`; common eight-GPU nodes round this toward `32 x 80 GB` or `16 x 141 GB`.

这只是 capacity arithmetic，不是兼容性证明。实际数量还取决于 serving engine 是否解压权重、expert/tensor parallel topology、interconnect、context、batch/concurrency、KV dtype、shared-layer replication 和 HA replica。CPU/NVMe offload 可减少 VRAM，但通常显著降低吞吐和增加延迟。

This is capacity arithmetic, not compatibility proof. Actual counts depend on whether serving expands weights, expert/tensor-parallel topology, interconnect, context, batch/concurrency, KV dtype, shared-layer replication, and HA replicas. CPU/NVMe offload can reduce VRAM but usually reduces throughput and increases latency substantially.

当前 12 GB RTX 4070 Ti 不能部署 Kimi K3；RAG 不减少模型权重。Kubernetes 也不会消除模型并行和硬件拓扑要求。

The current 12 GB RTX 4070 Ti cannot deploy Kimi K3; RAG does not reduce model weights. Kubernetes does not remove model-parallel and hardware-topology requirements.

企业采用前必须审查 license、model card、custom serving code、remote code、artifact/container digest、security、correctness、capacity、power/cooling 和 total cost。Hosted API 会让数据离开本地边界，不能处理高价值数据，除非另有明确 transfer、recipient、contract、budget 和 security authorization。

Enterprise adoption requires license, model-card, custom-serving-code, remote-code, artifact/container-digest, security, correctness, capacity, power/cooling, and total-cost review. A hosted API moves data outside the local boundary and cannot handle high-value data without separate transfer, recipient, contract, budget, and security authorization.

## 24. 工作治理、Issue、Branch、Commit 和 PR / Work Governance, Issues, Branches, Commits, and PRs

项目采用“一项可独立验收的工作一个 canonical Issue”。Issue 保存目标、范围变化、关键决策、阻塞、外部副作用和验收证据；README/architecture/roadmap 保存当前事实。普通迭代命令和重复测试不需要逐条评论。

The project uses one canonical Issue per independently acceptable deliverable. Issues retain objectives, scope changes, material decisions, blockers, external effects, and acceptance evidence; README/architecture/roadmap retain current truth. Routine commands and repeated tests do not receive per-command comments.

### 24.1 Owning Repository

- 父仓库：总体路线、跨组件 contract、父级 docs、integration acceptance、submodule URL/branch/gitlink。 / Parent: roadmap, cross-component contracts, parent docs, integration acceptance, and submodule metadata/pins.
- 子仓库：组件 source、tests、component docs、security fixes 和 release。 / Child: component source, tests, component docs, security fixes, and releases.
- 跨仓库任务：父 umbrella Issue + 子 implementation Issue，并使用完整 `owner/repo#N`。 / Cross-repository work: parent umbrella plus child implementation Issue with fully qualified references.

### 24.2 Lifecycle

```text
Route -> Define -> Start when needed -> Branch -> Implement -> Validate -> Deliver -> Close
```

branch 格式是 `<type>/<issue-number>-<slug>`。Commit 使用 `Refs #N`；中间 commit 不使用 `Closes/Fixes`。只有 merge 即完成且 PR 保留全部证据时，PR body 才使用 `Closes #N`。

Branches use `<type>/<issue-number>-<slug>`. Commits use `Refs #N`; intermediate commits never use `Closes/Fixes`. A PR body uses `Closes #N` only when merge itself completes delivery and the PR retains all evidence.

修改代码不自动授权 stage/commit；commit 不自动授权 push；push 不自动授权 PR/merge；PR 不自动授权 merge/release/settings。默认 branch 不直推，不 force push，不把无关 dirty files 混入 commit。

Editing does not automatically authorize staging/committing; committing does not authorize pushing; pushing does not authorize a PR/merge; a PR does not authorize merge/release/settings. Do not push the default branch directly, force-push, or mix unrelated dirty files into a commit.

当前 handbook Issue 是 [#4](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/4)，branch 为 `docs/4-implementation-handbook`。它只允许本文件和根 README 导航，不允许把任何本地 child checkout（包括历史 `367f971`）混入提交。

The current handbook Issue is [#4](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/4) on `docs/4-implementation-handbook`. It permits only this document and root README navigation; no local child checkout, including historical `367f971`, may be staged.

### 24.3 数据和安全记录 / Data and Security Records

普通 Issue、PR、commit 和 CI log 不得包含 credentials、private keys、signed URLs、真实科研数据、真实 sample names、机密未公开结论、完整 raw logs 或敏感 prompt content。只使用公开/合成 fixture 和最小复现片段。

Ordinary Issues, PRs, commits, and CI logs must not contain credentials, private keys, signed URLs, real research data, real sample names, confidential unpublished findings, complete raw logs, or sensitive prompt content. Use public/synthetic fixtures and minimal reproductions only.

普通非机密 hardening 可走 Issue；机密漏洞不进入普通 GitHub object，应按 [SECURITY.md](../SECURITY.md) 先通过既有一对一私密渠道请求受限 intake。当前 SECURITY 文件是 routing process，不是技术性 private-reporting system。

Ordinary non-confidential hardening can use an Issue; confidential vulnerabilities do not enter ordinary GitHub objects and follow [SECURITY.md](../SECURITY.md) to request restricted intake through an existing one-to-one private channel. The current SECURITY file is a routing process, not a technical private-reporting system.

## 25. 已知实现缺口与后续修复边界 / Known Implementation Gaps and Future Fix Boundaries

本表记录源码审查事实，不表示 Issue #4 获准修复它们。每项代码修改都需要正确 owning repository 的独立 Issue、测试和兼容性评估。

This table records source-review facts and does not authorize Issue #4 to fix them. Each code change requires a separate Issue in the owning repository, tests, and compatibility assessment.

| 缺口 / Gap | 当前影响 / Current impact | 当前缓解 / Current mitigation |
| --- | --- | --- |
| `why_it_works` 无 evidence IDs | 关键叙事逻辑不能机械证明来自 cited evidence。 / Core narrative logic is not mechanically citation-bound. | Prompt policy、报告 disclaimer、人工复核。 / Prompt policy, disclaimer, human review. |
| Manual validator/schema parity incomplete | 若 Ollama endpoint 不严格执行 schema，部分 invalid enum/type 可能通过。 / Some invalid enum/type values may pass if endpoint schema enforcement is weak. | Ollama structured format + existing manual checks; future exhaustive parity tests. |
| Numeric citation repair is semantic-blind | 常见数值可能被补到语义不相关 evidence。 / Common numbers may be linked to semantically unrelated evidence. | Warning 明示只按精确数值匹配；人工检查。 / Warning states exact numeric matching; human review. |
| FDTD constraints mainly prompt-level | “simulation vs experiment”及 convergence/optimality 可能仍被模型误写。 / Model may still misstate simulation/experiment or convergence/optimality. | Domain prompt + expert review; future deterministic domain validator. |
| Cleanup ignores deletion errors | 失败时极端情况下可能留下 partial sensitive run。 / Extreme failures may leave a partial sensitive run. | Private parent directory; future explicit cleanup error/audit/quarantine design. |
| Export lacks authenticity | ZIP 只能证明包内自洽，不能证明 signed origin。 / ZIP proves internal consistency, not signed origin. | Review warning; future secure-release signature/encryption. |
| Startup token has no object ownership | 同 token 可 list/read/export 全部 run。 / One token can access all runs. | Strict loopback single-user deployment only; future E2/E4. |
| Provider preflight is trusted in-process only (E1) | 不能隔离恶意 provider code，也未全面复核所有 metadata/result。 / Cannot isolate malicious provider code or exhaustively verify all metadata/results. | Explicit allowlist; future out-of-process E3 gateway with service identity and network policy. |
| PDF parser not fully sandboxed | 未知恶意 PDF 的 parser attack surface 仍存在。 / Parser attack surface remains for unknown malicious PDFs. | Trusted PDFs only, resource limits, external isolated conversion for unknown files. |
| No OS egress enforcement | 配置错误或受损进程仍可能联网。 / Misconfiguration or a compromised process may still reach networks. | Public/synthetic data only in current environment; future host firewall/namespace controls. |
| Scientific acceptance incomplete | 不能声称提高论文质量或科研判断质量。 / Cannot claim improved manuscript or research-decision quality. | Complete 5-case, 2-reviewer evaluation before such claims. |

## 26. 完整文件导航 / Complete File Navigation

### 26.1 Parent Repository

| 文件 / File | 何时阅读 / When to read |
| --- | --- |
| [README.md](../README.md) | 先看当前状态、clone 和资料入口。 / Start with status, clone, and navigation. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 理解 superproject、local/enterprise topology 和边界。 / Understand topology and boundaries. |
| [ROADMAP.md](ROADMAP.md) | 判断完成度、当前顺序和 exit gates。 / Determine completion, current sequence, and exit gates. |
| [ENTERPRISE_DEPLOYMENT.md](ENTERPRISE_DEPLOYMENT.md) | 阅读字段级 enterprise/secure-release contract 和 threat matrix。 / Read field-level contracts and threat tests. |
| [AGENTS.md](../AGENTS.md) | 修改任何内容前阅读。 / Read before changing anything. |
| [SECURITY.md](../SECURITY.md) | 报告安全问题前阅读。 / Read before reporting security issues. |

### 26.2 Child Repository

| 路径 / Path | 内容 / Content |
| --- | --- |
| `README.md` | 安装、运行、安全和组件范围。 / Installation, operation, security, and component scope. |
| `STAGE1A_HANDOFF.md` | **HISTORICAL** 技术交接；旧优先级由父 Roadmap 取代。 / Historical technical handoff; parent Roadmap supersedes old priorities. |
| `examples/synthetic_waveguide_notes.md` | 第一组合成光子学文字 fixture。 / First synthetic photonics text fixture. |
| `examples/synthetic_transmission_sweep.csv` | 同案例的合成表格 fixture。 / Synthetic table fixture for the same case. |
| `runs/.gitkeep` | 保留空目录；默认 runtime 不写这里。 / Keeps an empty directory; default runtime does not write here. |
| `src/good_story_agent/` | 本手册第 5.2 节列出的 runtime source。 / Runtime source indexed in section 5.2. |
| `tests/` | 本手册第 17 节列出的 engineering acceptance tests。 / Engineering acceptance tests indexed in section 17. |

## 27. 阅读完成后的自检 / Reader Comprehension Check

读完后，应能准确回答：

After reading, you should be able to answer accurately:

1. 父仓库为什么可能显示 submodule modified，即使 gitlink 已固定到 `efea263`？ / Why can the parent show a modified submodule even when the gitlink is pinned to `efea263`?
2. Audit 模式验证了什么，为什么它不算科学故事生成？ / What does audit verify, and why is it not story generation?
3. 一个 CSV row 如何变成 source hash、locator 和 evidence ID？ / How does a CSV row become a source hash, locator, and evidence ID?
4. 哪些规则由代码机械强制，哪些只在 prompt 中？ / Which rules are mechanically enforced and which are prompt-only?
5. 为什么 valid citation 不证明结论正确？ / Why does a valid citation not prove a correct conclusion?
6. Export ZIP 删除了什么，又仍可能泄露什么？ / What does the export ZIP remove, and what can it still reveal?
7. startup token 为什么不能用于企业身份？ / Why is the startup token not enterprise identity?
8. 为什么 RAG 不能授权，metadata filter 也不能替代 RLS？ / Why can neither RAG nor metadata filters authorize access or replace RLS?
9. E1 provider boundary 已实现了什么，为什么仍不属于父固定版本？ / What does E1 implement, and why is it not parent-pinned?
10. Secure release 为什么必须独立于 Stage 1A export？ / Why must secure release remain separate from Stage 1A export?
11. Tidy3D adapter 为什么只读且不持有 API key？ / Why is the Tidy3D adapter read-only and keyless?
12. Kimi K3 的 `104B active` 为什么不意味着只需 104B 模型显存？ / Why does `104B active` not mean memory for only a 104B model?
13. 哪些能力已固定、待审、仅设计或未实现？ / Which capabilities are pinned, under review, design-only, or unimplemented?

如果其中任一答案仍不清楚，应回到相应章节和固定源码；不要用产品名称或计划图推断未实现行为。

If any answer remains unclear, return to the corresponding section and pinned source; never infer unimplemented behavior from product names or roadmap diagrams.

## 28. 术语表 / Glossary

| 术语 / Term | 本项目含义 / Meaning in This Project |
| --- | --- |
| Agent | LLM 综合加确定性输入、验证、溯源、权限和输出工作流。 / LLM synthesis inside deterministic ingestion, validation, provenance, permission, and output workflow. |
| Source | 一个完整上传文件及其 hash/coverage metadata。 / One complete uploaded file and its hash/coverage metadata. |
| Evidence item | 从 source 提取的可定位 text/table/structured/PDF chunk。 / A locatable text/table/structured/PDF chunk extracted from a source. |
| Evidence-bounded | 输出只能引用本次已提供 evidence set；不等于 scientific truth。 / Output can cite only the supplied evidence set; not scientific truth. |
| Run | 一次输入、选项、analysis、report 和 provenance 的本地目录。 / One local directory containing inputs, options, analysis, report, and provenance. |
| Audit mode | 无 LLM 的 ingestion/provenance pipeline verification。 / Ingestion/provenance pipeline verification without an LLM. |
| Provider | 向 Stage 1A 返回 structured synthesis result 的受控内部接口；当前固定版本尚无通用 provider layer。 / Controlled interface returning structured synthesis; no generic provider layer exists in the pin. |
| RAG | 在已授权 source set 内做 relevance retrieval；不是授权系统。 / Relevance retrieval inside an already authorized source set; not authorization. |
| RLS | PostgreSQL row-level policy，作为数据层强制授权。 / PostgreSQL row-level policy as data-layer enforcement. |
| Tenant | 未来由机构定义的隔离域，可能是 lab/project/institution；当前尚未决定。 / Future institution-defined isolation domain; not yet decided. |
| Secure release | 独立的人审、接收者验证、加密、签名、receipt 和 audit workflow。 / Separate human approval, recipient verification, encryption, signature, receipt, and audit workflow. |
| FlexCredits | Tidy3D cloud 使用的可变商业额度；不是 Stage 1A 依赖。 / Variable commercial allowance for Tidy3D cloud; not a Stage 1A dependency. |
| Total parameters | MoE 全部需要存储的 model weights。 / All model weights that an MoE must store. |
| Active parameters | 每 token 被 routing 选择参与计算的部分参数。 / Parameters selected by routing for computation per token. |

---

本手册的目的不是替代源码，而是让源码、测试、架构、路线和安全边界可以在同一张地图上被准确阅读。任何后续实现改变上述事实时，都必须通过新的 canonical Issue 同步源码、测试和持久文档。

This handbook does not replace source. It makes source, tests, architecture, roadmap, and security boundaries readable on one accurate map. Any later implementation that changes these facts requires a new canonical Issue updating source, tests, and durable documentation together.
