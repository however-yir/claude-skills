---
name: bishe-manual
description: 用于撰写、补写、压缩、仿写、规范化交付中文毕业设计与毕业设计说明书（兼容课程设计说明书、技术报告）。用户提到毕业设计、毕设说明书、开题报告、任务书、学校模板、样文、参考文献、摘要、图表、截图、Word 成稿、查重口吻优化，或需要基于真实项目代码生成说明书正文时必须使用。内置样文结构学习、样式提取、章节控字、参考文献筛选、Mermaid/PlantUML 图表处理、Chrome MCP/Playwright 截图工作流与 doc/docx 成稿交付。
---

# BiShe Manual

## Overview

这个技能用于把“真实项目事实 + 样文/模板 + 文献约束 + 图表截图 + Word 成稿要求”稳定转化为可交付的《毕业设计说明书》。
目标不是把内容写厚，而是按样文体量、真实项目能力和版式规则，输出结构完整、字数可控、图表齐全的 `.docx` 成稿。

## Scope And Trigger

触发词（命中任一即触发）：

- 毕业设计
- 毕设说明书
- 毕业设计说明书
- 开题报告落稿
- 任务书转正文
- 说明书润色
- 查重降重
- 毕设答辩稿
- 基于项目代码生成说明书

排除词（命中时默认不触发本技能，除非用户明确要求）：

- 周报
- 日报
- 产品 PRD
- 运营文案
- 普通课程作业（非毕业设计）
- 新闻稿
- 社媒文案

冲突规则：

- 同时命中触发词和排除词时，先用一句话确认“是否进入毕业设计说明书流程”。

## Personal Defaults

以下为默认参数，除非用户明确覆盖：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `direction_track` | `software_engineering` | 专业方向默认软件工程/计科应用型项目 |
| `doc_type` | `undergrad_bishe_manual` | 默认文种为“本科毕业设计说明书” |
| `advisor_preference` | `engineering_first` | 章节重实现、重模块、轻空泛理论 |
| `min_year` | `2020` | 参考文献默认最早年份 |
| `cn_count_range` | `10-12` | 中文文献默认数量区间 |
| `en_count_range` | `3-5` | 英文文献默认数量区间 |
| `reference_whitelist` | `CNKI, 万方, 维普, IEEE, ACM, Elsevier, Springer, MDPI` | 优先来源 |
| `reference_blacklist` | `不可核验网页, 无作者条目, 来路不明二次转载` | 默认剔除来源 |
| `naming_template` | `title_only` | 文件名默认使用“标题” |

可切换选项：

- `doc_type`:
  1. `undergrad_bishe_manual`（本科毕业设计说明书）
  2. `undergrad_bishe_report`（本科毕业设计报告）
  3. `course_design_manual`（课程设计说明书）
- `advisor_preference`:
  1. `engineering_first`（工程实现优先）
  2. `theory_first`（理论分析优先）
  3. `experiment_first`（实验评测优先）

## Hard Gates

以下规则是硬约束：

1. 用户第一次说“为项目生成毕业设计说明书”时，必须先索要辅助资料。
2. 输入资料分级：
   - 必需资料：项目源码路径、题目、字数要求、学校模板（若无需用户明确确认“无模板”）
   - 可选资料：往届样文、开题报告、任务书、封面字段要求、导师意见截图
3. 在用户明确表示“没有更多资料”或已经给出可分析资料之前，禁止直接生成正文初稿。
4. 如果用户给了样文或模板，必须先分析样文与样式，先回传“建议目录 + 目标字数 + 样式摘要 + 冲突项”，等待确认后才能开写。
5. 无样文应急流程仅在用户明确同意后启用：按学校模板 + 项目源码 + 默认章节模式写“可修订版初稿”，并显式标记风险。
6. 严禁虚构实验结果、虚构系统模块、虚构部署数据、虚构参考文献。
7. 必须执行敏感信息过滤：账号、口令、密钥、手机号、身份证号、真实服务器公网信息默认脱敏。
8. 输出文件名必须使用题目命名模板，不得使用 `final`、`draft`、`paper-final` 等通用名。
9. 除主说明书 `.docx` 外，必须额外交付一个“附件 `.docx`”，用于收录正文中的 Mermaid / PlantUML / E-R 图源码及关键流程源码。
10. 第 4 章“系统详细设计与实现”默认是全文最长章节，且每个一级模块默认都要包含：模块说明、页面截图、关键实现片段。
11. 第 4 章最长规则允许例外：
    - 学校模板明确要求“实验评测”章节更长
    - 项目是算法/实验型课题且用户确认以实验章为主
