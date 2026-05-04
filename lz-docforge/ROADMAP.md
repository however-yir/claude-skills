# Roadmap

## 2026 Q2

- [x] 品牌化改造（DocForge 命名、Logo、README 重写）
- [x] CLI 双入口（`docling` + `docforge`）
- [x] VLM API 地址支持环境变量覆盖
- [x] Actor 端点与日志键配置化
- [x] 发布补充协议与仓库品牌配置文档

## 2026 Q3

- [ ] 增加 `SECURITY.md` + 自动化密钥扫描 workflow
- [ ] 增加配置校验脚本（环境变量、URL、目录权限）
- [ ] 建立依赖升级策略（小步快跑 + 回归基线）
- [ ] 输出协议文档化（转换产物 manifest）
- [ ] 增加 RAG 前处理 profile（分块、清洗、元数据标签）

## 2026 Q4

- [ ] 支持任务级 trace id 与结构化日志
- [ ] 大文档并行解析与失败重试策略
- [ ] 文档质量评分与结果完整性检查
- [ ] 发布生产部署样例（Docker Compose + K8s Job）
- [ ] 引入端到端回归样本集（多语言、多格式）

## 版本策略

- `minor`：新增能力与兼容增强
- `patch`：缺陷修复与安全补丁
- `major`：破坏性变更（需迁移说明）
