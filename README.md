# Claude Skills Collection

[![CI](https://github.com/however-yir/claude-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/however-yir/claude-skills/actions/workflows/ci.yml)

这是一个面向 **Claude Code / Codex** 的可安装、可维护 AI 工作流工具箱，不是普通资料合集。

每个 skill 都应能被独立复制到本地 skills 目录，被 Claude Code 或 Codex 读取 `SKILL.md` 后触发使用；根目录负责统一索引、安装说明、状态标记和 CI 质量闸门。

## Status Policy

| 状态 | 含义 |
|------|------|
| `stable` | 可日常安装使用，README / SKILL.md / LICENSE 齐全，已有测试或明确为纯知识 skill。 |
| `draft` | 可试用，但触发边界、依赖、测试或交付格式仍在迭代。 |
| `archived` | 保留为迁移记录或参考项目，不作为当前主推安装项维护。 |

## Install

### 单个安装

从本仓库根目录执行。Claude Code 默认使用 `~/.claude/skills`，Codex 本地 skills 目录常用 `~/.codex/skills`；如果你有自定义路径，把 `DEST` 改成对应目录即可。

```bash
# Claude Code
DEST="$HOME/.claude/skills"
mkdir -p "$DEST"
rm -rf "$DEST/ai-agent-workflow"
cp -R skills/ai-agent-workflow "$DEST/ai-agent-workflow"

# Codex
DEST="$HOME/.codex/skills"
mkdir -p "$DEST"
rm -rf "$DEST/ai-agent-workflow"
cp -R skills/ai-agent-workflow "$DEST/ai-agent-workflow"
```

### 批量安装 `skills/*`

```bash
DEST="$HOME/.claude/skills"
mkdir -p "$DEST"

for skill in skills/*/; do
  name="$(basename "$skill")"
  rm -rf "$DEST/$name"
  cp -R "$skill" "$DEST/$name"
done
```

把 `DEST` 换成 `$HOME/.codex/skills` 即可批量安装到 Codex 本地 skills 目录。

### 项目内安装

如果只想让当前项目使用这些 skills：

```bash
mkdir -p .claude/skills
cp -R skills/github-job-showcase .claude/skills/github-job-showcase
```

### 卸载

```bash
# 卸载单个 skill
rm -rf "$HOME/.claude/skills/ai-agent-workflow"
rm -rf "$HOME/.codex/skills/ai-agent-workflow"

# 卸载本仓库批量安装的 skills/*
for skill in skills/*/; do
  name="$(basename "$skill")"
  rm -rf "$HOME/.claude/skills/$name"
  rm -rf "$HOME/.codex/skills/$name"
done
```

## Skills

| Skill | 用途 | 安装源 | 测试 | 状态 |
|-------|------|--------|------|------|
| [ai-agent-workflow](skills/ai-agent-workflow) | AI Agent 工作流设计：prompts、MCP、评估循环、workflow spec | `skills/ai-agent-workflow` | 纯知识 skill；CI 包装检查 | `stable` |
| [local-ai-systems-studio](skills/local-ai-systems-studio) | 本地 LLM 选型与部署规划：MLX、GGUF、Ollama、LM Studio、vLLM | `skills/local-ai-systems-studio` | 纯知识 skill；CI 包装检查 | `draft` |
| [java-fullstack-engineering](skills/java-fullstack-engineering) | Spring Boot / MyBatis / SQL / API 加固与全栈工程任务 | `skills/java-fullstack-engineering` | 纯知识 skill；CI 包装检查 | `stable` |
| [github-job-showcase](skills/github-job-showcase) | GitHub 仓库转求职 README、简历 bullets、面试项目叙事 | `skills/github-job-showcase` | 纯知识 skill；CI 包装检查 | `stable` |
| [xiaohongshu-content-studio](skills/xiaohongshu-content-studio) | 小红书内容包：标题、钩子、正文、封面文案、轮播方向 | `skills/xiaohongshu-content-studio` | 纯知识 skill；CI 包装检查 | `stable` |
| [office-doc-presentation](skills/office-doc-presentation) | Word / WPS / PPT / PDF 的结构优化、润色与汇报材料制作 | `skills/office-doc-presentation` | 纯知识 skill；CI 包装检查 | `draft` |
| [digital-self](skills/digital-self) | 将个人材料、表达风格和工作判断蒸馏为数字分身 skill | `skills/digital-self` | `cd skills/digital-self && pytest tests/` | `draft` |
| [bestie](skills/bestie) | 将搭子/同事的工作方法、表达风格沉淀为可调用 AI Skill | `skills/bestie` | `cd skills/bestie && pytest tests/` | `draft` |

## Independent And Legacy Projects

这些目录也保留在仓库中，但不属于根 CI 当前遍历的 `skills/*` 包装检查。

| 项目 | 用途 | 安装/使用 | 测试 | 状态 |
|------|------|-----------|------|------|
| [last30days-cn-skill](last30days-cn-skill/) | 中国社媒趋势分析：X、微博、小红书、抖音 | `cp -R last30days-cn-skill ~/.claude/skills/last30days` | `cd last30days-cn-skill && pytest tests/` | `stable` |
| [bishe-manual-skill](bishe-manual-skill/) | 中文毕业设计说明书撰写、样文仿写、DOCX 交付 | `cp -R bishe-manual-skill ~/.claude/skills/bishe-manual` | `cd bishe-manual-skill && pytest tests -q` | `stable` |
| [xhs-cover-studio](xhs-cover-studio/) | 小红书封面生成，包含品牌风格 HTML/PNG 模板 | `cp -R xhs-cover-studio ~/.claude/skills/xhs-cover-studio` | 需 Chrome + Python，当前以人工验收为主 | `draft` |
| [lz-docforge](lz-docforge/) | DocForge：基于 Docling 的中文文档处理工程化实验项目 | `cd lz-docforge && pip install -e .` | `cd lz-docforge && pytest tests/` | `archived` |

## Skill Contract

`skills/<skill-name>/` 目录约定：

```text
skills/<skill-name>/
  SKILL.md        # 必须：YAML frontmatter（--- 分隔，至少包含 name / description）
  README.md       # 必须：用途、触发场景、安装、测试、示例 prompt
  LICENSE         # 必须：默认 MIT，或保留原项目 license
  references/     # 可选：按需加载的参考文档
  examples/       # 可选：使用示例
  tests/          # 可选：pytest 或 README 说明
  scripts/        # 可选：可执行脚本
  tools/          # 可选：工具函数
  prompts/        # 可选：Prompt 模板
```

根 CI（[`.github/workflows/ci.yml`](.github/workflows/ci.yml)）会在 push / PR 时检查 `skills/*` 下每个 skill 是否满足：

- `SKILL.md` 存在并包含 YAML frontmatter
- `README.md` 存在
- `LICENSE` 存在
- Python skill 的 `requirements.txt` 与 `tests/` 目录可被识别

有真实 pytest 测试的 skill 需要在修改后本地运行对应测试。

## Migration Notes

以下独立仓库已合并到本仓库：

| 原仓库名 | 新位置 | 说明 |
|----------|--------|------|
| `codex-skill-ai-agent-workflow` | [skills/ai-agent-workflow](skills/ai-agent-workflow) | AI Agent 工作流 |
| `codex-skill-local-ai-systems-studio` | [skills/local-ai-systems-studio](skills/local-ai-systems-studio) | 本地 LLM 部署 |
| `codex-skill-java-fullstack-engineering` | [skills/java-fullstack-engineering](skills/java-fullstack-engineering) | Java 全栈工程 |
| `codex-skill-github-job-showcase` | [skills/github-job-showcase](skills/github-job-showcase) | 求职作品集 |
| `codex-skill-xiaohongshu-content-studio` | [skills/xiaohongshu-content-studio](skills/xiaohongshu-content-studio) | 小红书内容 |
| `codex-skill-office-doc-presentation` | [skills/office-doc-presentation](skills/office-doc-presentation) | 办公文档 |
| `digital-self-skill` | [skills/digital-self](skills/digital-self) | 数字分身 |
| `bestie-skill` | [skills/bestie](skills/bestie) | 搭子/同事 Skill |
| `last30days-cn-skill` | [last30days-cn-skill](last30days-cn-skill/) | 社媒趋势分析 |
| `xhs-cover-studio` | [xhs-cover-studio](xhs-cover-studio/) | 小红书封面 |
| `bishe-manual-skill` | [bishe-manual-skill](bishe-manual-skill/) | 毕设说明书 |
| `lz-docforge` | [lz-docforge](lz-docforge/) | 文档处理实验项目 |

## Contributing

新增或修改 skill 时，请优先保持改动可安装、可验证：

1. 更新 `SKILL.md` frontmatter 与触发描述。
2. 更新对应 `README.md` 的 Skill Card。
3. 保留或补齐 `LICENSE`。
4. 如果包含脚本或工具，补充最小 pytest 或在 `tests/README.md` 写清人工验收方式。
5. 本地复刻 CI 检查，并运行有测试的 skill。

## License

本仓库采用 [MIT License](LICENSE)。各子 skill 保持其原有 License，详见子目录 `LICENSE` 文件。
