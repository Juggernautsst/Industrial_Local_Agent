# Industrial_Local_Agent

`Industrial_Local_Agent` 是一个 private Git superproject，用于组织本地科研 Agent、受控仿真辅助和后续安全发布组件。它通过 Git submodule 固定各组件的已审查版本，不复制组件源码或改写其独立历史。

`Industrial_Local_Agent` is a private Git superproject for organizing local scientific agents, controlled simulation assistance, and later secure-release components. It pins reviewed component versions through Git submodules without copying their source or rewriting their independent histories.

## 当前结论 / Current Status

- Stage 1A 工程 MVP 已完成：本地、证据可追溯的科研故事 Agent，版本 `0.1.1`，自动化测试为 `38 passed`。
  The Stage 1A engineering MVP is complete: a local, evidence-traceable scientific-story agent at version `0.1.1`, with `38 passed` automated tests.
- Stage 1A 的科研质量验收尚未完成；当前只有一组合成光子学案例，还需要四组案例和独立人工评估。
  Stage 1A scientific-quality acceptance is not complete; the current evidence includes one synthetic photonics case, with four additional cases and independent human evaluation still required.
- Stage 1B 尚未实现。下一项工程任务是只读 Tidy3D 结果适配器，而不是让 Agent 持有 API key 或自动提交云端任务。
  Stage 1B is not implemented. The next engineering task is a read-only Tidy3D result adapter, not an agent that holds API keys or automatically submits cloud jobs.
- 安全发布、跨机构传输和区块链均未实现。未来必须先建立威胁模型、加密、密钥管理、访问控制和审计，再判断区块链是否解决剩余问题。
  Secure release, cross-institution transfer, and blockchain are not implemented. A future stage must first define threat modeling, encryption, key management, access control, and auditing before deciding whether blockchain solves a remaining problem.

## 仓库结构 / Repository Structure

| 路径 / Path | 类型 / Type | 职责 / Responsibility | 当前固定版本 / Current Pin |
| --- | --- | --- | --- |
| `components/stage1a-good-story-agent/` | Git submodule | 本地证据可追溯科研写作 Agent / Local evidence-traceable scientific-writing agent | `4e3bdda` |
| `docs/ARCHITECTURE.md` | 父仓库文档 / Parent documentation | 组件边界、更新规则和安全模型 / Component boundaries, update rules, and security model | 当前父仓库 / Current parent |
| `docs/ROADMAP.md` | 父仓库文档 / Parent documentation | Stage 1A 至 Stage 3 的验收路线 / Acceptance roadmap from Stage 1A through Stage 3 | 当前父仓库 / Current parent |

未来可能增加 `tidy3d-adapter`、`secure-data-transfer` 和 `workflow-orchestrator`，但在接口与验收条件稳定前不创建空组件。

Future components may include `tidy3d-adapter`, `secure-data-transfer`, and `workflow-orchestrator`, but empty components will not be created before their interfaces and acceptance criteria are stable.

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

## 安全边界 / Security Boundaries

- 父仓库和子仓库均应保持 private；父仓库权限不会自动授予 private 子仓库权限。
  Both parent and child repositories should remain private; parent access does not automatically grant access to a private submodule.
- 不得提交真实科研数据、模型文件、运行产物、导出包、`.env`、API token、密码或私钥。
  Do not commit real research data, model files, run artifacts, export bundles, `.env` files, API tokens, passwords, or private keys.
- 当前 `/mnt/d` 工作副本只用于开发、公开材料和合成数据，不适合未公开或高价值材料。
  The current `/mnt/d` working copy is for development, public material, and synthetic data only; it is unsuitable for unpublished or high-value material.
- private GitHub 可见性不是数据加密、主机隔离或外发控制。
  Private GitHub visibility is not data encryption, host isolation, or egress control.
- 公开任一仓库前，必须单独完成许可证、安全和机器信息清理审查。
  Before making either repository public, perform separate licensing, security, and machine-information reviews.

## 详细资料 / Detailed Records

- [总体架构 / Architecture](docs/ARCHITECTURE.md)
- [实施路线 / Roadmap](docs/ROADMAP.md)
- [Stage 1A 完整交接 / Complete Stage 1A handoff](components/stage1a-good-story-agent/STAGE1A_HANDOFF.md)
- [Stage 1A 使用说明 / Stage 1A usage](components/stage1a-good-story-agent/README.md)

父仓库当前未声明统一许可证。每个组件保留自己的许可证责任；父仓库许可证不会自动覆盖 submodule。

The parent currently declares no unified license. Each component retains its own licensing responsibility; a parent license would not automatically cover a submodule.
