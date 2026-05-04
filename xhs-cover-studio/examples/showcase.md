# Showcase

## Example 1: Single Cover Export

```bash
python /Users/liuzhuoran/.codex/skills/xhs-cover-studio/scripts/build_cover.py \
  --style apple \
  --series-tag "AI 工具图鉴" \
  --author-name "Codex" \
  --headline "这个工具\n让我写代码\n效率翻倍" \
  --subheadline "从需求到交付，全流程可复用" \
  --output-dir /Users/liuzhuoran/Documents/Playground/xhs-cover-md/output \
  --filename-prefix showcase-single
```

## Example 2: Long Copy to 3 Variants

```bash
python /Users/liuzhuoran/.codex/skills/xhs-cover-studio/scripts/build_cover.py \
  --style notion \
  --series-tag "选题实验室" \
  --author-name "Codex" \
  --copy-text "最近我把多个 AI 工作流整合成一个日常系统。核心是减少切换成本、让信息沉淀、并把重复动作脚本化。这个方案对学生项目、实习任务和副业内容都很实用。" \
  --auto-variants 3 \
  --output-dir /Users/liuzhuoran/Documents/Playground/xhs-cover-md/output \
  --filename-prefix showcase-variants
```

## Example 3: Fixed Copy + Custom Cards

```bash
python /Users/liuzhuoran/.codex/skills/xhs-cover-studio/scripts/build_cover.py \
  --style linear \
  --headline "求职项目\n怎么讲得\n更有说服力" \
  --subheadline "不是堆技术名词，而是展示解决问题的路径" \
  --feature "问题定义|先说业务问题，不先说框架" \
  --feature "方案落地|用可量化结果证明价值" \
  --feature "复盘表达|强调可迁移的方法论" \
  --output-dir /Users/liuzhuoran/Documents/Playground/xhs-cover-md/output \
  --filename-prefix showcase-custom
```
