# 实施路线 / Roadmap

路线按可验收证据推进，不按技术名词堆叠。任何阶段只有在其明确验收条件满足后才能标记完成。编号表示稳定的能力边界，不表示当前实施顺序。

The roadmap advances through testable evidence, not accumulated technology labels. A stage may be marked complete only after its stated acceptance conditions are met. Stage numbers identify stable capability boundaries, not the current implementation order.

| 阶段 / Stage | 交付内容 / Deliverable | 当前状态 / Current Status | 进入下一阶段的门槛 / Exit Gate |
| --- | --- | --- | --- |
| 1A 工程 / 1A Engineering | 本地证据可追溯科研故事 Agent / Local evidence-traceable scientific-story agent | 工程 MVP 已完成 / Engineering MVP complete | 自动化、安全边界和真实本地模型演示已验证 / Automation, security boundaries, and a real local-model demonstration verified |
| 1A 科研验收 / 1A Scientific Acceptance | 光子学案例人工评估 / Human evaluation on photonics cases | 未完成 / Incomplete | 至少五组公开或合成案例及双人独立评分 / At least five public or synthetic cases with two independent evaluators |
| 1B | 只读 Tidy3D 结果适配器 / Read-only Tidy3D result adapter | 未实现 / Not implemented | 规范化产物、来源校验、失败降级和五案例评估 / Normalized artifacts, provenance validation, failure degradation, and five-case evaluation |
| 2 | 受控安全发布与跨机构传输 / Controlled secure release and cross-institution transfer | 协议基线已起草；实现未开始 / Protocol baseline drafted; implementation not started | 威胁模型、加密、密钥、权限、签名、撤销和审计经过测试 / Tested threat model, encryption, keys, access, signatures, revocation, and audit |
| 3 | 研究人员统一工作流 / Integrated researcher workflow | 未开始 / Not started | 写作、仿真结果和安全发布在最小权限下端到端验收 / End-to-end acceptance of writing, simulation results, and secure release under least privilege |

## Enterprise E0-E4 架构路线 / Enterprise E0-E4 Architecture Track

Enterprise 路线解决“一台受控服务器或集群供多个内网用户使用，并按身份检索各自有权数据”的部署问题。它与安全发布、Stage 1B Tidy3D 保持独立架构边界，不替代这些路线；当前代码实施按下述安全优先顺序推进，而不是同时展开。

The enterprise track addresses deployment on one controlled server or cluster for multiple intranet users, with identity-scoped retrieval of only authorized data. It retains boundaries independent from secure release and Stage 1B Tidy3D and does not replace those tracks; implementation follows the security-first order below rather than proceeding concurrently.

| Enterprise stage | 交付内容 / Deliverable | 当前状态 / Current status | Exit gate / 退出门槛 |
| --- | --- | --- | --- |
| E0 | Local/enterprise 模式、威胁模型、identity/bundle/provider/audit 契约 / Local/enterprise modes, threat model, and identity/bundle/provider/audit contracts | 设计基线已定义；生产控制未实现 / Design baseline defined; production controls not implemented | README、架构、路线与 [企业部署文档](ENTERPRISE_DEPLOYMENT.md) 一致，非目标清楚 / README, architecture, roadmap, and [enterprise deployment document](ENTERPRISE_DEPLOYMENT.md) agree with explicit non-goals |
| E1 | Stage 1A 稳定 synthesis-provider boundary / Stable Stage 1A synthesis-provider boundary | 已合并并固定到 child `efea263` / Merged and pinned at child `efea263` | audit/Ollama 统一 contract tests、preflight、真实 provenance、no fallback、CLI/Web/manifest 兼容 / Shared audit/Ollama contract tests, preflight, truthful provenance, no fallback, and CLI/Web/manifest compatibility |
| E2 | Identity-aware retrieval service / 身份感知检索服务 | 合成 model-free vertical slice 已实现；生产集成未实现 / Synthetic model-free vertical slice implemented; production integration not implemented | 先验收 Issue #10 的 synthetic contract；后续 OIDC、RBAC+ABAC、PostgreSQL/pgvector forced RLS、持久化 policy/audit 和 E4 集成 / First accept the Issue #10 synthetic contract; later add OIDC, RBAC+ABAC, PostgreSQL/pgvector forced RLS, durable policy/audit, and E4 integration |
| E3 | Controlled model gateway / 受控模型 gateway | 未实现 / Not implemented | registered/pinned provider、mTLS/service identity、endpoint/egress policy、capacity、digest provenance、no content logs、no fallback / Registered and pinned providers, mTLS/service identity, endpoint/egress policy, capacity, digest provenance, no content logs, and no fallback |
| E4 | Enterprise Stage 1A integration / 企业 Stage 1A 集成 | 未实现 / Not implemented | 只有 `AuthorizedEvidenceBundle` 进入 Stage 1A，citation subset 与 tenant run/list/read/export 隔离通过，并保持 secure-release 独立 / Only `AuthorizedEvidenceBundle` enters Stage 1A, citation subset and tenant run/list/read/export isolation pass, and secure release remains separate |

