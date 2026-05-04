"""Tests for source resolution priority hierarchy (Unit 4).

Validates the free-first priority chain:
  env AUTH_TOKEN/CT0 -> browser cookies -> XAI_API_KEY -> None
"""

import os
from unittest.mock import patch, MagicMock

import pytest

from scripts.lib import env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_config(**overrides):
    """Return a minimal config dict with typical defaults."""
    cfg = {
        "AUTH_TOKEN": None,
        "CT0": None,
        "XAI_API_KEY": None,
        "SCRAPECREATORS_API_KEY": None,
        "OPENAI_API_KEY": None,
        "OPENAI_AUTH_STATUS": "missing",
        "OPENROUTER_API_KEY": None,
        "PARALLEL_API_KEY": None,
        "BRAVE_API_KEY": None,
        "BSKY_HANDLE": None,
        "BSKY_APP_PASSWORD": None,
        "TRUTHSOCIAL_TOKEN": None,
        "WEIBO_SUB": None,
        "WEIBO_SUBP": None,
        "FROM_BROWSER": None,
        "SETUP_COMPLETE": None,
        "INCLUDE_SOURCES": None,
        "_AUTH_TOKEN_SOURCE": None,
    }
    cfg.update(overrides)
    return cfg


def _mock_bird_installed(installed=True):
    """Patch bird_x.is_bird_installed to return the given value."""
    return patch("scripts.lib.bird_x.is_bird_installed", return_value=installed)


def _mock_bird_authenticated(username=None):
    """Patch bird_x.is_bird_authenticated to return the given value."""
    return patch("scripts.lib.bird_x.is_bird_authenticated", return_value=username)


def _mock_bird_status(installed=True, authenticated=True, username="env AUTH_TOKEN"):
    """Patch bird_x.get_bird_status to return a status dict."""
    return patch("scripts.lib.bird_x.get_bird_status", return_value={
        "installed": installed,
        "authenticated": authenticated,
        "username": username,
        "can_install": True,
    })


# ---------------------------------------------------------------------------
# Tests: X source resolution priority
# ---------------------------------------------------------------------------

class TestXSourcePriority:
    """Test the X source priority chain: env -> browser cookies -> xAI -> None."""

    def test_no_env_cookies_found_resolves_bird_browser(self):
        """No env vars, SETUP_COMPLETE=true, cookies found -> Bird with browser method."""
        config = _base_config(
            AUTH_TOKEN="cookie_tok",
            CT0="cookie_ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="browser-firefox",
        )

        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"):
            source, method = env.get_x_source_with_method(config)

        assert source == "bird"
        assert method == "browser-firefox"

    def test_env_auth_token_plus_cookies_env_wins(self):
        """AUTH_TOKEN in .env + cookies available -> env wins (method='env')."""
        config = _base_config(
            AUTH_TOKEN="explicit_token",
            CT0="explicit_ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="env",
        )

        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"):
            source, method = env.get_x_source_with_method(config)

        assert source == "bird"
        assert method == "env"

    def test_no_env_no_cookies_xai_key_resolves_xai(self):
        """No env vars, no cookies, XAI_API_KEY set -> xAI with method 'api'."""
        config = _base_config(XAI_API_KEY="xai-key-123")

        with _mock_bird_installed(True), _mock_bird_authenticated(None):
            source, method = env.get_x_source_with_method(config)

        assert source == "xai"
        assert method == "api"

    def test_no_env_no_cookies_no_api_keys_none(self):
        """No env vars, no cookies, no API keys -> X not available."""
        config = _base_config()

        with _mock_bird_installed(True), _mock_bird_authenticated(None):
            source, method = env.get_x_source_with_method(config)

        assert source is None
        assert method is None

    def test_bird_not_installed_falls_to_xai(self):
        """Bird not installed, XAI_API_KEY set -> xAI."""
        config = _base_config(XAI_API_KEY="xai-key")

        with _mock_bird_installed(False), _mock_bird_authenticated(None):
            source, method = env.get_x_source_with_method(config)

        assert source == "xai"
        assert method == "api"

    def test_bird_not_installed_no_xai_none(self):
        """Bird not installed, no XAI_API_KEY -> None."""
        config = _base_config()

        with _mock_bird_installed(False), _mock_bird_authenticated(None):
            source, method = env.get_x_source_with_method(config)

        assert source is None
        assert method is None

    def test_browser_chrome_method_tracked(self):
        """Cookies from Chrome -> method is 'browser-chrome'."""
        config = _base_config(
            AUTH_TOKEN="chrome_tok",
            CT0="chrome_ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="browser-chrome",
        )

        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"):
            source, method = env.get_x_source_with_method(config)

        assert source == "bird"
        assert method == "browser-chrome"

    def test_browser_safari_method_tracked(self):
        """Cookies from Safari -> method is 'browser-safari'."""
        config = _base_config(
            AUTH_TOKEN="safari_tok",
            CT0="safari_ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="browser-safari",
        )

        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"):
            source, method = env.get_x_source_with_method(config)

        assert source == "bird"
        assert method == "browser-safari"


