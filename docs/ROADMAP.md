# 实施路线 / Roadmap

路线按可验收证据推进，不按技术名词堆叠。任何阶段只有在其明确验收条件满足后才能标记完成。

The roadmap advances through testable evidence, not accumulated technology labels. A stage may be marked complete only after its stated acceptance conditions are met.

| 阶段 / Stage | 交付内容 / Deliverable | 当前状态 / Current Status | 进入下一阶段的门槛 / Exit Gate |
| --- | --- | --- | --- |
| 1A 工程 / 1A Engineering | 本地证据可追溯科研故事 Agent / Local evidence-traceable scientific-story agent | 工程 MVP 已完成 / Engineering MVP complete | 自动化、安全边界和真实本地模型演示已验证 / Automation, security boundaries, and a real local-model demonstration verified |
| 1A 科研验收 / 1A Scientific Acceptance | 光子学案例人工评估 / Human evaluation on photonics cases | 未完成 / Incomplete | 至少五组公开或合成案例及双人独立评分 / At least five public or synthetic cases with two independent evaluators |
| 1B | 只读 Tidy3D 结果适配器 / Read-only Tidy3D result adapter | 未实现 / Not implemented | 规范化产物、来源校验、失败降级和五案例评估 / Normalized artifacts, provenance validation, failure degradation, and five-case evaluation |
| 2 | 受控安全发布与跨机构传输 / Controlled secure release and cross-institution transfer | 未开始 / Not started | 威胁模型、加密、密钥、权限、签名、撤销和审计经过测试 / Tested threat model, encryption, keys, access, signatures, revocation, and audit |
| 3 | 研究人员统一工作流 / Integrated researcher workflow | 未开始 / Not started | 写作、仿真结果和安全发布在最小权限下端到端验收 / End-to-end acceptance of writing, simulation results, and secure release under least privilege |

## 近期工作 / Immediate Work

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
- 把原始数据写入区块链 / Writing raw data to a blockchain
- 在缺少科研质量评估时声称系统提高论文质量 / Claiming improved paper quality without scientific-quality evaluation

Tidy3D 免费账户额度和 FlexCredits 价格可能变化，不作为固定研究假设。任何付费或云端执行都需要单独授权、实际账户核验和硬预算。

Tidy3D free-account allowances and FlexCredit pricing may change and are not fixed research assumptions. Any paid or cloud execution requires separate authorization, actual-account verification, and a hard budget.