12. 若正文数据库设计部分缺少 E-R 图，则视为未完成。
13. 若用户提供任务书/开题报告/模板/样文，必须先分析这些材料，禁止绕过分析直接生成正文。
14. 冲突默认优先级：学校模板 > 任务书/开题报告 > 用户明确要求 > 样文 > 项目源码 > README > 旧说明文档。
15. 允许用户覆盖冲突优先级。覆盖格式：`冲突优先级覆盖: A > B > C`。
16. 旧部署说明、历史演示文档默认低可信；除非用户明确指定，否则不能作为事实主依据。

## Execution States

本技能默认按以下状态机执行：

1. `intake_only`
   只收资料，不写正文。
2. `sample_analysis_done`
   已完成样文/模板/任务书分析，但未开写。
3. `outline_confirmed`
   用户已确认目录、字数和样式方案。
4. `writing_allowed`
   允许开始正文写作。
5. `revision_round`
   根据导师或用户反馈执行定向回改。
6. `qa_gate`
   进入最终校验关卡，未通过不得交付。
7. `delivery_done`
   已生成主说明书、附件与校验产物。

状态约束：

- 未进入 `outline_confirmed` 前，禁止写正文。
- 若用户补交新模板、新样文或新任务书，状态必须退回 `sample_analysis_done`。
- 只有进入 `writing_allowed` 后，才允许生成主说明书 `.md` / `.docx`。
- `revision_round` 完成后必须再次进入 `qa_gate`。

## Core Flow

### 1. 锁定输入

先确认以下输入并确定优先级：

1. 学校模板
2. 任务书/开题报告
3. 往届样文
4. 用户口头要求
5. 项目源码
6. README
7. 旧项目说明文档
8. 技能默认规则

首次响应毕业设计请求时，必须主动告诉用户可提供本地路径，示例：

- `D:\毕业设计模板.docx`
- `D:\毕设样文1.docx`
- `D:\开题报告.pdf`

并明确说明：

- 未提供样文、模板或任务书前，当前阶段只收集资料与分析，不直接开写。
- 用户确认“没有更多资料”后，才可按源码和默认规则继续。

### 2. 冻结项目事实

先读项目代码和文档，再提炼“固定事实底稿”。后续各章只能基于该底稿扩写。

冻结事实时必须区分：

1. 任务书要求
2. 源码实际实现
3. 说明书最终采用口径

若三者不一致，必须在目录确认阶段提前提示，不得写完后再返工。

每章写作前后都要维护“事实来源表”，至少包含：

- `chapter`
- `fact_id`
- `claim`
- `source_type`（template/taskbook/code/readme/user）
- `source_path_or_ref`
- `confidence`

### 3. 学样文，不只学目录

如果用户提供样文或模板，必须同时分析：

- 结构：目录、页数、字数、图表节奏
- 样式：标题、正文、摘要、关键词、图题表题、参考文献、致谢
- 细节：中英文正文的字体字号、段前段后、行距、首行缩进
- 标题：各级标题字体字号、加粗、对齐、分页方式
- 表图代码：图题、表题、表格内容、代码块/代码截图插入位置与样式

对应资源：

- `prompts/sample_analyzer.md`
- `prompts/style_extractor.md`
- `tools/analyze_sample_pdf.py`
- `tools/analyze_docx.py`

### 3.5 先回传设计，再开写

模板和样文分析结束后，必须先回传并等待确认：

1. 当前建议目录
2. 各章目标字数
3. 正文/标题/摘要/关键词/图题/表题样式
4. 与默认规则冲突项

回传时默认输出 4 张表：

1. 输入资料表
2. 建议目录表
3. 字数预算表
4. 样式与冲突表

若用户补充了新样文、模板或任务书，必须中断写作并回到本步骤重分析。

### 4. 先定字数，再写作

写正文前必须生成目标章节字数表。默认贴近样文体量，不默认写厚。

- 写完一章就统计一次，超出即压缩。
- 章节策略默认遵循 `advisor_preference`。
- 第 4 章默认最长；若触发例外规则，需先记录“例外原因 + 用户确认”。