# ---------------------------------------------------------------------------
# Tests: get_x_source() backward compat
# ---------------------------------------------------------------------------

class TestGetXSourceBackwardCompat:
    """Ensure get_x_source() returns the same string as before."""

    def test_bird_returns_bird(self):
        config = _base_config(AUTH_TOKEN="tok", CT0="ct0", _AUTH_TOKEN_SOURCE="env")
        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"):
            assert env.get_x_source(config) == "bird"

    def test_xai_returns_xai(self):
        config = _base_config(XAI_API_KEY="key")
        with _mock_bird_installed(True), _mock_bird_authenticated(None):
            assert env.get_x_source(config) == "xai"

    def test_none_returns_none(self):
        config = _base_config()
        with _mock_bird_installed(False):
            assert env.get_x_source(config) is None


# ---------------------------------------------------------------------------
# Tests: get_x_source_status() method field
# ---------------------------------------------------------------------------

class TestGetXSourceStatusMethod:
    """Test that get_x_source_status() includes the method field."""

    def test_bird_env_method(self):
        config = _base_config(AUTH_TOKEN="tok", CT0="ct0", _AUTH_TOKEN_SOURCE="env")
        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"), \
             _mock_bird_status(installed=True, authenticated=True, username="env AUTH_TOKEN"):
            status = env.get_x_source_status(config)

        assert status["source"] == "bird"
        assert status["method"] == "env"
        assert "bird_installed" in status
        assert "xai_available" in status

    def test_bird_browser_method(self):
        config = _base_config(
            AUTH_TOKEN="tok", CT0="ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="browser-firefox",
        )
        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"), \
             _mock_bird_status(installed=True, authenticated=True):
            status = env.get_x_source_status(config)

        assert status["source"] == "bird"
        assert status["method"] == "browser-firefox"

    def test_xai_api_method(self):
        config = _base_config(XAI_API_KEY="key")
        with _mock_bird_installed(True), _mock_bird_authenticated(None), \
             _mock_bird_status(installed=True, authenticated=False, username=None):
            status = env.get_x_source_status(config)

        assert status["source"] == "xai"
        assert status["method"] == "api"

    def test_no_source_method_none(self):
        config = _base_config()
        with _mock_bird_installed(False), \
             _mock_bird_status(installed=False, authenticated=False, username=None):
            status = env.get_x_source_status(config)

        assert status["source"] is None
        assert status["method"] is None


# ---------------------------------------------------------------------------
# Tests: get_available_sources() with various configs
# ---------------------------------------------------------------------------

