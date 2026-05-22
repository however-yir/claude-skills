# office-doc-presentation &mdash; Office Doc Presentation Skill

[![Codex](https://img.shields.io/badge/Codex-compatible-6e3bff)](https://github.com/anthropics/claude-code)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-d97706)](https://github.com/anthropics/claude-code)

适用于 **Codex / Claude Code** 双平台的办公文档技能。聚焦 Word/WPS/PPT/PDF 的结构优化、排版润色与演示文稿制作。

## Skill Card

- 用途：创建或优化 Word、WPS、PPT、PDF、报告、提案、总结和项目汇报材料。
- 触发场景：用户要整理笔记、截图、PDF 或会议纪要，输出正式文档、演示稿、项目报告或可提交材料。
- 安装：从本仓库根目录执行。

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
cp -R skills/office-doc-presentation ~/.claude/skills/office-doc-presentation
cp -R skills/office-doc-presentation ~/.codex/skills/office-doc-presentation
```

- 测试：纯知识 skill；维护检查为 `SKILL.md` frontmatter、`README.md`、`LICENSE`。
- 示例 prompt：`把这些会议纪要和截图整理成一份项目复盘 PPT 大纲，并给出每页标题和要点。`

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 目标与场景](#2-目标与场景)
- [3. 核心能力](#3-核心能力)
- [4. 技术栈](#4-技术栈)
- [5. 仓库结构](#5-仓库结构)
- [6. Quick Start](#6-quick-start)
- [7. License](#12-license)

## 1. 项目概述

本仓库是一个 **Codex / Claude Code 双平台通用 Skill**，用于创建和优化办公文档——Word 报告、WPS 文档、PPT 演示、PDF 导出，覆盖从原始材料到最终交付物的完整流程。

## 2. 目标与场景

适用场景：

- 将笔记、PDF、截图整理为结构清晰的办公文档。
- 制作项目汇报 PPT / 课程演示。
- 润色提案、报告，使其更适合正式提交。
- 团队中文档规范的标准化与复用。

## 3. 核心能力

- 文档结构梳理与大纲生成。
- 内容润色与可读性优化。
- 幻灯片故事线与页面布局建议。
- PDF 格式导出前的最后打磨。

## 4. Quick Start

**Claude Code / Codex**：从本合集仓库根目录复制 skill 目录。

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
cp -R skills/office-doc-presentation ~/.claude/skills/office-doc-presentation
cp -R skills/office-doc-presentation ~/.codex/skills/office-doc-presentation
```

## 5. License

请以仓库内现有 License 文件为准。