对应资源：

- `prompts/chapter_writer.md`
- `tools/count_chapter_words.py`
- `references/chapter-patterns.md`

### 4.5 章节完成定义（DoD）

每章在进入下一章前，至少满足：

1. 本章事实来源表已更新
2. 有明确小结，且与本章内容一致
3. 关键术语与命名前后一致
4. 图表、截图、代码片段编号连续
5. 未出现“实现了较好效果”等无依据空话

### 5. 图表与截图闭环

图表默认分两档：

- 最小可交付集（必须）：
  1. 系统架构图
  2. 功能模块图
  3. 关键业务流程图
  4. E-R 图（总表 + 核心表）
  5. 测试用例表
- 增强集（按时间和资料补充）：
  1. 权限流程图
  2. 时序图
  3. 部署拓扑图
  4. 关键接口时延/吞吐图

截图默认要求：

- 第 4 章每个主要模块至少 1 张页面截图
- 跨角色模块优先补“管理端 + 用户端”双端截图
- 截图标题必须对应模块名，禁止“系统页面图”这类泛标题

截图失败回退：

1. 无法登录系统时，先保留截图占位并标记原因
2. 以线框图/流程图临时替代，并在附件写明“待替换截图清单”
3. 交付前明确区分“真实截图”和“占位图”

代码片段默认要求：

- 第 4 章每个主要模块至少 1 段关键实现（代码或 SQL）
- 代码用于解释业务规则，不堆大段源码
- 大段源码放附件，不直接塞正文

若存在 `mermaid` / `plantuml`，优先渲染真实图片；失败再退回源码或占位。

对应资源：

- `tools/render_mermaid.py`
- `tools/ensure_thesis_assets.py`
- `tools/extract_screenshot_placeholders.py`
- `tools/build_screenshot_plan.py`
- `tools/capture_thesis_screenshots.py`

### 6. 参考文献先建池再回填

文献工作流必须分 5 步执行：

1. 建候选池
2. 做真实性核验
3. 做相关性筛选
4. 格式化参考文献
5. 生成文献核验清单

默认约束采用参数化，而非写死：

- 年份下限：`min_year`（默认 `2020`）
- 中文数量：`cn_count_range`（默认 `10-12`）
- 英文数量：`en_count_range`（默认 `3-5`）

来源策略：

- 优先 `reference_whitelist`
- 直接剔除 `reference_blacklist`
- 不确定真实性的条目不写入正文

必须增加“引用-正文映射检查”：

- 每条参考文献至少在正文出现 1 次引用落点
- 每个正文引用标记必须能映射到参考文献列表条目
- 发现孤儿引用或孤儿条目必须修复后再交付

文献交付产物默认至少包括：

- 正文参考文献列表
- `references-verified.json` 文献核验清单

文献核验字段：

- `title`
- `authors`
- `year`
- `source`
- `doi_or_url`
- `citation_count_if_available`
- `relevance_note`
- `status`

对应资源：

- `prompts/reference_selector.md`
- `tools/build_reference_pool.py`

### 7. DOCX 成稿交付

如果环境具备 `doc` / `docx` 能力，必须生成 `.docx` 成稿，不得只停留在 Markdown。

交付物至少包括：

1. 主说明书 `.md`
2. 主说明书 `.docx`
3. 图像映射文件
4. 附件 `.docx`
5. `references-verified.json`
6. 答辩版精简稿 `.docx`

命名模板（至少支持二选一）：

1. `title_only`：`题目.docx`
2. `student_name_title`：`学号-姓名-题目-毕业设计说明书.docx`

派生文件命名示例：

- `题目.md`
- `题目.docx`
- `题目-附件.docx`
- `题目-image-map.json`
- `题目-文献核验清单.json`
- `题目-答辩版.docx`

附件 `.docx` 默认内容：

- 正文中的 Mermaid / PlantUML 源码
- 数据库 E-R 图源码
- 关键流程图源码
- 必要时补充核心 SQL / 接口结构说明

答辩版精简稿要求：

- 删除超长源码段，仅保留关键片段
- 合并重复图表
- 每章结尾补“答辩要点”小节

默认样式规则：

