# Industrial_Local_Agent

`Industrial_Local_Agent` 是一个 private Git superproject，用于组织本地科研 Agent、受控仿真辅助和后续安全发布组件。它通过 Git submodule 固定各组件的已审查版本，不复制组件源码或改写其独立历史。

`Industrial_Local_Agent` is a private Git superproject for organizing local scientific agents, controlled simulation assistance, and later secure-release components. It pins reviewed component versions through Git submodules without copying their source or rewriting their independent histories.

## 当前结论 / Current Status

- Stage 1A 工程 MVP 已完成：本地、证据可追溯的科研故事 Agent，版本 `0.1.1`，自动化测试为 `38 passed`。
  The Stage 1A engineering MVP is complete: a local, evidence-traceable scientific-story agent at version `0.1.1`, with `38 passed` automated tests.
- Stage 1A 的科研质量验收尚未完成；当前只有一组合成光子学案例，还需要四组案例和独立人工评估。
  Stage 1A scientific-quality acceptance is not complete; the current evidence includes one synthetic photonics case, with four additional cases and independent human evaluation still required.
- Stage 1B 尚未实现。它仍是独立的只读 Tidy3D 结果适配器，但当前工程优先完成身份感知授权检索与安全发布基础；这些安全门槛通过后再实施适配器。Agent 不持有 API key，也不自动提交云端任务。
  Stage 1B is not implemented. It remains an independent read-only Tidy3D result adapter, but current engineering first establishes identity-aware authorized retrieval and the secure-release foundation; adapter implementation follows those security gates. The agent does not hold API keys or automatically submit cloud jobs.
- Enterprise E0 已定义单用户 local 与身份感知 enterprise 两种模式、跨组件契约和威胁模型；SSO、授权检索、RLS、多租户服务和集中式模型 gateway 仍未实现。
  Enterprise E0 defines single-user local and identity-aware enterprise modes, cross-component contracts, and a threat model; SSO, authorized retrieval, RLS, multitenant service, and a centralized model gateway remain unimplemented.
- Stage 1A 的 provider-boundary 实施正在子仓库中独立审查；在子 PR 合并并另行更新 gitlink 前，父仓库固定版本仍是 `4e3bdda`，不能把开发分支描述成已部署能力。
  The Stage 1A provider-boundary implementation is under independent review in the child repository. Until its child PR is merged and the gitlink is updated separately, the parent pin remains `4e3bdda` and the development branch is not a deployed capability.
- 安全发布、跨机构传输和区块链均未实现。未来必须先建立威胁模型、加密、密钥管理、访问控制和审计，再判断区块链是否解决剩余问题。
  Secure release, cross-institution transfer, and blockchain are not implemented. A future stage must first define threat modeling, encryption, key management, access control, and auditing before deciding whether blockchain solves a remaining problem.

## 仓库结构 / Repository Structure

| 路径 / Path | 类型 / Type | 职责 / Responsibility | 当前固定版本 / Current Pin |
| --- | --- | --- | --- |
| `components/stage1a-good-story-agent/` | Git submodule | 本地证据可追溯科研写作 Agent / Local evidence-traceable scientific-writing agent | `4e3bdda` |
| `docs/ARCHITECTURE.md` | 父仓库文档 / Parent documentation | 组件边界、更新规则和安全模型 / Component boundaries, update rules, and security model | 当前父仓库 / Current parent |
| `docs/ENTERPRISE_DEPLOYMENT.md` | 父仓库文档 / Parent documentation | 企业部署模式、契约、威胁模型和验收门槛 / Enterprise deployment modes, contracts, threat model, and acceptance gates | E0 设计基线 / E0 design baseline |
| `docs/ROADMAP.md` | 父仓库文档 / Parent documentation | Stage 1A 至 Stage 3 的验收路线 / Acceptance roadmap from Stage 1A through Stage 3 | 当前父仓库 / Current parent |

未来可能增加 `tidy3d-adapter`、identity-aware retrieval、model gateway、`secure-data-transfer` 和 `workflow-orchestrator`，但在接口与验收条件稳定前不创建空组件。

Future components may include `tidy3d-adapter`, identity-aware retrieval, a model gateway, `secure-data-transfer`, and `workflow-orchestrator`, but empty components will not be created before their interfaces and acceptance criteria are stable.

## 获取完整仓库 / Clone the Complete Repository

普通 GitHub ZIP 不包含 submodule 的源码。请使用递归克隆，并确保账号同时拥有父仓库和 private 子仓库的读取权限：

A normal GitHub ZIP does not include submodule source. Clone recursively and ensure the account has read access to both the parent and private child repositories:

