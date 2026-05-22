# local-ai-systems-studio &mdash; Local AI Systems Studio Skill

[![Codex](https://img.shields.io/badge/Codex-compatible-6e3bff)](https://github.com/anthropics/claude-code)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-d97706)](https://github.com/anthropics/claude-code)

适用于 **Codex / Claude Code** 双平台的本地 AI 系统规划技能。聚焦本地模型选型、部署方案评估（MLX/GGUF/Ollama/LM Studio/vLLM）、硬件适配与执行计划输出。

## Skill Card

- 用途：把本地 AI 想法、问题或模糊需求转成可执行系统方案，覆盖模型选型、部署路径、硬件适配和执行计划。
- 触发场景：用户在比较 MLX / GGUF / Ollama / LM Studio / vLLM，或询问某台机器能否本地跑某类 AI 工作流。
- 安装：从本仓库根目录执行。

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
cp -R skills/local-ai-systems-studio ~/.claude/skills/local-ai-systems-studio
cp -R skills/local-ai-systems-studio ~/.codex/skills/local-ai-systems-studio
```

- 测试：纯知识 skill；维护检查为 `SKILL.md` frontmatter、`README.md`、`LICENSE`。
- 示例 prompt：`我有一台 M4 Mac mini，想本地跑代码问答和文档总结，帮我选模型、工具和部署路径。`

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 目标与场景](#2-目标与场景)
- [3. 核心能力](#3-核心能力)
- [4. Quick Start](#6-quick-start)
- [5. License](#12-license)

## 1. 项目概述

本仓库是一个 **Codex / Claude Code 双平台通用 Skill**，用于将本地 AI 想法转化为可执行的系统方案——覆盖任务分析、模型与工具评估、部署路径选择和执行规划。

## 2. 目标与场景

适用场景：

- 选择本地 LLM 部署方案（MLX vs GGUF vs Ollama vs LM Studio vs vLLM）。
- 评估本地模型对特定任务的适用性。
- 设计本地 AI 工作流的端到端架构。
- 将模糊的"我想在本地跑一个 AI 系统"转化为具体执行计划。
- 排查本地 AI 工作流的性能与可靠性问题。

## 3. 核心能力

- 任务分析与问题澄清。
- 本地模型与工具的多维度对比。
- 部署方案推荐（含硬件适配）。
- 分阶段执行计划输出。
- 风险与依赖显式标注。

## 4. Quick Start

**Claude Code / Codex**：从本合集仓库根目录复制 skill 目录。

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
cp -R skills/local-ai-systems-studio ~/.claude/skills/local-ai-systems-studio
cp -R skills/local-ai-systems-studio ~/.codex/skills/local-ai-systems-studio
```

## 5. License

请以仓库内现有 License 文件为准。
