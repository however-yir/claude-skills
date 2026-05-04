# 小红书封面生成工作室 / XHS Cover Studio

一个面向 Codex 的小红书封面生成 Skill：基于 58 套 DESIGN.md 风格模板，快速产出小红书封面 HTML/PNG，并支持长文案一次生成多版本（单次最多 3 张）。

## 这个 Skill 能做什么

这个 Skill 用来把你的想法或文案，快速变成可发布的小红书封面图。它会保持所选品牌风格的一致性，支持替换标题/副标题/卖点等内容，并通过本地脚本稳定导出 `1500x2000` 的 PNG 文件。

## 适用场景

- 小红书图文封面制作
- DESIGN.md 风格封面复刻
- 一键 HTML + PNG 导出
- 长文案拆分为多版本封面
- A/B/C 封面对比（最多 3 张）
- 快速替换标题、副标题、卖点卡片

## 输入

常见输入包括：

- 风格名（例如 `apple`、`notion`、`linear`）
- 主题或核心信息
- 标题与副标题文案
- 可选的特征卡片文案与底部标签
- 可选的长文案（用于多版本自动生成）
- 输出目录与文件名前缀

## 输出

常见输出包括：

- 一张或多张可编辑 HTML
- 对应的 `1500x2000` PNG 文件
- 风格一致的多版本封面
- 可直接使用的绝对路径

## 非目标

这个 Skill 不用于：

- 从零生成全新视觉系统
- 大规模重构模板 CSS 布局
- 小红书正文内容策略本身
- 月度选题或内容日历规划

## 示例提示词

- `用 apple 风格做一张“AI 工具推荐”小红书封面，直接导出 PNG。`
- `这段长文案帮我拆成 3 张不同角度的封面，保持 notion 风格。`
- `给我一套 linear 风格封面，标题更偏求职项目包装。`
- `先列出可用风格，然后用 figma 风格生成一版。`

## 仓库结构

```text
.
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── covers/
│       └── <58 style folders>
├── examples/
│   └── showcase.md
├── references/
│   └── style-catalog.md
└── scripts/
    ├── build_cover.py
    └── capture.sh
```

## 示例集合

可查看 [examples/showcase.md](./examples/showcase.md)，包含单图生成和三图生成的实用命令示例。

## 文件说明

- [SKILL.md](./SKILL.md)：触发逻辑、工作流和命令模式
- [scripts/build_cover.py](./scripts/build_cover.py)：单图/多图核心生成脚本
- [scripts/capture.sh](./scripts/capture.sh)：Chrome headless 截图导出脚本
- [references/style-catalog.md](./references/style-catalog.md)：风格列表索引
- [examples/showcase.md](./examples/showcase.md)：可直接运行的示例命令
- [LICENSE](./LICENSE)：MIT 许可证

## 搭配使用

- `xiaohongshu-content-studio`
- `copywriting`
- `content-humanizer`
- `generate-image`
- `frontend-design`

## 许可证

本项目基于 MIT License 发布，详见 [LICENSE](./LICENSE)。

## 备注

当文案较长且想快速获得 A/B/C 三版封面时，优先使用：`--copy-text --auto-variants 3`。
