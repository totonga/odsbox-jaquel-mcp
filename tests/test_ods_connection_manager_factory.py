"""Tests for ODSConnectionManager.connect_with_factory() — ConIFactory dispatch."""

from unittest.mock import Mock, patch

import pytest
from fastmcp.exceptions import ToolError

from odsbox_jaquel_mcp import ODSConnectionManager


class TestConnectWithFactory:
    """Test connect_with_factory dispatches to correct ConIFactory methods."""

    def setup_method(self):
        """Reset singleton instance before each test."""
        ODSConnectionManager._instance = None
        ODSConnectionManager._con_i = None
        ODSConnectionManager._model_cache = None
        ODSConnectionManager._model = None
        ODSConnectionManager._connection_info = {}

    def _mock_con_i(self):
        """Create a standard mock ConI instance."""
        mock = Mock()
        mock.con_i_url.return_value = "http://test:8087/api"
        mock.mc = Mock()
        model = Mock()
        model.entities = {"Measurement": Mock(), "Test": Mock()}
        mock.model.return_value = model
        return mock

    @patch("odsbox_jaquel_mcp.connection.ConIFactory")
    def test_basic_mode(self, mock_factory):
        """Basic mode calls ConIFactory.basic with correct args."""
        mock_con_i = self._mock_con_i()
        mock_factory.basic.return_value = mock_con_i

        auth_args = {
            "mode": "basic",
            "url": "http://test:8087/api",
            "username": "admin",
            "password": "secret",
            "verify_certificate": False,
        }

        result = ODSConnectionManager.connect_with_factory(auth_args)

        mock_factory.basic.assert_called_once_with(
            url="http://test:8087/api",
            username="admin",
            password="secret",
            verify_certificate=False,
        )
        assert result["connection"]["username"] == "admin"
        assert result["connection"]["status"] == "connected"
        assert ODSConnectionManager.is_connected()

    @patch("odsbox_jaquel_mcp.connection.ConIFactory")
    def test_m2m_mode(self, mock_factory):
        """M2M mode calls ConIFactory.m2m with correct args."""
        mock_con_i = self._mock_con_i()
        mock_factory.m2m.return_value = mock_con_i

        auth_args = {
            "mode": "m2m",
            "url": "http://test:8087/api",
            "token_endpoint": "http://auth/token",
            "client_id": "my-client",
            "client_secret": "my-secret",
            "scope": ["api", "admin"],
            "verify_certificate": True,
        }

        result = ODSConnectionManager.connect_with_factory(auth_args)

        mock_factory.m2m.assert_called_once_with(
            url="http://test:8087/api",
            token_endpoint="http://auth/token",
            client_id="my-client",
            client_secret="my-secret",
            scope=["api", "admin"],
            verify_certificate=True,
        )
        assert result["connection"]["username"] == "my-client"
        assert result["connection"]["status"] == "connected"

    @patch("odsbox_jaquel_mcp.connection.ConIFactory")
    def test_oidc_mode(self, mock_factory):
        """OIDC mode calls ConIFactory.oidc with correct args."""
        mock_con_i = self._mock_con_i()
        mock_factory.oidc.return_value = mock_con_i

        auth_args = {
            "mode": "oidc",
            "url": "http://test:8087/api",
            "client_id": "oidc-client",
            "redirect_uri": "http://127.0.0.1:1234",
            "redirect_url_allow_insecure": True,
            "client_secret": None,
            "scope": ["openid"],
            "authorization_endpoint": "http://auth/authorize",
            "token_endpoint": "http://auth/token",
            "login_timeout": 30,
            "verify_certificate": True,
            "webfinger_path_prefix": "/ods",
        }

        result = ODSConnectionManager.connect_with_factory(auth_args)

        mock_factory.oidc.assert_called_once_with(
            url="http://test:8087/api",
            client_id="oidc-client",
            redirect_uri="http://127.0.0.1:1234",
            redirect_url_allow_insecure=True,
            client_secret=None,
            scope=["openid"],
            authorization_endpoint="http://auth/authorize",
            token_endpoint="http://auth/token",
            login_timeout=30,
            verify_certificate=True,
            webfinger_path_prefix="/ods",
        )
        assert result["connection"]["username"] == "oidc-client"

    @patch("odsbox_jaquel_mcp.connection.ConIFactory")
    def test_oidc_minimal_defaults(self, mock_factory):
        """OIDC with missing optional keys uses defaults via .get()."""
        mock_con_i = self._mock_con_i()
        mock_factory.oidc.return_value = mock_con_i

        auth_args = {
            "mode": "oidc",
            "url": "http://test:8087/api",
            "client_id": "cid",
            "redirect_uri": "http://127.0.0.1:1234",
        }

        ODSConnectionManager.connect_with_factory(auth_args)

        mock_factory.oidc.assert_called_once_with(
            url="http://test:8087/api",
            client_id="cid",
            redirect_uri="http://127.0.0.1:1234",
            redirect_url_allow_insecure=False,
            client_secret=None,
            scope=None,
            authorization_endpoint=None,
            token_endpoint=None,
            login_timeout=60,
            verify_certificate=True,
            webfinger_path_prefix="",
        )

    @patch("odsbox_jaquel_mcp.connection.ConIFactory")
    def test_connection_failure_wraps_in_tool_error(self, mock_factory):
        """ConIFactory exceptions are wrapped in ToolError."""
        mock_factory.basic.side_effect = Exception("auth failed")

        auth_args = {
            "mode": "basic",
            "url": "http://test:8087/api",
            "username": "user",
            "password": "pass",
        }

        with pytest.raises(ToolError, match="Connection failed.*basic.*auth failed"):
            ODSConnectionManager.connect_with_factory(auth_args)

        assert not ODSConnectionManager.is_connected()

    @patch("odsbox_jaquel_mcp.connection.ConIFactory")
    def test_unknown_mode_raises_tool_error(self, mock_factory):
        """Unknown mode raises ToolError via ValueError."""
        auth_args = {"mode": "unknown_mode"}

        with pytest.raises(ToolError, match="Unknown authentication mode"):
            ODSConnectionManager.connect_with_factory(auth_args)

    @patch("odsbox_jaquel_mcp.connection.ConIFactory")
    def test_replaces_existing_connection(self, mock_factory):
        """Calling connect_with_factory when already connected replaces connection."""
        mock_con_i_1 = self._mock_con_i()
        mock_con_i_2 = self._mock_con_i()
        mock_con_i_2.con_i_url.return_value = "http://new-server/api"
        mock_factory.basic.side_effect = [mock_con_i_1, mock_con_i_2]

        auth_args = {
            "mode": "basic",
            "url": "http://test:8087/api",
            "username": "user1",
            "password": "pass1",
        }

        ODSConnectionManager.connect_with_factory(auth_args)
        assert ODSConnectionManager.is_connected()

        auth_args["username"] = "user2"
        result = ODSConnectionManager.connect_with_factory(auth_args)

        assert result["connection"]["username"] == "user2"
        mock_con_i_1.close.assert_called_once()
