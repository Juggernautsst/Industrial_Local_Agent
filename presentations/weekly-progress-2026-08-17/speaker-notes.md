# Week 3 Speaker Notes / 第三周讲稿

**Deck synchronisation / 页面同步：** 8 slides / 8 页。顺序为：Title → Target Workflow → This Week's Result → Enterprise E2 → Executed Demo I → Executed Demo II → What the Demo Proves → Bunya Model Plan.

## One-sentence message / 一句话主线

本周我把“先授权、后检索”从设计图变成了一个可以运行、测试和现场操作的安全切片。LLM 是主要的推理组件，但通过清晰的 provider/chat 契约与授权、证据、审计和工作流解耦，因此可以替换模型而不重写整套 Agent。当前演示使用合成身份和合成数据，仍然是本地回环演示，不是 UQ 生产服务。

This week I turned “authorize before retrieval” from a design idea into a runnable, testable, and hands-on security slice. The LLM is the main reasoning component, but clear provider and chat contracts decouple it from authorization, evidence, audit, and workflow layers. That makes model replacement practical without rewriting the Agent. The current demo uses synthetic identities and synthetic data, and remains a local loopback demo rather than a UQ production service.

## Slide 1: Title / 标题页

**中文讲稿：**

这一页只介绍主题、人员和日期。核心信息是：这周的进展不是再画一张架构图，而是把授权顺序做成了可执行证据。

**English script:**

This slide introduces the topic, people, and date. The key message is that this week moved beyond architecture: the authorization order is now executable evidence.

## Slide 2: Target Workflow / 目标工作流

**中文讲稿：**

这张图沿用上次汇报的目标工作流，并将受保护区域标为 UQ NETWORK。这个标签表示计划中的 UQ 部署边界，不表示已经接入校园网或 UQ 身份系统。我会现场手动画圈，指出本周完成的授权和检索边界。MCP、外部应用和账本仍然是后续目标设计。

**English script:**

This is the target workflow from the previous report, with the protected area labelled UQ NETWORK. The label denotes the planned UQ deployment boundary; it does not mean campus networking or UQ identity services are already connected. I will draw the completed authorization and retrieval boundary live. MCP, external applications, and the ledger remain future design elements.

## Slide 3: This Week's Result / 本周结果

**中文讲稿：**

左边是已经实现并验证的内容：合成身份、服务端策略、强制检索范围、来源重新授权、签名证据包和审计链。右边是下一步集成：UQ 身份、生产 RLS/RAG、模型网关、Tidy3D、Bunya 和安全外发。演示范围明确是 loopback、synthetic-only，并且授权决策不调用模型。

**English script:**

The left side is implemented and tested: synthetic identities, server-side policy, forced retrieval scope, source reauthorization, a signed evidence bundle, and an audit chain. The right side is the next integration: UQ identity, production RLS/RAG, a model gateway, Tidy3D, Bunya, and secure release. The demo is loopback-only, synthetic-only, and the access decision does not call a model.

## Slide 4: Enterprise E2 / 企业 E2

**中文讲稿：**

E2 可以用两个问题解释：谁在问？他可以看到什么？服务端先从可信身份和策略得到允许的 source 集合，再只在这个集合内检索；每个结果进入 evidence bundle 前还要重新授权。最后返回签名证据并记录不含正文的审计链。这样 RAG 或模型不会成为权限判断者。

**English script:**

E2 can be explained with two questions: who is asking, and what may this person see? The server derives an allowed source set from trusted identity and policy, searches only inside that set, and reauthorizes every result before it enters the evidence bundle. It then returns signed evidence and a content-free audit chain. RAG and the model are not the authority here.

## Slide 5: Executed Demo I / 已执行演示一

**中文讲稿：**

这是实际运行过的浏览器截图。Carol 查询 `control result` 得到 tenant-b 的 `source-b1`；Alice 提出完全相同的问题，只得到 `NO EVIDENCE`。重点是同一个问题不会自动跨越 tenant 边界。

**English script:**

This is a screenshot from the executed browser demo. Carol queries `control result` and receives tenant-b's `source-b1`; Alice asks exactly the same question and receives `NO EVIDENCE`. The important result is that the same query does not cross the tenant boundary.

## Slide 6: Executed Demo II / 已执行演示二

**中文讲稿：**

这里演示访问生命周期。Alice 一开始不能读取 Bob 的 `source-a2`；明确 share 后可以读取；revoke 后下一次检索立即恢复为 `NO EVIDENCE`。访问是明确授予、版本化并可撤回的。

**English script:**

