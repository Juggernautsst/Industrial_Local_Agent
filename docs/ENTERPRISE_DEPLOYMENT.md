# 企业部署与威胁模型 / Enterprise Deployment and Threat Model

> 状态：本文件是 Enterprise E0 的架构与威胁模型基线，不是生产部署说明，也不表示 SSO、RAG、多租户数据库、集中式模型服务或安全发布已经实现。
>
> Status: this document is the Enterprise E0 architecture and threat-model baseline. It is not a production deployment guide and does not claim that SSO, RAG, a multitenant database, centralized model serving, or secure release has been implemented.

## 1. 不可改变的架构决策 / Non-negotiable Architecture Decisions

1. RAG 只做相关性检索，不做授权；LLM 永远不判断权限。
   RAG performs relevance retrieval, never authorization; the LLM never decides access.
2. 客户端不能声明或覆盖 user、tenant、role、group、clearance 或 policy version。可信 gateway 根据机构身份和当前策略生成短期委托上下文。
   A client cannot declare or override user, tenant, role, group, clearance, or policy version. A trusted gateway derives a short-lived delegated context from institutional identity and current policy.
3. Stage 1A 只接收已经授权的 evidence bundle，不直接连接全局语料库，也不拥有 SSO、ACL 或数据库管理员权限。
   Stage 1A receives only an already authorized evidence bundle. It does not connect to the global corpus or hold SSO, ACL, or database-administrator privileges.
4. 模型 gateway 管理已注册模型、endpoint、版本、超时和 provenance；retrieval gateway 管理身份、授权、检索、撤销和 retrieval audit。
   The model gateway owns registered models, endpoints, versions, timeouts, and provenance. The retrieval gateway owns identity, authorization, retrieval, revocation, and retrieval audit.
5. 安全发布是独立的人审与密码学组件。Stage 1A export ZIP 不是加密传输，private GitHub 也不是高价值数据传输通道。
   Secure release is a separate human-approval and cryptographic component. The Stage 1A export ZIP is not encrypted transfer, and private GitHub is not a high-value data-transfer channel.
6. 任何身份、策略、RLS、audit 或 capability 校验失败都默认拒绝，不得静默降级到其他 provider、全局检索或云服务。
   Any identity, policy, RLS, audit, or capability-validation failure defaults to denial. It must not silently fall back to another provider, global retrieval, or a cloud service.

## 2. 当前能力与目标能力 / Current and Target Capability

| 模式 / Mode | 当前状态 / Current status | 身份与数据范围 / Identity and data scope | 模型路径 / Model path | 允许的用途 / Permitted use |
| --- | --- | --- | --- | --- |
| Local | 已实现并固定在 Stage 1A 子模块版本；单用户、回环访问 / Implemented and pinned in the Stage 1A submodule; single-user and loopback-only | 启动令牌只是本地会话控制；只处理用户明确上传的本次材料 / Startup token is local session control only; processes explicitly uploaded material for the current run | 材料审计或回环 Ollama，无云回退 / Evidence audit or loopback Ollama with no cloud fallback | 公开或合成数据的开发与演示 / Development and demonstration with public or synthetic data |
| Enterprise target | 仅设计，未实现 / Design only, not implemented | 机构 SSO、服务端身份委托、RBAC+ABAC、数据库 RLS、source reauthorization / Institutional SSO, server-side identity delegation, RBAC+ABAC, database RLS, and source reauthorization | 经注册的内网 model gateway；模型不能看到权限系统 / Registered intranet model gateway; the model cannot access the authorization system | 通过安全、隐私、运维和机构审批后的受控试点 / Controlled pilot after security, privacy, operations, and institutional approval |

当前 Flask Web 服务不能通过把 `127.0.0.1` 改成内网地址而变成企业服务。它的 startup token 不是用户身份，run list/read/export 没有 tenant ownership，因此直接暴露会形成对象级越权风险。

The current Flask Web service cannot become an enterprise service by changing `127.0.0.1` to an intranet address. Its startup token is not a user identity, and run list/read/export has no tenant ownership, so direct exposure would create object-level authorization risk.

## 3. 部署形态 / Deployment Profiles

| Profile | 适用范围 / Intended scope | 模型规模 / Model scale | 限制 / Limitations |
| --- | --- | --- | --- |
| Local workstation / 本地工作站 | 当前 Stage 1A 开发与演示 / Current Stage 1A development and demonstration | 单张 GPU 可运行的小模型 / Small models that fit one GPU | 单用户、无 SSO、无 RAG、无 HA / Single-user, no SSO, no RAG, no HA |
| Controlled single-host pilot / 受控单机试点 | 少量已认证内网用户和合成/批准数据 / A small number of authenticated intranet users with synthetic or approved data | 适合该服务器 GPU/内存的小模型 / Models sized for that server GPU and memory | 逻辑隔离但共享故障域；不是简单 Flask 暴露 / Logical separation but one failure domain; not direct Flask exposure |
| Enterprise cluster / 企业集群 | 多团队、较高并发、独立 GPU 节点和高可用需求 / Multiple teams, higher concurrency, separate GPU nodes, and HA requirements | vLLM/SGLang 等受控 serving 层上的注册模型 / Registered models behind a controlled serving layer such as vLLM or SGLang | 需要平台运维、容量测试、mTLS、集中审计和正式安全评审 / Requires platform operations, capacity testing, mTLS, centralized audit, and formal security review |

受控单机试点仍必须保持逻辑边界：

A controlled single-host pilot still requires logical boundaries:

```text
Researcher browser
        |
        v
TLS reverse proxy + institutional SSO
        |
        v
API gateway (trusted identity derivation)
        |
        +---------------------> append-only audit sink
        |
        v
identity-aware retrieval service
        |
        +----> policy service
        +----> PostgreSQL + pgvector with forced RLS
        |
        v
AuthorizedEvidenceBundle
        |
        v
Stage 1A worker ----> model gateway ----> registered local model provider
        |
        v
tenant-scoped result storage
        |
        v
separate human-approved secure-release component
```

只有 reverse proxy/API gateway 对用户网络开放。数据库、Stage 1A worker、Ollama/vLLM、audit sink 和内部管理接口必须由主机防火墙、独立服务身份和最小端口规则限制。单机部署节省硬件，但不能提供高可用，也不能抵御拥有主机管理员权限的攻击者。

Only the reverse proxy/API gateway is exposed to the user network. The database, Stage 1A worker, Ollama/vLLM, audit sink, and internal management interfaces must be restricted by host firewall rules, separate service identities, and minimal port exposure. A single host saves hardware but provides no high availability and cannot defend against an attacker with host-administrator privileges.

### 3.1 唯一外发出口与工作流 / Sole Egress and Workflow

入口 API gateway 和外发传输 gateway 是两个逻辑边界。外发 gateway 可以在受控单机试点中与 MCP、Secure-Release Service 共址，但必须使用独立进程/容器、service identity、网络命名空间、端口和 default-deny 防火墙策略。生产部署应优先将内网控制平面、Secure-Release/KMS 区和 DMZ egress relay 分开。

The ingress API gateway and outbound transfer gateway are separate logical boundaries. In a controlled single-host pilot, the outbound gateway may share hardware with MCP and the Secure-Release Service, but it must use separate processes/containers, service identities, network namespaces, ports, and default-deny firewall rules. Production should preferably separate the intranet control plane, Secure-Release/KMS zone, and DMZ egress relay.

![外发网关安全工作流 / Secure egress workflow](figures/intranet-secure-release-egress.svg)

MCP 只允许把研究者意图转换为结构化 `ReleaseCandidate`，例如 `artifacts.search`、`recipients.resolve`、`release.create_draft`、`release.preview`、`release.submit_for_approval`、`release.status` 和 `release.cancel`。MCP 不得直接 approve、send_file、调用任意 shell/filesystem/HTTP、修改 classification、读取私钥或建立公网连接；LLM 对话中的“确认”也不是最终审批。

MCP only converts researcher intent into a structured `ReleaseCandidate`, using limited operations such as `artifacts.search`, `recipients.resolve`, `release.create_draft`, `release.preview`, `release.submit_for_approval`, `release.status`, and `release.cancel`. MCP must not directly approve or send files, call arbitrary shell/filesystem/HTTP tools, modify classification, read private keys, or establish Internet connections; a confirmation in an LLM conversation is not final approval.

