# Backend Status

This local derivative now has native collection paths for all four target platforms.

## Current Capability Matrix

| Platform | Current state | How to collect |
| --- | --- | --- |
| X / Twitter | Native support exists | Bundled script |
| Weibo | Native support exists (cookie-auth) | Bundled script (`WEIBO_SUB`) |
| Xiaohongshu / RED | Native support exists | Bundled script via local Xiaohongshu API |
| Douyin | Native support exists | Bundled script (public hot-search API) |
| TikTok global | Native support exists but forbidden in this variant | Do not use as Douyin substitute |

## Locate Skill Root

Use this before running any bundled script:

```bash
for dir in \
  "." \
  "$HOME/.codex/skills/last30days" \
  "$HOME/.claude/skills/last30days" \
  "$HOME/.agents/skills/last30days"; do
  [ -f "$dir/scripts/last30days.py" ] && SKILL_ROOT="$dir" && break
done

if [ -z "${SKILL_ROOT:-}" ]; then
  echo "ERROR: Could not find scripts/last30days.py" >&2
  exit 1
fi
```

## Diagnose Native Backends

Run:

```bash
python3 "${SKILL_ROOT}/scripts/last30days.py" --diagnose
```

Important fields:

- `x_source`, `bird_installed`, `bird_authenticated` for X
- `xiaohongshu` and `xiaohongshu_api_base` for Xiaohongshu
- `weibo` and `weibo_auth_method` for Weibo
- `douyin` for Douyin

## X Collection

Preferred command:

```bash
TMP_JSON="$(mktemp /tmp/last30days-x.XXXXXX.json)"
TMP_LOG="$(mktemp /tmp/last30days-x.XXXXXX.log)"
python3 "${SKILL_ROOT}/scripts/last30days.py" "$TOPIC" --emit=json --search x --no-native-web --days=30 >"$TMP_JSON" 2>"$TMP_LOG"
```

Notes:

- X usually needs browser cookies or an `XAI_API_KEY`.
- If the X backend is unavailable, fall back to `WebSearch` restricted to `site:x.com`.
- Read `"$TMP_JSON"` as the structured payload and treat `"$TMP_LOG"` as diagnostics only.

## Xiaohongshu Collection

Preferred command:

```bash
TMP_JSON="$(mktemp /tmp/last30days-xhs.XXXXXX.json)"
TMP_LOG="$(mktemp /tmp/last30days-xhs.XXXXXX.log)"
python3 "${SKILL_ROOT}/scripts/last30days.py" "$TOPIC" --emit=json --search xiaohongshu --no-native-web --days=30 >"$TMP_JSON" 2>"$TMP_LOG"
```

Notes:

- Xiaohongshu uses the local `xiaohongshu-mcp` HTTP service.
- It must be reachable and logged in.
- In JSON output, Xiaohongshu items land in the `web` array with `source_domain = "xiaohongshu.com"`.
- Read `"$TMP_JSON"` as the structured payload and treat `"$TMP_LOG"` as diagnostics only.

## Weibo Collection

Preferred command:

```bash
TMP_JSON="$(mktemp /tmp/last30days-weibo.XXXXXX.json)"
TMP_LOG="$(mktemp /tmp/last30days-weibo.XXXXXX.log)"
python3 "${SKILL_ROOT}/scripts/last30days.py" "$TOPIC" --emit=json --search weibo --no-native-web --days=30 >"$TMP_JSON" 2>"$TMP_LOG"
```

Notes:

- Weibo requires `WEIBO_SUB` cookie (and optional `WEIBO_SUBP`).
- In JSON output, Weibo items land in `web` with `source_domain = "weibo.com"`.

## Douyin Collection

Preferred command:

```bash
TMP_JSON="$(mktemp /tmp/last30days-douyin.XXXXXX.json)"
TMP_LOG="$(mktemp /tmp/last30days-douyin.XXXXXX.log)"
python3 "${SKILL_ROOT}/scripts/last30days.py" "$TOPIC" --emit=json --search douyin --no-native-web --days=30 >"$TMP_JSON" 2>"$TMP_LOG"
```

Notes:

- Douyin uses a native hot-search endpoint (no API key required).
- In JSON output, Douyin items land in `web` with `source_domain = "douyin.com"`.

## Practical Reality

This means the current implementation is:

- script-native for `X`, `Weibo`, `Xiaohongshu`, and `Douyin`
- no mandatory WebSearch fallback path for these four sources