class TestGetAvailableSources:
    """Test get_available_sources() returns correct strings."""

    def test_no_x_no_web_reddit_only(self):
        """No X source, no web keys -> 'reddit' (Reddit always available)."""
        config = _base_config()
        with _mock_bird_installed(False):
            result = env.get_available_sources(config)
        assert result == "reddit"

    def test_xai_key_no_web(self):
        """XAI_API_KEY set, no web keys -> 'both'."""
        config = _base_config(XAI_API_KEY="key")
        with _mock_bird_installed(True), _mock_bird_authenticated(None):
            result = env.get_available_sources(config)
        assert result == "both"

    def test_bird_auth_no_web(self):
        """Bird authenticated (cookies), SETUP_COMPLETE=true, no web keys -> 'both'."""
        config = _base_config(
            AUTH_TOKEN="tok", CT0="ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="browser-firefox",
        )
        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"):
            result = env.get_available_sources(config)
        assert result == "both"

    def test_bird_auth_with_web(self):
        """Bird authenticated + web keys -> 'all'."""
        config = _base_config(
            AUTH_TOKEN="tok", CT0="ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="browser-firefox",
            BRAVE_API_KEY="brave-key",
        )
        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"):
            result = env.get_available_sources(config)
        assert result == "all"

    def test_no_x_with_web(self):
        """No X source, web keys -> 'reddit-web'."""
        config = _base_config(BRAVE_API_KEY="brave-key")
        with _mock_bird_installed(False):
            result = env.get_available_sources(config)
        assert result == "reddit-web"

    def test_reddit_hn_polymarket_always_available(self):
        """Reddit, HN, and Polymarket are always available regardless of config."""
        config = _base_config()
        # These functions don't depend on config
        assert env.is_hackernews_available() is True
        assert env.is_polymarket_available() is True
        # Reddit: get_available_sources always includes it
        with _mock_bird_installed(False):
            result = env.get_available_sources(config)
        assert result in ("reddit", "reddit-web")  # never 'none' when Reddit is always True


# ---------------------------------------------------------------------------
# Tests: Full resolution with mixed config
# ---------------------------------------------------------------------------

class TestFullResolution:
    """Test that each source resolves independently with mixed config."""

    def test_mixed_config_all_sources(self):
        """Bird for X, public Reddit, web keys, YouTube/TikTok available."""
        config = _base_config(
            AUTH_TOKEN="tok", CT0="ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="browser-chrome",
            BRAVE_API_KEY="brave-key",
            SCRAPECREATORS_API_KEY="sc-key",
            BSKY_HANDLE="user.bsky.social",
            BSKY_APP_PASSWORD="app-pw",
        )

        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"):
            x_source, x_method = env.get_x_source_with_method(config)
            available = env.get_available_sources(config)

        assert x_source == "bird"
        assert x_method == "browser-chrome"
        assert available == "all"  # reddit + x + web
        assert env.is_bluesky_available(config) is True
        assert env.is_tiktok_available(config) is True
        assert env.is_hackernews_available() is True
        assert env.is_polymarket_available() is True

    def test_no_config_minimal_sources(self):
        """No API keys, no cookies -> Reddit + HN + Polymarket only."""
        config = _base_config()

        with _mock_bird_installed(False):
            x_source = env.get_x_source(config)
            available = env.get_available_sources(config)

        assert x_source is None
        assert available == "reddit"
        assert env.is_hackernews_available() is True
        assert env.is_polymarket_available() is True
        assert env.is_bluesky_available(config) is False
        assert env.is_tiktok_available(config) is False


class TestWeiboDouyinAvailability:
    """Test availability checks for Weibo and Douyin connectors."""

    def test_weibo_requires_sub_cookie(self):
        cfg = _base_config(WEIBO_SUB=None)
        assert env.is_weibo_available(cfg) is False

        cfg2 = _base_config(WEIBO_SUB="sub-cookie")
        assert env.is_weibo_available(cfg2) is True

    def test_douyin_available_without_keys(self):
        cfg = _base_config()
        assert env.is_douyin_available(cfg) is True