Secure-Release Service 在包离开内网前完成服务端分类、接收者公钥 fingerprint 核验、可信 UI/MFA/人工审批绑定、应用层 envelope encryption 和签名，并通过 KMS/HSM 托管密钥。外发 relay 只接受带持久 audit receipt、状态为 `delivery_pending` 的 encrypted + signed package；它负责 allowlisted destination、固定 DNS/IP/port、TLS/mTLS、expiry、大小/速率和 idempotency 检查，不持有明文或解密私钥。Stage 1A、检索、数据库、模型和 MCP 均默认没有公网路由。

Before a package leaves the intranet, the Secure-Release Service performs server-side classification, recipient public-key fingerprint verification, trusted-UI/MFA/human-approval binding, application-level envelope encryption, and signing, with keys held by KMS/HSM. The egress relay accepts only an encrypted and signed package in `delivery_pending` state with a persisted audit receipt. It enforces an allowlisted destination, pinned DNS/IP/port, TLS/mTLS, expiry, size/rate, and idempotency checks, and holds neither plaintext nor decryption private keys. Stage 1A, retrieval, the database, the model, and MCP have no default Internet route.

外部端点只返回可验证的分级回执；`accepted_by_transport`、`downloaded`、`key_unwrapped` 和 `decryption_acknowledged_by_recipient` 不能混写成一个含糊的 “delivered”。超时或回执丢失进入 `pending_reconciliation`，不得盲目重试。当前图、边界和流程仍是设计基线，未表示 secure-release 或跨网传输已经实现。

The external endpoint returns a verifiable, graded receipt. `accepted_by_transport`, `downloaded`, `key_unwrapped`, and `decryption_acknowledged_by_recipient` must not be collapsed into an ambiguous “delivered”. A timeout or lost receipt enters `pending_reconciliation`; blind retry is forbidden. The figure, boundaries, and workflow are design baselines and do not mean secure release or cross-network transfer has been implemented.

## 4. 组件责任 / Component Responsibilities

| 组件 / Component | 必须负责 / Must own | 明确不得负责 / Must not own |
| --- | --- | --- |
| Institutional IdP / 机构 IdP | 用户认证、MFA、账号生命周期 / User authentication, MFA, and account lifecycle | 科研内容检索或模型调用 / Research-content retrieval or model invocation |
| API gateway | 验证 IdP token，生成签名短期委托，限流，请求 ID / Validate IdP tokens, create signed short-lived delegation, rate limit, and assign request IDs | 接受客户端自报 tenant/role，或把原始 IdP token 传给模型 / Accept client-declared tenant/role or pass raw IdP tokens to the model |
| MCP intent adapter / MCP 意图适配器 | 受限 typed tools、创建/预览 `ReleaseCandidate` / Restricted typed tools and creation/preview of `ReleaseCandidate` | 公网访问、审批、直接发送、任意 shell/filesystem/HTTP、私钥访问 / Internet access, approval, direct sending, arbitrary shell/filesystem/HTTP, or private-key access |
| Policy service | RBAC+ABAC、项目成员关系、数据分类和撤销 / RBAC+ABAC, project membership, data classification, and revocation | 语义排名或生成回答 / Semantic ranking or answer generation |
| Retrieval service | 在授权范围内做 lexical/vector ranking，重新授权 top-K source，构造 bundle / Rank lexically or by vector inside the authorized scope, reauthorize top-K sources, and build the bundle | 把 metadata filter 当成授权，或让 LLM批准访问 / Treat metadata filters as authorization or ask the LLM to approve access |
| PostgreSQL/pgvector | tenant/source ACL 的权威记录，强制 RLS，事务一致性 / Authoritative tenant/source ACL records, forced RLS, and transactional consistency | 依赖应用层过滤作为唯一隔离 / Depend on application filtering as the only isolation |
| Stage 1A worker | 校验 bundle，生成 evidence-bounded analysis，确保 citation 是 bundle 子集 / Validate the bundle, generate evidence-bounded analysis, and ensure citations are a subset of the bundle | 查询全局语料库、修改 ACL、执行仿真或发布数据 / Query the global corpus, modify ACLs, execute simulations, or release data |
| Model gateway | provider allowlist、固定版本、endpoint、timeout、capacity、provenance / Provider allowlist, pinned versions, endpoints, timeouts, capacity, and provenance | 用户授权或 source selection / User authorization or source selection |
| Model provider | 对收到的最小 prompt 做推理，不保留 prompt/output，也不用于训练 / Infer over the minimal supplied prompt without retaining prompts/outputs or using them for training | 访问 IdP、ACL、数据库、外部工具或未授权 source / Access the IdP, ACLs, database, external tools, or unauthorized sources |
| Audit sink | 完整性保护的最小安全事件 / Integrity-protected minimal security events | 保存原始 evidence、prompt、embedding、reasoning 或完整输出 / Store raw evidence, prompts, embeddings, reasoning, or full outputs |
| KMS/HSM + key registry / 密钥服务 | 包级密钥生成/封装、签名操作、recipient-key 生命周期 / Package-key generation/wrapping, signing operations, and recipient-key lifecycle | 向 MCP、LLM 或 egress relay 暴露私钥 / Expose private keys to MCP, the LLM, or the egress relay |
| Secure release | 接收者核验、人审、加密、签名、密钥封装、撤销与交付证明 / Recipient verification, human approval, encryption, signatures, key wrapping, revocation, and delivery evidence | 自动相信 Stage 1A 输出可以外发 / Automatically assume Stage 1A output is releasable |
| Outbound egress gateway / 外发出口网关 | 唯一公网路由、destination allowlist、TLS/mTLS、幂等 dispatch、回执对账 / Sole Internet route, destination allowlist, TLS/mTLS, idempotent dispatch, and receipt reconciliation | 明文加密根、审批根、解密私钥、通用 forward proxy / Plaintext crypto root, approval root, decryption private keys, or generic forward proxy |

## 5. 请求与数据流 / Request and Data Flow

1. 用户在机构 IdP 完成认证；API gateway 验证 signature、issuer、audience、expiry、MFA/assurance 和 token type。
   The user authenticates with the institutional IdP; the API gateway verifies signature, issuer, audience, expiry, MFA/assurance, and token type.
2. Gateway 查询当前 tenant、project membership、purpose 和 policy version，生成签名且短期有效的 `DelegatedIdentityContext`。客户端字段不能覆盖该上下文。
   The gateway resolves current tenant, project membership, purpose, and policy version, then creates a signed short-lived `DelegatedIdentityContext`. Client fields cannot override it.
3. Retrieval service 先根据身份和策略缩小可访问 source set，再在该范围内执行 lexical/vector ranking。全局搜索后过滤是不允许的。
   The retrieval service first narrows the accessible source set from identity and policy, then performs lexical/vector ranking inside that set. Global search followed by filtering is not allowed.
4. PostgreSQL 使用 `FORCE ROW LEVEL SECURITY` 作为最后一道数据层控制。应用连接角色不能拥有表、不能具有 `BYPASSRLS`，request identity 必须以 transaction-local context 设置并在连接池复用前清除。
   PostgreSQL uses `FORCE ROW LEVEL SECURITY` as the final data-layer control. The application role must not own tables or have `BYPASSRLS`; request identity is set as transaction-local context and cleared before pooled-connection reuse.
5. 每个 top-K source 在进入 prompt 前使用当前 policy version 重新授权；stale ACL、撤销或策略服务不可用时拒绝请求。
   Every top-K source is reauthorized against the current policy version before entering a prompt. Stale ACLs, revocation, or unavailable policy service cause denial.
6. Retrieval service 生成签名、短期有效且大小受限的 `AuthorizedEvidenceBundle`。该 bundle 是 Stage 1A 唯一允许的 evidence 输入。
   The retrieval service creates a signed, short-lived, size-bounded `AuthorizedEvidenceBundle`. This bundle is the only allowed evidence input to Stage 1A.
7. Stage 1A 校验 identity/bundle binding、audience、expiry、policy version、content hash 和 schema，再调用经过预检的 model provider。
   Stage 1A validates identity/bundle binding, audience, expiry, policy version, content hashes, and schema before invoking a preflighted model provider.
8. Stage 1A 保持现有结构、数字和 citation 校验，并要求每个输出 evidence ID 都属于本次 bundle。
   Stage 1A retains its structure, numeric, and citation validation and requires every output evidence ID to belong to the current bundle.
9. 结果写入 tenant-scoped storage；audit 只记录 ID、decision、版本、hash 和状态，不记录科研正文。
   Results are written to tenant-scoped storage; audit records IDs, decisions, versions, hashes, and status, not research content.
