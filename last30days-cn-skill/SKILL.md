---
name: last30days
version: "3.0-local"
description: "Analyzes the last 30 days of trends across X/Twitter, Weibo, Xiaohongshu, and Douyin, then returns concise Chinese reports with cross-platform overlaps, regional differences, and emerging signals. Use when the user asks about recent trends, social buzz, internet-native topics, China-vs-global narratives, or fast-moving platform analysis."
argument-hint: "last30 最近30天 AI 趋势, last30 中国互联网热点, last30 消费电子"
allowed-tools: Bash, Read, Write, AskUserQuestion
user-invocable: true
---

# last30days

This local variant is a trend-analysis skill, not a general web research skill.

## What This Skill Does

Analyze the last 30 days of discussion across:
- X / Twitter
- Weibo
- Xiaohongshu / RED
- Douyin

Return a structured report in Chinese focused on:
- Top trends
- Cross-platform overlaps
- China vs global narrative differences
- Emerging signals
- High-level takeaways

## Non-Negotiable Rules

- Use only the four platforms above as evidence.
- Never cite Reddit, Hacker News, Polymarket, YouTube, Instagram, TikTok, Bluesky, Truth Social, or generic blogs/news sites.
- Douyin and TikTok are not interchangeable.
- Keep the evidence window to the last 30 days.
- Output in Chinese.
- If a platform is unavailable, say so explicitly and lower confidence instead of silently replacing it with another source.

## Read These Files

Before running tools for any real request, read these files in order:

1. `references/source-policy.md`
2. `references/backend-status.md`
3. `references/execution-workflow.md`
4. `references/report-template.md`

## Tooling Strategy

- Use `Bash` to run the bundled script for all four platforms (X / Weibo / Xiaohongshu / Douyin).
- Do not use `WebSearch` as a primary data path in this variant.
- Use `Read` for references and local outputs.
- Use `AskUserQuestion` only when the user gave an underspecified scope and a wrong assumption would materially change the report.

## Start Every Run Like This

Before any tool call, briefly restate:

- topic or scope
- time window = last 30 days
- platforms = X / Weibo / Xiaohongshu / Douyin
- output language = Chinese

Then follow `references/execution-workflow.md`.
