"""Tests for Douyin native connector."""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import douyin


class TestParseDouyinResponse(unittest.TestCase):
    def test_parses_and_filters_by_topic(self):
        response = {
            "status_code": 0,
            "word_list": [
                {
                    "word": "AI agent",
                    "hot_value": 1234567,
                    "position": 1,
                    "sentence_id": "123",
                    "event_time": 1773686400,  # 2026-03-15 UTC
                },
                {
                    "word": "cats dancing",
                    "hot_value": 987654,
                    "position": 2,
                    "sentence_id": "456",
                    "event_time": 1773686400,
                },
            ],
        }

        items = douyin.parse_douyin_response(
            response=response,
            topic="AI",
            from_date="2000-01-01",
            to_date="2100-01-01",
            depth="default",
        )

        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["id"], "DY1")
        self.assertEqual(item["source_domain"], "douyin.com")
        self.assertIn("hotsearch rank #1", item["why_relevant"])
        self.assertTrue(item["url"].startswith("https://www.douyin.com/"))


class TestSearchDouyin(unittest.TestCase):
    @patch("lib.douyin.http.get")
    def test_search_handles_http_error(self, mock_get):
        mock_get.side_effect = RuntimeError("network down")
        result = douyin.search_douyin(
            topic="AI",
            from_date="2026-03-01",
            to_date="2026-03-31",
            depth="default",
        )
        self.assertEqual(result["items"], [])
        self.assertIn("network down", result["error"])


if __name__ == "__main__":
    unittest.main()
