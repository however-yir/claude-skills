"""End-to-end NUX integration tests.

Verifies that setup wizard, status banner, quality nudge, and SKILL.md
first-run flow work together coherently:
- first_run flag emitted / not emitted based on SETUP_COMPLETE
- setup subcommand runs auto_setup and writes config
- quality score is consistent with source configuration
- quality nudge disappears at 100%
- banner and quality nudge don't contradict each other
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add scripts dir to path
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from lib import setup_wizard, quality_nudge, ui


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_config(**overrides):
    """Return a minimal config dict."""
    config = {
        "AUTH_TOKEN": None,
        "CT0": None,
        "XAI_API_KEY": None,
        "SCRAPECREATORS_API_KEY": None,
    }
    config.update(overrides)
    return config


def _base_results(**overrides):
    """Return a minimal research_results dict with no errors."""
    results = {
        "x_error": None,
        "youtube_error": None,
        "reddit_error": None,
    }
    results.update(overrides)
    return results


def _base_diag(**overrides):
    """Return a minimal diag dict for banner testing."""
    diag = {
        "setup_complete": False,
        "reddit_source": None,
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


def _compute(config_overrides=None, result_overrides=None, ytdlp_installed=False):
    """Helper to call compute_quality_score with mocked yt-dlp check."""
    from lib import youtube_yt

    config = _base_config(**(config_overrides or {}))
    results = _base_results(**(result_overrides or {}))

    with patch.object(youtube_yt, "is_ytdlp_installed", return_value=ytdlp_installed):
        return quality_nudge.compute_quality_score(config, results)


# ---------------------------------------------------------------------------
# First-run flag detection
# ---------------------------------------------------------------------------

class TestFirstRunDetection:
    """first_run flag is emitted based on SETUP_COMPLETE in config."""

    def test_first_run_when_setup_not_complete(self):
        """SETUP_COMPLETE missing -> is_first_run returns True."""
        config = _base_config()
        assert setup_wizard.is_first_run(config) is True

    def test_first_run_when_setup_complete_empty(self):
        """SETUP_COMPLETE='' -> is_first_run returns True."""
        config = _base_config(SETUP_COMPLETE="")
        assert setup_wizard.is_first_run(config) is True

    def test_not_first_run_when_setup_complete(self):
        """SETUP_COMPLETE=true -> is_first_run returns False."""
        config = _base_config(SETUP_COMPLETE="true")
        assert setup_wizard.is_first_run(config) is False

    def test_not_first_run_any_truthy_value(self):
        """SETUP_COMPLETE=1 -> is_first_run returns False."""
        config = _base_config(SETUP_COMPLETE="1")
        assert setup_wizard.is_first_run(config) is False


# ---------------------------------------------------------------------------
# Setup subcommand writes config
# ---------------------------------------------------------------------------

class TestSetupSubcommandWritesConfig:
    """setup subcommand runs auto_setup and writes SETUP_COMPLETE."""

    @patch("lib.cookie_extract.extract_cookies_with_source")
    @patch("shutil.which")
    def test_auto_setup_and_write(self, mock_which, mock_extract):
        """run_auto_setup + write_setup_config creates valid config."""
        mock_extract.return_value = ({"auth_token": "abc", "ct0": "xyz"}, "chrome")
        mock_which.return_value = "/usr/local/bin/yt-dlp"

        config = _base_config()
        results = setup_wizard.run_auto_setup(config)

        assert results["cookies_found"]["x"] == "chrome"
        assert results["ytdlp_installed"] is True

        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            written = setup_wizard.write_setup_config(env_path)
            assert written is True

            content = env_path.read_text()
            assert "SETUP_COMPLETE=true" in content
            assert "FROM_BROWSER=auto" in content

    @patch("lib.cookie_extract.extract_cookies_with_source")
    @patch("shutil.which")
    def test_after_setup_not_first_run(self, mock_which, mock_extract):
        """After write_setup_config, is_first_run should return False."""
        mock_extract.return_value = None
        mock_which.return_value = None

        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            setup_wizard.write_setup_config(env_path)

            # Simulate reading the config back
            config = {"SETUP_COMPLETE": "true"}
            assert setup_wizard.is_first_run(config) is False


# ---------------------------------------------------------------------------
# Quality score consistency with source config
# ---------------------------------------------------------------------------

class TestQualityScoreConsistency:
    """Quality score matches the source configuration state."""

    def test_zero_config_is_40_pct(self):
        """No X, no yt-dlp, no SC -> 40% (HN + Polymarket only)."""
        q = _compute()
        assert q["score_pct"] == 40
        assert set(q["core_active"]) == {"hn", "polymarket"}

    def test_x_cookies_is_60_pct(self):
        """X cookies active -> 60%."""
        q = _compute(config_overrides={"AUTH_TOKEN": "tok123"})
        assert q["score_pct"] == 60
        assert "x" in q["core_active"]

    def test_x_plus_ytdlp_is_80_pct(self):
        """X cookies + yt-dlp -> 80%."""
        q = _compute(
            config_overrides={"AUTH_TOKEN": "tok123"},
            ytdlp_installed=True,
        )
        assert q["score_pct"] == 80
        assert "x" in q["core_active"]
        assert "youtube" in q["core_active"]

    def test_full_config_is_100_pct(self):
        """X + yt-dlp + ScrapeCreators -> 100%."""
        q = _compute(
            config_overrides={
                "AUTH_TOKEN": "tok123",
                "SCRAPECREATORS_API_KEY": "sc_key",
            },
            ytdlp_installed=True,
        )
        assert q["score_pct"] == 100
        assert len(q["core_active"]) == 5

    def test_xai_key_also_enables_x(self):
        """XAI_API_KEY activates X source same as cookies."""
        q = _compute(config_overrides={"XAI_API_KEY": "xai_key"})
        assert q["score_pct"] == 60
        assert "x" in q["core_active"]


# ---------------------------------------------------------------------------
# Quality nudge disappears at 100%
# ---------------------------------------------------------------------------

class TestQualityNudgeDisappears:
    """Quality nudge is None at 100% and present below 100%."""

    def test_nudge_present_at_40(self):
        q = _compute()
        assert q["nudge_text"] is not None
        assert len(q["nudge_text"]) > 0

    def test_nudge_present_at_60(self):
        q = _compute(config_overrides={"AUTH_TOKEN": "tok123"})
        assert q["nudge_text"] is not None

    def test_nudge_present_at_80(self):
        q = _compute(
            config_overrides={"AUTH_TOKEN": "tok123"},
            ytdlp_installed=True,
        )
        assert q["nudge_text"] is not None

    def test_nudge_none_at_100(self):
        q = _compute(
            config_overrides={
                "AUTH_TOKEN": "tok123",
                "SCRAPECREATORS_API_KEY": "sc_key",
            },
            ytdlp_installed=True,
        )
        assert q["nudge_text"] is None
        assert q["core_missing"] == []


# ---------------------------------------------------------------------------
# Banner and quality nudge consistency
# ---------------------------------------------------------------------------

class TestBannerQualityNudgeConsistency:
    """Banner source count and quality nudge percentage don't contradict."""

    def test_zero_config_banner_3_sources_nudge_40(self):
        """Banner shows 3 sources (Reddit, HN, PM), nudge says 40%."""
        diag = _base_diag()
        banner = "\n".join(ui._build_status_banner(diag))

        # Banner shows 3 active sources
        assert "Reddit (threads only)" in banner
        assert "HN" in banner
        assert "Polymarket" in banner
        # X and YouTube should NOT be in the banner
        assert "X (" not in banner
        assert "YouTube" not in banner

        # Quality nudge is 40%
        q = _compute()
        assert q["score_pct"] == 40

    def test_after_wizard_banner_5_sources_nudge_80(self):
        """After wizard (X cookies + yt-dlp): banner shows 5+ sources, nudge ~80%."""
        diag = _base_diag(
            setup_complete=True,
            x_source="bird",
            x_method="browser-chrome",
            youtube=True,
        )
        banner = "\n".join(ui._build_status_banner(diag))

        # Banner shows X and YouTube
        assert "X (Chrome)" in banner
        assert "YouTube" in banner
        assert "Reddit (threads only)" in banner
        assert "HN" in banner
        assert "Polymarket" in banner

        # Quality nudge is 80%
        q = _compute(
            config_overrides={"AUTH_TOKEN": "tok123"},
            ytdlp_installed=True,
        )
        assert q["score_pct"] == 80

    def test_full_config_banner_all_nudge_gone(self):
        """Full config: banner shows all sources, nudge disappears (100%)."""
        diag = _base_diag(
            setup_complete=True,
            reddit_source="scrapecreators",
            x_source="bird",
            x_method="browser-chrome",
            youtube=True,
            tiktok=True,
            instagram=True,
            scrapecreators=True,
        )
        banner = "\n".join(ui._build_status_banner(diag))

        assert "Reddit (with comments)" in banner
        assert "X (Chrome)" in banner
        assert "YouTube" in banner
        assert "TikTok" in banner
        assert "Instagram" in banner

        # Quality nudge is 100% / gone
        q = _compute(
            config_overrides={
                "AUTH_TOKEN": "tok123",
                "SCRAPECREATORS_API_KEY": "sc_key",
            },
            ytdlp_installed=True,
        )
        assert q["score_pct"] == 100
        assert q["nudge_text"] is None

    def test_banner_first_run_suggests_setup(self):
        """First-run banner suggests running setup wizard."""
        diag = _base_diag(setup_complete=False)
        banner = "\n".join(ui._build_status_banner(diag))
        assert "First Run" in banner
        assert "/last30days setup" in banner

    def test_banner_partial_suggests_scrapecreators(self):
        """After setup, missing SC is the only recommendation."""
        diag = _base_diag(
            setup_complete=True,
            x_source="bird",
            x_method="browser-chrome",
            youtube=True,
            scrapecreators=False,
        )
        banner = "\n".join(ui._build_status_banner(diag))
        assert "SCRAPECREATORS_API_KEY" in banner
        assert "100 free calls, no CC" in banner


