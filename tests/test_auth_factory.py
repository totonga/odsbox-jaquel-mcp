"""Tests for auth_factory module — environment variable resolution and keyring fallback."""

from unittest.mock import patch

import pytest

from odsbox_jaquel_mcp.auth_factory import resolve_auth_args_from_env


class TestResolveMode:
    """Test mode detection and validation."""

    def test_default_mode_is_basic(self, monkeypatch):
        """When MODE is not set, defaults to basic."""
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_USERNAME", "user")
        monkeypatch.setenv("ODSBOX_MCP_PASSWORD", "pass")

        result = resolve_auth_args_from_env("ODSBOX_MCP")
        assert result["mode"] == "basic"

    def test_explicit_basic_mode(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "basic")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_USERNAME", "user")
        monkeypatch.setenv("ODSBOX_MCP_PASSWORD", "pass")

        result = resolve_auth_args_from_env("ODSBOX_MCP")
        assert result["mode"] == "basic"

    def test_m2m_mode(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "m2m")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_M2M_TOKEN_ENDPOINT", "http://auth/token")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_ID", "my-client")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_SECRET", "my-secret")

        result = resolve_auth_args_from_env("ODSBOX_MCP")
        assert result["mode"] == "m2m"

    def test_oidc_mode(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "oidc")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_CLIENT_ID", "my-client")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_REDIRECT_URI", "http://127.0.0.1:1234")

        result = resolve_auth_args_from_env("ODSBOX_MCP")
        assert result["mode"] == "oidc"

    def test_invalid_mode_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "foobar")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")

        with pytest.raises(ValueError, match="Invalid authentication mode.*foobar"):
            resolve_auth_args_from_env("ODSBOX_MCP")

    def test_mode_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "M2M")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_M2M_TOKEN_ENDPOINT", "http://auth/token")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_ID", "cid")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_SECRET", "sec")

        result = resolve_auth_args_from_env("ODSBOX_MCP")
        assert result["mode"] == "m2m"

    def test_mode_from_legacy_prefix(self, monkeypatch):
        """MODE can also be read from ODS_ legacy prefix."""
        monkeypatch.setenv("ODS_MODE", "m2m")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_M2M_TOKEN_ENDPOINT", "http://auth/token")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_ID", "cid")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_SECRET", "sec")

        result = resolve_auth_args_from_env("ODSBOX_MCP")
        assert result["mode"] == "m2m"


