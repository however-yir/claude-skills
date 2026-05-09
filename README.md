# Claude Skills Collection

[![CI](https://github.com/however-yir/claude-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/however-yir/claude-skills/actions/workflows/ci.yml)

个人 Claude Code / Codex Skill 合集，原分散在 12 个独立仓库，现合并为统一入口。

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/however-yir/claude-skills.git
cd claude-skills

# 安装单个 skill 到 Claude Code
mkdir -p ~/.claude/skills
cp -r skills/ai-agent-workflow ~/.claude/skills/ai-agent-workflow

# 或安装顶层工具项目
cp -r xhs-cover-studio ~/.claude/skills/xhs-cover-studio
```

## Skills 目录

| Skill | 用途 | 安装 | 测试 | 维护状态 |
|-------|------|------|------|----------|
| [ai-agent-workflow](skills/ai-agent-workflow) | AI Agent 工作流设计（Prompts、MCP、评估循环） | `cp -r skills/ai-agent-workflow ~/.claude/skills/` | 纯知识 skill，无代码测试 | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [local-ai-systems-studio](skills/local-ai-systems-studio) | 本地 LLM 部署规划（MLX、GGUF、Ollama、vLLM） | `cp -r skills/local-ai-systems-studio ~/.claude/skills/` | 纯知识 skill，无代码测试 | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [java-fullstack-engineering](skills/java-fullstack-engineering) | Spring Boot 全栈工程（SQL 调优、API 加固） | `cp -r skills/java-fullstack-engineering ~/.claude/skills/` | 纯知识 skill，无代码测试 | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [github-job-showcase](skills/github-job-showcase) | GitHub 仓库转面试级 README / 作品集 | `cp -r skills/github-job-showcase ~/.claude/skills/` | 纯知识 skill，无代码测试 | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [xiaohongshu-content-studio](skills/xiaohongshu-content-studio) | 小红书内容包生成（标题、钩子、正文、封面文案） | `cp -r skills/xiaohongshu-content-studio ~/.claude/skills/` | 纯知识 skill，无代码测试 | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [office-doc-presentation](skills/office-doc-presentation) | 办公文档优化（Word/WPS/PPT/PDF 排版润色） | `cp -r skills/office-doc-presentation ~/.claude/skills/` | 纯知识 skill，无代码测试 | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [digital-self](skills/digital-self) | 个人工作流蒸馏为可复用数字分身 | `cp -r skills/digital-self ~/.claude/skills/` | `cd skills/digital-self && pytest tests/` | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [bestie](skills/bestie) | 闺蜜/同事工作方法蒸馏为可调用 AI Skill | `cp -r skills/bestie ~/.claude/skills/` | `cd skills/bestie && pytest tests/` | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [last30days](skills/last30days) | 多平台社媒趋势研究（Reddit、X、YouTube、TikTok、Instagram） | `cp -r skills/last30days ~/.claude/skills/` | `cd skills/last30days && pytest tests/` | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [lunwen](skills/lunwen) | 中文毕业设计说明书撰写 + DOCX 交付 | `cp -r skills/lunwen ~/.claude/skills/` | `cd skills/lunwen && pytest tests -q` | ![](https://img.shields.io/badge/status-active-brightgreen) |

## 工具与项目

| 项目 | 用途 | 安装 | 测试 | 维护状态 |
|------|------|------|------|----------|
| [last30days-cn-skill](last30days-cn-skill/) | 中国社媒趋势分析（X、微博、小红书、抖音） | `cp -r last30days-cn-skill ~/.claude/skills/` | `cd last30days-cn-skill && pytest tests/` | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [xhs-cover-studio](xhs-cover-studio/) | 小红书封面生成（58 品牌风格模板） | `cp -r xhs-cover-studio ~/.claude/skills/` | 需 Chrome + Python，无自动化测试 | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [bishe-manual-skill](bishe-manual-skill/) | 中文毕业设计说明书撰写 Skill | `cp -r bishe-manual-skill ~/.claude/skills/` | `cd bishe-manual-skill && pytest tests -q` | ![](https://img.shields.io/badge/status-active-brightgreen) |
| [lz-docforge](lz-docforge/) | DocForge：基于 Docling 的中文文档处理工程化 | `cd lz-docforge && pip install -e .` | `cd lz-docforge && pytest tests/` | ![](https://img.shields.io/badge/status-active-brightgreen) |

## Skill 类型说明

本仓库包含两种类型的 skill：

- **纯知识 skill**（ai-agent-workflow、local-ai-systems-studio 等）：仅包含 SKILL.md 规范和参考文档，通过 prompt 引导 Claude Code / Codex 的行为
- **代码 skill**（bestie、last30days-cn-skill、lz-docforge 等）：包含 Python/Node.js 工具脚本、测试用例和 CI 流水线

## 目录结构约定

```
skills/<skill-name>/
  SKILL.md        # 必须：YAML frontmatter（--- 分隔）
  README.md       # 必须：用途、安装、测试说明
  LICENSE         # 推荐：MIT
  CONTRIBUTING.md # 可选：该 skill 的贡献指南
  references/     # 可选：参考文档
  examples/       # 可选：使用示例
  tests/          # 可选：测试用例
  scripts/        # 可选：可执行脚本
  tools/          # 可选：工具函数
  prompts/        # 可选：Prompt 模板
```

根 CI（`.github/workflows/ci.yml`）会在每次 push/PR 时自动检查 `skills/` 下每个子目录是否满足 SKILL.md frontmatter + README.md + LICENSE 要求。

## 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](.github/CONTRIBUTING.md) 了解详情。

本项目采用 [Contributor Covenant](.github/CODE_OF_CONDUCT.md) 行为准则。

## 原仓库迁移说明

以下 12 个仓库已合并到本仓库：

| 原仓库名 | 新位置 | 说明 |
|----------|--------|------|
| `codex-skill-ai-agent-workflow` | [skills/ai-agent-workflow](skills/ai-agent-workflow) | AI Agent 工作流 |
| `codex-skill-local-ai-systems-studio` | [skills/local-ai-systems-studio](skills/local-ai-systems-studio) | 本地 LLM 部署 |
| `codex-skill-java-fullstack-engineering` | [skills/java-fullstack-engineering](skills/java-fullstack-engineering) | Java 全栈工程 |
| `codex-skill-github-job-showcase` | [skills/github-job-showcase](skills/github-job-showcase) | 求职作品集 |
| `codex-skill-xiaohongshu-content-studio` | [skills/xiaohongshu-content-studio](skills/xiaohongshu-content-studio) | 小红书内容 |
| `codex-skill-office-doc-presentation` | [skills/office-doc-presentation](skills/office-doc-presentation) | 办公文档 |
| `digital-self-skill` | [skills/digital-self](skills/digital-self) | 数字分身 |
| `bestie-skill` | [skills/bestie](skills/bestie) | 闺蜜 Skill |
| `last30days-cn-skill` | [last30days-cn-skill](last30days-cn-skill/) | 社媒趋势分析 |
| `xhs-cover-studio` | [xhs-cover-studio](xhs-cover-studio/) | 小红书封面 |
| `bishe-manual-skill` | [bishe-manual-skill](bishe-manual-skill/) | 毕设说明书 |
| `lz-docforge` | [lz-docforge](lz-docforge/) | 文档炼金炉 |

## License

本仓库采用 [MIT License](LICENSE)。各子 Skill 保持其原有 License，详见子目录 LICENSE 文件。
