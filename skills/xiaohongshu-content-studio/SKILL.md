---
name: xiaohongshu-content-studio
description: Use when creating Xiaohongshu content such as note topics, titles, hook lines, body copy, carousel structure, cover text, image concepts, visual direction, and posting packages. Trigger this for personal branding, project sharing, study notes, AI tool posts, before-after posts, and content that needs to feel native to Xiaohongshu rather than generic AI writing.
argument-hint: "[topic, product, or experience to share]"
version: "1.0.0"
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, WebFetch, WebSearch
---

# Xiaohongshu Content Studio

Use this skill when the goal is not just to write a post, but to create a Xiaohongshu-ready content package that feels natural, specific, and visually coherent.

The output should sound like a real person with experience, not a generic productivity template. Favor clarity, useful detail, and platform-native rhythm over corporate polish.

## Inputs

Useful inputs for this skill include:
- the topic, product, project, or experience you want to share
- your persona, tone, and target audience
- the post objective such as attracting clicks, building trust, sharing experience, or showing a project
- any examples, screenshots, data points, or before-after material
- whether you need titles only, full body copy, carousel direction, or a complete posting package

## Outputs

Strong outputs from this skill usually include:
- several title options with different hook styles
- cover text options
- a clear post angle and outline
- final body copy written in a Xiaohongshu-native rhythm
- image, cover, or carousel directions
- optional comment guidance or call-to-action suggestions

## Non-goals

This skill is not the best fit for:
- formal technical documentation or office reports
- generic SEO blog posts aimed at search engines first
- image generation without any content strategy context
- posts that should sound corporate, sterile, or platform-agnostic

## Workflow

1. Set the post objective.
Choose the dominant intent:
- attract clicks
- share experience
- teach something
- build trust
- package a project
- spark discussion

2. Define the persona and audience.
Be explicit about:
- who is speaking
- what credibility they have
- what problem the reader cares about
- what tone fits the post

3. Build the content package.
Whenever possible, produce:
- title options
- cover text
- post outline
- final body copy
- image or carousel directions
- optional comment guidance or CTA

4. Make it feel platform-native.
Favor:
- short readable paragraphs
- specific examples
- concrete numbers or scenes
- emotionally grounded hooks
- less AI polish, more lived-in phrasing

## Quality Bar

Avoid:
- vague "干货分享" filler
- over-formal wording
- too many empty adjectives
- clickbait that the body cannot support
- visual directions that ignore layout practicality

## Examples

### Example 1: Project packaging
User request:
> 把我的校园招聘推荐系统包装成一篇小红书笔记。

Good use of this skill:
- choose a believable personal angle instead of sounding like a press release
- turn system features into readable project-sharing beats
- provide title, cover text, body copy, and carousel direction as one package

### Example 2: AI tools post
User request:
> 帮我写一篇我本地部署 Qwen 的分享，想让人觉得真实，不要太 AI 味。

Good use of this skill:
- focus on what you actually used and learned
- keep the tone grounded in personal experience
- avoid empty hype and generic productivity claims

### Example 3: Cover and hook generation
User request:
> 给我 10 个封面标题和 3 套轮播图方向。

Good use of this skill:
- vary hook style instead of repeating one template
- keep cover text short and readable at small size
- make the visual direction match the topic and persona

## Pairing With Other Skills

Use these when useful:
- `copywriting` for titles and hooks
- `content-creator` for full post drafts
- `content-humanizer` and `copy-editing` for tone cleanup
- `brand-guidelines` and `ad-creative` for visual consistency
- `infographics` and `generate-image` for carousel or cover direction

## Triggers

Common requests that should trigger this skill:
- "帮我写一篇小红书"
- "给我几个封面标题"
- "帮我做轮播图文案"
- "把这个项目包装成小红书笔记"
- "生成配图和封面方向"

## Reference

Read [references/checklist.md](references/checklist.md) when you need a post package checklist.