10. 需要外发时，用户从 tenant storage 显式选择获批的 raw/derived artifact 或 Stage 1A 输出，进入独立 secure-release 流程完成接收者、人审和密码学操作；该流程不要求输入必须来自 Stage 1A。
    For external release, the user explicitly selects approved raw/derived artifacts or Stage 1A outputs from tenant storage and enters a separate secure-release workflow for recipient verification, human approval, and cryptographic operations; inputs need not originate from Stage 1A.

### 5.1 外发流程与出口规则 / External Release Flow and Egress Rules

1. MCP 仅创建或预览结构化 `ReleaseCandidate`；可信 UI 重新显示 artifact、classification、recipient/key fingerprint、purpose、expiry 和 channel。
   MCP only creates or previews a structured `ReleaseCandidate`; the trusted UI re-displays the artifacts, classification, recipient/key fingerprint, purpose, expiry, and channel.
2. 人工审批和必要的 MFA/双人控制绑定完整 manifest hash、recipient fingerprint、purpose、expiry 和 policy version。字段任何变化都会使审批失效。
   Human approval and required MFA/two-person control bind the complete manifest hash, recipient fingerprint, purpose, expiry, and policy version. Any field change invalidates the approval.
3. Secure-Release Service 调用 KMS/HSM 生成包级密钥、按已核验接收者封装、签名并生成 package hash；明文不进入 egress relay。
   The Secure-Release Service uses KMS/HSM to generate a package key, wrap it for the verified recipient, sign the package, and produce its package hash; plaintext never enters the egress relay.
4. approval、audit intent、package hash 和 idempotency key 在同一事务中持久化；只有拿到 signed audit receipt 后才进入 `delivery_pending`。
   Approval, audit intent, package hash, and the idempotency key are persisted transactionally; the record enters `delivery_pending` only after a signed audit receipt is received.
5. Egress relay 只允许固定目的地、协议、DNS/IP、port 和 mTLS 证书；禁止通用 forward proxy、SSRF、redirect、任意 DNS 解析和 unsolicited inbound。
   The egress relay allows only pinned destinations, protocols, DNS/IPs, ports, and mTLS certificates; generic forward proxies, SSRF, redirects, arbitrary DNS resolution, and unsolicited inbound connections are forbidden.
6. relay 发送后保存精确 receipt outcome；超时进入 `pending_reconciliation`，使用相同 idempotency key 对账，不盲目切换目的地或重复发送。
   After dispatch, the relay records the precise receipt outcome; a timeout enters `pending_reconciliation` and reconciles with the same idempotency key without changing destination or blindly resending.

除 egress relay 外，Stage 1A、retrieval、database、model gateway、MCP 和 audit sink 都应被主机/网络策略显式拒绝出网。普通防火墙规则不等于硬件 data diode；若机构要求真正单向传输，需要单独的网络工程和安全评审。

Except for the egress relay, Stage 1A, retrieval, the database, model gateway, MCP, and the audit sink should be explicitly denied Internet egress by host and network policy. Ordinary firewall rules are not a hardware data diode; a truly unidirectional requirement needs separate network engineering and security review.

## 6. 跨组件契约 / Cross-component Contracts

### 6.1 `DelegatedIdentityContext`

| 字段 / Field | 要求 / Requirement |
| --- | --- |
| `schema_version` | 固定且拒绝未知 major version / Pinned; reject unknown major versions |
| `delegation_id`, `request_id` | 全局唯一，用于重放检测和端到端关联 / Globally unique for replay detection and end-to-end correlation |
| `subject_id`, `tenant_id` | 机构生成的不透明标识，不使用邮箱作为主键 / Institution-derived opaque identifiers; email is not a primary key |
| `issuer`, `audience` | 必须匹配受信任 gateway 和目标服务 / Must match the trusted gateway and target service |
| `authentication_time`, `assurance_level` | 支持敏感操作的重新认证与 MFA gate / Support reauthentication and MFA gates for sensitive actions |
| `authorization_snapshot_id`, `policy_version` | 指向当前服务端策略快照；不能由客户端提供 / Reference the current server-side policy snapshot; never client supplied |
| `purpose_of_use` | 从允许值中选择并进入策略判断 / Selected from allowed values and included in policy evaluation |
| `issued_at`, `expires_at` | 短 TTL；过期、时钟偏差超限或重放时拒绝 / Short TTL; reject expiry, excessive clock skew, or replay |
| `key_id`, `signature` | 由 gateway 签名并支持密钥轮换 / Signed by the gateway with key rotation support |

role、group、clearance 和 project membership 必须从服务端目录/策略读取。若为了性能放入委托 token，它们仍必须由 gateway 签名、带 policy version、短期有效，并在敏感 source 上重新查询当前策略。

Roles, groups, clearance, and project membership are read from server-side directories or policy. If cached in a delegated token for performance, they remain gateway-signed, policy-versioned, short-lived, and are rechecked against current policy for sensitive sources.

### 6.2 `AuthorizedEvidenceBundle`

| 字段 / Field | 要求 / Requirement |
| --- | --- |
| `schema_version`, `bundle_id` | 可版本化且唯一 / Versioned and unique |
| `request_id`, `delegation_id` | 必须绑定到同一次授权请求 / Must bind to the same authorized request |
| `subject_id`, `tenant_id`, `purpose_of_use` | 必须与委托上下文完全一致 / Must exactly match the delegated context |
| `policy_version`, `authorization_decision_ids` | 记录每个 source 的可追踪授权决定 / Record traceable authorization decisions for each source |
| `issued_at`, `expires_at`, `audience` | 短 TTL，仅供目标 Stage 1A worker 使用 / Short TTL and restricted to the intended Stage 1A worker |
| `retrieval` | 只含 tenant-scoped keyed `query_fingerprint`、index version、method 和 bounded `top_k`；禁止使用可字典攻击的裸 hash，audit 不保存原始 query / Contains only a tenant-scoped keyed `query_fingerprint`, index version, method, and bounded `top_k`; raw dictionary-attackable hashes are prohibited and audit does not retain the query |
| `sources[]` | `source_id`、immutable version、content SHA-256、classification、locator namespace 和 decision ID / `source_id`, immutable version, content SHA-256, classification, locator namespace, and decision ID |
| `evidence_items[]` | bundle-local evidence ID、source ID、locator、quoted content 和 chunk SHA-256 / Bundle-local evidence ID, source ID, locator, quoted content, and chunk SHA-256 |
| `key_id`, `signature` | 由 retrieval service 签名；客户端不能增加或替换 evidence / Signed by the retrieval service; the client cannot add or replace evidence |

签名必须覆盖整个 versioned envelope 的唯一 canonical serialization。Stage 1A 必须拒绝：签名或 payload 篡改；未知、错误 signer 或已撤销 key；错误 audience；过期、尚未生效或时钟偏差超限；subject、tenant、request、delegation 或 purpose 替换；未知/降级 schema 或非 canonical/有歧义序列化；source ID/version/content、locator 或 chunk hash 变化；未知 source、重复 ID、policy version 不一致或超出配置上限。输出 citation set 必须是 bundle evidence set 的子集。

The signature covers the entire versioned envelope in one canonical serialization. Stage 1A rejects signature or payload tampering; unknown, wrong-signer, or revoked keys; wrong audience; expired, not-yet-valid, or excessive-skew timestamps; subject, tenant, request, delegation, or purpose substitution; unknown/downgraded schemas or non-canonical/ambiguous serialization; source ID/version/content, locator, or chunk-hash mutation; unknown sources, duplicate IDs, policy-version mismatch, or bundles over configured limits. The output citation set must be a subset of the bundle evidence set.

### 6.3 Synthesis Provider Contract / 综合 Provider 契约

provider 在接触 evidence 前必须提供 immutable capability：

Before receiving evidence, a provider supplies immutable capabilities:

- `provider_id`, `backend`, `model_endpoint`, `model_transport`, `cloud_fallback_configured`
- allowed model aliases and pinned artifact/revision policy / 允许的模型 alias 与固定 artifact/revision 策略
- maximum request size, timeout, concurrency, and structured-output support / 最大请求、超时、并发和 structured-output 支持

调用请求至少绑定 `request_id`、`bundle_id`、prompt version/hash、output schema version、registered model alias、timeout 和最小 evidence payload。返回结果包含 validated analysis、omitted evidence IDs、provider/server version、resolved model、artifact digest、endpoint、transport 和 inference parameters。

An invocation binds at least request ID, bundle ID, prompt version/hash, output-schema version, registered model alias, timeout, and the minimal evidence payload. The result contains validated analysis, omitted evidence IDs, provider/server version, resolved model, artifact digest, endpoint, transport, and inference parameters.

