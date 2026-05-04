#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[check-secrets] Scanning repository for common credential patterns..."

PATTERNS=(
  'sk-[A-Za-z0-9]{20,}'
  'AKIA[0-9A-Z]{16}'
  'ASIA[0-9A-Z]{16}'
  'LTAI[0-9A-Za-z]{12,}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'gh[pousr]_[A-Za-z0-9]{20,}'
  'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'
)

IGNORE_ARGS=(
  --glob '!**/.git/**'
  --glob '!**/.venv/**'
  --glob '!**/venv/**'
  --glob '!**/node_modules/**'
  --glob '!**/__pycache__/**'
  --glob '!tests/data/**'
  --glob '!tests/data_scanned/**'
  --glob '!tests/**/*.json'
  --glob '!uv.lock'
  --glob '!CHANGELOG.md'
)

HIT=0
for pattern in "${PATTERNS[@]}"; do
  if rg -n --pcre2 "$pattern" . "${IGNORE_ARGS[@]}" >/tmp/docforge_secret_hits.txt 2>/dev/null; then
    echo "[check-secrets] Potential hit for pattern: $pattern"
    cat /tmp/docforge_secret_hits.txt
    HIT=1
  fi
done

rm -f /tmp/docforge_secret_hits.txt

if [[ "$HIT" -eq 1 ]]; then
  echo "[check-secrets] Failed: potential secrets detected."
  exit 1
fi

echo "[check-secrets] Passed: no obvious secret patterns found."
