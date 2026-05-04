"""Tests for browser cookie extraction integration in env.py."""

from unittest.mock import patch, MagicMock

import pytest

from scripts.lib.env import extract_browser_credentials, COOKIE_DOMAINS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_config(**overrides):
    """Return a minimal config dict with common defaults."""
    cfg = {
        "AUTH_TOKEN": None,
        "CT0": None,
        "TRUTHSOCIAL_TOKEN": None,
        "WEIBO_SUB": None,
        "WEIBO_SUBP": None,
        "FROM_BROWSER": None,
        "SETUP_COMPLETE": None,
    }
    cfg.update(overrides)
    return cfg


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestExtractBrowserCredentials:
    """Unit tests for extract_browser_credentials()."""

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_auto_with_setup_complete_populates_credentials(self, mock_extract):
        """FROM_BROWSER=auto, SETUP_COMPLETE=true, mock returns valid cookies
        -> config now contains AUTH_TOKEN and CT0."""
        mock_extract.return_value = ({"auth_token": "tok123", "ct0": "ct0val"}, "chrome")

        config = _base_config(FROM_BROWSER="auto", SETUP_COMPLETE="true")
        result = extract_browser_credentials(config)

        assert result["AUTH_TOKEN"] == "tok123"
        assert result["CT0"] == "ct0val"
        # Should have been called for x domain
        mock_extract.assert_any_call("auto", ".x.com", ["auth_token", "ct0"])

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_explicit_auth_token_skips_x_extraction(self, mock_extract):
        """Config already has AUTH_TOKEN and CT0 from env var
        -> cookie extraction skipped for X (explicit takes priority)."""
        # Return None for any non-X domains that still get checked (e.g. Truth Social)
        mock_extract.return_value = None
        config = _base_config(
            AUTH_TOKEN="explicit_token",
            CT0="explicit_ct0",
            FROM_BROWSER="auto",
            SETUP_COMPLETE="true",
        )
        result = extract_browser_credentials(config)

        # X cookies should not appear in result (already set)
        assert "AUTH_TOKEN" not in result
        assert "CT0" not in result
        # extract_cookies should NOT have been called for .x.com
        for call in mock_extract.call_args_list:
            assert call[0][1] != ".x.com", "Should not extract cookies for X when credentials already set"

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_from_browser_off_skips_all(self, mock_extract):
        """FROM_BROWSER=off -> no cookie extraction attempted."""
        config = _base_config(FROM_BROWSER="off", SETUP_COMPLETE="true")
        result = extract_browser_credentials(config)

        assert result == {}
        mock_extract.assert_not_called()

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_no_setup_complete_no_from_browser_defaults_off(self, mock_extract):
        """FROM_BROWSER not set and SETUP_COMPLETE not set
        -> no extraction (wizard hasn't run)."""
        config = _base_config()  # both None
        result = extract_browser_credentials(config)

        assert result == {}
        mock_extract.assert_not_called()

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_setup_complete_no_from_browser_defaults_auto(self, mock_extract):
        """SETUP_COMPLETE is set but FROM_BROWSER is not
        -> defaults to 'auto'."""
        mock_extract.return_value = ({"auth_token": "found", "ct0": "found_ct0"}, "firefox")

        config = _base_config(SETUP_COMPLETE="true")  # FROM_BROWSER=None
        result = extract_browser_credentials(config)

        assert result["AUTH_TOKEN"] == "found"
        # extract_cookies should have been called with 'auto'
        mock_extract.assert_any_call("auto", ".x.com", ["auth_token", "ct0"])

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_from_browser_firefox_only(self, mock_extract):
        """FROM_BROWSER=firefox -> only Firefox extraction attempted."""
        mock_extract.return_value = ({"auth_token": "ff_tok", "ct0": "ff_ct0"}, "firefox")

        config = _base_config(FROM_BROWSER="firefox", SETUP_COMPLETE="true")
        result = extract_browser_credentials(config)

        assert result["AUTH_TOKEN"] == "ff_tok"
        # All calls should use 'firefox' as the browser arg
        for call in mock_extract.call_args_list:
            assert call[0][0] == "firefox"

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_extraction_returns_none_config_unchanged(self, mock_extract):
        """Cookie extraction returns None for X -> config unchanged for AUTH_TOKEN."""
        mock_extract.return_value = None

        config = _base_config(FROM_BROWSER="auto", SETUP_COMPLETE="true")
        result = extract_browser_credentials(config)

        assert "AUTH_TOKEN" not in result
        assert "CT0" not in result

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_extraction_raises_exception_config_unchanged(self, mock_extract):
        """Cookie extraction raises exception -> caught, config unchanged."""
        mock_extract.side_effect = RuntimeError("database locked")

        config = _base_config(FROM_BROWSER="auto", SETUP_COMPLETE="true")
        result = extract_browser_credentials(config)

        # Should not raise, and no credentials populated
        assert "AUTH_TOKEN" not in result
        assert "CT0" not in result

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_partial_credentials_only_fills_missing(self, mock_extract):
        """If AUTH_TOKEN is set but CT0 is not, only CT0 gets filled."""
        mock_extract.return_value = ({"auth_token": "cookie_tok", "ct0": "cookie_ct0"}, "chrome")

        config = _base_config(
            AUTH_TOKEN="explicit",
            CT0=None,
            FROM_BROWSER="auto",
            SETUP_COMPLETE="true",
        )
        result = extract_browser_credentials(config)

        # AUTH_TOKEN already set, should not be overridden
        assert "AUTH_TOKEN" not in result
        # CT0 was missing, should be filled
        assert result["CT0"] == "cookie_ct0"


class TestGetConfigCookieIntegration:
    """Integration test: get_config() calls extract_browser_credentials."""

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    @patch("scripts.lib.env._find_project_env", return_value=None)
    @patch("scripts.lib.env.load_env_file", return_value={})
    @patch("scripts.lib.env.get_openai_auth")
    def test_get_config_injects_cookies(
        self, mock_openai, mock_load, mock_proj, mock_extract
    ):
        """get_config merges browser cookies into the returned config."""
        from scripts.lib.env import get_config, OpenAIAuth

        mock_openai.return_value = OpenAIAuth(
            token=None, source="none", status="missing",
            account_id=None, codex_auth_file="/fake",
        )
        mock_extract.return_value = ({"auth_token": "browser_tok", "ct0": "browser_ct0"}, "firefox")

        import os
        env_patch = {
            "SETUP_COMPLETE": "true",
            "FROM_BROWSER": "auto",
            "LAST30DAYS_CONFIG_DIR": "",
        }
        with patch.dict(os.environ, env_patch, clear=False):
            config = get_config()

        assert config["AUTH_TOKEN"] == "browser_tok"
        assert config["CT0"] == "browser_ct0"