class TestBasicMode:
    """Test basic authentication mode resolution."""

    def test_all_env_vars_set(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_USERNAME", "admin")
        monkeypatch.setenv("ODSBOX_MCP_PASSWORD", "secret123")
        monkeypatch.setenv("ODSBOX_MCP_VERIFY", "false")

        result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["mode"] == "basic"
        assert result["url"] == "http://server/api"
        assert result["username"] == "admin"
        assert result["password"] == "secret123"
        assert result["verify_certificate"] is False

    def test_legacy_env_vars_fallback(self, monkeypatch):
        """Legacy ODS_ prefix variables should work."""
        monkeypatch.setenv("ODS_URL", "http://server/api")
        monkeypatch.setenv("ODS_USER", "admin")
        monkeypatch.setenv("ODS_PWD", "secret123")

        result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["url"] == "http://server/api"
        assert result["username"] == "admin"
        assert result["password"] == "secret123"

    def test_api_url_alias(self, monkeypatch):
        """API_URL should work as alternative to URL."""
        monkeypatch.setenv("ODSBOX_MCP_API_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_USERNAME", "user")
        monkeypatch.setenv("ODSBOX_MCP_PASSWORD", "pass")

        result = resolve_auth_args_from_env("ODSBOX_MCP")
        assert result["url"] == "http://server/api"

    def test_missing_url_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_USERNAME", "user")
        monkeypatch.setenv("ODSBOX_MCP_PASSWORD", "pass")

        with pytest.raises(ValueError, match="ODSBOX_MCP_URL"):
            resolve_auth_args_from_env("ODSBOX_MCP")

    def test_missing_username_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_PASSWORD", "pass")

        with pytest.raises(ValueError, match="ODSBOX_MCP_USERNAME"):
            resolve_auth_args_from_env("ODSBOX_MCP")

    def test_missing_password_no_keyring_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_USERNAME", "user")

        with patch("odsbox_jaquel_mcp.auth_factory._get_secret_from_keyring", return_value=None):
            with pytest.raises(ValueError, match="keyring set"):
                resolve_auth_args_from_env("ODSBOX_MCP")

    def test_password_from_keyring(self, monkeypatch):
        """When PASSWORD not in env, fall back to keyring."""
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_USERNAME", "admin")

        with patch(
            "odsbox_jaquel_mcp.auth_factory._get_secret_from_keyring",
            return_value="keyring-password",
        ) as mock_kr:
            result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["password"] == "keyring-password"
        mock_kr.assert_called_once_with("http://server/api", "admin")

    def test_verify_defaults_to_true(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_USERNAME", "user")
        monkeypatch.setenv("ODSBOX_MCP_PASSWORD", "pass")

        result = resolve_auth_args_from_env("ODSBOX_MCP")
        assert result["verify_certificate"] is True

    def test_custom_prefix(self, monkeypatch):
        """Custom prefix should be used for all lookups."""
        monkeypatch.setenv("MY_APP_URL", "http://custom/api")
        monkeypatch.setenv("MY_APP_USERNAME", "user")
        monkeypatch.setenv("MY_APP_PASSWORD", "pass")

        result = resolve_auth_args_from_env("MY_APP")

        assert result["url"] == "http://custom/api"
        assert result["username"] == "user"


class TestM2MMode:
    """Test M2M authentication mode resolution."""

    def test_all_env_vars_set(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "m2m")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_M2M_TOKEN_ENDPOINT", "http://auth/token")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_ID", "my-client")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_SECRET", "my-secret")
        monkeypatch.setenv("ODSBOX_MCP_M2M_SCOPE", "api,admin")

        result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["mode"] == "m2m"
        assert result["url"] == "http://server/api"
        assert result["token_endpoint"] == "http://auth/token"
        assert result["client_id"] == "my-client"
        assert result["client_secret"] == "my-secret"
        assert result["scope"] == ["api", "admin"]

    def test_scope_is_none_when_not_set(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "m2m")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_M2M_TOKEN_ENDPOINT", "http://auth/token")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_ID", "cid")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_SECRET", "sec")

        result = resolve_auth_args_from_env("ODSBOX_MCP")
        assert result["scope"] is None

    def test_missing_token_endpoint_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "m2m")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_ID", "cid")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_SECRET", "sec")

        with pytest.raises(ValueError, match="M2M_TOKEN_ENDPOINT"):
            resolve_auth_args_from_env("ODSBOX_MCP")

    def test_missing_client_id_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "m2m")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_M2M_TOKEN_ENDPOINT", "http://auth/token")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_SECRET", "sec")

        with pytest.raises(ValueError, match="M2M_CLIENT_ID"):
            resolve_auth_args_from_env("ODSBOX_MCP")

    def test_missing_secret_no_keyring_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "m2m")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_M2M_TOKEN_ENDPOINT", "http://auth/token")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_ID", "cid")

        with patch("odsbox_jaquel_mcp.auth_factory._get_secret_from_keyring", return_value=None):
            with pytest.raises(ValueError, match="keyring set"):
                resolve_auth_args_from_env("ODSBOX_MCP")

    def test_client_secret_from_keyring(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "m2m")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_M2M_TOKEN_ENDPOINT", "http://auth/token")
        monkeypatch.setenv("ODSBOX_MCP_M2M_CLIENT_ID", "my-client")

        with patch(
            "odsbox_jaquel_mcp.auth_factory._get_secret_from_keyring",
            return_value="kr-secret",
        ) as mock_kr:
            result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["client_secret"] == "kr-secret"
        mock_kr.assert_called_once_with("http://auth/token", "my-client")