E1 子仓库待审实施中的 Stage 1A provider boundary 只允许 `audit` 和回环 Ollama。它是兼容性基础，不是远端 model gateway；任何网络 provider 都需要独立 Issue、endpoint policy、mTLS/service identity、日志评估和无 fallback 测试。

The Stage 1A provider boundary under review in the E1 child implementation allows only `audit` and loopback Ollama. It is a compatibility foundation, not a remote model gateway. Any network provider requires a separate issue, endpoint policy, mTLS/service identity, logging assessment, and no-fallback tests.

capability preflight 防止误配置 provider 在接触 evidence 前通过，但它不是恶意 Python/process 的沙箱。in-process factory 属于可信代码边界；企业网络 provider 必须放在受控独立进程或服务中，使用最小 service identity、网络 allowlist 和 OS/container isolation。

Capability preflight rejects a misconfigured provider before it receives evidence, but it is not a sandbox for malicious Python or a malicious process. An in-process factory is inside the trusted-code boundary. An enterprise network provider runs in a controlled separate process or service with a least-privilege service identity, network allowlist, and OS/container isolation.

### 6.4 Audit Event / 审计事件

| 字段 / Field | 要求 / Requirement |
| --- | --- |
| `schema_version` | 固定且拒绝未知 major version；canonical event encoding 随版本定义 / Pinned with unknown major versions rejected; the version defines canonical event encoding |
| `event_id`, `occurred_at`, `request_id` | 唯一、UTC、可关联 / Unique, UTC, and correlatable |
| `tenant_id`, `subject_id`, `service_id` | 使用不透明 ID；审计访问本身受限 / Use opaque IDs; audit access is itself restricted |
| `action`, `resource_ids`, `decision` | 记录 ingest/retrieve/analyze/export/release 与 allow/deny/error / Record ingest/retrieve/analyze/export/release and allow/deny/error |
| `reason_code`, `policy_version`, `decision_ids` | 机器可解析，不依赖自由文本解释 / Machine-readable and not dependent on free-text explanations |
| `bundle_id`, `provider_id`, `model_artifact_digest` | 仅在适用时记录 / Record only when applicable |
| `input_hashes`, `output_artifact_hashes` | 用于完整性关联，不替代科学真实性 / Support integrity correlation, not scientific truth |
| `status`, `latency_bucket` | 支持运维但避免高精度 timing oracle / Support operations while avoiding a high-resolution timing oracle |
| `integrity_envelope` | audit sink 分配的 `stream_id`、连续 `sequence`、`previous_event_hash`、canonical `event_hash`、`checkpoint_id`、`key_id`、sink signature 与 signed append/checkpoint receipt / Audit-sink-assigned `stream_id`, contiguous `sequence`, `previous_event_hash`, canonical `event_hash`, `checkpoint_id`, `key_id`, sink signature, and signed append/checkpoint receipt |

`AuditEventBody` 是上表除 `integrity_envelope` 外的 versioned canonical unsigned object。`event_hash` 使用固定 hash context `Industrial_Local_Agent/AuditEventHash/v1` 对 `AuditEventBody` 计算；它不包含自身、signature 或 receipt。sink 使用独立 signature context `Industrial_Local_Agent/AuditEnvelopeSignature/v1` 签名 canonical `{stream_id, sequence, previous_event_hash, event_hash, checkpoint_id}`（不含 signature）。`AuditAppendReceiptBody`/checkpoint body 同样是 versioned canonical unsigned object，其 hash/signature 字段不属于自身输入，因此不存在自引用。

`AuditEventBody` is the versioned canonical unsigned object containing the table fields except `integrity_envelope`. The `event_hash` is computed over `AuditEventBody` with the fixed hash context `Industrial_Local_Agent/AuditEventHash/v1`; it excludes itself, signatures, and receipts. Using the separate signature context `Industrial_Local_Agent/AuditEnvelopeSignature/v1`, the sink signs canonical `{stream_id, sequence, previous_event_hash, event_hash, checkpoint_id}` without the signature. Each `AuditAppendReceiptBody`/checkpoint body is likewise a versioned canonical unsigned object whose hash/signature fields are excluded from its own input, avoiding self-reference.

Audit 不得包含原始 document、prompt、query、embedding、reasoning、token、cookie、认证 header 或完整模型输出。强制 audit 写入失败时，高价值流程默认失败；audit sink 使用 append-only/integrity controls、独立保留策略和最小读取权限。

Audit must not contain raw documents, prompts, queries, embeddings, reasoning, tokens, cookies, authorization headers, or full model outputs. High-value workflows fail closed when mandatory audit writes fail. The audit sink uses append-only/integrity controls, a separate retention policy, and least-privilege read access.

完整性验收必须检测 event 篡改、删除、重排、重复 `event_id`，以及 audit signing key 的轮换、未知与撤销；append-only 声明本身不构成证据。key registry 保留历史公钥、有效期和 compromise/revocation cutoff；verifier 拒绝有效期外或 cutoff 之后的签名，轮换不得删除旧事件所需的验证材料，retroactive compromise 必须触发 incident review。

Integrity acceptance detects event tampering, deletion, reordering, duplicate `event_id` values, and audit-signing-key rotation, unknown keys, and revocation; an append-only claim alone is not evidence. The key registry retains historical public keys, validity intervals, and compromise/revocation cutoffs. The verifier rejects signatures outside their valid interval or after the applicable cutoff, rotation never removes verification material required by old events, and retroactive compromise triggers incident review.

对于不可逆的外发，secure-release 先在同一事务中持久化 approval、recipient、package hash、idempotency key 与 audit intent。状态机固定为 `approved -> audit_committed -> delivery_pending -> delivered | pending_reconciliation | failed`，且 dispatcher 领取前允许原子转入 `cancelled`：只有 audit sink 返回并持久化与 intent hash 绑定的 signed append receipt 后，才能进入 `audit_committed`；delivery dispatcher 只能领取 `delivery_pending` outbox record。外发前 audit 失败或未确认 acknowledgment 必须阻止交付。若 acknowledgment 丢失，使用相同 `event_id` 幂等查询/追加以取回 receipt；若 delivery timeout 发生在可能已经交付之后，则进入 `pending_reconciliation`，使用相同 idempotency key 和接收方 delivery receipt 对账，禁止盲目重试或错误声称未交付。

For irreversible release, secure release first persists approval, recipient, package hash, idempotency key, and audit intent in one transaction. The fixed state machine is `approved -> audit_committed -> delivery_pending -> delivered | pending_reconciliation | failed`, with an atomic transition to `cancelled` allowed before dispatcher claim. Transition to `audit_committed` requires an audit-sink signed append receipt bound to the intent hash to be received and persisted, and the delivery dispatcher can claim only `delivery_pending` outbox records. Audit failure or an unconfirmed acknowledgment before release blocks delivery. If an acknowledgment is lost, the same `event_id` is used to idempotently query/append and recover the receipt. If a delivery timeout occurs after delivery may have happened, the state becomes `pending_reconciliation`; reconciliation uses the same idempotency key and recipient delivery receipt, with no blind retry or false claim of non-delivery.

content hash、source ID 和 query fingerprint 本身也可能泄露关联关系，必须按受限 metadata 保护。低熵或可猜测内容使用 tenant-scoped keyed HMAC，不把普通 SHA-256 当作匿名化。

Content hashes, source IDs, and query fingerprints can themselves leak relationships and are protected as restricted metadata. Low-entropy or guessable content uses tenant-scoped keyed HMAC; ordinary SHA-256 is not anonymization.

### 6.5 Secure-Release Contract / 安全发布契约

本节只定义 Stage 2.0 协议基线，不表示传输已实现。研究者显式选择一个 `ReleaseCandidate`；系统不得默认包含整个 Stage 1A run、RAG corpus、prompt、cache、凭据或未选择的 source。candidate 可以包含原始实验 artifact、derived analysis 或 Stage 1A 输出，但每项都必须使用 immutable ID/version/hash、kind、服务端权威 classification、size 和 media type 单独列入 manifest。服务端根据机构分类序计算最严格的 aggregate classification；研究者、客户端和 Agent 均不能提供或降低它。derived/Agent 输出不会自动降低原数据分类，也不构成外发批准。

This section defines only the Stage 2.0 protocol baseline and does not mean transfer is implemented. A researcher explicitly selects a `ReleaseCandidate`; the system never implicitly includes an entire Stage 1A run, RAG corpus, prompt, cache, credential, or unselected source. A candidate may contain raw experimental artifacts, derived analysis, or Stage 1A output, but each item is individually listed in the manifest with immutable ID/version/hash, kind, server-authoritative classification, size, and media type. The server derives the strictest aggregate classification under institutional ordering; the researcher, client, and agent cannot supply or lower it. Derived or agent output does not automatically lower source classification or constitute release approval.