This slide shows the access lifecycle. Alice initially cannot read Bob's `source-a2`. After an explicit share she can retrieve it; after revocation the next request immediately returns `NO EVIDENCE`. Access is explicit, versioned, and reversible.

## Slide 7: What the Demo Proves / 演示证明了什么

**中文讲稿：**

26 个 E2 测试覆盖隔离、share/revoke、伪造身份、篡改 bundle 和审计链。CLI 与浏览器共用同一个 runtime。这里验证的是授权合同和失败模式，不是生产密码学、生产 RAG 或 UQ 多用户部署；这些是下一步工程工作。

**English script:**

Twenty-six E2 tests cover isolation, share/revoke, forged identity, bundle tampering, and the audit chain. The CLI and browser use the same runtime. This validates the authorization contract and its failure modes, not production cryptography, production RAG, or a multi-user UQ deployment. Those are the next engineering steps.

## Slide 8: Bunya Model Plan / Bunya 模型规划

**中文讲稿：**

本地 3B 模型和 CPU-only E2 足以完成当前演示。若获得 Bunya 资源，先测试 4-bit 14B，起点按一张至少 16 GB 显存的 GPU、8 个 CPU 核心和 32 GB RAM 讨论，具体配置和费用由 RCC 确认。32B 或 70B-class 只有在质量 benchmark 证明值得时才升级；实际成本取决于 GPU 配额、作业时间、存储和 serving 复杂度。

还要强调一点：LLM 虽然负责推理和回答，但它只是可替换的组件。授权、证据、审计和工作流契约不绑定某一个模型；换模型需要做兼容性、质量和资源 benchmark，而不是重写整套 Agent。

**English script:**

The local 3B model and CPU-only E2 are enough for the current demonstration. If Bunya access is approved, I would start with a 4-bit 14B benchmark, using one GPU with at least 16 GB of VRAM, eight CPU cores, and 32 GB of RAM as a planning point; RCC must confirm the actual configuration and charges. Move to 32B or 70B-class only if a quality benchmark justifies it. Cost depends on GPU quota, job time, storage, and serving complexity.

One architectural point is important: the LLM performs reasoning and response generation, but it is a replaceable component. Authorization, evidence, audit, and workflow contracts are not tied to one model. A model switch requires compatibility, quality, and resource benchmarks, not a rewrite of the Agent.

**收尾强调 / Closing emphasis:**

整套流程的核心体验由 LLM 提供，但可信控制不在 LLM 内部。模型可以从本地 3B 换成 Bunya 上的 14B，之后也可以换成其他兼容模型；只要遵守同一 provider/chat 契约，授权、证据、审计和外发控制都保持不变。

The LLM provides the core reasoning experience, but the trusted controls do not live inside the model. The model can move from a local 3B model to a 14B model on Bunya, and later to another compatible model. As long as it follows the same provider and chat contracts, authorization, evidence, audit, and release controls remain unchanged.

## Live demo runbook / 现场演示流程

启动浏览器演示：

Start the browser demo:

```bash
python3 scripts/e2_web_demo.py --port 0
```

打开程序打印的完整 token URL，不要保存 token。依次执行：

Open the complete tokenized URL printed by the program. Do not save the token. Then:

1. Carol + `control result` -> `ALLOW`, `source-b1`.
2. Alice + the same query -> `NO EVIDENCE`.
3. Alice + `Ring linewidth` -> share, retrieve `source-a2`, revoke, retrieve `NO EVIDENCE`.
4. Run forged-claim and bundle-tamper checks -> `DENY`.
5. Verify the audit chain -> `PASS`.

从笔记本远程演示时，服务保持 loopback-only，通过 SSH 转发同一随机端口：

For a laptop demonstration, keep the service loopback-only and forward the same random port over SSH:

```bash
ssh -N -L PORT:127.0.0.1:PORT USER@DESKTOP
```

## Boundaries to say explicitly / 必须明确说明的边界

- 当前使用 synthetic identities and synthetic data；不要说已经接入 UQ SSO、MFA 或真实科研数据。 / The current demo uses synthetic identities and synthetic data; do not call it UQ SSO, MFA, or real research data.
- E2 尚未与 Stage 1A、LLM、MCP、Tidy3D 或 Bunya 端到端连接。 / E2 is not yet connected end to end to Stage 1A, the LLM, MCP, Tidy3D, or Bunya.
- SQLite 和 HMAC 是原型验证工具，不是生产 RLS 或生产密码学。 / SQLite and HMAC are prototype mechanisms, not production RLS or production cryptography.
- secure release、接收者密钥、外部投递和区块链 checkpoint 仍是后续工作。 / Secure release, recipient keys, external delivery, and a blockchain checkpoint remain future work.