class TestOIDCMode:
    """Test OIDC authentication mode resolution."""

    def test_minimal_oidc(self, monkeypatch):
        """OIDC with just required fields — WebFinger discovery."""
        monkeypatch.setenv("ODSBOX_MCP_MODE", "oidc")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_CLIENT_ID", "my-client")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_REDIRECT_URI", "http://127.0.0.1:1234")

        with patch("odsbox_jaquel_mcp.auth_factory._get_secret_from_keyring", return_value=None):
            result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["mode"] == "oidc"
        assert result["url"] == "http://server/api"
        assert result["client_id"] == "my-client"
        assert result["redirect_uri"] == "http://127.0.0.1:1234"
        assert result["client_secret"] is None  # public client
        assert result["redirect_url_allow_insecure"] is False
        assert result["login_timeout"] == 60
        assert result["webfinger_path_prefix"] == ""

    def test_oidc_with_explicit_endpoints(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "oidc")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_CLIENT_ID", "my-client")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_REDIRECT_URI", "http://127.0.0.1:1234")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_AUTHORIZATION_ENDPOINT", "http://auth/authorize")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_TOKEN_ENDPOINT", "http://auth/token")

        with patch("odsbox_jaquel_mcp.auth_factory._get_secret_from_keyring", return_value=None):
            result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["authorization_endpoint"] == "http://auth/authorize"
        assert result["token_endpoint"] == "http://auth/token"

    def test_oidc_with_all_options(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "oidc")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_CLIENT_ID", "my-client")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_REDIRECT_URI", "http://127.0.0.1:1234")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_CLIENT_SECRET", "oidc-secret")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_REDIRECT_INSECURE", "true")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_WEBFINGER_PATH_PREFIX", "/ods")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_LOGIN_TIMEOUT", "30")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_SCOPE", "openid,profile,email")
        monkeypatch.setenv("ODSBOX_MCP_VERIFY", "false")

        result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["client_secret"] == "oidc-secret"
        assert result["redirect_url_allow_insecure"] is True
        assert result["webfinger_path_prefix"] == "/ods"
        assert result["login_timeout"] == 30
        assert result["scope"] == ["openid", "profile", "email"]
        assert result["verify_certificate"] is False

    def test_missing_client_id_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "oidc")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_REDIRECT_URI", "http://127.0.0.1:1234")

        with pytest.raises(ValueError, match="OIDC_CLIENT_ID"):
            resolve_auth_args_from_env("ODSBOX_MCP")

    def test_missing_redirect_uri_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "oidc")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_CLIENT_ID", "my-client")

        with pytest.raises(ValueError, match="OIDC_REDIRECT_URI"):
            resolve_auth_args_from_env("ODSBOX_MCP")

    def test_client_secret_from_keyring(self, monkeypatch):
        """OIDC client_secret falls back to keyring."""
        monkeypatch.setenv("ODSBOX_MCP_MODE", "oidc")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_CLIENT_ID", "my-client")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_REDIRECT_URI", "http://127.0.0.1:1234")

        with patch(
            "odsbox_jaquel_mcp.auth_factory._get_secret_from_keyring",
            return_value="kr-oidc-secret",
        ) as mock_kr:
            result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["client_secret"] == "kr-oidc-secret"
        mock_kr.assert_called_once_with("http://server/api", "my-client")

    def test_no_client_secret_is_ok_for_public_client(self, monkeypatch):
        """OIDC should NOT raise if client_secret is missing — public client."""
        monkeypatch.setenv("ODSBOX_MCP_MODE", "oidc")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_CLIENT_ID", "my-client")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_REDIRECT_URI", "http://127.0.0.1:1234")

        with patch("odsbox_jaquel_mcp.auth_factory._get_secret_from_keyring", return_value=None):
            result = resolve_auth_args_from_env("ODSBOX_MCP")

        assert result["client_secret"] is None

    def test_invalid_login_timeout_raises(self, monkeypatch):
        monkeypatch.setenv("ODSBOX_MCP_MODE", "oidc")
        monkeypatch.setenv("ODSBOX_MCP_URL", "http://server/api")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_CLIENT_ID", "my-client")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_REDIRECT_URI", "http://127.0.0.1:1234")
        monkeypatch.setenv("ODSBOX_MCP_OIDC_LOGIN_TIMEOUT", "not-a-number")

        with pytest.raises(ValueError, match="OIDC_LOGIN_TIMEOUT.*integer"):
            resolve_auth_args_from_env("ODSBOX_MCP")


class TestKeyringFallback:
    """Test keyring integration edge cases."""

    def test_keyring_import_failure_returns_none(self):
        """If keyring is not installed, _get_secret_from_keyring returns None."""
        from odsbox_jaquel_mcp.auth_factory import _get_secret_from_keyring

        with patch.dict("sys.modules", {"keyring": None}):
            # Importing None module raises TypeError, caught by except Exception
            result = _get_secret_from_keyring("service", "user")
            assert result is None

    def test_keyring_get_password_raises_returns_none(self):
        """If keyring.get_password raises, _get_secret_from_keyring returns None."""
        import keyring

        from odsbox_jaquel_mcp.auth_factory import _get_secret_from_keyring

        with patch.object(keyring, "get_password", side_effect=RuntimeError("no backend")):
            result = _get_secret_from_keyring("svc", "usr")
            assert result is None