| 对象 / Object | 必要内容 / Required content |
| --- | --- |
| `ReleaseCandidate` | `release_id`、tenant/project、creator、purpose、artifact manifest、server-derived aggregate classification、recipient IDs 与公钥 fingerprints、policy/approval version、expiry 和 idempotency key / `release_id`, tenant/project, creator, purpose, artifact manifest, server-derived aggregate classification, recipient IDs and public-key fingerprints, policy/approval version, expiry, and idempotency key |
| Approval record / 审批记录 | 绑定完整 manifest hash、recipient/key fingerprints、purpose、expiry、approver identity、decision、time 与 signature；candidate 任一字段变化都使审批失效 / Bound to the complete manifest hash, recipient/key fingerprints, purpose, expiry, approver identity, decision, time, and signature; any candidate change invalidates approval |
| `SecureReleasePackage` | versioned manifest、aggregate classification、policy/approval version、ciphertext artifact hashes、approved algorithm suite、每个 recipient 的 wrapped content key、sender key ID/signature、package hash 与 expiry；不包含 private/decryption key / Versioned manifest, aggregate classification, policy/approval version, ciphertext artifact hashes, approved algorithm suite, a wrapped content key for each recipient, sender key ID/signature, package hash, and expiry; never a private/decryption key |
| Researcher instruction / 研究者说明 | 使用获批工具验证 sender signature/package hash、确认 recipient fingerprint、获取/unwrap key、解密和报告失败的步骤；不包含 secret 或绕过审批的命令 / Steps using approved tooling to verify the sender signature/package hash, confirm the recipient fingerprint, obtain/unwrap the key, decrypt, and report failures; no secrets or commands that bypass approval |
| Delivery receipt / 交付回执 | 由受信任 transport/recipient signer 认证绑定 `receipt_id`、`release_id`、recipient ID/key fingerprint、package hash、idempotency key、channel、outcome、time、signer ID、receipt key ID/signature / Authentically binds `receipt_id`, `release_id`, recipient ID/key fingerprint, package hash, idempotency key, channel, outcome, time, signer ID, and receipt key ID/signature through a trusted transport/recipient signer |

`SecureReleasePackageBody` 是 versioned canonical unsigned object，包含 schema/version、canonical manifest、aggregate classification、policy/approval version、algorithm suite、wrapped-key metadata、expiry 和按 manifest 排序的 ciphertext hashes，但不包含 `package_hash`、sender signature 或任何 delivery receipt。`package_hash` 使用固定 hash context `Industrial_Local_Agent/SecureReleasePackageHash/v1` 对该 body 计算；sender 使用独立 signature context `Industrial_Local_Agent/SecureReleaseSignature/v1` 签名 canonical `{release_id, package_hash, policy_version, approval_version}`。验证器必须从 ciphertext bytes 重新计算各 artifact hash。任何字段或 artifact 变化都必须使验证失败；验证器先校验 schema、size/count limits、signature 和 hashes，再尝试 unwrap/decrypt。

`SecureReleasePackageBody` is a versioned canonical unsigned object containing schema/version, canonical manifest, aggregate classification, policy/approval version, algorithm suite, wrapped-key metadata, expiry, and manifest-ordered ciphertext hashes, but excluding `package_hash`, sender signature, and every delivery receipt. The `package_hash` is computed over this body with the fixed hash context `Industrial_Local_Agent/SecureReleasePackageHash/v1`; using the separate signature context `Industrial_Local_Agent/SecureReleaseSignature/v1`, the sender signs canonical `{release_id, package_hash, policy_version, approval_version}`. The verifier recomputes each artifact hash from the ciphertext bytes. Any field or artifact mutation must fail verification; the verifier checks schema, size/count limits, signature, and hashes before attempting unwrap or decryption.

`DeliveryReceiptBody` 是 versioned canonical unsigned object，包含 `receipt_id`、`release_id`、recipient ID/key fingerprint、`package_hash`、`idempotency_key`、channel、outcome、occurred time、signer ID 和 receipt `key_id`，不包含 `receipt_hash` 或 signature。`receipt_hash` 使用 `Industrial_Local_Agent/DeliveryReceiptHash/v1` 计算，signer 使用 `Industrial_Local_Agent/DeliveryReceiptSignature/v1` 签名 canonical `{receipt_id, receipt_hash, outcome}`；验证时同时检查 signer/key trust、有效期、撤销和重放。

`DeliveryReceiptBody` is a versioned canonical unsigned object containing `receipt_id`, `release_id`, recipient ID/key fingerprint, `package_hash`, `idempotency_key`, channel, outcome, occurrence time, signer ID, and receipt `key_id`, while excluding `receipt_hash` and signature. The `receipt_hash` uses `Industrial_Local_Agent/DeliveryReceiptHash/v1`, and the signer uses `Industrial_Local_Agent/DeliveryReceiptSignature/v1` to sign canonical `{receipt_id, receipt_hash, outcome}`; verification also checks signer/key trust, validity, revocation, and replay.

安全发布使用经过维护的密码学库和机构批准算法，不自制 encryption/signature primitive。应用层 package encryption/signature 必须由受保护的 Secure-Release Service 完成，并由 KMS/HSM 托管或执行密钥操作；DMZ egress relay 只处理 encrypted + signed package。传输 channel 是独立配置，TLS/mTLS 不能替代包级加密；package 在离开系统边界前已经加密并签名。链上记录不是解密所需条件，也不能代替 recipient verification、key custody、access policy 或 delivery receipt。

Secure release uses maintained cryptographic libraries and institution-approved algorithms, never custom encryption or signature primitives. Application-level package encryption and signing happen inside the protected Secure-Release Service, with key operations held or performed by KMS/HSM; the DMZ egress relay handles only encrypted and signed packages. The transport channel is configured separately, and TLS/mTLS cannot replace package encryption; the package is encrypted and signed before leaving the system boundary. An on-chain record is not required for decryption and cannot replace recipient verification, key custody, access policy, or a delivery receipt.

receipt 的 `outcome` 只能使用明确层级，例如 `accepted_by_transport`、`downloaded`、`key_unwrapped` 或 `decryption_acknowledged_by_recipient`，并由能证明该层级的主体签名。`delivered` 只表示 deployment policy 配置的 receipt 层级，UI/audit 必须同时显示精确 `outcome`。transport 接收或下载回执不能被解释为接收方已经 unwrap key 或成功解密；没有可信回执时保持 `pending_reconciliation`。

The receipt `outcome` uses explicit levels such as `accepted_by_transport`, `downloaded`, `key_unwrapped`, or `decryption_acknowledged_by_recipient`, signed by an actor able to attest to that level. `delivered` means only the receipt level configured by deployment policy, and the UI/audit always displays the exact `outcome`. A transport-acceptance or download receipt must not be interpreted as recipient key unwrap or successful decryption; without a trustworthy receipt, the release remains `pending_reconciliation`.

撤销能力必须按时间点限定：dispatcher 原子领取前可取消并阻止发送；若 key unwrap 依赖在线 KMS，unwrap 前可拒绝；一旦接收方已获得 content key、离线 package 可独立解密，或明文已经产生，系统无法保证撤回。expiry/revocation 只能阻止未来在线访问，不能删除接收方已有副本；此时只能记录 incident、通知接收方并按制度补救。区块链不能改变这一残余风险。

Revocation is explicitly time-bounded: delivery can be cancelled before atomic dispatcher claim; online KMS-backed key unwrap can be denied before unwrap; once a recipient has obtained the content key, can independently decrypt an offline package, or has produced plaintext, recall cannot be guaranteed. Expiry and revocation can stop future online access but cannot delete an existing recipient copy; the remaining controls are incident recording, recipient notification, and institutional remediation. Blockchain does not change this residual risk.

## 7. RAG 与授权规则 / RAG and Authorization Rules

- 未认证请求返回 `401`；已认证但无权请求返回 `403`，或在 object-existence 敏感场景返回一致的 `404`。
  Unauthenticated requests return `401`; authenticated but unauthorized requests return `403`, or a consistent `404` when object existence is sensitive.
- RBAC 表达职责，ABAC 表达 tenant、project、classification、purpose、ownership 和 embargo；两者都由服务端策略执行。
  RBAC expresses duties; ABAC expresses tenant, project, classification, purpose, ownership, and embargo. Both are enforced by server-side policy.
