# ai-agent-workflow &mdash; AI Agent Workflow Skill

[![Codex](https://img.shields.io/badge/Codex-compatible-6e3bff)](https://github.com/anthropics/claude-code)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-d97706)](https://github.com/anthropics/claude-code)

适用于 **Codex / Claude Code** 双平台的 AI 工程工作流技能。聚焦技能化方法沉淀，通过标准化模板帮助团队复用工作流与最佳实践。

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 目标与场景](#2-目标与场景)
- [3. 核心能力](#3-核心能力)
- [4. 技术栈](#4-技术栈)
- [5. 仓库结构](#5-仓库结构)
- [6. Quick Start](#6-quick-start)
- [7. 配置建议](#7-配置建议)
- [8. 开发与测试](#8-开发与测试)
- [9. 协作与发布](#9-协作与发布)
- [10. 路线图](#10-路线图)
- [11. 贡献指南](#11-贡献指南)
- [12. License](#12-license)

## 1. 项目概述

本仓库是一个 **Codex / Claude Code 双平台通用 Skill**，用于设计和改进 AI 工程工作流——涵盖 prompt pipeline、MCP 集成、工具型 agent、评估循环和可复用工作流规范。

同时兼容两个平台：在 Codex 中通过 skill 市场安装，在 Claude Code 中通过 `/skill` 或 plugin 机制加载，SKILL.md 为共用文件。

## 2. 目标与场景

适用场景：

- 将一次性 AI 任务转化为可复用的结构化工作流。
- 在 prompt、skill、MCP server、脚本之间做最优抽象选择。
- 为 agent 设计评估循环和迭代优化流程。
- 团队内 AI 工作流的知识沉淀与规范统一。

## 3. 核心能力

- 提供技能说明、示例与参考资料。
- 支持按场景快速复用与团队协作。
- 支持持续迭代与标准化沉淀。

## 4. 技术栈

- Skill Specification

## 5. 仓库结构

建议优先阅读：

- README.md：项目入口与整体说明。
- docs 或同类目录：架构、规范、部署与 FAQ。
- 核心源码目录：按模块深入阅读。

## 6. Quick Start

**Codex**：在 skill 市场中搜索 `ai-agent-workflow` 一键安装。

**Claude Code**：将本仓库克隆到 skills 目录或通过 plugin 加载：

    git clone https://github.com/however-yir/codex-skill-ai-agent-workflow.git

## 7. 配置建议

建议按 dev / staging / prod 分层配置，并将密钥类信息放入环境变量或密钥管理系统。

## 8. 开发与测试

推荐流程：

1. 基于默认分支创建功能分支。
2. 小步提交并保持提交目标单一。
3. 本地完成构建与测试后再推送。
4. 通过 Pull Request 完成评审与合并。

## 9. 协作与发布

建议使用语义化版本，发布说明应包含新增、修复与兼容性说明。

## 10. 路线图

建议按以下顺序推进：

1. 稳定主流程与关键接口。
2. 优化模块边界与可观测性。
3. 完善自动化测试与文档体系。

## 11. 贡献指南

提交建议包含：变更背景、实现说明、验证结果、风险评估。

## 12. License

请以仓库内现有 License 文件为准。
