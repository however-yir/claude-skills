---
name: xhs-cover-studio
description: Generate Xiaohongshu (小红书) cover images (1500x2000, 3:4) from prebuilt brand templates. Use this skill whenever the user asks for 小红书封面, XHS cover, 图文封面, 封面模板, DESIGN.md 风格封面, or wants one-click HTML+PNG exports. Also use this skill when the user provides long copy and asks for multiple cover variants (up to 3 images).
---

# XHS Cover Studio

## Overview

This skill turns style templates into ready-to-post Xiaohongshu covers.
It supports 58 brand styles, deterministic PNG export, and auto-generation of up to 3 cover variants from long copy.

## Workflow

1. Confirm style and copy direction.
If style is unspecified, choose a suitable one and state the assumption.

2. Generate cover files.
Use `scripts/build_cover.py` to output HTML and PNG.

3. Return artifacts.
Always return absolute paths for generated HTML and PNG files.

## Quick Start

List available styles:

```bash
python /Users/liuzhuoran/.codex/skills/xhs-cover-studio/scripts/build_cover.py --list-styles
```

Generate one cover:

```bash
python /Users/liuzhuoran/.codex/skills/xhs-cover-studio/scripts/build_cover.py \
  --style apple \
  --series-tag "AI Cover Lab · Demo" \
  --author-name "Codex × You" \
  --author-desc "From DESIGN.md to publish-ready cover" \
  --headline "One template\\nBrand-level look\\nXHS cover" \
  --subheadline "Pick style, change copy, export 1500x2000 in one shot" \
  --feature "Template-first|58 styles ready to edit" \
  --feature "Copy-fast|Headline, cards, tags in one command" \
  --feature "Export-ready|Auto PNG at 1500x2000" \
  --output-dir /Users/liuzhuoran/Documents/Playground/xhs-cover-md/output \
  --filename-prefix demo-apple
```

Generate 3 covers from long copy:

```bash
python /Users/liuzhuoran/.codex/skills/xhs-cover-studio/scripts/build_cover.py \
  --style apple \
  --series-tag "选题实验室" \
  --author-name "Codex" \
  --copy-text "把你的长文案放这里。脚本会自动拆成三个版本的标题、副标题和卖点卡片。适合一次想尝试多种角度时使用。" \
  --auto-variants 3 \
  --output-dir /Users/liuzhuoran/Documents/Playground/xhs-cover-md/output \
  --filename-prefix long-copy-demo
```

## Script Notes

- Script: `/Users/liuzhuoran/.codex/skills/xhs-cover-studio/scripts/build_cover.py`
- Capture helper: `/Users/liuzhuoran/.codex/skills/xhs-cover-studio/scripts/capture.sh`
- Templates: `/Users/liuzhuoran/.codex/skills/xhs-cover-studio/assets/covers/<style>/template.html`
- `--feature` format is `Title|Description` and can be repeated.
- Use `\\n` in text fields to force line breaks.
- Use `--copy-text --auto-variants 3` for long-copy multi-output mode.
- Use `--no-png` when only HTML is needed.

## Quality Checks

Before finalizing:

- Ensure output PNG is exactly `1500x2000`.
- Ensure headline remains readable (usually 2-3 lines).
- Ensure Chinese copy reads naturally for Xiaohongshu.
- Keep the selected style's visual language unchanged unless user requests design edits.

## References

- Style index: `references/style-catalog.md`
- Original upstream project: `/Users/liuzhuoran/Documents/Playground/xhs-cover-md`