# ---------------------------------------------------------------------------
# Tests: extract_browser_credentials tracks browser source
# ---------------------------------------------------------------------------

class TestExtractBrowserCredentialsSource:
    """Test that extract_browser_credentials tracks __X_BROWSER."""

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_tracks_firefox_source(self, mock_extract):
        """Cookies from Firefox -> __X_BROWSER set to 'firefox'."""
        mock_extract.return_value = (
            {"auth_token": "tok", "ct0": "ct0val"},
            "firefox",
        )

        config = {
            "AUTH_TOKEN": None,
            "CT0": None,
            "TRUTHSOCIAL_TOKEN": None,
            "FROM_BROWSER": "auto",
            "SETUP_COMPLETE": "true",
        }
        result = env.extract_browser_credentials(config)

        assert result["AUTH_TOKEN"] == "tok"
        assert result["CT0"] == "ct0val"
        assert result["__X_BROWSER"] == "firefox"

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_tracks_chrome_source(self, mock_extract):
        """Cookies from Chrome -> __X_BROWSER set to 'chrome'."""
        mock_extract.return_value = (
            {"auth_token": "tok", "ct0": "ct0val"},
            "chrome",
        )

        config = {
            "AUTH_TOKEN": None,
            "CT0": None,
            "TRUTHSOCIAL_TOKEN": None,
            "FROM_BROWSER": "chrome",
            "SETUP_COMPLETE": "true",
        }
        result = env.extract_browser_credentials(config)

        assert result["__X_BROWSER"] == "chrome"

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    def test_no_cookies_no_browser_key(self, mock_extract):
        """No cookies found -> no __X_BROWSER key."""
        mock_extract.return_value = None

        config = {
            "AUTH_TOKEN": None,
            "CT0": None,
            "TRUTHSOCIAL_TOKEN": None,
            "FROM_BROWSER": "auto",
            "SETUP_COMPLETE": "true",
        }
        result = env.extract_browser_credentials(config)

        assert "__X_BROWSER" not in result


# ---------------------------------------------------------------------------
# Tests: get_config() _AUTH_TOKEN_SOURCE tracking
# ---------------------------------------------------------------------------

