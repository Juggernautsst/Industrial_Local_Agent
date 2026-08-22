# Speaker Notes / 讲稿

## Core message / 核心思路

这套 slides 讲的不是“已经完成了一个企业级系统”，而是：我们已经验证了本地证据工作流，并把企业内网、授权检索、科研软件适配和受控外发拆成了可以逐步验证的信任边界。所有 `TARGET DESIGN`、`PROPOSED` 和 `CONCEPT` 内容都应明确说成目标或待验证能力。

The presentation is not claiming that an enterprise system is already complete. It shows that the local evidence workflow has been validated, while the intranet, authorized retrieval, scientific-software adapters, and controlled release are separated into trust boundaries that can be validated incrementally. Explicitly describe `TARGET DESIGN`, `PROPOSED`, and `CONCEPT` items as future or unvalidated capabilities.

## Slide 1 — Secure AI Workflow for Confidential Research / 保密科研的安全 AI 工作流

**中文讲稿：**

今天汇报的主题是面向保密科研的安全 AI 工作流。核心问题不是单纯选择一个更大的模型，而是在数据不能随意离开保护网络的情况下，让研究人员仍然能够使用本地模型、科研软件和受控的外部协作能力。

**English script:**

Today I will present a secure AI workflow for confidential research. The central problem is not simply choosing a larger model, but allowing researchers to use local models, scientific software, and controlled external collaboration without freely exposing protected data.

## Slide 2 — Research Problem / 研究问题

**中文讲稿：**

这里把问题归纳为三个约束。第一，文件和模型上下文要留在受保护的网络中；第二，模型只能看到经过授权的证据；第三，工具调用和数据外发都必须通过狭窄、可审查的接口。也就是说，我们关注的是数据边界和操作边界，而不只是模型回答质量。

**English script:**

The problem has three constraints. First, files and model context must remain inside the protected network. Second, the model may see only authorized evidence. Third, tool calls and data release must pass through narrow, reviewable interfaces. The focus is therefore on data and action boundaries, not only on answer quality.

## Slide 3 — Target Workflow / 目标工作流

**中文讲稿：**

这张图是目标架构的全景。研究人员的请求先进入内网中的策略和检索路径，授权后的证据再交给本地 LLM。模型如果需要科研软件结果，只能通过 MCP 工具边界读取经过批准的导出物。需要离开内网的数据还要经过 Release Gate；外部应用接收链下的受保护数据包，区块链只保存哈希和回执等最小证明。这里的流程是目标设计，不代表所有组件已经实现。

**English script:**

This is the target architecture. A researcher request enters the policy and retrieval path inside the intranet, and only authorized evidence is passed to the local LLM. If the model needs scientific-software results, it can read approved exports only through the MCP tool boundary. Data leaving the intranet must pass the Release Gate; the external application receives a protected off-chain package, while the ledger stores only minimal proof such as a hash and receipt. This is a target design, not a claim that every component is implemented.

## Slide 4 — Authorize Before Retrieval / 先鉴权再检索

**中文讲稿：**

这一页展开最重要的安全顺序：先识别用户和权限，再决定允许访问哪些源，最后才进行 RAG 检索。RAG 本身不是鉴权机制，它只能在已经确定的范围内组织证据。授权后的证据交给 Evidence Analysis Worker，也就是由当前 Stage 1A Agent 演化出的分析执行角色；它再通过独立的 Model Gateway 调用登记过的本地模型。如果策略拒绝，请求应该在进入检索前停止。

**English script:**

This slide expands the key security order: identify the user and permissions first, determine the allowed sources, and only then run RAG retrieval. RAG itself is not an authorization mechanism; it organizes evidence only within an already authorized scope. Authorized evidence reaches the Evidence Analysis Worker, the analysis-execution role derived from the current Stage 1A agent; it then uses a separate Model Gateway to invoke the registered local model. A denied request should stop before retrieval.

## Slide 5 — MCP as the Tool Boundary / MCP 作为工具边界

**中文讲稿：**

这里具体说明 MCP 的职责。模型可以提出一个受限的只读导入请求，策略检查通过后，由通用科研软件适配器读取已批准的导出结果。Tidy3D 只是第一个验证案例，不是整个架构的限制。这个适配器不运行仿真、不修改软件状态、不持有 API key，也不提供绕过策略的外部网络通道。

**English script:**

This slide defines the role of MCP. The model may make a bounded read-only import request; after a policy check, a generic scientific-software adapter reads approved exports. Tidy3D is only the first validation case, not a limitation of the architecture. The adapter does not run simulations, modify software state, hold an API key, or provide an external network path around policy.

## Slide 6 — Confidential Collaboration / 保密协作

**中文讲稿：**