- pgvector metadata filter 只是性能优化。即使删除 filter，PostgreSQL RLS 也必须返回零条跨 tenant/source 记录。
  A pgvector metadata filter is only a performance optimization. Removing it must still yield zero cross-tenant/source rows because PostgreSQL RLS remains authoritative.
- embedding 与原 source 具有同等敏感级别。不同 tenant 之间不得复用 embedding、semantic cache、KV cache、retrieval result 或 prompt cache。
  Embeddings carry the same sensitivity as their source. Embeddings, semantic caches, KV caches, retrieval results, and prompt caches are not shared across tenants.
- ACL 撤销后，新请求必须立即失败；旧 bundle 依靠短 TTL 失效。极高价值 source 可要求每次 Stage 1A 使用前在线重新授权。
  New requests fail immediately after ACL revocation; old bundles expire through short TTLs. Very high-value sources may require online reauthorization before each Stage 1A use.
- 检索文档中的 prompt injection 始终是 quoted evidence，不能改变权限、调用工具、选择其他 source 或覆盖系统规则。
  Prompt injection in retrieved documents remains quoted evidence and cannot change permissions, call tools, select other sources, or override system rules.

## 8. 威胁模型 / Threat Model

受保护资产包括：原始科研材料、derived text、source/hash metadata、identity 与 ACL、embedding、模型 prompt/output、API/签名密钥、audit 和安全发布包。主要不可信输入包括浏览器请求、上传文件、检索文档、Issue/评论内容和模型输出。

Protected assets include raw research material, derived text, source/hash metadata, identity and ACLs, embeddings, model prompts/outputs, API/signing keys, audit records, and secure-release packages. Primary untrusted inputs include browser requests, uploaded files, retrieved documents, issue/comment content, and model output.

| 威胁 / Threat | 必须控制 / Required control | 验证证据 / Verification evidence |
| --- | --- | --- |
| 客户端伪造 identity/tenant/role / Client forges identity, tenant, or role | Gateway-derived signed context；忽略客户端 claims / Gateway-derived signed context; ignore client claims | Tamper、wrong issuer/audience、expiry、replay tests / 篡改、错误 issuer/audience、过期和重放测试 |
| Confused deputy / 混淆代理 | audience/purpose/resource binding、短 TTL、service identity / audience, purpose, resource binding, short TTL, service identity | 跨 audience 与跨 purpose 测试 / Cross-audience and cross-purpose tests |
| 跨 tenant 检索 / Cross-tenant retrieval | RBAC+ABAC、forced RLS、非 owner DB role、source reauthorization / RBAC+ABAC, forced RLS, non-owner DB role, source reauthorization | 删除 metadata filter 后仍为零结果 / Zero results after removing metadata filters |
| 同 tenant 跨 project/owner/source 越权 / Same-tenant cross-project/owner/source access | project membership、ownership、source ACL、explicit-share grant 与 forced RLS / Project membership, ownership, source ACLs, explicit-share grants, and forced RLS | `retrieve/list/read/export` allow/deny/share/revoke matrix / `retrieve/list/read/export` allow/deny/share/revoke matrix |
| Evidence bundle 伪造或替换 / Evidence-bundle forgery or substitution | Canonical signed envelope、trusted key registry、identity/request/audience/time/source binding / Canonical signed envelope, trusted key registry, and identity/request/audience/time/source binding | Tamper、unknown/revoked key、substitution、schema downgrade 与 content mutation tests / 篡改、未知/撤销 key、替换、schema downgrade 与内容变更测试 |
| 连接池身份残留 / Pooled identity leakage | transaction-local identity、rollback/reset、pool checkout guard / Transaction-local identity, rollback/reset, pool checkout guard | 并发交错 tenant 测试 / Interleaved concurrent-tenant tests |
| SQL 注入或不安全 query composition / SQL injection or unsafe query composition | parameterized SQL、read-minimal DB role、forced RLS、bounded query API / Parameterized SQL, read-minimal DB role, forced RLS, and a bounded query API | injection fixtures、multi-statement refusal、RLS bypass tests / 注入 fixture、多语句拒绝和 RLS 绕过测试 |
| Stale ACL/index/cache / 过期 ACL、索引或缓存 | policy version、short TTL、revocation event、tenant-scoped cache key / Policy version, short TTL, revocation event, tenant-scoped cache key | 撤销与检索竞态测试 / Revocation-retrieval race tests |
| Prompt injection / 提示注入 | quoted evidence、无工具权限、citation subset、固定 system contract / Quoted evidence, no tool privileges, citation subset, fixed system contract | 恶意 source 试图提权或泄露其他 source / Malicious source attempts privilege escalation or source leakage |
| Model endpoint SSRF/redirect/proxy / 模型 endpoint SSRF、重定向或代理 | 注册 endpoint、DNS/IP policy、禁 redirect/proxy、mTLS、preflight / Registered endpoint, DNS/IP policy, no redirect/proxy, mTLS, preflight | SSRF、DNS rebinding、redirect 和 proxy tests / SSRF、DNS rebinding、重定向和代理测试 |
| 模型供应链或自定义远程代码 / Model supply chain or custom remote code | 固定 repository commit、model digest、container digest，人工审查 custom code，隔离加载且禁止自动漂移 / Pin repository commit, model digest, and container digest; review custom code; isolate loading and prohibit automatic drift | digest mismatch、tampered artifact 和 unreviewed-code refusal tests / digest 不匹配、篡改 artifact 和未审代码拒绝测试 |
| Silent cloud fallback / 静默云回退 | explicit provider allowlist、fail closed、egress firewall / Explicit provider allowlist, fail closed, egress firewall | provider outage 不产生第二次外部调用 / Provider outage causes no second external call |
| 日志与 cache 泄露 / Log and cache leakage | content-free audit、redaction、tenant isolation、bounded retention / Content-free audit, redaction, tenant isolation, bounded retention | 扫描 log/export/cache 不含正文或 token / Scan logs, exports, and caches for content or tokens |
| Prompt retention 或跨 tenant 训练泄露 / Prompt retention or cross-tenant training leakage | 禁止用请求训练、禁持久化 prompt/output、tenant-specific adapter/checkpoint isolation / Prohibit request training and prompt/output persistence; isolate tenant-specific adapters/checkpoints | retention scan、restart inspection、cross-tenant canary tests / 保留扫描、重启检查和跨 tenant canary 测试 |
| Object-existence timing oracle / 对象存在性 timing oracle | 一致的 403/404 policy、coarse latency metric、bounded padding where justified / Consistent 403/404 policy, coarse latency metrics, and bounded padding where justified | authorized/unauthorized timing distribution tests / 授权与未授权 timing distribution 测试 |
| 恶意或超大文件 / Malicious or oversized files | type/size/page limits、sandboxed parsing、timeouts、resource quotas / Type/size/page limits, sandboxed parsing, timeouts, resource quotas | malformed PDF、zip bomb、oversized top-K tests / 畸形 PDF、zip bomb 和超大 top-K 测试 |
| Audit unavailable or corrupted / 审计不可用或损坏 | mandatory-event fail closed、append-only integrity、key lifecycle、bounded buffer、operator alert / Mandatory-event fail closed, append-only integrity, key lifecycle, bounded buffer, and operator alert | Failure injection plus tamper/delete/reorder/duplicate/key-rotation tests / 失败注入及篡改、删除、重排、重复、密钥轮换测试 |
| 外发与审计结果不一致 / Release and audit outcome diverge | Pre-delivery audit intent、transactional outbox、idempotent delivery、receipt reconciliation / 外发前 audit intent、transactional outbox、幂等交付与 receipt 对账 | Pre-release audit failure 和 post-timeout ambiguous-outcome tests / 外发前审计失败与超时后不确定结果测试 |
| 未授权直接出网 / Unauthorized direct egress | Host/NACL default-deny；只有 egress relay 有公网路由；固定 destination/protocol/port / Host/NACL default-deny; only the egress relay has an Internet route; pin destination/protocol/port | Stage 1A、MCP、DB、model 和 retrieval 的 direct-egress packet tests / Direct-egress packet tests for Stage 1A, MCP, DB, model, and retrieval |
| MCP prompt injection 或工具越权 / MCP prompt injection or tool abuse | Typed-tool allowlist；无 approve/send/shell/filesystem/HTTP/key access；trusted UI/MFA / Typed-tool allowlist; no approve/send/shell/filesystem/HTTP/key access; trusted UI/MFA | Malicious intent、destination substitution、classification change 和 tool-abuse tests / Malicious-intent, destination-substitution, classification-change, and tool-abuse tests |
| Egress relay SSRF、DNS 绕过或重放 / Egress SSRF, DNS bypass, or replay | Pinned DNS/IP/port/certificate、no redirect/open proxy、package hash/expiry/idempotency validation / Pin DNS/IP/port/certificate, disable redirects/open proxies, validate package hash/expiry/idempotency | SSRF、DNS rebinding、redirect、wrong recipient/key、replay 和 duplicate-dispatch tests / SSRF, DNS-rebinding, redirect, wrong-recipient/key, replay, and duplicate-dispatch tests |
| 外发 relay 或传输端点看到明文 / Plaintext visible to relay or transport endpoint | Package encryption/signing before boundary、KMS/HSM key custody、content-free logs / Encrypt and sign before the boundary, keep keys in KMS/HSM, and use content-free logs | Packet capture、relay storage、debug-log 和 key-isolation scans / Packet-capture, relay-storage, debug-log, and key-isolation scans |
| Host administrator compromise / 主机管理员失陷 | hardened host、service isolation、key separation、backups、monitoring / Hardened host, service isolation, key separation, backups, monitoring | 属于残余风险，单机不能消除 / Residual risk not eliminated by one host |
| 错误接收者或外发 / Wrong recipient or release | separate approval、recipient key verification、encryption、signature、revocation / Separate approval, recipient-key verification, encryption, signature, revocation | 双人审批与错误 key/recipient tests / Two-person approval and wrong-key/recipient tests |

