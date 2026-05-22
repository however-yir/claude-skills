# java-fullstack-engineering &mdash; Java Fullstack Engineering Skill

[![Codex](https://img.shields.io/badge/Codex-compatible-6e3bff)](https://github.com/anthropics/claude-code)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-d97706)](https://github.com/anthropics/claude-code)

适用于 **Codex / Claude Code** 双平台的 Java 全栈工程技能。聚焦 Spring Boot、MyBatis/JPA、SQL 优化、API 规范、前后端联调与面试级项目加固。

## Skill Card

- 用途：处理 Java 全栈项目的开发、调试、重构、SQL 优化、API 规范和面试级工程加固。
- 触发场景：用户提到 Spring Boot、MyBatis/JPA、慢 SQL、接口联调、管理后台、项目加固、代码审查或 Java 项目面试包装。
- 安装：从本仓库根目录执行。

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
cp -R skills/java-fullstack-engineering ~/.claude/skills/java-fullstack-engineering
cp -R skills/java-fullstack-engineering ~/.codex/skills/java-fullstack-engineering
```

- 测试：纯知识 skill；维护检查为 `SKILL.md` frontmatter、`README.md`、`LICENSE`。
- 示例 prompt：`帮我审这个 Spring Boot 接口和 MyBatis 查询，指出性能风险并给出最小修改方案。`

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 目标与场景](#2-目标与场景)
- [3. 核心能力](#3-核心能力)
- [4. Quick Start](#6-quick-start)
- [5. License](#12-license)

## 1. 项目概述

本仓库是一个 **Codex / Claude Code 双平台通用 Skill**，用于 Java 全栈工程任务的开发、调试、优化与加固——覆盖 Spring Boot 后端、MyBatis/JPA 持久层、SQL 性能、REST API 规范和前端集成。

## 2. 目标与场景

适用场景：

- Spring Boot 功能开发与 Bug 修复。
- MyBatis/JPA SQL 查询优化。
- REST API 规范清理与重构。
- 前后端联调问题排查。
- 课程/毕业设计项目的面试级加固。
- 代码审查与工程规范对齐。

## 3. 核心能力

- Spring Boot 业务逻辑开发与 Bug 修复。
- SQL 查询优化与索引建议。
- API 契约规范与 DTO 边界梳理。
- 性能瓶颈定位（N+1、慢查询、慢接口）。
- 项目加固——校验、异常处理、测试覆盖。

## 4. Quick Start

**Claude Code / Codex**：从本合集仓库根目录复制 skill 目录。

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
cp -R skills/java-fullstack-engineering ~/.claude/skills/java-fullstack-engineering
cp -R skills/java-fullstack-engineering ~/.codex/skills/java-fullstack-engineering
```

## 5. License

请以仓库内现有 License 文件为准。