这张图是受控外发的概念方案，目前接口还没有定义。数据先经过 MCP 和 Release Gate，完成授权、审批、加密和审计，然后通过唯一的外发出口发送到外部应用。真正的保密数据放在链下受保护的数据包中；链上只记录哈希、签名或回执，用来做完整性证明和审计索引。区块链本身不会自动阻止绕过，网络出口和权限策略同样是必要控制。

**English script:**

This is the conceptual controlled-release path, and its interface is not yet defined. Data passes through MCP and the Release Gate for authorization, approval, encryption, and audit before using the sole egress path to the external application. The confidential payload remains in a protected off-chain package; the ledger records hashes, signatures, or receipts for integrity proof and audit indexing. The ledger alone does not prevent bypasses; network egress and authorization controls are also required.

## Slide 7 — Model Options / 模型选择

**中文讲稿：**

这一页比较的是部署规模，而不是简单的模型排行榜。Qwen2.5-3B 是本地规模候选，已经在一个合成光子学 fixture 上做过工程 smoke test，但这不等于科研质量验证。Kimi K3 是集群规模候选，不能直接假设可以部署到单机内网。目前两个候选都还没有完成企业集成，记录中的 qwen2.5:7b 仍是交接基线。

**English script:**

This slide compares deployment scale rather than presenting a simple model ranking. Qwen2.5-3B is the local-scale candidate and has passed one engineering smoke test on a synthetic photonics fixture, but that is not scientific-quality validation. Kimi K3 is a cluster-scale candidate and should not be assumed to run on a single intranet host. Neither candidate is enterprise-integrated yet, and qwen2.5:7b remains the recorded handoff baseline.

## Slide 8 — What Runs Today / 当前可运行内容

**中文讲稿：**

这一页把当前状态和目标状态分开。现在真正能运行的是单用户、本地访问、使用公开或合成数据的证据闭环：文件经过处理后进入本地 LLM，生成可追踪的检查报告。Agent 与本地模型之间的接口还在 review。企业级授权 RAG、MCP 工具、安全外发和外部账本都还没有建成，因此不能把第 3 页的目标架构当成现状。

**English script:**

This slide separates the current state from the target state. The operational part today is a single-user local evidence loop using public or synthetic data: files are processed by a local LLM and produce a traceable checked report. The interface between the agent and local model is still under review. Enterprise authorized RAG, MCP tools, secure release, and the external ledger are not built, so the target architecture on slide 3 must not be described as the current system.

## Slide 9 — Engineering Validation Path / 工程验证路径

**中文讲稿：**

这一页给出实际验证顺序。现在先完成本地模型接口的 review；下一步用合成数据测试授权检索；之后定义外发审批、加密和回执协议；再接入一个只读科研软件适配器；只有在确实需要时，才增加账本 checkpoint。这个顺序的原则是先验证每一个信任边界，再把边界连接起来。

**English script:**

This slide gives the engineering order. First, finish the local model-interface review. Next, test authorized retrieval with synthetic data. Then define approval, encryption, and receipt protocols for release, followed by one read-only scientific-software adapter. Add a ledger checkpoint only if a real need remains. The principle is to validate each trust boundary before connecting the boundaries together.

## Slide 10 — Seven-Day Usage and Cost / 七日用量与成本

**中文讲稿：**

这一页只使用 8 月 1 日到 8 月 7 日的 cc-switch 面板数据。它记录了 4,635 次请求、约 5.97 亿 token，以及约 5.47 亿次 cache reads；曲线在 8 月 6 日出现明显峰值。这里的 0.00 美元是该界面的估算值，不等于系统运行成本为零。它没有涵盖本地或集群硬件、科研软件云端求解，或者后续审计所需的成本。这个图的价值不是给出最终预算，而是说明用量、缓存行为和成本测量需要在系统扩大之前被单独记录和验证。

**English script:**

This slide uses only the cc-switch dashboard data from 1 to 7 August. It records 4,635 requests, about 597 million tokens, and about 547 million cache reads; the curve peaks clearly on 6 August. The US$0.00 figure is the interface estimate, not evidence that the system has zero operating cost. It does not cover local or cluster hardware, scientific-software cloud solving, or the cost of later audit. The value of this chart is not a final budget; it shows why usage, caching behaviour, and cost measurement need to be recorded and validated before the system scales.
## Closing / 结尾

**中文讲稿：**

所以，这个项目当前最明确的成果是一个可运行的本地证据闭环，以及一套需要逐步验证的信任边界。七日用量记录提供了一个实际的工程信号：在系统扩大之前，模型用量、缓存行为和成本都必须被独立测量。下一阶段是用合成数据逐个验证鉴权、工具调用和受控外发，而不是把目标架构当作已经完成的系统。

**English closing:**

The clearest result at this stage is a working local evidence loop and a set of trust boundaries that still require validation. The seven-day usage record adds a practical engineering signal: model use, caching behaviour, and cost must be measured separately before the system scales. The next step is to validate authorization, tool use, and controlled release one by one with synthetic data, rather than presenting the target architecture as a completed system.
