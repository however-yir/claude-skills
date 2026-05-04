# Security Policy

## 安全响应范围 Scope

本仓库接收以下安全问题报告：

- 明文密钥或令牌泄漏
- 依赖漏洞引入的高危风险
- 远程输入导致的命令执行、路径穿越、任意文件写入
- 未授权的数据访问或配置泄漏

## 报告方式 Reporting

请勿在公开 issue 中直接披露漏洞细节。建议通过以下方式私下反馈：

- GitHub Security Advisory（优先）
- 或维护者私信/邮件（包含复现步骤与影响范围）

如果你暂时无法使用私有通道，可先创建高层说明 issue，再请求私下沟通：

- `Security private report request`
- `Security vulnerability report`

对应模板位于：

- `.github/ISSUE_TEMPLATE/security_private_report.md`
- `.github/ISSUE_TEMPLATE/security_vulnerability.md`

## 报告建议内容

- 受影响版本或 commit
- 复现步骤（最小可复现）
- 预期行为与实际行为
- 影响评估（数据、权限、可利用性）
- 修复建议（可选）

## 漏洞提交流程模板 Template

建议按照以下格式提交：

```text
[Title]
Brief summary of the vulnerability (high-level only).

[Type]
credential exposure / command injection / path traversal / unauthorized access / etc.

[Affected scope]
Module, file path, version/commit range.

[Reproduction]
1) ...
2) ...
3) ...

[Impact]
What an attacker can do; what data can be affected.

[Evidence]
Logs, screenshots, stack traces (remove sensitive data).

[Suggested fix]
(Optional)
```

## 处理流程

1. 维护者在 72 小时内确认是否受理。
2. 若可复现，进入修复分支并评估影响范围。
3. 修复完成后发布变更说明与升级建议。
4. 对高风险问题优先发布补丁版本。

## 安全基线建议

- 所有密钥使用环境变量注入，不写入仓库。
- 提交前执行 `scripts/check-secrets.sh`。
- 生产环境使用固定镜像 tag，避免 `latest` 漂移。
- 对外部 URL 输入做白名单与长度限制。
- 日志中避免输出完整凭据与敏感载荷。