## 9. 数据生命周期 / Data Lifecycle

1. **分类 / Classify**：在 ingest 前标记 public、internal、restricted 或 high-value；未知分类按更高等级处理。
   **Classify**: label data public, internal, restricted, or high-value before ingest; unknown classification is treated as the higher class.
2. **最小化 / Minimize**：只保存业务需要的 source、chunk 和 metadata；prompt 只携带本次授权 bundle。
   **Minimize**: retain only required sources, chunks, and metadata; prompts contain only the current authorized bundle.
3. **隔离 / Isolate**：tenant-scoped storage、RLS、service identities、separate encryption context；高价值 tenant 不共享 cache。
   **Isolate**: tenant-scoped storage, RLS, service identities, and separate encryption contexts; high-value tenants do not share caches.
4. **保护 / Protect**：传输使用 TLS/mTLS，存储与备份使用机构密钥管理；应用和模型进程不持有长期用户凭据。
   **Protect**: use TLS/mTLS in transit and institutional key management for storage and backups; application and model processes hold no long-lived user credentials.
5. **保留与删除 / Retain and delete**：按分类定义 retention、legal hold、backup expiry 和 deletion verification。普通删除不等于 SSD/备份安全擦除。
   **Retain and delete**: define retention, legal hold, backup expiry, and deletion verification by class. Ordinary deletion is not secure erasure from SSDs or backups.
6. **发布 / Release**：derived output 仍可能敏感；只有 secure-release 组件和人审可以完成外发。
   **Release**: derived output may remain sensitive; only the secure-release component plus human review can authorize external release.

区块链不是此生命周期的前置条件，原始数据永不写链。只有在加密、签名、撤销和普通 append-only audit 仍留下明确的跨机构多方记账问题时，才单独评估 hash/timestamp/authorization event 上链。

Blockchain is not a prerequisite for this lifecycle, and raw data is never written on-chain. Hashes, timestamps, or authorization events are evaluated for a ledger only if encryption, signatures, revocation, and ordinary append-only audit leave a concrete cross-institution multiparty accounting problem.

## 10. Stage 2 与 Enterprise E2-E4 验收门槛 / Stage 2 and Enterprise E2-E4 Acceptance Gates

### Stage 2.0: Secure-Release Protocol / 安全发布协议

- researcher 只显式选择 manifest items，raw/derived/Stage 1A kind 与 classification 保持可见；whole-run、corpus、prompt、cache 和 credential 不会被隐式加入 / The researcher explicitly selects manifest items; raw/derived/Stage 1A kind and classification remain visible, while whole-run data, corpora, prompts, caches, and credentials are never implicitly included
- candidate/recipient/key/purpose/expiry 任一变化都会使旧 approval 失效 / Any candidate, recipient, key, purpose, or expiry change invalidates the old approval
- synthetic test vectors 覆盖 package round trip、wrong recipient/key、signature/hash/ciphertext tamper、expired policy 与 partial/truncated package / Synthetic test vectors cover package round trips, wrong recipient/key, signature/hash/ciphertext tampering, expired policy, and partial/truncated packages
- signed receipt 必须绑定 release、recipient/key、package hash、idempotency key 与 outcome；错误或重放 receipt 被拒绝 / The signed receipt binds release, recipient/key, package hash, idempotency key, and outcome; wrong or replayed receipts are rejected
- egress vertical slice 必须证明只有 relay 能够出网、relay 只接受 audit-committed encrypted package，且错误目的地、SSRF、redirect、DNS 绕过、wrong key、重放和明文日志均 fail closed / The egress vertical slice must prove that only the relay can connect externally, the relay accepts only audit-committed encrypted packages, and wrong destinations, SSRF, redirects, DNS bypass, wrong keys, replay, and plaintext logs fail closed
- 验收报告分别陈述 pre-delivery cancel、pre-unwrap revoke 与 post-key/plaintext 不可撤回的结果，不声称绝对撤销 / Acceptance evidence separately states pre-delivery cancellation, pre-unwrap revocation, and post-key/plaintext non-recall; it never claims absolute revocation

### E2: Identity-aware Retrieval / 身份感知检索

当前分支已经实现 Issue #10 的 synthetic model-free vertical slice，验证 synthetic token、服务端 tenant mapping、forced-scope SQLite 检索、source reauthorization、签名 `AuthorizedEvidenceBundle`、replay/cache isolation、bundle negative matrix 和 content-free audit hash chain。它是契约证据，不是 OIDC、PostgreSQL 或生产多租户服务。

The current branch implements the Issue #10 synthetic model-free vertical slice, covering synthetic tokens, server-side tenant mapping, forced-scope SQLite retrieval, source reauthorization, signed `AuthorizedEvidenceBundle`, replay/cache isolation, the bundle-negative matrix, and a content-free audit hash chain. It is contract evidence, not OIDC, PostgreSQL, or a production multi-tenant service.

The following are the remaining production E2 exit gates:

以下是生产 E2 尚未满足的退出门槛：

- valid、missing、expired、forged、wrong issuer/audience token 行为经过测试 / Test valid, missing, expired, forged, and wrong-issuer/audience tokens
- 两个 tenant 间的 ingest/list/read/retrieve/delete/export 全隔离 / Isolate ingest/list/read/retrieve/delete/export across two tenants
- 同一 tenant 内不同 user、project、owner 和 source ACL 的 `retrieve/list/read/export` allow、deny、explicit-share、revoke 矩阵通过 / Pass the `retrieve/list/read/export` allow, deny, explicit-share, and revoke matrix across users, projects, owners, and source ACLs within one tenant
- 未授权 `list/retrieve` 不泄露对象存在性，未授权 `read/export` 按对象敏感策略返回一致的 `403` 或 `404` / Unauthorized `list/retrieve` does not reveal object existence, and unauthorized `read/export` returns a consistent `403` or `404` under the object-sensitivity policy
- 删除 vector metadata filter 后 forced RLS 仍阻止跨 tenant 行 / Forced RLS still blocks cross-tenant rows after vector metadata filters are removed
- DB owner/`BYPASSRLS`、SQL injection、cross-tenant join 和 pooled request identity 残留测试通过 / Pass DB-owner/`BYPASSRLS`, SQL-injection, cross-tenant-join, and pooled-request-identity leakage tests
- top-K source reauthorization、ACL revocation、cache invalidation 和 policy outage fail-closed / Fail closed for top-K reauthorization, ACL revocation, cache invalidation, and policy outage
- log、embedding 和 cache 隔离测试通过 / Pass log, embedding, and cache-isolation tests
- `AuthorizedEvidenceBundle` 拒绝签名篡改、未知/错误 signer/撤销 key、错误 audience/time、subject/tenant/request/delegation/purpose 替换、schema downgrade/非 canonical serialization 和 source/content mutation / `AuthorizedEvidenceBundle` rejects signature tampering, unknown/wrong-signer/revoked keys, wrong audience/time, subject/tenant/request/delegation/purpose substitution, schema downgrade/non-canonical serialization, and source/content mutation

### E3: Controlled Model Gateway / 受控模型 Gateway