```bash
git clone --recurse-submodules git@github.com:Juggernautsst/Industrial_Local_Agent.git
cd Industrial_Local_Agent
```

如果已经克隆父仓库但组件目录为空：

If the parent has already been cloned without its component content:

```bash
git submodule update --init --recursive
```

## 更新组件版本 / Update a Component Pin

必须先在子仓库完成修改、验证、提交和推送，再在父仓库更新 gitlink。父仓库只记录被审查的子仓库提交，不应递归暂存组件文件。

First complete, verify, commit, and push changes in the child repository. Then update the gitlink in the parent. The parent records only a reviewed child commit and must not recursively stage component files.

```bash
git submodule update --remote components/stage1a-good-story-agent
git diff --submodule
git add components/stage1a-good-story-agent
git commit -m "chore: update Stage 1A component"
```

推送父仓库前，应确认子仓库目标提交已经存在于其远端，否则其他协作者无法检出该版本。

Before pushing the parent, confirm that the target child commit already exists on the child remote; otherwise collaborators cannot check it out.

## Tidy3D 与 FlexCredits / Tidy3D and FlexCredits

Tidy3D Python 客户端可公开获取，但常见 FDTD 求解流程通常涉及云端服务、凭据和 FlexCredits，不能等同于完整本地离线求解器。Stage 1B 首先读取公开或合成的导出结果，并规范化 simulation metadata、monitor CSV、单位、网格、边界、收敛检查和 SHA-256。免费账户额度可能变化，任何云任务都必须根据实际账户先估算成本并设置硬预算。

The Tidy3D Python client is publicly available, but common FDTD solving workflows usually involve cloud services, credentials, and FlexCredits; it is not equivalent to a complete local offline solver. Stage 1B will first read public or synthetic exports and normalize simulation metadata, monitor CSV data, units, grids, boundaries, convergence checks, and SHA-256 values. Free-account allowances may change, so any cloud job must use the actual account to estimate cost and set a hard budget first.

## 企业内网共享与权限检索 / Enterprise Intranet and Authorized Retrieval

一台服务器可以为多个内网用户提供较小的本地模型，但不能直接暴露当前 Flask 服务。企业目标需要机构 SSO、可信 API gateway、服务端身份委托、RBAC+ABAC、PostgreSQL/pgvector `FORCE ROW LEVEL SECURITY`、top-K source 重新授权、tenant-scoped storage/cache、model gateway 和最小 audit。只有入口 gateway 对用户网络开放。

One server can provide a smaller local model to multiple intranet users, but the current Flask service cannot be directly exposed. The enterprise target requires institutional SSO, a trusted API gateway, server-side identity delegation, RBAC+ABAC, PostgreSQL/pgvector `FORCE ROW LEVEL SECURITY`, top-K source reauthorization, tenant-scoped storage/cache, a model gateway, and minimal audit. Only the entry gateway is exposed to the user network.

RAG 只在已经授权的 source set 内排序相关内容；metadata filter 不是授权，LLM 也不能批准访问。retrieval gateway 生成短期签名 `AuthorizedEvidenceBundle`，Stage 1A 只能使用该 bundle，并验证所有输出 citation 都属于它。当前 startup token 只是本地会话控制，不是 user identity。

RAG ranks relevant content only inside an already authorized source set. Metadata filters are not authorization, and the LLM cannot approve access. The retrieval gateway creates a signed short-lived `AuthorizedEvidenceBundle`; Stage 1A can use only that bundle and verifies that every output citation belongs to it. The current startup token is local session control, not user identity.

当前实施顺序是：审查 E1 provider boundary；用合成数据验证 E2 身份委托、同 tenant/跨 tenant 授权与 RLS；先定义 secure-release package/receipt 协议，再分别实现审批与接收者密钥、加密 envelope/verifier、audit-committed outbox；然后实施 Tidy3D Stage 1B。各组件在架构上保持独立，这个顺序不表示上述未实现能力已经可用。

The current implementation order is: review the E1 provider boundary; validate E2 identity delegation, same-tenant and cross-tenant authorization, and RLS with synthetic data; define the secure-release package/receipt protocol, then separately implement approval and recipient keys, the cryptographic envelope/verifier, and an audit-committed outbox; then implement Tidy3D Stage 1B. These components remain architecturally independent, and this order does not imply that the unimplemented capabilities are available.

Kimi K3 仅作为未来 cluster-class model gateway 的候选 open-weight provider。官方规模约为 2.8T 总参数、104B 激活参数和约 1.561 TB checkpoint，不能部署在当前 RTX 4070 Ti 工作站；RAG 不会降低模型权重内存。完整设计、非目标与验收测试见 [企业部署与威胁模型](docs/ENTERPRISE_DEPLOYMENT.md)。

