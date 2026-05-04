# Source Policy

This skill is intentionally narrow. Treat it as a four-platform trend scanner.

## Allowed Evidence

| Platform | Allowed domain / source | Preferred collection path |
| --- | --- | --- |
| X / Twitter | `x.com`, `twitter.com` | Bundled script |
| Weibo | `weibo.com` | Bundled script (native connector) |
| Xiaohongshu / RED | `xiaohongshu.com` | Bundled script |
| Douyin | `douyin.com` | Bundled script (native connector) |

## Hard Exclusions

Do not use these as evidence:

- Reddit
- Hacker News
- Polymarket
- YouTube
- Instagram
- TikTok global
- Bluesky
- Truth Social
- Generic blogs, newsletters, or news sites
- Search-result summaries whose landing pages are outside the four allowed platform domains

## Time Window

- Only use content from the last 30 days.
- Prefer items with explicit dates.
- If a date is missing, treat that item as lower confidence and do not let it anchor a major trend by itself.

## Evidence Quality Rules

For each platform, prioritize:

1. High engagement
2. Fast growth or repeated reposting
3. Repeated phrasing, hashtags, formats, or narratives
4. Representative examples that clearly illustrate the trend

Each major trend should have:

- repeated evidence from multiple posts, or
- clear cross-platform confirmation, or
- strong single-platform intensity that you explicitly label as platform-local

## Platform-Specific Notes

- `Douyin != TikTok`. Do not substitute the bundled TikTok pipeline for Douyin evidence in this variant.
- `Xiaohongshu != generic web`. Only count `xiaohongshu.com` notes as Xiaohongshu evidence.
- `Weibo` evidence must come from the native Weibo connector (`weibo.com` posts), not third-party summaries.
- `X` evidence can come from the bundled script or, if that backend is unavailable, site-restricted `WebSearch`.

## Output Guardrails

- No raw URLs in the final report.
- Use short evidence descriptions such as platform + post angle + engagement cue.
- If one of the four platforms is unavailable, mention it once and keep going with the remaining coverage.
