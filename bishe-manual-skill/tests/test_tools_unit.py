from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from build_reference_pool import classify_language, extract_year, parse_references
from build_screenshot_plan import SCHEMA_VERSION, build_entries
from build_screenshot_plan import main as build_screenshot_plan_main
from build_screenshot_plan import safe_filename
from ensure_thesis_assets import (
    FIGURE_RE,
    TABLE_RE,
    analyze_missing_items,
    append_templates,
    next_number,
)
from markdown_utils import compute_text_metrics, markdown_to_visible_text


def test_safe_filename_replaces_illegal_chars_and_handles_empty() -> None:
    assert safe_filename("系统/首页:截图?") == "系统-首页-截图-"
    assert safe_filename("   ") == "screenshot"


def test_build_entries_assigns_stable_filenames_for_duplicate_labels() -> None:
    entries = build_entries(["系统首页", "系统首页", "系统首页"])

    assert entries[0]["filename"] == "系统首页.png"
    assert entries[1]["filename"] == "系统首页-2.png"
    assert entries[2]["filename"] == "系统首页-3.png"


def test_schema_version_is_positive_integer() -> None:
    assert isinstance(SCHEMA_VERSION, int)
    assert SCHEMA_VERSION >= 1


def test_next_number_handles_decimal_integer_and_empty_cases() -> None:
    assert next_number("图 2.3 示例", FIGURE_RE) == "2.4"
    assert next_number("表 4 样例", TABLE_RE) == "5"
    assert next_number("没有图表编号", FIGURE_RE) == "1.1"


def test_analyze_missing_items_recognizes_existing_keywords() -> None:
    text = "系统包含总体架构图、测试用例，并且有 [此处插入截图：系统首页]。"
    missing_ids = {item["id"] for item in analyze_missing_items(text)}

    assert "architecture" not in missing_ids
    assert "test_table" not in missing_ids
    assert "screenshot" not in missing_ids


def test_append_templates_adds_incremented_figure_and_table_numbers() -> None:
    source = "# 章节\n图 3.2 现有图\n表 7 已有表\n"
    missing = [
        {
            "id": "flow",
            "label": "关键业务流程图",
            "kind": "figure",
            "template": "图 {number} {label}",
        },
        {
            "id": "data_table",
            "label": "核心数据表设计",
            "kind": "table",
            "template": "表 {number} {label}",
        },
    ]

    updated = append_templates(source, missing)

    assert "图 3.3 关键业务流程图" in updated
    assert "表 8 核心数据表设计" in updated


def test_markdown_to_visible_text_strips_non_visible_sections() -> None:
    markdown = """
# 标题
[此处插入截图：系统首页]

| 列A | 列B |
| --- | --- |
| `值1` | **值2** |

```python
print('ignore')
```

段落与 [链接](https://example.com)
"""

    visible = markdown_to_visible_text(markdown)

    assert "标题" in visible
    assert "值1 值2" in visible
    assert "ignore" not in visible
    assert "此处插入截图" not in visible
    assert "链接" in visible


def test_compute_text_metrics_counts_cjk_and_non_cjk_tokens() -> None:
    metrics = compute_text_metrics("这是 test 文本 with API-v2")

    assert metrics["chinese_chars"] == 4
    assert metrics["non_chinese_words"] >= 3
    assert metrics["approx_word_count"] == metrics["chinese_chars"] + metrics["non_chinese_words"]


def test_parse_references_parses_valid_lines_and_skips_invalid(tmp_path: Path) -> None:
    ref_file = tmp_path / "refs.md"
    ref_file.write_text(
        "\n".join(
            [
                "[1] 中文文献标题，2024，doi:10.1/abc",
                "not a reference line",
                "[2] English paper title (2021)",
            ]
        ),
        encoding="utf-8",
    )

    refs = parse_references(ref_file)

    assert len(refs) == 2
    assert refs[0]["language"] == "zh"
    assert refs[0]["year"] == 2024
    assert refs[0]["has_doi"] is True
    assert refs[1]["language"] == "en"
    assert refs[1]["year"] == 2021


def test_parse_references_raises_file_not_found_for_missing_input(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        parse_references(tmp_path / "missing.md")


def test_extract_year_and_language_boundaries() -> None:
    assert extract_year("no year here") is None
    assert extract_year("published in 2025 and revised 2026") == 2025
    assert classify_language("No Chinese characters") == "en"
    assert classify_language("包含中文") == "zh"


def test_build_screenshot_plan_main_raises_on_invalid_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    labels = tmp_path / "labels.json"
    output = tmp_path / "plan.json"
    labels.write_text("{invalid-json", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["build_screenshot_plan.py", str(labels), str(output)],
    )

    with pytest.raises(json.JSONDecodeError):
        build_screenshot_plan_main()
