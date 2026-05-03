# Claude Skills Collection

个人 Claude Code / Codex Skill 合集，原分散在 8 个独立仓库，现合并为统一入口。

## Skills 目录

| Skill | 说明 | 来源 |
|-------|------|------|
| [ai-agent-workflow](skills/ai-agent-workflow) | 可复用的 AI Agent 工作流（Prompts、工具、MCP 集成、评估循环） | 原创 |
| [local-ai-systems-studio](skills/local-ai-systems-studio) | 本地 LLM 规划与部署（MLX、GGUF、Ollama、LM Studio） | 原创 |
| [java-fullstack-engineering](skills/java-fullstack-engineering) | Spring Boot 全栈工程（SQL 调优、API 加固、面试级项目升级） | 原创 |
| [github-job-showcase](skills/github-job-showcase) | GitHub 仓库转面试级 README / 作品集 / 简历项目展示 | 原创 |
| [xiaohongshu-content-studio](skills/xiaohongshu-content-studio) | 小红书内容包生成（标题、钩子、正文、封面文案、图片方向） | 原创 |
| [office-doc-presentation](skills/office-doc-presentation) | 办公文档优化（Word/WPS/PPT/PDF 结构优化与排版润色） | 原创 |
| [digital-self](skills/digital-self) | 个人工作流、表达风格、决策模式蒸馏为可复用数字分身 | 改编自 colleague-skill |
| [bestie](skills/bestie) | 闺蜜/同事工作方法与人格蒸馏为可调用 AI Skill | 改编自 colleague-skill |

## 安装方式

每个 Skill 目录独立，可直接复制到 Claude Code skills 目录使用：

```bash
# 示例：安装 ai-agent-workflow
mkdir -p ~/.claude/skills
cp -r skills/ai-agent-workflow ~/.claude/skills/ai-agent-workflow
```

## 原仓库迁移说明

以下 8 个仓库已合并到本仓库，原仓库已删除：

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

## License

各 Skill 保持其原有 License，详见子目录 LICENSE 文件。
