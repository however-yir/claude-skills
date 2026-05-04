"""Tests for the redesigned status banner (free-first design)."""

import pytest

from scripts.lib.ui import _build_status_banner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_diag(**overrides):
    """Return a minimal diag dict with common defaults."""
    diag = {
        "setup_complete": False,
        "reddit_source": None,  # None = public fallback
        "x_source": None,
        "x_method": None,
        "youtube": False,
        "tiktok": False,
        "instagram": False,
        "hackernews": True,
        "polymarket": True,
        "bluesky": False,
        "truthsocial": False,
        "xiaohongshu": False,
        "weibo": False,
        "douyin": False,
        "scrapecreators": False,
        "web_search_backend": None,
    }
    diag.update(overrides)
    return diag


def _banner_text(diag):
    """Return full banner as a single string."""
    return "\n".join(_build_status_banner(diag))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestZeroConfig:
    """Zero-config state: SETUP_COMPLETE not set, wizard hasn't run."""

    def test_shows_first_run_title(self):
        banner = _banner_text(_base_diag())
        assert "First Run" in banner

    def test_shows_three_free_sources(self):
        banner = _banner_text(_base_diag())
        assert "Reddit (threads only)" in banner
        assert "HN" in banner
        assert "Polymarket" in banner

    def test_shows_setup_prompt(self):
        banner = _banner_text(_base_diag())
        assert "/last30days setup" in banner

    def test_does_not_show_source_status_title(self):
        banner = _banner_text(_base_diag())
        assert "Source Status" not in banner


class TestFullConfig:
    """Fully configured: X + yt-dlp + ScrapeCreators = everything active."""

    def _full_diag(self):
        return _base_diag(
            setup_complete=True,
            reddit_source="scrapecreators",
            x_source="bird",
            x_method="browser-chrome",
            youtube=True,
            tiktok=True,
            instagram=True,
            hackernews=True,
            polymarket=True,
            bluesky=True,
            truthsocial=True,
            xiaohongshu=True,
            weibo=True,
            douyin=True,
            scrapecreators=True,
            web_search_backend="parallel",
        )

    def test_shows_source_status_title(self):
        banner = _banner_text(self._full_diag())
        assert "Source Status" in banner

    def test_shows_all_sources(self):
        banner = _banner_text(self._full_diag())
        assert "Reddit (with comments)" in banner
        assert "X (Chrome)" in banner
        assert "YouTube" in banner
        assert "HN" in banner
        assert "Polymarket" in banner
        assert "TikTok" in banner
        assert "Instagram" in banner
        assert "Bluesky" in banner
        assert "Truth Social" in banner
        assert "Xiaohongshu" in banner
        assert "Weibo" in banner
        assert "Douyin" in banner

    def test_no_recommendations(self):
        banner = _banner_text(self._full_diag())
        assert "⭐" not in banner
        assert "scrapecreators.com" not in banner
        assert "/last30days setup" not in banner


class TestPartialConfig:
    """Partially configured: X + yt-dlp but no ScrapeCreators."""

    def _partial_diag(self):
        return _base_diag(
            setup_complete=True,
            reddit_source=None,  # public fallback
            x_source="bird",
            x_method="browser-chrome",
            youtube=True,
            scrapecreators=False,
        )

    def test_shows_active_sources(self):
        banner = _banner_text(self._partial_diag())
        assert "Reddit (threads only)" in banner
        assert "X (Chrome)" in banner
        assert "YouTube" in banner
        assert "HN" in banner
        assert "Polymarket" in banner

    def test_recommends_scrapecreators(self):
        banner = _banner_text(self._partial_diag())
        assert "SCRAPECREATORS_API_KEY" in banner

    def test_scrapecreators_free_calls_copy(self):
        banner = _banner_text(self._partial_diag())
        assert "100 free calls, no CC" in banner
        assert "scrapecreators.com" in banner

    def test_shows_tiktok_instagram_unlock(self):
        banner = _banner_text(self._partial_diag())
        assert "TikTok" in banner
        assert "Instagram" in banner


