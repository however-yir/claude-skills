"""Tests for Weibo native connector."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import weibo


class TestParseWeiboResponse(unittest.TestCase):
    def test_parses_cards_and_strips_html(self):
        response = {
            "ok": 1,
            "data": {
                "cards": [
                    {
                        "card_type": 9,
                        "mblog": {
                            "id": "123",
                            "bid": "AbCdEf",
                            "created_at": "Tue Mar 31 12:34:56 +0800 2026",
                            "text": "<a href='x'>AI</a> trend is <b>booming</b>",
                            "attitudes_count": 120,
                            "reposts_count": 30,
                            "comments_count": 45,
                            "user": {
                                "id": "999",
                                "screen_name": "alice",
                            },
                        },
                    },
                ],
            },
        }

        items = weibo.parse_weibo_response(
            response=response,
            topic="AI",
            from_date="2000-01-01",
            to_date="2100-01-01",
            depth="default",
        )

        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["id"], "WB1")
        self.assertEqual(item["source_domain"], "weibo.com")
        self.assertIn("AI trend is booming", item["snippet"])
        self.assertIn("likes=120", item["why_relevant"])
        self.assertTrue(item["url"].startswith("https://"))


class TestSearchWeibo(unittest.TestCase):
    def test_requires_sub_cookie(self):
        result = weibo.search_weibo(
            topic="AI",
            from_date="2026-03-01",
            to_date="2026-03-31",
            depth="default",
            sub="",
        )
        self.assertEqual(result["items"], [])
        self.assertIn("WEIBO_SUB", result["error"])


if __name__ == "__main__":
    unittest.main()
