# xiaohongshu-content-studio &mdash; Xiaohongshu Content Studio Skill

[![Codex](https://img.shields.io/badge/Codex-compatible-6e3bff)](https://github.com/anthropics/claude-code)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-d97706)](https://github.com/anthropics/claude-code)

适用于 **Codex / Claude Code** 双平台的小红书内容创作技能。聚焦标题、封面文字、正文、轮播图方向、配图概念的完整内容包输出。

## Skill Card

- 用途：生成小红书原生感内容包，包括选题、标题、钩子、正文、封面文字、轮播结构和发布建议。
- 触发场景：用户要做个人品牌、项目分享、AI 工具体验、学习笔记、前后对比内容，且希望风格像小红书而非通用 AI 文案。
- 安装：从本仓库根目录执行。

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
cp -R skills/xiaohongshu-content-studio ~/.claude/skills/xiaohongshu-content-studio
cp -R skills/xiaohongshu-content-studio ~/.codex/skills/xiaohongshu-content-studio
```

- 测试：纯知识 skill；维护检查为 `SKILL.md` frontmatter、`README.md`、`LICENSE`。
- 示例 prompt：`围绕我这次用 AI 重构简历的经历，生成一套小红书标题、封面文案、正文和轮播图结构。`

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 目标与场景](#2-目标与场景)
- [3. 核心能力](#3-核心能力)
- [4. Quick Start](#6-quick-start)
- [5. License](#12-license)

## 1. 项目概述

本仓库是一个 **Codex / Claude Code 双平台通用 Skill**，用于生成本地化、真实感强的小红书内容包——包括标题、封面文字、正文、轮播图方向和发布策略。

## 2. 目标与场景

适用场景：

- 个人品牌内容策划与输出。
- 项目/产品分享的社交平台包装。
- AI 工具使用经验分享。
- 学习笔记、前后对比类内容。
- 需要平台原生感而非通用 AI 写作风格的场景。

## 3. 核心能力

- 多种钩子风格的标题生成。
- 封面文字与视觉方向建议。
- 小红书节奏感的正文撰写。
- 轮播图/配图内容方向规划。
- 完整的发布内容包输出。

## 4. Quick Start

**Claude Code / Codex**：从本合集仓库根目录复制 skill 目录。

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
cp -R skills/xiaohongshu-content-studio ~/.claude/skills/xiaohongshu-content-studio
cp -R skills/xiaohongshu-content-studio ~/.codex/skills/xiaohongshu-content-studio
```

## 5. License

请以仓库内现有 License 文件为准。
