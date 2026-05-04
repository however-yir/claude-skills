"""Tests for yt-dlp invocation safety flags."""

import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import youtube_yt


class _DummyProc:
    def __init__(self):
        self.pid = 12345
        self.returncode = 0

    def communicate(self, timeout=None):
        return "", ""

    def wait(self, timeout=None):
        return 0


class TestYtDlpFlags(unittest.TestCase):
    def test_search_ignores_global_config_and_browser_cookies(self):
        proc = _DummyProc()
        with mock.patch.object(youtube_yt, "is_ytdlp_installed", return_value=True), \
             mock.patch.object(youtube_yt.subprocess, "Popen", return_value=proc) as popen_mock:
            youtube_yt.search_youtube("Claude Code", "2026-02-01", "2026-03-01")

        cmd = popen_mock.call_args.args[0]
        self.assertIn("--ignore-config", cmd)
        self.assertIn("--no-cookies-from-browser", cmd)

    def test_transcript_fetch_ignores_global_config_and_browser_cookies(self):
        proc = _DummyProc()
        with tempfile.TemporaryDirectory() as temp_dir, \
             mock.patch.object(youtube_yt, "is_ytdlp_installed", return_value=True), \
             mock.patch.object(youtube_yt.subprocess, "Popen", return_value=proc) as popen_mock:
            youtube_yt.fetch_transcript("abc123", temp_dir)

        cmd = popen_mock.call_args.args[0]
        self.assertIn("--ignore-config", cmd)
        self.assertIn("--no-cookies-from-browser", cmd)


class TestExtractTranscriptHighlights(unittest.TestCase):
    def test_extracts_specific_sentences(self):
        transcript = (
            "Hey guys welcome back to the channel. "
            "In today's video we're looking at something special. "
            "The Lego Bugatti Chiron took 13,438 hours to build with over 1 million pieces. "
            "Don't forget to subscribe and hit the bell. "
            "The tolerance on each brick is 0.002 millimeters which is insane for injection molding. "
            "So yeah that's pretty cool. "
            "Thanks for watching see you next time."
        )
        highlights = youtube_yt.extract_transcript_highlights(transcript, "Lego")
        self.assertTrue(len(highlights) > 0)
        # Should pick the sentences with numbers and topic relevance, not filler
        joined = " ".join(highlights)
        self.assertIn("13,438", joined)
        self.assertNotIn("subscribe", joined)
        self.assertNotIn("welcome back", joined)

    def test_empty_transcript(self):
        self.assertEqual(youtube_yt.extract_transcript_highlights("", "test"), [])

    def test_respects_limit(self):
        sentences = ". ".join(
            f"The model {i} has {i * 100} parameters and runs at {i * 10} tokens per second"
            for i in range(20)
        ) + "."
        highlights = youtube_yt.extract_transcript_highlights(sentences, "model", limit=3)
        self.assertEqual(len(highlights), 3)