E0 的完成只代表设计决策和验收标准可复核，不代表 enterprise system 已经可部署。E1 子仓库 PR 在合并和父 gitlink 单独更新前也不属于当前固定版本。

Completion of E0 means only that design decisions and acceptance criteria are reviewable; it does not mean the enterprise system is deployable. E2's synthetic slice is executable evidence, but it is not a production deployment or a completed E4 integration.

`deploy/bunya/` 中的 Qwen3.8-27B-FP8 试点是独立的模型可运行性验证，不是 E3 model gateway，也不表示 Bunya、SSO、RAG、Stage 1A remote provider 或多用户服务已经部署。Codex 只用于辅助部署和检查。

The Qwen3.8-27B-FP8 pilot in `deploy/bunya/` is an independent model feasibility check, not the E3 model gateway. It does not mean that Bunya, SSO, RAG, a Stage 1A remote provider, or a multi-user service is deployed. Codex is only used for deployment assistance and inspection.

## 当前实施优先级 / Current Implementation Priority

1. 审查并固定已合并的 E1 provider boundary；父 gitlink 已指向 child `efea263`。
   Review the merged E1 provider boundary; the parent gitlink now points to child `efea263`.
2. 仅用合成数据验收 E2 最小 vertical slice：可信身份委托、同 tenant/跨 tenant 授权、forced scope、source reauthorization、签名 `AuthorizedEvidenceBundle` 和 content-free audit，暂不连接模型。
   Accept the smallest E2 vertical slice using synthetic data only: trusted identity delegation, same-tenant/cross-tenant authorization, forced scope, source reauthorization, signed `AuthorizedEvidenceBundle`, and content-free audit, without connecting a model.
3. 先完成 Stage 2.0 secure-release 协议：明确 researcher input/output、`ReleaseCandidate`、`SecureReleasePackage`、签名 receipt、撤销时间边界和 synthetic test vectors；先不使用区块链。
   First complete the Stage 2.0 secure-release protocol: define researcher input/output, `ReleaseCandidate`, `SecureReleasePackage`, signed receipts, time-bounded revocation semantics, and synthetic test vectors; do not use blockchain initially.
4. 协议通过后，用独立 Issue 依次实现审批与接收者密钥验证、加密 envelope/verifier、audit-committed transactional outbox 和幂等交付对账。
   After protocol acceptance, use separate issues to implement approval and recipient-key verification, the cryptographic envelope/verifier, and an audit-committed transactional outbox with idempotent delivery reconciliation.
5. 最小 secure-release vertical slice 通过独立验收后，再实施只读 Tidy3D Stage 1B adapter；保留现有数据契约，不加入 API key 或云任务权限。
   After the minimal secure-release vertical slice passes independent acceptance, implement the read-only Tidy3D Stage 1B adapter using the existing data contract, without API-key or cloud-job privileges.

这是本项目按风险和有限资源确定的串行排期，不表示 secure-release 在架构上依赖 E2，也不表示 E3/E4 可以跳过各自验收。

This is the project's serial schedule based on risk and limited resources. It does not make secure release architecturally dependent on E2, nor does it allow E3/E4 to bypass their own acceptance gates.

子仓库的 [Stage 1A 历史交接](../components/stage1a-good-story-agent/STAGE1A_HANDOFF.md) 保留当时的技术判断和 Tidy3D 数据契约；其中“第一项实现任务”和旧优先级已由本父仓库路线取代。

The child repository's [historical Stage 1A handoff](../components/stage1a-good-story-agent/STAGE1A_HANDOFF.md) retains the technical assessment and Tidy3D data contract from that handoff; its “first implementation task” and older priority order are superseded by this parent roadmap.

## Stage 1A 科研验收与后续 Tidy3D / Stage 1A Scientific Acceptance and Later Tidy3D

Stage 1A 的公开/合成案例人工评估可以继续准备；下列第 3-5 项 Tidy3D 专项工作等待上述安全门槛。

Preparation of Stage 1A human evaluation on public/synthetic cases may continue; Tidy3D-specific items 3-5 below wait for the security gates above.

1. 向导师演示固定的 Stage 1A 合成案例，明确它是工程 MVP，不是自动科学真理判断器。
   Demonstrate the fixed synthetic Stage 1A case to the supervisor and identify it as an engineering MVP, not an automatic scientific-truth evaluator.
2. 增加四组公开或合成光子学案例，由光子学研究者和科研写作评估者独立评分。
   Add four public or synthetic photonics cases and obtain independent scores from a photonics researcher and a scientific-writing evaluator.
3. 选定一个 waveguide transmission 或 ring resonator 黄金案例，定义 Tidy3D 导出数据包。
   Select one waveguide-transmission or ring-resonator golden case and define the Tidy3D export bundle.
4. 实现只读适配器，输出规范化 `metadata.json` 和 `observables.csv`，再交给 Stage 1A 分析。
   Implement a read-only adapter that emits normalized `metadata.json` and `observables.csv` for Stage 1A analysis.
