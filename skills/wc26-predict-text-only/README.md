# wc26-predict-text-only -- WC26 Text-Only Rebuild Skill

[![Codex](https://img.shields.io/badge/Codex-compatible-6e3bff)](https://github.com/anthropics/claude-code)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-d97706)](https://github.com/anthropics/claude-code)

适用于 **Codex / Claude Code** 双平台的纯文本 WC26 预测项目重建 skill。它用于在只能分发 `.md` / `.txt` 文件的环境里，基于内置参考文档还原一个可运行的 ELO 版 WC26 预测应用。

## Skill Card

- 用途：从 `references/*.md` 中重建 WC26 预测项目所需代码和数据文件，不依赖上游 GitHub 仓库下载。
- 触发场景：用户需要“只含 md/txt 的 skill”、要把 WC26 预测项目发给无法接收完整仓库的朋友，或希望在离线/受限环境中重建项目。
- 安装：从本仓库根目录执行。

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
cp -R skills/wc26-predict-text-only ~/.claude/skills/wc26-predict-text-only
cp -R skills/wc26-predict-text-only ~/.codex/skills/wc26-predict-text-only
```

- 测试：纯知识/文本分发 skill；维护检查为 `SKILL.md` frontmatter、`README.md`、`LICENSE`。
- 示例 prompt：`给我一个只含 md/txt 的 WC26 预测 skill，并直接帮我在本地重建项目。`

## 项目概述

这个 skill 面向“只能传文本、不能传完整仓库”的交付场景。它把一个可运行的 WC26 ELO 预测项目拆成若干参考文档，再由 agent 按固定流程把这些文档还原回项目文件。

skill 的设计目标是：

- 保持分发内容为纯文本；
- 不依赖下载上游仓库；
- 保留 ELO 工作流以及天气/球场辅助分析；
- 明确声明 Dixon-Coles 模型文件未随 text-only 版本分发。

## 仓库结构

```text
skills/wc26-predict-text-only/
  SKILL.md
  README.md
  LICENSE
  references/
    app-files.md
    data-core.md
    data-schedule.md
```

## 使用方式

触发后，agent 应按 `SKILL.md` 中的约束执行：

1. 创建 `elo/`、`data/`、`data/cache/` 目录结构。
2. 读取 `references/` 下的参考文档。
3. 将代码块中的文件内容逐个写回目标项目。
4. 安装缺失的 R 依赖。
5. 先做 source check，再做运行检查。
6. 需要时启动 Shiny 应用，并返回本地访问地址。

## 验证预期

重建完成后，应至少能说明以下结果：

- 项目写入到了哪个目录；
- 使用了哪些 `references/*.md`；
- 是否安装了 R 依赖；
- 是否已启动应用；
- 若已启动，对应的 localhost URL；
- 天气和球场数据默认作为辅助分析；
- Dixon-Coles 不包含在 text-only 版本中。

## License

请以仓库内 `LICENSE` 文件为准。
