#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[verify] running env validation..."
python3 scripts/validate_env.py

echo "[verify] running secret scan..."
bash scripts/check-secrets.sh

echo "[verify] readiness checks passed."
