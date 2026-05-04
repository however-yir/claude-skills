#!/usr/bin/env python3
"""Validate project environment examples and selected runtime variables."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent


def _read_env_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    if not path.exists():
        return keys

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def _is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def main() -> int:
    main_env = ROOT / ".env.example"
    actor_env = ROOT / ".actor" / ".env.example"

    required_main = {
        "DOCLING_VLM_API_URL",
        "DOCLING_VLM_OLLAMA_URL",
        "DOCLING_VLM_LMSTUDIO_URL",
        "DOCLING_VLM_OPENAI_URL",
        "DOCLING_CACHE_DIR",
        "DOCLING_ARTIFACTS_PATH",
        "DOCLING_SERVE_API_ENDPOINT",
        "DOCLING_ACTOR_LOG_KEY",
        "DOCLING_ACTOR_MANIFEST_KEY",
    }
    required_actor = {
        "DOCLING_SERVE_API_ENDPOINT",
        "DOCLING_ACTOR_LOG_KEY",
        "DOCLING_ACTOR_MANIFEST_KEY",
    }

    missing: list[str] = []

    main_keys = _read_env_keys(main_env)
    actor_keys = _read_env_keys(actor_env)

    for key in sorted(required_main - main_keys):
        missing.append(f"{main_env}: missing key {key}")
    for key in sorted(required_actor - actor_keys):
        missing.append(f"{actor_env}: missing key {key}")

    url_keys = [
        "DOCLING_VLM_API_URL",
        "DOCLING_VLM_OLLAMA_URL",
        "DOCLING_VLM_LMSTUDIO_URL",
        "DOCLING_VLM_OPENAI_URL",
        "DOCLING_SERVE_API_ENDPOINT",
    ]

    invalid_urls: list[str] = []
    for key in url_keys:
        val = os.getenv(key)
        if not val:
            continue
        if not _is_valid_url(val):
            invalid_urls.append(f"env {key} has invalid URL: {val}")

    if missing or invalid_urls:
        print("[validate-env] FAILED")
        for item in missing + invalid_urls:
            print(f" - {item}")
        return 1

    print("[validate-env] PASSED")
    print(f" - checked: {main_env}")
    print(f" - checked: {actor_env}")
    print(" - URL syntax validated for exported env keys when present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