class TestFetchTranscriptDirect(unittest.TestCase):
    """Tests for _fetch_transcript_direct() — direct HTTP transcript fetching."""

    # Minimal ytInitialPlayerResponse JSON with a caption track
    _PLAYER_RESPONSE = json.dumps({
        "captions": {
            "playerCaptionsTracklistRenderer": {
                "captionTracks": [
                    {
                        "baseUrl": "https://www.youtube.com/api/timedtext?v=abc123&lang=en",
                        "languageCode": "en",
                    }
                ]
            }
        }
    })

    _WATCH_HTML = (
        '<html><script>var ytInitialPlayerResponse = '
        + _PLAYER_RESPONSE
        + ';</script></html>'
    )

    _SAMPLE_VTT = (
        "WEBVTT\n\n"
        "00:00:00.000 --> 00:00:02.000\n"
        "Hello world this is a test sentence with enough words to pass.\n\n"
        "00:00:02.000 --> 00:00:04.000\n"
        "Another line of transcript text here for testing purposes.\n"
    )

    def _mock_urlopen(self, url_or_req, *, timeout=None):
        """Return watch HTML or VTT depending on URL."""
        url = url_or_req.full_url if hasattr(url_or_req, 'full_url') else url_or_req

        class _Resp:
            def __init__(self, data):
                self._data = data.encode("utf-8")
            def read(self):
                return self._data
            def __enter__(self):
                return self
            def __exit__(self, *a):
                pass

        if "watch?" in url:
            return _Resp(self._WATCH_HTML)
        elif "timedtext" in url:
            return _Resp(self._SAMPLE_VTT)
        raise urllib.error.URLError("unexpected URL")

    def test_extracts_vtt_from_mock_page(self):
        """Happy path: extracts VTT text from a page with captions."""
        with mock.patch("lib.youtube_yt.urllib.request.urlopen", side_effect=self._mock_urlopen):
            result = youtube_yt._fetch_transcript_direct("abc123")
        self.assertIsNotNone(result)
        self.assertIn("WEBVTT", result)
        self.assertIn("Hello world", result)

    def test_no_captions_returns_none(self):
        """Video with no caption tracks returns None."""
        no_captions_response = json.dumps({"captions": {"playerCaptionsTracklistRenderer": {"captionTracks": []}}})
        html = f'<html><script>var ytInitialPlayerResponse = {no_captions_response};</script></html>'

        class _Resp:
            def __init__(self, data):
                self._data = data.encode("utf-8")
            def read(self):
                return self._data
            def __enter__(self):
                return self
            def __exit__(self, *a):
                pass

        def mock_open(req, *, timeout=None):
            return _Resp(html)

        with mock.patch("lib.youtube_yt.urllib.request.urlopen", side_effect=mock_open):
            result = youtube_yt._fetch_transcript_direct("nocaps")
        self.assertIsNone(result)

    def test_http_timeout_returns_none(self):
        """HTTP timeout on watch page returns None."""
        def timeout_open(req, *, timeout=None):
            raise TimeoutError("timed out")

        with mock.patch("lib.youtube_yt.urllib.request.urlopen", side_effect=timeout_open):
            result = youtube_yt._fetch_transcript_direct("timeout_vid")
        self.assertIsNone(result)

    def test_direct_vtt_feeds_into_clean_vtt(self):
        """VTT from direct fetch produces clean plaintext via _clean_vtt()."""
        cleaned = youtube_yt._clean_vtt(self._SAMPLE_VTT)
        self.assertNotIn("WEBVTT", cleaned)
        self.assertNotIn("-->", cleaned)
        self.assertIn("Hello world", cleaned)
        self.assertIn("Another line", cleaned)


class TestFetchTranscriptFallback(unittest.TestCase):
    """Tests that fetch_transcript picks yt-dlp or direct path correctly."""

    def test_uses_ytdlp_when_installed(self):
        """When yt-dlp is installed, uses _fetch_transcript_ytdlp."""
        with mock.patch.object(youtube_yt, "is_ytdlp_installed", return_value=True), \
             mock.patch.object(youtube_yt, "_fetch_transcript_ytdlp", return_value="WEBVTT\n\nfake") as yt_mock, \
             mock.patch.object(youtube_yt, "_fetch_transcript_direct") as direct_mock:
            result = youtube_yt.fetch_transcript("vid1", "/tmp/test")
        yt_mock.assert_called_once_with("vid1", "/tmp/test")
        direct_mock.assert_not_called()

    def test_uses_direct_when_ytdlp_missing(self):
        """When yt-dlp is NOT installed, falls back to _fetch_transcript_direct."""
        sample_vtt = (
            "WEBVTT\n\n"
            "00:00:00.000 --> 00:00:02.000\n"
            "Direct transcript content with enough words for testing.\n"
        )
        with mock.patch.object(youtube_yt, "is_ytdlp_installed", return_value=False), \
             mock.patch.object(youtube_yt, "_fetch_transcript_ytdlp") as yt_mock, \
             mock.patch.object(youtube_yt, "_fetch_transcript_direct", return_value=sample_vtt) as direct_mock:
            result = youtube_yt.fetch_transcript("vid2", "/tmp/test")
        yt_mock.assert_not_called()
        direct_mock.assert_called_once_with("vid2")
        self.assertIsNotNone(result)
        self.assertIn("Direct transcript content", result)

    def test_returns_none_when_both_fail(self):
        """Returns None when the chosen path returns None."""
        with mock.patch.object(youtube_yt, "is_ytdlp_installed", return_value=False), \
             mock.patch.object(youtube_yt, "_fetch_transcript_direct", return_value=None):
            result = youtube_yt.fetch_transcript("novid", "/tmp/test")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
