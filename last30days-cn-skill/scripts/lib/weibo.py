"""Weibo native connector for /last30days.

Uses the mobile Weibo search API with authenticated cookies (SUB) and
normalizes posts into the project's web-item shape.
"""

from __future__ import annotations

import html
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from . import http
from .relevance import token_overlap_relevance

SEARCH_ENDPOINT = "https://m.weibo.cn/api/container/getIndex"

DEPTH_CONFIG = {
    "quick": {"pages": 1, "limit": 8},
    "default": {"pages": 2, "limit": 15},
    "deep": {"pages": 3, "limit": 25},
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


def _strip_html(value: str) -> str:
    """Remove HTML tags and unescape entities."""
    text = html.unescape(str(value or ""))
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _parse_weibo_date(value: Any) -> Optional[str]:
    """Parse Weibo created_at into YYYY-MM-DD."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    now = datetime.now(timezone.utc)

    # Canonical format: Tue Mar 31 12:34:56 +0800 2026
    try:
        dt = datetime.strptime(text, "%a %b %d %H:%M:%S %z %Y")
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
    except ValueError:
        pass

    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return text

    match_md = re.match(r"^(\d{2})-(\d{2})(?:\s+\d{2}:\d{2})?$", text)
    if match_md:
        month, day = match_md.groups()
        return f"{now.year}-{month}-{day}"

    match_cn = re.match(r"^(\d{1,2})月(\d{1,2})日$", text)
    if match_cn:
        month, day = match_cn.groups()
        return f"{now.year}-{int(month):02d}-{int(day):02d}"

    if text.startswith("昨天"):
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")

    if any(k in text for k in ("刚刚", "秒前", "分钟前", "小时前", "今天")):
        return now.strftime("%Y-%m-%d")

    return None


def _build_headers(sub: str, subp: str = "") -> Dict[str, str]:
    """Build authenticated request headers."""
    cookies = [f"SUB={sub}"]
    if subp:
        cookies.append(f"SUBP={subp}")

    return {
        "Cookie": "; ".join(cookies),
        "Referer": "https://m.weibo.cn/",
        "Accept": "application/json, text/plain, */*",
    }


def _extract_mblogs(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten mblog payloads from cards/card_group structures."""
    items: List[Dict[str, Any]] = []

    for card in cards:
        if not isinstance(card, dict):
            continue

        mblog = card.get("mblog")
        if isinstance(mblog, dict):
            items.append(mblog)

        group = card.get("card_group")
        if isinstance(group, list):
            items.extend(_extract_mblogs(group))

    return items


def _query_relevance(topic: str, text: str) -> float:
    """Compute query relevance with a compact-string fallback."""
    base = token_overlap_relevance(topic, text)
    topic_compact = re.sub(r"\s+", "", (topic or "").lower())
    text_compact = re.sub(r"\s+", "", (text or "").lower())

    if topic_compact and topic_compact in text_compact:
        floor = 0.75 if len(topic_compact) >= 4 else 0.60
        base = max(base, floor)

    return min(1.0, max(0.0, base))


def _engagement_bonus(attitudes: int, reposts: int, comments: int) -> float:
    """Convert engagement counts into a modest relevance bonus."""
    weighted = attitudes + (reposts * 2.0) + (comments * 1.5)
    return min(0.20, math.log1p(max(0.0, weighted)) / 28.0)


def parse_weibo_response(
    response: Dict[str, Any],
    topic: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Parse raw Weibo API response to normalized web-item dicts."""
    if not isinstance(response, dict):
        return []

    if isinstance(response.get("items"), list):
        return response.get("items", [])

    data = response.get("data", {})
    cards = data.get("cards", []) if isinstance(data, dict) else []
    if not isinstance(cards, list):
        return []

    cfg = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    limit = cfg["limit"]

    posts = _extract_mblogs(cards)
    items: List[Dict[str, Any]] = []
    for post in posts:
        if not isinstance(post, dict):
            continue

        text = _strip_html(post.get("raw_text") or post.get("text") or "")
        if not text:
            continue

        attitudes = _to_int(post.get("attitudes_count"))
        reposts = _to_int(post.get("reposts_count"))
        comments = _to_int(post.get("comments_count"))
        date_value = _parse_weibo_date(post.get("created_at"))
        if date_value and (date_value < from_date or date_value > to_date):
            continue

        relevance = _query_relevance(topic, text)
        relevance = round(min(1.0, relevance + _engagement_bonus(attitudes, reposts, comments)), 3)
        if relevance < 0.20:
            continue

        user = post.get("user", {}) if isinstance(post.get("user"), dict) else {}
        author = str(user.get("screen_name") or "").strip()
        uid = str(user.get("id") or "").strip()
        bid = str(post.get("bid") or "").strip()
        post_id = str(post.get("id") or "").strip()

        url = str(post.get("scheme") or "").strip()
        if url and url.startswith("//"):
            url = "https:" + url
        if not url:
            if uid and bid:
                url = f"https://weibo.com/{uid}/{bid}"
            elif post_id:
                url = f"https://m.weibo.cn/detail/{post_id}"
            else:
                query = quote(text[:30])
                url = f"https://s.weibo.com/weibo?q={query}"

        title = f"@{author}: {text[:120]}" if author else text[:140]
        why = (
            f"Weibo engagement: likes={attitudes}, reposts={reposts}, comments={comments}"
        )

        items.append({
            "id": f"WB{len(items) + 1}",
            "title": title[:200],
            "url": url,
            "source_domain": "weibo.com",
            "snippet": text[:500],
            "date": date_value,
            "date_confidence": "high" if date_value else "low",
            "relevance": relevance,
            "why_relevant": why,
            "engagement": {
                "likes": attitudes,
                "reposts": reposts,
                "comments": comments,
            },
        })

        if len(items) >= limit:
            break

    return items


def search_weibo(
    topic: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
    sub: str = "",
    subp: str = "",
) -> Dict[str, Any]:
    """Search Weibo with authenticated cookie credentials."""
    if not sub:
        return {"items": [], "error": "No WEIBO_SUB configured"}

    cfg = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    headers = _build_headers(sub=sub, subp=subp)
    container_id = quote(f"100103type=1&q={topic}", safe="")

    all_items: List[Dict[str, Any]] = []
    last_error: Optional[str] = None

    for page in range(1, cfg["pages"] + 1):
        url = f"{SEARCH_ENDPOINT}?containerid={container_id}&page_type=searchall&page={page}"
        try:
            response = http.get(url, headers=headers, timeout=15, retries=1)
        except http.HTTPError as exc:
            code = exc.status_code
            if code in (302, 401, 403, 432):
                return {
                    "items": [],
                    "error": "Weibo auth blocked (cookie expired or invalid). Refresh WEIBO_SUB.",
                }
            return {"items": [], "error": f"HTTPError: {exc}"}
        except Exception as exc:
            return {"items": [], "error": f"{type(exc).__name__}: {exc}"}

        if not isinstance(response, dict):
            return {"items": [], "error": "Unexpected Weibo response format"}

        ok_flag = response.get("ok")
        if ok_flag not in (1, "1", True, None):
            msg = str(response.get("msg") or response.get("message") or "unknown error")
            last_error = f"Weibo API error: {msg}"
            break

        page_items = parse_weibo_response(
            response, topic=topic, from_date=from_date, to_date=to_date, depth=depth,
        )
        if not page_items:
            # No more usable results.
            continue

        all_items.extend(page_items)
        if len(all_items) >= cfg["limit"]:
            all_items = all_items[:cfg["limit"]]
            break

    result: Dict[str, Any] = {"items": all_items}
    if last_error and not all_items:
        result["error"] = last_error
    return result