# ---------------------------------------------------------------------------
# Progressive narrowing of nudge suggestions
# ---------------------------------------------------------------------------

class TestProgressiveNarrowing:
    """As users configure more, nudge suggestions narrow."""

    def test_baseline_mentions_all_three_missing(self):
        q = _compute()
        assert "X/Twitter" in q["nudge_text"]
        assert "YouTube" in q["nudge_text"]
        assert "Reddit with comments" in q["nudge_text"]

    def test_with_x_mentions_yt_and_sc(self):
        q = _compute(config_overrides={"AUTH_TOKEN": "tok123"})
        assert "X/Twitter" not in q["nudge_text"]
        assert "YouTube" in q["nudge_text"]
        assert "Reddit with comments" in q["nudge_text"]

    def test_with_x_and_yt_mentions_sc_only(self):
        q = _compute(
            config_overrides={"AUTH_TOKEN": "tok123"},
            ytdlp_installed=True,
        )
        assert "X/Twitter" not in q["nudge_text"]
        assert "YouTube" not in q["nudge_text"]
        # SC nudge is present
        assert "Reddit" in q["nudge_text"] or "ScrapeCreators" in q["nudge_text"].lower() or "scrapecreators" in q["nudge_text"]

    def test_full_coverage_no_nudge(self):
        q = _compute(
            config_overrides={
                "AUTH_TOKEN": "tok123",
                "SCRAPECREATORS_API_KEY": "sc_key",
            },
            ytdlp_installed=True,
        )
        assert q["nudge_text"] is None


# ---------------------------------------------------------------------------
# Render quality nudge integration
# ---------------------------------------------------------------------------

class TestRenderQualityNudge:
    """render_quality_nudge produces correct output."""

    def test_render_at_80_pct(self):
        from lib.render import render_quality_nudge

        q = _compute(
            config_overrides={"AUTH_TOKEN": "tok123"},
            ytdlp_installed=True,
        )
        rendered = render_quality_nudge(q)
        assert "80%" in rendered
        assert "Research Coverage" in rendered

    def test_render_at_100_pct_is_empty(self):
        from lib.render import render_quality_nudge

        q = _compute(
            config_overrides={
                "AUTH_TOKEN": "tok123",
                "SCRAPECREATORS_API_KEY": "sc_key",
            },
            ytdlp_installed=True,
        )
        rendered = render_quality_nudge(q)
        assert rendered == ""
