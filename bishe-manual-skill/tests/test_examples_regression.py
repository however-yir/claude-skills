from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"


def _run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_sample_outline_word_metrics_matches_golden() -> None:
    result = _run_tool("tools/count_chapter_words.py", "examples/sample-outline.md")

    assert result.returncode == 0, result.stderr
    expected = (GOLDEN_DIR / "sample-outline.metrics.txt").read_text(encoding="utf-8").strip()
    assert result.stdout.strip() == expected


def test_extract_screenshot_placeholders_matches_golden(tmp_path: Path) -> None:
    output_json = tmp_path / "labels.json"
    result = _run_tool(
        "tools/extract_screenshot_placeholders.py",
        "examples/sample-screenshot-placeholders.md",
        "--json-out",
        str(output_json),
    )

    assert result.returncode == 0, result.stderr
    expected = json.loads((GOLDEN_DIR / "sample-screenshot-labels.json").read_text(encoding="utf-8"))
    actual = json.loads(output_json.read_text(encoding="utf-8"))
    assert actual == expected


def test_build_screenshot_plan_matches_golden(tmp_path: Path) -> None:
    labels_json = GOLDEN_DIR / "sample-screenshot-labels.json"
    output_plan = tmp_path / "plan.json"

    result = _run_tool(
        "tools/build_screenshot_plan.py",
        str(labels_json),
        str(output_plan),
        "--base-url",
        "http://127.0.0.1:3000",
        "--output-dir",
        "output/doc",
        "--image-map",
        "image-map.json",
        "--cdp-url",
        "",
    )

    assert result.returncode == 0, result.stderr
    expected = json.loads((GOLDEN_DIR / "sample-screenshot-plan.json").read_text(encoding="utf-8"))
    actual = json.loads(output_plan.read_text(encoding="utf-8"))
    assert actual == expected
