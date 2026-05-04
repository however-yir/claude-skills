"""Douyin native connector for /last30days.

Fetches Douyin hot-search trends from ByteDance's public endpoint and
normalizes them into the web-item shape used by this project.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from . import http
from .relevance import token_overlap_relevance

HOTSEARCH_URL = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"

DEPTH_LIMIT = {
    "quick": 8,
    "default": 15,
    "deep": 25,
}


def _to_int(value: Any) -> int:
    """Convert numeric-ish values to int."""
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return 0


def _timestamp_to_date(value: Any) -> Optional[str]:
    """Convert Douyin timestamp to YYYY-MM-DD (accepts sec or ms)."""
    iv = _to_int(value)
    if iv <= 0:
        return None

    # Heuristic: 13 digits means milliseconds.
    if iv > 10_000_000_000:
        iv = iv // 1000

    try:
        dt = datetime.fromtimestamp(iv, tz=timezone.utc)
    except (OSError, OverflowError, ValueError):
        return None
    return dt.strftime("%Y-%m-%d")


def _query_relevance(topic: str, text: str) -> float:
    """Compute query relevance with a light Chinese substring boost."""
    base = token_overlap_relevance(topic, text)
    topic_compact = re.sub(r"\s+", "", (topic or "").lower())
    text_compact = re.sub(r"\s+", "", (text or "").lower())

    if topic_compact and topic_compact in text_compact:
        # Keep a stronger floor for exact topic containment.
        floor = 0.75 if len(topic_compact) >= 4 else 0.60
        base = max(base, floor)

    return min(1.0, max(0.0, base))


def _relevance_with_hot_value(topic_rel: float, hot_value: int) -> float:
    """Blend semantic relevance with hotness signal."""
    if topic_rel <= 0:
        return 0.0
    hot_bonus = min(0.25, math.log1p(max(0, hot_value)) / 25.0)
    return round(min(1.0, topic_rel + hot_bonus), 3)


def parse_douyin_response(
    response: Dict[str, Any],
    topic: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Parse raw Douyin hot-search payload to normalized web-item dicts."""
    if not isinstance(response, dict):
        return []

    if isinstance(response.get("items"), list):
        return response.get("items", [])

    word_list = response.get("word_list")
    if not isinstance(word_list, list):
        data = response.get("data", {})
        if isinstance(data, dict):
            word_list = data.get("word_list", [])
    if not isinstance(word_list, list):
        return []

    limit = DEPTH_LIMIT.get(depth, DEPTH_LIMIT["default"])
    now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    items: List[Dict[str, Any]] = []
    for idx, row in enumerate(word_list):
        if not isinstance(row, dict):
            continue

        word = str(row.get("word") or row.get("sentence") or "").strip()
        if not word:
            continue

        hot_value = _to_int(row.get("hot_value") or row.get("hot_score") or row.get("value"))
        rank = _to_int(row.get("position") or row.get("rank") or (idx + 1))
        label = str(row.get("label") or row.get("event_desc") or "").strip()
        sentence_id = str(row.get("sentence_id") or row.get("id") or "").strip()

        title = word
        if label:
            title = f"{word} ({label})"

        topic_rel = _query_relevance(topic, f"{word} {label}")
        relevance = _relevance_with_hot_value(topic_rel, hot_value)
        # Keep only topic-relevant entries.
        if relevance < 0.20:
            continue

        date_signal = (
            _timestamp_to_date(row.get("event_time"))
            or _timestamp_to_date(row.get("create_time"))
            or _timestamp_to_date(row.get("active_time"))
        )
        date_value = date_signal or now_date
        if date_value and (date_value < from_date or date_value > to_date):
            continue

        query = quote(word)
        trend_url = f"https://www.douyin.com/search/{query}"
        if sentence_id:
            trend_url = f"https://www.douyin.com/hot/{sentence_id}"

        why = f"Douyin hotsearch rank #{rank}, hot_value={hot_value}"
        if label:
            why += f", label={label}"

        items.append({
            "id": f"DY{len(items) + 1}",
            "title": title[:200],
            "url": trend_url,
            "source_domain": "douyin.com",
            "snippet": f"{word} {label}".strip()[:500],
            "date": date_value,
            "date_confidence": "high" if date_signal else "med",
            "relevance": relevance,
            "why_relevant": why,
            "engagement": {
                "hot_value": hot_value,
                "rank": rank,
            },
        })

        if len(items) >= limit:
            break

    return items


def search_douyin(
    topic: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> Dict[str, Any]:
    """Fetch Douyin trends and return normalized result payload."""
    try:
        response = http.get(HOTSEARCH_URL, timeout=15, retries=1)
    except Exception as exc:
        return {"items": [], "error": f"{type(exc).__name__}: {exc}"}

    if not isinstance(response, dict):
        return {"items": [], "error": "Unexpected Douyin response format"}

    status_code = response.get("status_code")
    if status_code not in (None, 0, "0"):
        status_msg = str(response.get("status_msg") or response.get("message") or "unknown error")
        return {"items": [], "error": f"Douyin API error: {status_msg}"}

    items = parse_douyin_response(response, topic, from_date, to_date, depth=depth)
    return {"items": items}
