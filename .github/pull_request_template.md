## 关联 Issue / Linked Issue

Closes #

<!-- 若仍需合并后或部署后验收，请把 Closes 改为 Refs。 -->
<!-- Replace Closes with Refs when post-merge or post-deployment acceptance remains. -->

跨仓库引用请使用完整的 `owner/repository#number`。
Use complete `owner/repository#number` references across repositories.

## 结果摘要 / Outcome Summary

<!-- 说明完成后的可观察结果，而不是逐文件列表。 -->
<!-- Describe the observable outcome, not a file-by-file inventory. -->

## 范围与非目标 / Scope and Non-goals

**范围内 / In scope**

-

**非目标 / Non-goals**

-

## 主要变更 / Material Changes

-

## 验收证据 / Acceptance Evidence

- [ ] Issue 中的每项验收条件都有证据。 / Every Issue acceptance criterion has evidence.

## 验证 / Validation

| 检查 / Check | 结果 / Result | 证据摘要 / Evidence summary |
| --- | --- | --- |
| Tests / 测试 | Not run / 未运行 | |
| Static or syntax checks / 静态或语法检查 | Not run / 未运行 | |
| Manual review / 人工检查 | Not run / 未运行 | |

未运行的检查必须说明原因和风险。
Explain the reason and risk for every check not run.

## 数据、安全与外部副作用 / Data, Security, and External Effects

- 数据分类 / Data classification:
- 凭据或隐私影响 / Credential or privacy impact:
- 云端、付费、消息或设置变更 / Cloud, paid, messaging, or setting changes:
- 回滚方式 / Rollback path:

## 文档与 Submodule / Documentation and Submodules

- [ ] 当前事实已更新到 README 或 `docs/`，或不需要更新并已说明。 / Current truth is updated in README or `docs/`, or the reason no update is needed is stated.
- [ ] 子仓库 commit 已推送且远端可达，或本 PR 不涉及 submodule。 / The child commit is pushed and remotely reachable, or this PR does not affect a submodule.
- [ ] `git diff --submodule` 已审查，或本 PR 不涉及 submodule。 / `git diff --submodule` was reviewed, or this PR does not affect a submodule.

## 遗留风险与后续 / Residual Risk and Follow-up

- 遗留风险 / Residual risk:
- 后续 Issue / Follow-up Issue:

## 最终检查 / Final Checklist

- [ ] PR 只处理一个 canonical Issue 的交付。 / This PR delivers one canonical Issue.
- [ ] 没有提交 token、私钥、真实科研数据、真实研究中的机密或受限未公开结论，或完整原始日志。 / No tokens, private keys, real research data, confidential or restricted unpublished findings from real research, or complete raw logs are included.
- [ ] 完整 diff 和用户已有修改已检查。 / The complete diff and existing user changes were reviewed.
- [ ] 使用 `Closes` 仅因为 head 已推送、变更已满足验收、必要检查与审查通过，且没有合并后验收项。 / `Closes` is used only because the head is pushed, acceptance is satisfied, required checks and review pass, and no post-merge acceptance remains.
