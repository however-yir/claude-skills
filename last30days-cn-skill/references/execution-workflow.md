# Execution Workflow

## 1. Parse The Request

Identify:

- the topic or landscape scope
- whether the user wants a broad market scan or a single-topic scan
- whether the report should compare China vs global narratives explicitly

If the scope is broad, create a small query basket of 3-6 subtopics before searching.
Prefer the user's exact language first, then add obvious aliases or Chinese/English variants only when useful.

## 2. Restate The Plan Before Searching

Before any tool call, state:

- what you are analyzing
- that the window is the last 30 days
- that the platforms are limited to X, Weibo, Xiaohongshu, and Douyin
- that the output will be in Chinese

## 3. Collect All Four Platforms With The Bundled Script

Locate `SKILL_ROOT` using the snippet from `references/backend-status.md`.

Run focused searches. Preferred pattern:

```bash
TMP_JSON="$(mktemp /tmp/last30days-trends.XXXXXX.json)"
TMP_LOG="$(mktemp /tmp/last30days-trends.XXXXXX.log)"
python3 "${SKILL_ROOT}/scripts/last30days.py" "$TOPIC" --emit=json --search x,weibo,xiaohongshu,douyin --no-native-web --days=30 >"$TMP_JSON" 2>"$TMP_LOG"
```

Use a timeout of `300000` ms for tool execution.

If you are using multiple subqueries, run them one by one and merge the findings manually.

### How To Read The JSON

- read `"$TMP_JSON"` as the structured payload
- treat `"$TMP_LOG"` as diagnostics only
- `x` contains X posts
- `web` contains native web-shaped items from Weibo / Xiaohongshu / Douyin
- keep `web` items only when `source_domain` ends with one of:
  - `weibo.com`
  - `xiaohongshu.com`
  - `douyin.com`
- ignore any other source arrays in this variant, even if they appear in the schema

## 4. Handle Connector Gaps Explicitly

If a native connector is unavailable:

- keep the other sources strict and source-clean
- report which platform failed and why (for example, missing `WEIBO_SUB`)
- do not silently replace platform evidence with generic web coverage

## 5. Build The Trend Set

For each platform, collect:

1. trending topics, hashtags, or repeated themes
2. high-engagement or high-velocity posts
3. 2-3 representative examples per major trend
4. repeated phrasing or narratives that show the trend is real

Then cluster similar signals into unified trends.

## 6. Distinguish Trend Type

For each cluster, decide whether it is:

- `短期 hype`: sharp spike, meme-like, event-driven, weak staying power
- `持续趋势`: repeated across time, formats, or platforms, with clear downstream implications

Do not guess. Use evidence density, cross-platform repetition, and persistence cues.

## 7. Compare China Vs Global Narratives

Always look for:

- cross-platform overlaps
- sentiment or framing differences
- local platform-native expressions
- whether the same topic is treated as product, meme, policy, creator story, or consumer signal depending on region

As a default mapping:

- `X` skews more global
- `Weibo`, `Xiaohongshu`, and `Douyin` skew more China-local

Use that as context, not as a shortcut.

## 8. Write The Report

Follow `references/report-template.md` exactly.

Additional writing rules:

- be concise
- be analytical
- make evidence do the work
- no fluff
- no raw links
- call out missing coverage if one platform was unavailable

## 9. If A Platform Is Unavailable

Do this explicitly:

- say which platform was unavailable
- keep the rest of the report source-clean
- lower confidence where relevant
- do not backfill from disallowed sources
