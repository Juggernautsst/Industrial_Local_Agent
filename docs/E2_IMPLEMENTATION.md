# Enterprise E2 Implementation / 企业 E2 实施说明

## Status / 状态

E2 now has a model-free, synthetic-data vertical slice on the implementation
branch for parent Issue [#10](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/10).
It is executable evidence for the authorization and evidence-bundle contracts;
it is not a production enterprise service.

E2 现在已经在父仓库 Issue [#10](https://github.com/Juggernautsst/Industrial_Local_Agent/issues/10)
对应的实施分支中提供一个不调用模型、只使用合成数据的纵向切片。它是授权和
evidence bundle 契约的可执行证据，不是生产企业服务。

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
- `fixtures/e2/synthetic_corpus.json`: two synthetic tenants, three users, three projects, and three synthetic sources.
- `tests/e2/`: identity, authorization, isolation, revocation, replay, cache, bundle-negative, audit, SQL-injection, and no-model tests.

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
python3 -m compileall -q src tests
git diff --check
```

The E2 tests must remain offline and use only the checked-in synthetic fixture.
They must not require Ollama, Tidy3D, MCP, PostgreSQL, UQ credentials, a cloud
endpoint, FlexCredits, or a blockchain node.

E2 测试必须保持离线，只使用仓库内的合成 fixture。它们不得依赖 Ollama、Tidy3D、
MCP、PostgreSQL、UQ 凭据、云端 endpoint、FlexCredits 或区块链节点。

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

1. Review and merge this synthetic E2 implementation with the Issue #10 evidence.
   审查并合并本合成 E2 实施，并在 Issue #10 留存验收证据。
2. Create a separate Stage 2.0 secure-release protocol Issue only after E2 acceptance.
   仅在 E2 验收后创建独立的 Stage 2.0 secure-release protocol Issue。
3. Implement PostgreSQL/OIDC and Stage 1A integration as separate E3/E4 work; do not silently replace the synthetic adapters.
   将 PostgreSQL/OIDC 和 Stage 1A 集成作为独立 E3/E4 工作，不要静默替换合成 adapter。
4. Keep the read-only Tidy3D Stage 1B adapter independent and limited to validated exports.
   保持只读 Tidy3D Stage 1B adapter 独立，并限制为经过验证的导出物。