class TestScrapeCreatorsRecommendation:
    """ScrapeCreators recommendation always includes key copy."""

    def test_always_includes_free_calls_no_cc(self):
        """Any config missing SC should show the free-calls copy."""
        # Zero config
        banner_zero = _banner_text(_base_diag())
        # Zero config doesn't recommend SC directly (recommends setup wizard)
        # But after setup, missing SC should always include the copy
        banner_partial = _banner_text(_base_diag(
            setup_complete=True,
            scrapecreators=False,
        ))
        assert "100 free calls, no CC" in banner_partial

    def test_present_when_x_available_but_no_sc(self):
        banner = _banner_text(_base_diag(
            setup_complete=True,
            x_source="xai",
            x_method="api",
            scrapecreators=False,
        ))
        assert "100 free calls, no CC" in banner
        assert "scrapecreators.com" in banner


class TestRedditLabelDisplay:
    """Reddit label reflects comment availability, not implementation details."""

    def test_no_scrapecreators_shows_threads_only(self):
        """Without SC, Reddit label should say 'threads only' regardless of OpenAI auth."""
        banner = _banner_text(_base_diag(
            setup_complete=True,
            reddit_source="openai",
            scrapecreators=False,
        ))
        assert "Reddit (threads only)" in banner
        assert "OpenAI" not in banner
        assert "Codex" not in banner

    def test_no_scrapecreators_public_shows_threads_only(self):
        """Public fallback also shows 'threads only'."""
        banner = _banner_text(_base_diag(
            setup_complete=True,
            reddit_source=None,
            scrapecreators=False,
        ))
        assert "Reddit (threads only)" in banner

    def test_scrapecreators_shows_with_comments(self):
        """With SC configured, Reddit label should say 'with comments'."""
        banner = _banner_text(_base_diag(
            setup_complete=True,
            reddit_source="scrapecreators",
            scrapecreators=True,
        ))
        assert "Reddit (with comments)" in banner

    def test_no_openai_or_codex_in_banner(self):
        """Banner should never mention OpenAI or Codex — those are implementation details."""
        for source in [None, "openai", "scrapecreators"]:
            banner = _banner_text(_base_diag(
                setup_complete=True,
                reddit_source=source,
                scrapecreators=(source == "scrapecreators"),
            ))
            assert "OpenAI" not in banner, f"Found 'OpenAI' with reddit_source={source}"
            assert "Codex" not in banner, f"Found 'Codex' with reddit_source={source}"


class TestXMethodDisplay:
    """X source shows auth method in parens."""

    def test_browser_chrome(self):
        banner = _banner_text(_base_diag(
            setup_complete=True,
            x_source="bird",
            x_method="browser-chrome",
        ))
        assert "X (Chrome)" in banner

    def test_browser_firefox(self):
        banner = _banner_text(_base_diag(
            setup_complete=True,
            x_source="bird",
            x_method="browser-firefox",
        ))
        assert "X (Firefox)" in banner

    def test_env_method(self):
        banner = _banner_text(_base_diag(
            setup_complete=True,
            x_source="bird",
            x_method="env",
        ))
        assert "X (env)" in banner

    def test_xai_api(self):
        banner = _banner_text(_base_diag(
            setup_complete=True,
            x_source="xai",
            x_method="api",
        ))
        assert "X (xAI)" in banner


class TestBannerStructure:
    """Banner formatting and structure tests."""

    def test_has_box_drawing(self):
        lines = _build_status_banner(_base_diag())
        assert lines[0].startswith("┌")
        assert lines[-1].startswith("└")

    def test_shows_config_path(self):
        banner = _banner_text(_base_diag())
        assert "~/.config/last30days/.env" in banner

    def test_max_10_inner_lines(self):
        """Banner should be compact — max 10 lines inside the box."""
        # Full config (most lines)
        diag = _base_diag(
            setup_complete=True,
            reddit_source="scrapecreators",
            x_source="bird",
            x_method="browser-chrome",
            youtube=True,
            tiktok=True,
            instagram=True,
            bluesky=True,
            truthsocial=True,
            xiaohongshu=True,
            weibo=True,
            douyin=True,
            scrapecreators=True,
        )
        lines = _build_status_banner(diag)
        # Subtract top and bottom border
        inner_lines = [l for l in lines if l.startswith("│")]
        assert len(inner_lines) <= 10, f"Banner has {len(inner_lines)} inner lines, max is 10"