- 只允许 registered provider、pinned model/revision 和 approved endpoint / Allow only registered providers, pinned models/revisions, and approved endpoints
- model repository、custom serving code、model artifact 与 container image 均固定 digest/commit 并通过供应链审查 / Pin and supply-chain review the model repository, custom serving code, model artifact, and container image by digest/commit
- mTLS/service identity、timeout、size/concurrency limit、proxy/redirect 禁用经过测试 / Test mTLS/service identity, timeouts, size/concurrency limits, and disabled proxies/redirects
- provider 失败时不回退，manifest 记录真实 endpoint/transport/model digest / No fallback on provider failure; manifests record actual endpoint, transport, and model digest
- prompt/output/content 不进入 provider 或 gateway debug log / Prompts, outputs, and content do not enter provider or gateway debug logs
- provider 不保留请求、不用 prompt/output 训练，tenant-specific adapter/checkpoint 不跨 tenant 复用 / Providers retain no requests and train on no prompts/outputs; tenant-specific adapters/checkpoints are not reused across tenants

### E4: Enterprise Integration / 企业集成

- 只有有效 `AuthorizedEvidenceBundle` 能进入 Stage 1A / Only a valid `AuthorizedEvidenceBundle` can enter Stage 1A
- 每个 citation 都属于本次 bundle，且 bundle 绑定 request/identity/policy / Every citation belongs to the bundle, which is bound to request, identity, and policy
- 两个并发 tenant 的 run/list/read/export 不互相可见；同一 tenant 内不同 project/owner/source 也通过 allow、deny、explicit-share 与 revoke 矩阵 / Two concurrent tenants cannot observe each other through run/list/read/export; different projects, owners, and sources within one tenant also pass the allow, deny, explicit-share, and revoke matrix
- Stage 1A integration 重跑全部 bundle 负向签名、key lifecycle、binding、schema/serialization 和 source mutation tests / Stage 1A integration reruns the complete negative bundle-signature, key-lifecycle, binding, schema/serialization, and source-mutation tests
- secure-release handoff 保持独立审批和密码学边界 / Secure-release handoff retains separate approval and cryptographic boundaries
- audit verifier 使用 integrity envelope 检出 event 篡改、删除、重排、重复 ID，并验证 signing key 轮换、未知/撤销 key、有效期与 compromise cutoff / Using the integrity envelope, the audit verifier detects event tampering, deletion, reordering, and duplicate IDs and validates signing-key rotation, unknown/revoked keys, validity intervals, and compromise cutoffs
- 外发前 audit failure 或 acknowledgment 丢失阻止 dispatcher；`approved -> audit_committed -> delivery_pending` gate 和 transactional outbox/幂等状态机通过重复、timeout 与 `pending_reconciliation` 对账测试 / Pre-release audit failure or a lost acknowledgment blocks the dispatcher; the `approved -> audit_committed -> delivery_pending` gate and transactional outbox/idempotent state machine pass duplicate, timeout, and `pending_reconciliation` reconciliation tests
- 完成容量、恢复、监控、安全和隐私评审后，才能把 pilot 描述为 production / Capacity, recovery, monitoring, security, and privacy reviews are required before calling a pilot production

## 11. Kimi K3 与模型选择 / Kimi K3 and Model Selection

Kimi K3 可以作为未来集群 model gateway 后面的候选 provider，但不能作为当前 RTX 4070 Ti 工作站的默认本地模型。Moonshot AI 在 2026-07-29 的官方资料列出约 2.8T 总参数、104B 激活参数；官方 Hugging Face checkpoint index 约为 1.561 TB。它是采用自定义 Kimi K3 License 的 open-weight 模型，部署流程还要求审查并固定自定义 serving code；不应在未做许可证、远程代码、容量、正确性和安全评审时简称为可直接企业部署的“开源模型”。

Kimi K3 may be evaluated later as a provider behind a cluster model gateway, but it cannot be the default local model on the current RTX 4070 Ti workstation. Moonshot AI official material available on 2026-07-29 lists approximately 2.8T total parameters and 104B active parameters; the official Hugging Face checkpoint index is approximately 1.561 TB. It is an open-weight model under the custom Kimi K3 License, and deployment also requires review and pinning of custom serving code. It should not be described as directly enterprise-deployable open source without license, remote-code, capacity, correctness, and security review.

- Official repository / 官方仓库: <https://github.com/MoonshotAI/Kimi-K3>
- Official model card / 官方模型卡: <https://huggingface.co/moonshotai/Kimi-K3>
- Official license / 官方许可证: <https://huggingface.co/moonshotai/Kimi-K3/blob/main/LICENSE>

单服务器可以为内网多人提供较小模型，只要 GPU/内存、并发和延迟经过容量测试。Kimi K3 需要 cluster-class serving 方案，不能通过 RAG 减少模型权重占用。托管 API 会让数据离开本地边界，不能用于高价值数据，除非另有明确的数据传输、接收方、合同、预算和安全授权。

A single server can serve smaller models to multiple intranet users when GPU/memory capacity, concurrency, and latency are tested. Kimi K3 requires a cluster-class serving design; RAG does not reduce model-weight memory. A hosted API moves data outside the local boundary and cannot handle high-value data without separate authorization covering transfer, recipient, contract, budget, and security.

## 12. 推进、回滚与待决策项 / Rollout, Rollback, and Open Decisions

推进顺序固定为：public/synthetic test -> isolated security test -> approved low-sensitivity pilot -> formal review -> bounded production。任何阶段发现跨 tenant 泄露、日志正文、错误授权、无审计或云回退，都停止 rollout 并撤销 gateway route/service identity。

The fixed rollout order is public/synthetic test -> isolated security test -> approved low-sensitivity pilot -> formal review -> bounded production. Any cross-tenant leak, content-bearing log, incorrect authorization, missing audit, or cloud fallback stops rollout and revokes the gateway route/service identity.

E0 只有文档与接口决策，回滚方式是普通 Git revert；它不迁移数据、不创建服务、不改变 firewall，也不产生云成本。Enterprise、安全发布与 Tidy3D 保持独立组件和 Issue 边界，但当前实施顺序是 E1 审查 -> E2 identity/authorized-retrieval vertical slice -> Stage 2.0 协议及其独立 implementation slices -> Tidy3D Stage 1B adapter；这不是多条路线同时实施。E3/E4 在机构 provider、容量和运维边界确定后另行排期。后续 E2-E4 与 secure-release 必须各自拥有 canonical Issue、migration/rollback plan、synthetic fixtures 和保留的验收证据。

E0 contains documentation and interface decisions only and can be rolled back with a normal Git revert. It migrates no data, creates no services, changes no firewall, and incurs no cloud cost. Enterprise, secure release, and Tidy3D retain separate component and issue boundaries, but the current implementation order is E1 review -> E2 identity/authorized-retrieval vertical slice -> the Stage 2.0 protocol and its independent implementation slices -> Tidy3D Stage 1B adapter; multiple tracks are not being implemented concurrently. E3/E4 are scheduled separately after institutional provider, capacity, and operational boundaries are known. Each later E2-E4 and secure-release change requires its own canonical issue, migration/rollback plan, synthetic fixtures, and retained acceptance evidence.

该箭头是本项目基于风险和有限资源的排期，不是架构依赖声明：secure-release contract 不需要调用 E2 retrieval，但本项目在开始 Stage 2 实现前先验收 E2。

The arrow is this project's risk- and resource-based schedule, not an architectural dependency statement: the secure-release contract does not call E2 retrieval, but this project accepts E2 before starting Stage 2 implementation.

实施前仍需由项目所有者和机构回答：

The project owner and institution must still decide before implementation:

- 机构 IdP/OIDC issuer、MFA 与 service identity 标准 / Institutional IdP/OIDC issuer, MFA, and service-identity standards
- tenant 是 lab、project 还是 institution，以及跨 project sharing 的审批模型 / Whether a tenant is a lab, project, or institution, and the approval model for cross-project sharing
- 数据分类、retention、backup、RTO/RPO、legal hold 和删除要求 / Data classification, retention, backup, RTO/RPO, legal hold, and deletion requirements
- 授权 policy owner、紧急访问、撤销 SLA 和 audit reader / Authorization policy owner, emergency access, revocation SLA, and audit readers
- 单机 pilot 的并发/延迟目标，以及何时必须拆分数据库或 GPU 节点 / Single-host pilot concurrency/latency targets and when database or GPU nodes must separate
- 可注册模型、许可证、模型评估、更新 cadence 和供应链固定策略 / Registrable models, licenses, model evaluation, update cadence, and supply-chain pinning
- secure-release 的接收者验证、密钥托管、审批人和跨机构法律要求 / Secure-release recipient verification, key custody, approvers, and cross-institution legal requirements
