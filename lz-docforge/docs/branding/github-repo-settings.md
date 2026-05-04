# 仓库品牌配置建议 / GitHub Branding Settings

## 1) 主仓库建议

- Repository Name: `lz-docforge`
- Display Name: `文档炼金炉 DocForge`
- Description:
  `面向中文与多格式文档处理的 Docling 工程化分支，支持解析、结构化抽取、RAG 前处理与本地部署。`
- Homepage:
  `https://github.com/however-yir/lz-docforge`
- Topics:
  `document-ai, pdf-parser, docling, ocr, rag, markdown, python, vlm, chinese, docforge`

## 2) Actor 仓库建议

- Repository Name: `lz-docforge-actor`
- Display Name: `文档炼金炉云端封装 DocForge Actor`
- Description:
  `基于 docling-serve 的文档处理 Actor，支持 URL 批量解析与多格式导出。`
- Topics:
  `apify, actor, docling, document-processing, ocr, markdown, json, serverless`

## 3) 品牌统一建议

- README 顶部统一使用 `docs/assets/docforge_logo.svg`
- 所有 badge 标题统一为 `DocForge`
- 对外 API 示例统一使用 `DOCFORGE_*` 或 `DOCLING_*` 环境变量形式
- 保留 `docling` 兼容命令，同时对外主推 `docforge` 命令别名