5. 验证缺少单位、网格、边界或收敛信息时系统会降低主张或拒绝，而不是补造结论。
   Verify that missing units, grids, boundaries, or convergence information causes claim reduction or refusal rather than invented conclusions.

## 安全优先工程细目 / Security-first Engineering Details

1. 审查并固定已合并的 Stage 1A E1 provider boundary；父 gitlink 已指向 child `efea263`。
   Review and pin the merged Stage 1A E1 provider boundary; the parent gitlink now points to child `efea263`.
2. 在生产 E2 implementation 前确定机构 IdP、tenant 定义、数据分类、policy owner、retention、RTO/RPO 和 audit reader；synthetic Issue #10 不假装完成这些机构决策。
   Before production E2 implementation, decide the institutional IdP, tenant definition, data classification, policy owner, retention, RTO/RPO, and audit readers; synthetic Issue #10 does not pretend these institutional decisions are complete.
3. 先用 synthetic fixtures 建立两个 tenant、多个 user/project/source 的 threat-test matrix；当前 vertical slice 验证 retrieve、share、revoke、bundle 和 audit，生产 E2 仍需补齐 `list/read/export` 与数据库级测试，不得导入真实科研数据。
   Using synthetic fixtures only, build a threat-test matrix with two tenants and multiple users/projects/sources; the current slice tests retrieve/share/revoke/bundle/audit, while production E2 still needs list/read/export and database-level tests; do not ingest real research data.
4. E2 vertical slice 已完成：synthetic verified token -> delegated identity -> forced-scope retrieval -> signed `AuthorizedEvidenceBundle` -> content-free audit，不连接模型。
   The E2 vertical slice is implemented: synthetic verified token -> delegated identity -> forced-scope retrieval -> signed `AuthorizedEvidenceBundle` -> content-free audit, without connecting a model.
5. E2 通过同 tenant 项目隔离、跨 tenant、撤销、pool identity、cache、bundle 负向验证和 audit failure tests 后，创建 Stage 2.0 协议 Issue；验收协议和 synthetic vectors 后，才拆分 secure-release implementation Issues。
   After E2 passes same-tenant project isolation, cross-tenant, revocation, pooled-identity, cache, negative bundle-validation, and audit-failure tests, create the Stage 2.0 protocol issue; split secure-release implementation issues only after the protocol and synthetic vectors are accepted.
6. E3 model gateway 与 E4 enterprise integration 保持独立 Issue，在机构 provider、容量和运维边界确定后排期；它们不与本轮 E2/Stage 2/Tidy3D 代码同时启动。
   Keep the E3 model gateway and E4 enterprise integration in independent issues scheduled after institutional provider, capacity, and operational boundaries are known; do not start them concurrently with the current E2/Stage 2/Tidy3D implementation queue.

## Stage 1B 最小数据契约 / Minimum Stage 1B Data Contract

- `artifact_kind=simulation`
- solver 名称与版本 / solver name and version
- task ID，如存在 / task ID, when available
- 几何、材料与单位 / geometry, materials, and units
- source、monitor、boundary、PML 和 grid 设置 / source, monitor, boundary, PML, and grid settings
- 仿真域、运行时间与停止条件 / simulation domain, run time, and stopping condition
- 网格、边界、域大小和运行时间收敛检查 / mesh, boundary, domain-size, and run-time convergence checks
- 导出文件 SHA-256 与生成时间 / export-file SHA-256 and generation time
- simulation、experiment 与 derived analysis 的显式区分 / explicit separation of simulation, experiment, and derived analysis

## 暂不实施 / Explicitly Deferred

- Agent 自动持有或管理 Tidy3D API key / Agent ownership or management of Tidy3D API keys
- 自动提交云任务或无预算参数扫描 / Automatic cloud submission or unbudgeted parameter sweeps
- 执行 LLM 生成代码 / Execution of LLM-generated code
- 把当前 Flask/startup-token 服务改绑定地址后直接暴露给内网用户 / Direct intranet exposure of the current Flask/startup-token service by changing its bind address
- 使用 RAG score、vector metadata filter 或 LLM 输出作为授权决定 / Using RAG scores, vector metadata filters, or LLM output as authorization decisions
- 在当前 RTX 4070 Ti 工作站下载或部署 Kimi K3 / Downloading or deploying Kimi K3 on the current RTX 4070 Ti workstation
- 在 E2-E4 验收前声称 enterprise RAG、集中式模型服务或多用户隔离已完成 / Claiming enterprise RAG, centralized model serving, or multiuser isolation before E2-E4 acceptance
- 把原始数据写入区块链 / Writing raw data to a blockchain
- 在缺少科研质量评估时声称系统提高论文质量 / Claiming improved paper quality without scientific-quality evaluation

Tidy3D 免费账户额度和 FlexCredits 价格可能变化，不作为固定研究假设。任何付费或云端执行都需要单独授权、实际账户核验和硬预算。

Tidy3D free-account allowances and FlexCredit pricing may change and are not fixed research assumptions. Any paid or cloud execution requires separate authorization, actual-account verification, and a hard budget.
