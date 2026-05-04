from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


SCHEMA_VERSION = 1


def safe_filename(label: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "-", label).strip() or "screenshot"


def build_entries(labels: list[str]) -> list[dict]:
    entries = []
    seen: defaultdict[str, int] = defaultdict(int)

    for label in labels:
        stem = safe_filename(label)
        seen[stem] += 1
        suffix = f"-{seen[stem]}" if seen[stem] > 1 else ""

        entries.append(
            {
                "label": label,
                "url": "",
                "wait_for_selector": "",
                "wait_for_text": "",
                "clip_selector": "",
                "filename": f"{stem}{suffix}.png",
                "full_page": True,
                "actions": [],
            }
        )

    return entries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a screenshot capture plan from thesis screenshot placeholders.")
    parser.add_argument("labels_json", type=Path)
    parser.add_argument("output_plan", type=Path)
    parser.add_argument("--base-url", dest="base_url", default="")
    parser.add_argument("--output-dir", dest="output_dir", default="output/doc")
    parser.add_argument("--image-map", dest="image_map_output", default="image-map.json")
    parser.add_argument("--cdp-url", dest="cdp_url", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.labels_json.read_text(encoding="utf-8"))
    labels = payload.get("labels", [])
    entries = build_entries(labels)

    plan = {
        "schema_version": SCHEMA_VERSION,
        "base_url": args.base_url,
        "cdp_url": args.cdp_url,
        "output_dir": args.output_dir,
        "image_map_output": args.image_map_output,
        "headless": True,
        "viewport": {"width": 1440, "height": 900},
        "entries": entries,
    }

    args.output_plan.parent.mkdir(parents=True, exist_ok=True)
    args.output_plan.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output_plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
