from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_build_image_map_prefers_existing_manual_entries(tmp_path: Path) -> None:
    labels = tmp_path / "labels.json"
    image_dir = tmp_path / "images"
    output = tmp_path / "map.json"
    manual = tmp_path / "manual.json"

    image_dir.mkdir(parents=True)
    auto_image = image_dir / "系统首页.png"
    auto_image.write_text("x", encoding="utf-8")
    manual_image = tmp_path / "manual-dashboard.png"
    manual_image.write_text("y", encoding="utf-8")

    labels.write_text(json.dumps({"labels": ["系统首页", "核心功能页面"]}, ensure_ascii=False), encoding="utf-8")
    manual.write_text(
        json.dumps(
            {
                "核心功能页面": str(manual_image),
                "不存在文件": str(tmp_path / "missing.png"),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = _run_tool(
        "tools/build_image_map.py",
        str(labels),
        str(image_dir),
        str(output),
        "--manual",
        str(manual),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["系统首页"] == str(auto_image)
    assert payload["核心功能页面"] == str(manual_image)


def test_ensure_thesis_assets_check_only_returns_nonzero_when_missing(tmp_path: Path) -> None:
    markdown = tmp_path / "manual.md"
    markdown.write_text("# 示例\n\n正文内容。\n", encoding="utf-8")

    result = _run_tool("tools/ensure_thesis_assets.py", str(markdown), "--check-only")

    assert result.returncode == 2
    assert "MISSING_COUNT" in result.stdout


def test_ensure_thesis_assets_in_place_adds_templates(tmp_path: Path) -> None:
    markdown = tmp_path / "manual.md"
    markdown.write_text("# 示例\n\n图 2.1 已有图\n", encoding="utf-8")

    result = _run_tool("tools/ensure_thesis_assets.py", str(markdown), "--in-place")

    assert result.returncode == 0, result.stderr
    updated = markdown.read_text(encoding="utf-8")
    assert "图表与截图补全草稿" in updated
    assert "图 2.2" in updated
