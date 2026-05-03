<div align="center">

# 分身.skill

> **非官方声明（Non-Affiliation）**  
> 本仓库为社区维护的衍生/二次开发版本，与上游项目及其权利主体不存在官方关联、授权背书或从属关系。  
> **商标声明（Trademark Notice）**  
> 相关项目名称、Logo 与商标归其各自权利人所有。本仓库仅用于说明兼容/来源，不主张任何商标权利。


> *"把你蒸馏成可调用的数字生命，让关键判断不再只存在于你的脑子里。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

你的方法论只在你脑子里，团队无法复用？<br>
你的表达风格和决策路径很强，但新人很难接住？<br>
你想把自己的经验、习惯、判断标准沉淀成可调用能力？<br>
你希望在高压场景里，AI 能够“像你一样”思考和回应？<br>

**把你自己做成一个可协作的数字生命分身。**

<br>

提供你的原材料（聊天记录、文档、邮件、语音转写、截图）加上你的主观描述<br>
生成一个**真正能按你的方式工作的 AI Skill**<br>
用你的标准做决策，用你的语气表达结论，在关键场景保持你的风格一致性

[数据来源](#支持的数据来源) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [详细安装说明](INSTALL.md) · [**English**](README_EN.md)

</div>

---

### 改编说明（License）

本项目基于 [titanwings/colleague-skill](https://github.com/titanwings/colleague-skill) 按 **MIT License** 改编。

- 保留了原项目 LICENSE
- 场景从“复刻他人”重构为“蒸馏自己”
- 命令与目录采用“分身”语义（如 `create-digital-self`、`selves/`）

详细来源说明见 [NOTICE](NOTICE)。

---

## 支持的数据来源

> 当前为分身.skill 的 beta 版本，欢迎持续反馈你想接入的来源。

| 来源 | 消息记录 | 文档 / Wiki | 多维表格 | 备注 |
|------|:-------:|:-----------:|:-------:|------|
| 飞书（自动采集） | ✅ API | ✅ | ✅ | 输入姓名即可自动拉取 |
| 钉钉（自动采集） | ⚠️ 浏览器 | ✅ | ✅ | 钉钉 API 不支持完整历史消息 |
| Slack（自动采集） | ✅ API | — | — | 需管理员安装 Bot；免费版限 90 天 |
| 微信聊天记录 | ✅ SQLite | — | — | 推荐先导出再导入 |
| PDF | — | ✅ | — | 手动上传 |
| 图片 / 截图 | ✅ | — | — | 手动上传 |
| 飞书 JSON 导出 | ✅ | ✅ | — | 手动上传 |
| 邮件 `.eml` / `.mbox` | ✅ | — | — | 手动上传 |
| Markdown | ✅ | ✅ | — | 手动上传 |
| 直接粘贴文字 | ✅ | — | — | 手动输入 |

### 推荐的微信聊天记录导出工具

以下工具为独立开源项目，本项目不包含其代码，仅适配其导出格式：

| 工具 | 平台 | 说明 |
|------|------|------|
| [WeChatMsg](https://github.com/LC044/WeChatMsg) | Windows | 微信聊天记录导出，支持多种格式 |
| [PyWxDump](https://github.com/xaoyaoo/PyWxDump) | Windows | 微信数据库解密导出 |
| [留痕](https://github.com/greyovo/留痕) | macOS | 微信聊天记录导出（Mac 用户推荐） |

---

## 安装

### Claude Code

> **重要**：Claude Code 从 **git 仓库根目录** 的 `.claude/skills/` 查找 skill。请在正确位置执行。

```bash
# 安装到当前项目（在 git 仓库根目录执行）
mkdir -p .claude/skills
git clone https://github.com/however-yir/digital-self-skill .claude/skills/create-digital-self

# 或安装到全局（所有项目都能用）
git clone https://github.com/however-yir/digital-self-skill ~/.claude/skills/create-digital-self
```

### OpenClaw

```bash
git clone https://github.com/however-yir/digital-self-skill ~/.openclaw/workspace/skills/create-digital-self
```

### 依赖（可选）

```bash
pip3 install -r requirements.txt
```

> 飞书/钉钉自动采集需配置 App 凭证，详见 [INSTALL.md](INSTALL.md)

---

## 使用

在 Claude Code 中输入：

```
/create-digital-self
```

按提示输入你的身份背景（如 `字节 2-1 后端工程师`）、性格标签、决策偏好，然后选择数据来源。字段都可跳过，仅凭描述也能生成基础版本。

完成后用 `/{slug}` 调用你的分身 Skill。

### 管理命令

| 命令 | 说明 |
|------|------|
| `/list-digital-selves` | 列出所有分身 Skill |
| `/{slug}` | 调用完整 Skill（Persona + Work） |
| `/{slug}-work` | 仅工作能力 |
| `/{slug}-persona` | 仅人格与表达 |
| `/digital-self-rollback {slug} {version}` | 回滚到历史版本 |
| `/delete-digital-self {slug}` | 删除 |

---

## 效果示例

> 输入：`互联网后端工程师，INTJ，重视边界，结果导向，表达直接`

**场景一：架构评审**

```
用户      ❯ 帮我看下这个接口设计

分身.skill ❯ 先补齐目标和约束：吞吐量、延迟预算、失败重试策略。
             再看实现：这里会出现 N+1 查询，建议改批量读取。
             返回结构统一成 {code, message, data}，否则后续客户端要到处兼容。
```

**场景二：任务拆解**

```
用户      ❯ 这个需求今天能上线吗

分身.skill ❯ 能做灰度，但不能直接全量。先切三步：
             1) 开关 + 监控埋点
             2) 小流量验证
             3) 次日放量
             这样你不会在晚上被告警叫醒。
```

---

## 功能特性

### 生成的 Skill 结构

每个分身 Skill 由两部分组成：

| 部分 | 内容 |
|------|------|
| **Part A — Work Skill** | 系统设计偏好、技术规范、流程习惯、经验知识库 |
| **Part B — Persona** | 5 层人格结构：硬规则 → 身份 → 表达风格 → 决策模式 → 人际行为 |

运行逻辑：`接到任务 → Persona 判断取向 → Work Skill 执行 → 用你的语气输出`

### 支持的标签

**个性**：认真负责 · 结果导向 · 完美主义 · 快速试错 · 追求稳定 · 直接表达 · 谨慎保守 · 关注风险 · 擅长推进 · 强执行

**工作文化**：字节范 · 阿里味 · 腾讯味 · 华为味 · 百度味 · 美团味 · 第一性原理 · OKR 驱动 · 创业模式 · 平台化思维

**职级支持**：字节 2-1~3-3+ · 阿里 P5~P11 · 腾讯 T1~T4 · 百度 T5~T9 · 美团 P4~P8 · 华为 13~21 级 · 网易 · 京东 · 小米

### 进化机制

- **追加材料** → 自动分析增量 → merge 到对应能力层，不覆盖既有结论
- **对话纠正** → 你说「我不会这样，我更可能 xxx」→ 写入 Correction 层并即时生效
- **版本管理** → 每次更新自动存档，支持回滚任意历史版本

---

## 项目结构

本项目遵循 [AgentSkills](https://agentskills.io) 开放标准，整个 repo 就是一个 skill 目录：

```
create-digital-self/
├── SKILL.md              # skill 入口（官方 frontmatter）
├── prompts/              # Prompt 模板
│   ├── intake.md         #   对话式信息录入
│   ├── work_analyzer.md  #   工作能力提取
│   ├── persona_analyzer.md #  人格行为提取
│   ├── work_builder.md   #   work.md 生成模板
│   ├── persona_builder.md #   persona.md 五层结构模板
│   ├── merger.md         #   增量 merge 逻辑
│   └── correction_handler.md # 对话纠正处理
├── tools/                # Python 工具
│   ├── feishu_auto_collector.py   # 飞书全自动采集
│   ├── feishu_browser.py          # 飞书浏览器方案
│   ├── feishu_mcp_client.py       # 飞书 MCP 方案
│   ├── dingtalk_auto_collector.py # 钉钉全自动采集
│   ├── slack_auto_collector.py    # Slack 全自动采集
│   ├── email_parser.py            # 邮件解析
│   ├── skill_writer.py            # Skill 文件管理
│   └── version_manager.py         # 版本存档与回滚
├── selves/             # 生成的分身 Skill（gitignored）
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## 注意事项

- **原材料质量决定分身质量**：真实聊天 + 长文档 > 仅手动描述
- 建议优先收集：你**主动写的**长文 > **决策类回复** > 高频协作对话
- 自动采集前先确认合规边界，避免导入敏感数据
- 当前仍是 demo 版本，欢迎提 issue 一起迭代

---

## Star History

<a href="https://www.star-history.com/?repos=however-yir%2Fdigital-self-skill&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=however-yir/digital-self-skill&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=however-yir/digital-self-skill&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=however-yir/digital-self-skill&type=date&legend=top-left" />
 </picture>
</a>

---

<div align="center">

MIT License © [however-yir](https://github.com/however-yir)


</div>
