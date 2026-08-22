# Enterprise E2 Implementation / 企业 E2 实施说明

## Status / 状态

E2 has a model-free, synthetic-data vertical slice merged into parent `main`
under Issue [#10](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/10).
Its CLI and loopback browser adapters provide executable presentation evidence
for the authorization and evidence-bundle contracts; they are not production
enterprise services.

E2 已经通过父仓库 Issue [#10](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/10)
把一个不调用模型、只使用合成数据的纵向切片合并到 `main`。命令行和回环浏览器
adapter 为授权和 evidence bundle 契约提供可执行演示证据，但都不是生产企业服务。

| Boundary / 边界 | Current implementation / 当前实现 | Production follow-up / 生产后续 |
| --- | --- | --- |
| Identity / 身份 | Synthetic signed token authority and verifier | Institutional OIDC/SSO, key discovery and rotation |
| Delegation / 委托 | Server-derived tenant and signed `DelegatedIdentityContext` | Gateway service identity, mTLS and institutional policy |
| Policy / 策略 | In-memory two-tenant allow/share/revoke policy store | Durable RBAC+ABAC policy service with an identified owner |
| Retrieval / 检索 | SQLite forced-scope adapter with tenant predicate | PostgreSQL `FORCE ROW LEVEL SECURITY` and production vector index |
| Evidence / 证据 | Signed, bounded `AuthorizedEvidenceBundle` | Institution-approved asymmetric keys and key custody |
| Audit / 审计 | Content-free HMAC hash-chain sink with verification | Append-only durable audit stream and independent verifier |
| Model/tools / 模型与工具 | No LLM, MCP, Tidy3D, cloud or blockchain call | Separate E3/E4 and Stage 1B/2 Issues |

## Request flow / 请求流程

```text
synthetic identity token
        |
        v
verify signature, issuer, audience, time and revocation
        |
        v
derive server-side tenant + policy version
        |
        v
sign DelegatedIdentityContext (request, purpose, audience, expiry)
        |
        v
compute authorized source set and issue opaque forced scope
        |
        v
SQL tenant/source predicates, then lexical relevance ranking
        |
        v
reauthorize every returned source against the current policy version
        |
        v
sign and immediately verify bounded AuthorizedEvidenceBundle
        |
        v
append content-free audit event and return bundle + receipt ID
```

The order is intentional: relevance ranking is performed only after policy
authorization, and every candidate is checked again before it enters a bundle.
An LLM never decides access and receives no data in this slice.

顺序是有意设计的：相关性排序只能在策略授权之后进行，每个候选 source 在进入
bundle 前都必须再次授权。本切片中 LLM 永远不决定访问权限，也不会收到数据。

## Source map / 源码索引

- `src/industrial_local_agent/e2/identity.py`: synthetic token verification, server tenant mapping, and delegated identity signing.
- `src/industrial_local_agent/e2/policy.py`: tenant/project/source allow, explicit share, revoke, and policy-version snapshots.
- `src/industrial_local_agent/e2/storage.py`: SQLite forced-scope retrieval adapter; SQL values are parameterized and tenant predicates are unconditional.
- `src/industrial_local_agent/e2/bundle.py`: canonical signed bundle creation and strict schema, binding, freshness, evidence, hash, and key checks.
- `src/industrial_local_agent/e2/audit.py`: content-free events, hash-chain receipts, and chain/signature verification.
- `src/industrial_local_agent/e2/service.py`: model-free orchestration, replay protection, cache scoping, source reauthorization, and fail-closed sequencing.
- `src/industrial_local_agent/e2/demo.py`: shared isolated runtime used by both presentation adapters.
- `src/industrial_local_agent/e2/demo_web.py` and `demo_static/`: loopback HTTP boundary and browser console.
- `fixtures/e2/synthetic_corpus.json`: two synthetic tenants, three users, three projects, and three synthetic sources.
- `tests/e2/`: identity, authorization, isolation, revocation, replay, cache, bundle-negative, audit, SQL-injection, and no-model tests.
- `scripts/e2_demo.py`: interactive local demonstration menu; it uses the same synthetic fixture and never calls a model or network.
- `scripts/e2_web_demo.py`: loopback browser launcher with a random per-process API token.

## Authorization matrix / 授权矩阵

The fixture demonstrates the following cases without real data:

| Case / 情况 | Expected result / 预期结果 |
| --- | --- |
| Alice reads her `tenant-a` project source | Allowed |
| Carol asks for Alice's waveguide source | No cross-tenant evidence |
| Alice reads Bob's project before explicit share | Denied |
| Alice reads Bob's project after same-tenant share | Allowed |
| Alice reads it after share revocation | Denied and policy version advances |
| Client submits a forged tenant/role claim | Request rejected |
| Policy or audit service is unavailable | No consumable bundle |
| Request ID is reused | Replay rejected |
| Bundle is expired, mutated, downgraded, or signed by an unknown/revoked key | Verification rejected |

## Reproducible validation / 可复现验证

From the repository root:

```bash
pytest -q tests/e2
python3 -m compileall -q src tests scripts
git diff --check
```

The E2 tests must remain offline and use only the checked-in synthetic fixture.
They must not require Ollama, Tidy3D, MCP, PostgreSQL, UQ credentials, a cloud
endpoint, FlexCredits, or a blockchain node.

E2 测试必须保持离线，只使用仓库内的合成 fixture。它们不得依赖 Ollama、Tidy3D、
MCP、PostgreSQL、UQ 凭据、云端 endpoint、FlexCredits 或区块链节点。

## Interactive demonstration / 交互式演示

From the repository root, run:

```bash
python3 scripts/e2_demo.py
```

Choose a menu item during the presentation, or run every scenario non-interactively:

```bash
python3 scripts/e2_demo.py --all
```

The menu demonstrates the observable sequence below. It prints source IDs and
policy decisions, but deliberately omits research content.

| Action / 操作 | Observable result / 可观察结果 |
| --- | --- |
| Alice retrieves `waveguide transmission` | `tenant-a`, `source-a1`, signed bundle |
| Carol retrieves `control result` | `tenant-b`, `source-b1`; Alice cannot see it |
| Alice tries Bob's linewidth source | No evidence before share; evidence after same-tenant share; no evidence after revoke |
| Client sends `tenant-b`/`admin` claims | Request rejected |
| Bundle content is modified | Signature/content-hash verification rejected |
| Audit verification | Hash chain passes and research content is absent from recorded fields |

这个菜单是演示辅助工具，不是生产 Web UI，也不代表 E2 已经连接 Stage 1A、真实
身份或 PostgreSQL。需要展示 Stage 1A 聊天界面时，使用 child component 的
`scripts/start-local.sh`；两条演示路径应分别说明。

For a more visual presentation, start the browser console:

```bash
python3 scripts/e2_web_demo.py
```

Open the complete `READY http://127.0.0.1:8780/#token=...` URL printed by the
launcher. The console supports identity selection, retrieval presets,
same-tenant share/revoke, forged-claim and bundle-tamper checks, audit-chain
verification, and state reset. It returns source IDs and security metadata only;
research content is deliberately omitted.

如需更直观的现场演示，运行上述浏览器控制台命令，并打开 launcher 输出的完整
`READY http://127.0.0.1:8780/#token=...` URL。控制台支持身份选择、检索预设、
同 tenant share/revoke、伪造 claim 与 bundle 篡改检查、audit 链验证和状态重置。
它只返回 source ID 和安全元数据，刻意不返回科研正文。

The Web launcher binds exclusively to `127.0.0.1`; its API requires the random
startup token, bounds JSON bodies to 16 KiB, enforces an independent whole-connection
deadline and body deadline, rejects ambiguous framing and duplicate JSON fields,
checks loopback client and Host, disables caching and framing, and applies a
restrictive content-security policy. The
token is local presentation-session control, not user identity. The identity
selector and global fixture map are presenter controls over synthetic scenarios,
not tenant-scoped user views. Do not expose this server to an intranet or treat
it as Stage 1A/E4 integration.

Web launcher 只绑定 `127.0.0.1`；API 要求随机启动令牌，将 JSON body 限制为
16 KiB，分别设置独立的全连接 deadline 与 body deadline，拒绝歧义 framing 和
重复 JSON 字段，检查回环 client 与 Host，禁止缓存和 frame，并设置严格 CSP。该 token 只是本机演示会话控制，
不是用户身份；身份 selector 和全局 fixture map 是主讲人控制的合成场景，不是
tenant-scoped 用户视图。不得把该服务暴露到内网，也不得把它当作 Stage 1A/E4 集成。

## Security interpretation / 安全解释

This implementation demonstrates fail-closed sequencing and stable data
contracts, not cryptographic production readiness. HMAC keys are synthetic test
secrets held in process; SQLite only models the intended forced-RLS behavior;
the policy store is volatile; and the token authority is not OIDC. No raw
research data is committed, returned in audit events, or written to a chain.

该实现证明的是 fail-closed 顺序和稳定数据契约，而不是生产密码学就绪状态。HMAC
key 是进程内的合成测试 secret；SQLite 只是模拟 forced-RLS 行为；policy store
不持久化；token authority 不是 OIDC。没有真实科研数据被提交、写入 audit event
或写入区块链。

The following production claims remain prohibited until separately accepted:

以下生产级主张在独立验收前仍然禁止：

- “UQ SSO is integrated” / “已经接入 UQ SSO”
- “PostgreSQL RLS is enforced” / “已经实施 PostgreSQL RLS”
- “Enterprise RAG or multi-user isolation is complete” / “企业 RAG 或多用户隔离已经完成”
- “HMAC/SQLite prototype is a secure-release system” / “HMAC/SQLite 原型就是安全发布系统”
- “The model can approve access or send data externally” / “模型可以批准权限或向外发送数据”

## Next gates / 下一步门槛

1. Keep presentation adapters separate from production OIDC/PostgreSQL/E4 work and retain synthetic-only evidence under Issue #10.
   保持演示 adapter 与生产 OIDC/PostgreSQL/E4 工作分离，并在 Issue #10 中只留存合成证据。
2. Create a separate Stage 2.0 secure-release protocol Issue after the synthetic E2 acceptance evidence.
   仅在 E2 验收后创建独立的 Stage 2.0 secure-release protocol Issue。
3. Implement PostgreSQL/OIDC and Stage 1A integration as separate E3/E4 work; do not silently replace the synthetic adapters.
   将 PostgreSQL/OIDC 和 Stage 1A 集成作为独立 E3/E4 工作，不要静默替换合成 adapter。
4. Keep the read-only Tidy3D Stage 1B adapter independent and limited to validated exports.
   保持只读 Tidy3D Stage 1B adapter 独立，并限制为经过验证的导出物。