- 摘要、Abstract、参考文献、致谢标题居中
- 摘要与 Abstract 独立分页
- 一级章节分页开始
- 中文正文宋体，英文正文 Times New Roman
- 中文关键词单独成段，顶格；“关键词：”黑体小四加粗，内容宋体小四
- 英文关键词单独成段，顶格，不首行缩进，Times New Roman 小四
- 参考文献悬挂缩进

对应资源：

- `prompts/docx_formatter.md`
- `tools/generate_thesis_docx.py`
- `tools/analyze_docx.py`
- `references/default-style.md`

### 8. 最终检查（QA Gate）

交付前必须检查：

- 章节完整
- 字数接近样文目标
- 参考文献比例正确
- 引用-正文映射通过
- 图表编号连续
- 是否残留占位符
- `.docx` 是否真实存在
- 主说明书文件名是否符合命名模板
- 附件 `.docx` 是否真实存在
- 第 4 章是否满足“最长或例外已确认”
- 第 4 章每个主要模块是否包含截图
- 第 4 章每个主要模块是否包含关键实现片段
- 第 3 章设计图数量是否达标
- E-R 图是否按要求包含总表图和核心表图
- 文献年份是否满足 `min_year`
- 是否混入低可信旧文档事实

新增 AI 套话检测（命中后需改写）：

- “具有重要意义”
- “实现了良好效果”
- “具有较高实用价值”
- “在一定程度上”
- “为后续研究奠定基础”

命中规则：

- 单章重复命中 >= 3 次，必须改写该章。

只有通过该关卡，状态才允许从 `qa_gate` 进入 `delivery_done`。

### 9. 回改与答辩支持

导师或用户反馈后必须进入 `revision_round`，并输出“修改影响清单”：

1. 改动章节
2. 改动原因
3. 事实来源变化
4. 是否影响图表/引用/字数

必须生成“答辩问答清单（默认 20 题）”，覆盖：

- 选题背景
- 技术选型
- 核心模块
- 数据库设计
- 安全与权限
- 测试与性能
- 局限性与改进

每题至少包含：

- 标准回答（30-90 秒）
- 追问点
- 回答禁区（不能说的模糊话）

版本快照命名规则：

- `v0-intake`
- `v1-outline-confirmed`
- `v2-writing`
- `v3-revision-YYYYMMDD`
- `v4-qa-pass`
- `v5-delivery`

每次进入新状态都要保留快照，防止回改覆盖。

## Style Guardrails

正文语言默认遵循以下约束：

1. 模仿样文的章节推进节奏，不机械复刻原句。
2. 优先写项目事实，不先写空泛结论。
3. 避免密集排比句、模板化总分总和明显 AI 套话。
4. 每章至少一部分直接对应源码中的真实模块、真实规则或真实数据结构。
5. 致谢可自然，但正文章节不口语化。
6. 全文默认称呼统一为“毕业设计/毕业设计说明书”，不再使用“论文”作为主称呼。

最终检查细则见：

- `prompts/final_checker.md`

## Resource Map

- 项目输入与冲突决策：`prompts/intake.md`
- 样文结构分析：`prompts/sample_analyzer.md`
- 样式提取：`prompts/style_extractor.md`
- 项目事实提取：`prompts/fact_extractor.md`
- 章节写作与控字：`prompts/chapter_writer.md`
- 参考文献筛选：`prompts/reference_selector.md`
- Word 格式化：`prompts/docx_formatter.md`
- 最终检查：`prompts/final_checker.md`

- 默认版式：`references/default-style.md`
- 章节模式：`references/chapter-patterns.md`

- 统计章节字数：`tools/count_chapter_words.py`
- 分析样文 PDF：`tools/analyze_sample_pdf.py`
- 分析样文 DOCX：`tools/analyze_docx.py`
- 检查参考文献池：`tools/build_reference_pool.py`
- 生成文献核验清单模板：`tools/write_reference_verification_template.py`
- 图表与截图补全检查：`tools/ensure_thesis_assets.py`
- 提取截图占位符：`tools/extract_screenshot_placeholders.py`
- 生成图源码附件 DOCX：`tools/generate_diagram_appendix_docx.py`
- 生成截图计划：`tools/build_screenshot_plan.py`
- 自动抓取页面截图：`tools/capture_thesis_screenshots.py`
- 渲染 Mermaid：`tools/render_mermaid.py`
- 生成 DOCX：`tools/generate_thesis_docx.py`