class TestGetConfigAuthTokenSource:
    """Test that get_config() sets _AUTH_TOKEN_SOURCE correctly."""

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    @patch("scripts.lib.env._find_project_env", return_value=None)
    @patch("scripts.lib.env.load_env_file", return_value={})
    @patch("scripts.lib.env.get_openai_auth")
    def test_env_var_auth_token_source_env(
        self, mock_openai, mock_load, mock_proj, mock_extract
    ):
        """AUTH_TOKEN from env var -> _AUTH_TOKEN_SOURCE='env'."""
        from scripts.lib.env import get_config, OpenAIAuth

        mock_openai.return_value = OpenAIAuth(
            token=None, source="none", status="missing",
            account_id=None, codex_auth_file="/fake",
        )
        mock_extract.return_value = None

        env_patch = {
            "AUTH_TOKEN": "env_token",
            "CT0": "env_ct0",
            "LAST30DAYS_CONFIG_DIR": "",
        }
        with patch.dict(os.environ, env_patch, clear=False):
            config = get_config()

        assert config["_AUTH_TOKEN_SOURCE"] == "env"

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    @patch("scripts.lib.env._find_project_env", return_value=None)
    @patch("scripts.lib.env.load_env_file", return_value={})
    @patch("scripts.lib.env.get_openai_auth")
    def test_browser_cookies_auth_token_source_browser(
        self, mock_openai, mock_load, mock_proj, mock_extract
    ):
        """AUTH_TOKEN from cookies -> _AUTH_TOKEN_SOURCE='browser-firefox'."""
        from scripts.lib.env import get_config, OpenAIAuth

        mock_openai.return_value = OpenAIAuth(
            token=None, source="none", status="missing",
            account_id=None, codex_auth_file="/fake",
        )
        mock_extract.return_value = (
            {"auth_token": "cookie_tok", "ct0": "cookie_ct0"},
            "firefox",
        )

        env_patch = {
            "SETUP_COMPLETE": "true",
            "FROM_BROWSER": "auto",
            "LAST30DAYS_CONFIG_DIR": "",
        }
        # Ensure AUTH_TOKEN is NOT in env
        clean_env = {k: v for k, v in os.environ.items()
                     if k not in ("AUTH_TOKEN", "CT0")}
        clean_env.update(env_patch)
        with patch.dict(os.environ, clean_env, clear=True):
            config = get_config()

        assert config["AUTH_TOKEN"] == "cookie_tok"
        assert config["_AUTH_TOKEN_SOURCE"] == "browser-firefox"

    @patch("scripts.lib.cookie_extract.extract_cookies_with_source")
    @patch("scripts.lib.env._find_project_env", return_value=None)
    @patch("scripts.lib.env.load_env_file", return_value={})
    @patch("scripts.lib.env.get_openai_auth")
    def test_no_auth_token_source_none(
        self, mock_openai, mock_load, mock_proj, mock_extract
    ):
        """No AUTH_TOKEN at all -> _AUTH_TOKEN_SOURCE=None."""
        from scripts.lib.env import get_config, OpenAIAuth

        mock_openai.return_value = OpenAIAuth(
            token=None, source="none", status="missing",
            account_id=None, codex_auth_file="/fake",
        )
        mock_extract.return_value = None

        clean_env = {k: v for k, v in os.environ.items()
                     if k not in ("AUTH_TOKEN", "CT0")}
        clean_env["LAST30DAYS_CONFIG_DIR"] = ""
        with patch.dict(os.environ, clean_env, clear=True):
            config = get_config()

        assert config["_AUTH_TOKEN_SOURCE"] is None


# ---------------------------------------------------------------------------
# Tests: SETUP_COMPLETE gate — Bird cookie probing blocked before consent
# ---------------------------------------------------------------------------

