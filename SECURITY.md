# 安全报告 / Security Reporting

## 当前渠道 / Current Channel

本 private 研究开发仓库当前没有配置匿名或 GitHub 原生 private vulnerability reporting 入口。不要通过普通 Issue、PR、评论、commit 或 CI 日志提交机密漏洞详情。

This private research-development repository does not currently provide anonymous or GitHub-native private vulnerability reporting. Do not submit confidential vulnerability details through ordinary Issues, PRs, comments, commits, or CI logs.

当前可执行流程如下：

Use the following current process:

1. 通过授予仓库访问权限时使用的既有一对一私密渠道联系仓库 owner。
   Contact the repository owner through the pre-existing one-to-one private channel used when repository access was granted.
2. 第一条消息只说明仓库名、影响类别和“有一份机密报告待安全接收”；不要附漏洞细节、日志、数据、凭据或利用代码。
   In the first message, state only the repository name, impact category, and that a confidential report awaits secure intake; do not include vulnerability details, logs, data, credentials, or exploit code.
3. 等 owner 明确确认受限渠道、接收者和最小必要内容后，再提供脱敏报告。
   Wait for the owner to confirm the restricted channel, recipients, and minimum necessary content before providing a redacted report.
4. 如果不存在既有私密渠道，只在当前已授权的直接交互中请求 owner 建立渠道，不发送技术详情。
   If no pre-existing private channel exists, ask the owner in the current authorized direct interaction to establish one, without sending technical details.
5. 如需项目进度留痕，可在获得授权后创建 redacted tracking Issue，但只能记录状态、影响类别和修复提交，不得记录漏洞机制。
   If project-level tracking is needed, an authorized redacted tracking Issue may record only status, impact category, and remediation commits, never vulnerability mechanics.

## 禁止内容 / Prohibited Content

任何普通 GitHub 对象都不得包含 token、API key、私钥、签名 URL、真实科研数据、真实样本名、真实研究中的机密或受限未公开结论、完整原始日志或可直接复现漏洞的敏感步骤。

No ordinary GitHub object may contain tokens, API keys, private keys, signed URLs, real research data, real sample names, confidential or restricted unpublished findings from real research, complete raw logs, or sensitive steps that directly reproduce a vulnerability.

## 非机密缺陷 / Non-confidential Defects

不涉及机密细节的普通安全加固、依赖更新或公开/合成数据复现，可以使用通用 Issue 表单，并遵循 `AGENTS.md` 的授权、验收和关闭流程。

Ordinary hardening, dependency updates, or reproductions using public or synthetic data without confidential details may use the general Issue form and must follow the authorization, acceptance, and closure rules in `AGENTS.md`.

## 已知限制 / Known Limitation

本文件提供流程路由，不是技术性私密报告系统。配置专用安全报告渠道、仓库 ruleset、branch protection 或权限变化属于独立高影响任务，需要新的 Issue 和明确授权。

This file provides process routing, not a technical private-reporting system. Configuring a dedicated security-reporting channel, repository ruleset, branch protection, or permission changes is a separate high-impact task requiring a new Issue and explicit authorization.
