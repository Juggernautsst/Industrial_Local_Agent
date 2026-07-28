# 总体架构 / Architecture

## 1. 组织模型 / Organization Model

本仓库是 Git superproject，不是运行时应用，也不是把全部代码复制到一个目录的 monorepo。每个可独立验证和发布的组件保留自己的仓库；父仓库只固定经过审查的组件提交，并记录跨组件边界。

This repository is a Git superproject, not a runtime application or a monorepo containing copied source. Each independently testable and releasable component retains its own repository. The parent pins reviewed component commits and records cross-component boundaries.

```text
Industrial_Local_Agent
        |
        +-- components/stage1a-good-story-agent  [implemented, pinned]
        |
        +-- Tidy3D result adapter                [planned, not created]
        |
        +-- secure release component             [planned, not created]
        |
        +-- workflow orchestrator                [planned, not created]
```

## 2. 当前组件 / Current Component

`components/stage1a-good-story-agent` 是当前唯一组件。它接收研究者明确选择的 TXT、Markdown、CSV、JSON 或可提取文本的 PDF，建立 SHA-256、来源定位和 evidence ID，再通过材料审计或本地 Ollama 生成受证据约束的暂定报告。

`components/stage1a-good-story-agent` is the only current component. It accepts researcher-selected TXT, Markdown, CSV, JSON, or text-extractable PDF inputs; builds SHA-256 values, source locators, and evidence IDs; then produces a provisional evidence-governed report through either material audit or local Ollama synthesis.

Stage 1A 不执行仿真、外部检索、云模型、自动代码、区块链或安全发布。形式正确的引用也不能证明科学解释正确，因此领域专家复核仍是强制步骤。

Stage 1A does not execute simulations, external retrieval, cloud models, generated code, blockchain, or secure release. Formally valid citations do not prove a scientific interpretation is correct, so domain-expert review remains mandatory.

## 3. Stage 1B 边界 / Stage 1B Boundary

第一项新增组件应是只读 Tidy3D 结果适配器。它把可信的公开或合成导出物转换为 Stage 1A 已支持的 JSON/CSV 边界，而不是把求解器权限加入写作 Agent。

The first new component should be a read-only Tidy3D result adapter. It converts trusted public or synthetic exports into the JSON/CSV boundary already supported by Stage 1A instead of adding solver privileges to the writing agent.

```text
Tidy3D export
  manifest + simulation config + monitor data + notes
        |
        v
read-only adapter
  validate schema, units, provenance, grid, boundary, convergence metadata
        |
        v
Stage 1A evidence pipeline
  evidence-linked interpretation, limitations, next-step suggestions, draft text
```

适配器不得默认持有 Tidy3D API key、提交任务、执行模型生成代码或加载来自不可信来源的 pickle/Python 对象。优先使用有明确 schema 的 JSON 和 CSV。

The adapter must not hold a Tidy3D API key by default, submit jobs, execute model-generated code, or load pickle/Python objects from untrusted sources. Prefer schema-governed JSON and CSV.

## 4. 安全发布边界 / Secure-Release Boundary

安全发布组件属于后续阶段。设计顺序必须是：威胁模型、数据分类、接收者身份、加密、密钥管理、访问控制、签名、撤销和审计。只有当这些机制留下明确的多方记账问题时，才评估区块链。

The secure-release component belongs to a later stage. Its design order is threat model, data classification, recipient identity, encryption, key management, access control, signatures, revocation, and auditing. Blockchain should be evaluated only if those controls leave a concrete multi-party ledger problem.

原始科研数据不得写入区块链。若未来使用不可变账本，候选内容仅限经过评估的哈希、时间戳、授权或撤销事件。

Raw research data must never be written to a blockchain. If an immutable ledger is later justified, candidate records are limited to evaluated hashes, timestamps, authorization events, or revocation events.

## 5. 版本与更新规则 / Version and Update Rules

1. 子组件先完成自己的测试、敏感信息扫描、提交和推送。
   The child component first completes its own tests, secret scan, commit, and push.
2. 父仓库把 gitlink 更新到已存在于子仓库远端的具体提交。
   The parent updates its gitlink to a specific commit already present on the child remote.
3. 父仓库使用 `git diff --submodule` 审查版本变化，并单独提交该指针更新。
   The parent reviews the version change with `git diff --submodule` and commits the pointer update separately.
4. 协作者使用 `git clone --recurse-submodules` 或 `git submodule update --init --recursive` 恢复完整工作树。
   Collaborators restore the complete tree with `git clone --recurse-submodules` or `git submodule update --init --recursive`.

父仓库的 private 状态不会向子仓库传播权限，CI 也需要单独获得每个 private submodule 的最小读取权限。

The parent's private status does not propagate permissions to child repositories. CI also needs separate least-privilege read access to each private submodule.

## 6. 部署安全模型 / Deployment Security Model

当前 superproject 只组织代码版本，不提供操作系统级隔离。`/mnt/d` 的开发副本不能用于真实高价值数据。处理未公开材料前，应在 Linux 文件系统重新部署、限制文件权限、验证外发控制，并重新建立独立虚拟环境。

The current superproject organizes code versions only; it provides no operating-system isolation. The `/mnt/d` development copy must not handle real high-value data. Before processing unpublished material, redeploy on a Linux filesystem, restrict permissions, verify egress controls, and create a fresh isolated virtual environment.
