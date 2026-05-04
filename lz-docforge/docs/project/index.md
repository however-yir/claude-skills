# 项目总览索引 Project Docs Index

## 1. 文档入口

- [品牌文档入口](../branding/index.md)
- [Actor 运行说明](../../.actor/README.md)
- [安全策略](../../SECURITY.md)
- [演进路线图](../../ROADMAP.md)
- [中文贡献指南](../../CONTRIBUTING.zh-CN.md)

## 2. 当前改造内容

- 品牌名称：`文档炼金炉 DocForge`
- 包发布名：`lz-docforge`
- CLI：保留 `docling`，新增 `docforge`
- 配置：新增 `.env.example`，支持 VLM 和 Actor endpoint 覆盖
- Actor：新增错误码体系与 output manifest 规范
- 治理：新增 security 流程、漏洞模板、依赖升级与轻量安全检查 workflow

## 3. 功能边界

### 3.1 主项目功能

- 多格式文档解析（PDF/Office/HTML/图片/文本）
- OCR 与 VLM 模式支持
- 结构化导出（Markdown/JSON/HTML/DocTags）

### 3.2 Actor 功能

- URL 输入触发文档转换
- 产物上传到 key-value store
- 生成并上传 `OUTPUT_MANIFEST`
- 写入 dataset 处理记录（含错误码）

## 4. 部署与检查

- 环境检查：`python3 scripts/validate_env.py`
- 密钥检查：`bash scripts/check-secrets.sh`
- 一键检查：`bash scripts/verify_repo_readiness.sh`

## 5. 迁移文档

- [从 Docling 迁移](../branding/migration-from-docling.md)
- [配置优先级](../branding/config-priority.md)
- [GitHub 品牌配置建议](../branding/github-repo-settings.md)