Kimi K3 is only a future candidate open-weight provider behind a cluster-class model gateway. Its official scale is approximately 2.8T total parameters, 104B active parameters, and a 1.561 TB checkpoint, so it cannot run on the current RTX 4070 Ti workstation; RAG does not reduce model-weight memory. See [Enterprise Deployment and Threat Model](docs/ENTERPRISE_DEPLOYMENT.md) for the full design, non-goals, and acceptance tests.

## 安全边界 / Security Boundaries

- 父仓库和子仓库均应保持 private；父仓库权限不会自动授予 private 子仓库权限。
  Both parent and child repositories should remain private; parent access does not automatically grant access to a private submodule.
- 不得提交真实科研数据、模型文件、运行产物、导出包、`.env`、API token、密码或私钥。
  Do not commit real research data, model files, run artifacts, export bundles, `.env` files, API tokens, passwords, or private keys.
- 当前 `/mnt/d` 工作副本只用于开发、公开材料和合成数据，不适合未公开或高价值材料。
  The current `/mnt/d` working copy is for development, public material, and synthetic data only; it is unsuitable for unpublished or high-value material.
- private GitHub 可见性不是数据加密、主机隔离或外发控制。
  Private GitHub visibility is not data encryption, host isolation, or egress control.
- 当前 Stage 1A startup token 不区分 user、tenant 或 owner，run list/read/export 也没有 tenant isolation；不得通过改变绑定地址直接用于内网多用户。
  The current Stage 1A startup token does not distinguish user, tenant, or owner, and run list/read/export has no tenant isolation; do not turn it into a multiuser intranet service by changing the bind address.
- RAG relevance、LLM 输出或 vector metadata filter 都不是授权证据；身份、策略和数据库层必须默认拒绝并独立审计。
  RAG relevance, LLM output, and vector metadata filters are not authorization evidence; identity, policy, and database layers must fail closed and be audited independently.
- 公开任一仓库前，必须单独完成许可证、安全和机器信息清理审查。
  Before making either repository public, perform separate licensing, security, and machine-information reviews.

## 工作治理与远端留痕 / Work Governance and Remote Traceability

所有持久性修改和外部副作用都使用“一项可验收工作一个 GitHub Issue”的流程。Issue 记录目标、范围、决策和验收历史，README 与 `docs/` 保存当前事实；不为每条本地命令创建 Issue 或评论。

All durable changes and external side effects follow one GitHub Issue per independently acceptable deliverable. Issues preserve objectives, scope, decisions, and acceptance history, while README and `docs/` preserve current truth; do not create Issues or comments for every local command.

- [Agent 工作规则 / Agent workflow rules](AGENTS.md)
- [创建 Issue / Create an Issue](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/new/choose)
- [查看工作记录 / View work history](https://github.com/Juggernautsst/Industrial_Local_Agent/issues)

普通 Issue 不得包含凭据、真实科研数据、真实研究中的机密或受限未公开结论，或机密漏洞详情。父仓库与组件仓库分别拥有自己的 Issue；跨仓库任务使用父 umbrella Issue 和子 implementation Issue 互链。

Ordinary Issues must not contain credentials, real research data, confidential or restricted unpublished findings from real research, or confidential vulnerability details. Parent and component repositories own separate Issues; cross-repository work uses linked parent umbrella and child implementation Issues.

- [安全报告流程 / Security reporting](SECURITY.md)

## 详细资料 / Detailed Records

- [项目完整实现手册 / Complete implementation handbook](docs/IMPLEMENTATION_HANDBOOK.md)：从版本状态进入 Stage 1A 源码调用链、运行契约、测试缺口和未来设计的统一阅读地图。 / A unified map from version status into the Stage 1A source call chain, runtime contracts, test gaps, and future design.
- [总体架构 / Architecture](docs/ARCHITECTURE.md)
- [企业部署与威胁模型 / Enterprise deployment and threat model](docs/ENTERPRISE_DEPLOYMENT.md)
- [实施路线 / Roadmap](docs/ROADMAP.md)
- [Stage 1A 历史交接 / Historical Stage 1A handoff](components/stage1a-good-story-agent/STAGE1A_HANDOFF.md)（其中 next-step 顺序已由父仓库 roadmap 取代 / its next-step ordering is superseded by the parent roadmap）
- [Stage 1A 使用说明 / Stage 1A usage](components/stage1a-good-story-agent/README.md)

父仓库当前未声明统一许可证。每个组件保留自己的许可证责任；父仓库许可证不会自动覆盖 submodule。

The parent currently declares no unified license. Each component retains its own licensing responsibility; a parent license would not automatically cover a submodule.