class TestSetupCompleteGate:
    """Test that Bird cookie probing is gated behind SETUP_COMPLETE consent."""

    def test_no_setup_complete_bird_has_cookies_returns_none(self):
        """SETUP_COMPLETE not set, Bird has browser cookies -> returns None (not 'bird').

        Bird's is_bird_authenticated() should NOT be called at all because
        there is no consent yet. Cookie-sourced AUTH_TOKEN must be ignored.
        """
        config = _base_config(
            AUTH_TOKEN="cookie_tok",
            CT0="cookie_ct0",
            SETUP_COMPLETE=None,  # not set — first run
            _AUTH_TOKEN_SOURCE="browser-chrome",
        )

        with _mock_bird_installed(True), \
             _mock_bird_authenticated("Chrome") as mock_auth:
            source = env.get_x_source(config)

        assert source is None
        # is_bird_authenticated should NOT have been called (no cookie probing)
        mock_auth.assert_not_called()

    def test_setup_complete_bird_has_cookies_returns_bird(self):
        """SETUP_COMPLETE=true, Bird has browser cookies -> returns 'bird'.

        After user consent, cookie probing should work normally.
        """
        config = _base_config(
            AUTH_TOKEN="cookie_tok",
            CT0="cookie_ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="browser-chrome",
        )

        with _mock_bird_installed(True), _mock_bird_authenticated("Chrome"):
            source = env.get_x_source(config)

        assert source == "bird"

    def test_no_setup_complete_explicit_auth_token_returns_bird(self):
        """SETUP_COMPLETE not set, AUTH_TOKEN from env var -> returns 'bird' with method 'env'.

        Explicit env var credentials must ALWAYS work regardless of SETUP_COMPLETE.
        """
        config = _base_config(
            AUTH_TOKEN="explicit_token",
            CT0="explicit_ct0",
            SETUP_COMPLETE=None,  # not set
            _AUTH_TOKEN_SOURCE="env",
        )

        with _mock_bird_installed(True), _mock_bird_authenticated("env AUTH_TOKEN"):
            source, method = env.get_x_source_with_method(config)

        assert source == "bird"
        assert method == "env"

    def test_no_setup_complete_xai_key_returns_xai(self):
        """SETUP_COMPLETE not set, XAI_API_KEY configured -> returns 'xai'.

        API keys always work without setup consent.
        """
        config = _base_config(
            XAI_API_KEY="xai-key-123",
            SETUP_COMPLETE=None,  # not set
        )

        with _mock_bird_installed(True), _mock_bird_authenticated(None):
            source, method = env.get_x_source_with_method(config)

        assert source == "xai"
        assert method == "api"

    def test_no_setup_complete_status_reports_not_configured(self):
        """First-run status banner should show X as not configured when only cookies exist."""
        config = _base_config(
            AUTH_TOKEN="cookie_tok",
            CT0="cookie_ct0",
            SETUP_COMPLETE=None,
            _AUTH_TOKEN_SOURCE="browser-firefox",
        )

        with _mock_bird_installed(True):
            status = env.get_x_source_status(config)

        assert status["source"] is None
        assert status["method"] is None
        assert status["bird_authenticated"] is False

    def test_setup_complete_status_reports_bird(self):
        """After consent, status banner should show Bird as configured."""
        config = _base_config(
            AUTH_TOKEN="cookie_tok",
            CT0="cookie_ct0",
            SETUP_COMPLETE="true",
            _AUTH_TOKEN_SOURCE="browser-firefox",
        )

        with _mock_bird_installed(True), _mock_bird_authenticated("Firefox"), \
             _mock_bird_status(installed=True, authenticated=True, username="Firefox"):
            status = env.get_x_source_status(config)

        assert status["source"] == "bird"
        assert status["method"] == "browser-firefox"
        assert status["bird_authenticated"] is True


# ---------------------------------------------------------------------------
# Tests: BIRD_DISABLE_BROWSER_COOKIES env var on first run
# ---------------------------------------------------------------------------

class TestBirdDisableBrowserCookiesEnvVar:
    """Test that BIRD_DISABLE_BROWSER_COOKIES is set to block Bird's Node.js
    sweet-cookie scanner on first run before user consent."""

    def _run_main_flow_env_setup(self, config, first_run):
        """Simulate the env-var-setting logic from last30days.py main flow.

        Mirrors the block right after first_run detection in main().
        """
        if first_run and config.get('_AUTH_TOKEN_SOURCE') != 'env':
            os.environ['BIRD_DISABLE_BROWSER_COOKIES'] = '1'
        else:
            os.environ.pop('BIRD_DISABLE_BROWSER_COOKIES', None)

    def test_first_run_no_auth_token_sets_env_var(self):
        """first_run=True, no AUTH_TOKEN -> BIRD_DISABLE_BROWSER_COOKIES is set."""
        config = _base_config(SETUP_COMPLETE=None, _AUTH_TOKEN_SOURCE=None)
        try:
            self._run_main_flow_env_setup(config, first_run=True)
            assert os.environ.get('BIRD_DISABLE_BROWSER_COOKIES') == '1'
        finally:
            os.environ.pop('BIRD_DISABLE_BROWSER_COOKIES', None)

    def test_not_first_run_no_env_var(self):
        """first_run=False -> BIRD_DISABLE_BROWSER_COOKIES is NOT set."""
        config = _base_config(SETUP_COMPLETE="true", _AUTH_TOKEN_SOURCE="browser-firefox")
        try:
            self._run_main_flow_env_setup(config, first_run=False)
            assert 'BIRD_DISABLE_BROWSER_COOKIES' not in os.environ
        finally:
            os.environ.pop('BIRD_DISABLE_BROWSER_COOKIES', None)

    def test_first_run_explicit_auth_token_no_env_var(self):
        """first_run=True, AUTH_TOKEN explicitly set -> BIRD_DISABLE_BROWSER_COOKIES is NOT set."""
        config = _base_config(
            AUTH_TOKEN="explicit_token",
            CT0="explicit_ct0",
            SETUP_COMPLETE=None,
            _AUTH_TOKEN_SOURCE="env",
        )
        try:
            self._run_main_flow_env_setup(config, first_run=True)
            assert 'BIRD_DISABLE_BROWSER_COOKIES' not in os.environ
        finally:
            os.environ.pop('BIRD_DISABLE_BROWSER_COOKIES', None)


# ---------------------------------------------------------------------------
# Tests: INCLUDE_SOURCES config override
# ---------------------------------------------------------------------------

class TestIncludeSourcesOverride:
    """Test that INCLUDE_SOURCES forces sources on regardless of tier."""

    def _simulate_source_decisions(self, config, query_type="breaking_news"):
        """Simulate the source decision logic from last30days.py main flow.

        Returns (search_run_tiktok, search_run_instagram) after tier + override.
        """
        from scripts.lib import query_type as qt

        has_tiktok = env.is_tiktok_available(config)
        has_instagram = env.is_instagram_available(config)

        # Tier system decision
        search_run_tiktok = has_tiktok and qt.is_source_enabled("tiktok", query_type)
        search_run_instagram = has_instagram and qt.is_source_enabled("instagram", query_type)

        # INCLUDE_SOURCES override (mirrors last30days.py logic)
        _include_sources = {
            s.strip().lower()
            for s in (config.get('INCLUDE_SOURCES') or '').split(',')
            if s.strip()
        }
        if _include_sources:
            if 'tiktok' in _include_sources and has_tiktok:
                if not search_run_tiktok:
                    search_run_tiktok = True
            if 'instagram' in _include_sources and has_instagram:
                if not search_run_instagram:
                    search_run_instagram = True

        return search_run_tiktok, search_run_instagram

    def test_include_sources_forces_tiktok_and_instagram_on(self):
        """INCLUDE_SOURCES=tiktok,instagram + SC key + GENERAL query -> both forced on."""
        config = _base_config(
            SCRAPECREATORS_API_KEY="sc-key",
            INCLUDE_SOURCES="tiktok,instagram",
        )
        run_tiktok, run_instagram = self._simulate_source_decisions(config, "breaking_news")
        assert run_tiktok is True
        assert run_instagram is True

    def test_no_include_sources_tier_controls(self):
        """No INCLUDE_SOURCES + SC key + GENERAL query -> tier system controls (both off)."""
        config = _base_config(
            SCRAPECREATORS_API_KEY="sc-key",
        )
        run_tiktok, run_instagram = self._simulate_source_decisions(config, "breaking_news")
        # breaking_news tier doesn't include tiktok or instagram
        assert run_tiktok is False
        assert run_instagram is False

    def test_include_sources_no_sc_key_still_off(self):
        """INCLUDE_SOURCES=tiktok but no SC key -> TikTok still off (no backend)."""
        config = _base_config(
            INCLUDE_SOURCES="tiktok",
        )
        run_tiktok, run_instagram = self._simulate_source_decisions(config, "breaking_news")
        assert run_tiktok is False
        assert run_instagram is False

    def test_include_sources_none_is_safe(self):
        """INCLUDE_SOURCES=None should keep default tier behavior and not crash."""
        config = _base_config(
            SCRAPECREATORS_API_KEY="sc-key",
            INCLUDE_SOURCES=None,
        )
        run_tiktok, run_instagram = self._simulate_source_decisions(config, "breaking_news")
        assert run_tiktok is False
        assert run_instagram is False
