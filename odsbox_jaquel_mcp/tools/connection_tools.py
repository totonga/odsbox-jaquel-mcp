"""ODS connection tool handlers."""

from __future__ import annotations

import os
from typing import Any

from mcp.types import TextContent

from ..connection import ODSConnectionManager
from .base_handler import BaseToolHandler


class ConnectionToolHandler(BaseToolHandler):
    """Handles ODS connection management tools."""

    @staticmethod
    def ods_connect(arguments: dict[str, Any]) -> list[TextContent]:
        """Establish connection to ASAM ODS server."""
        try:
            url = arguments.get("url")
            if not url or not isinstance(url, str) or not url.strip():
                raise ValueError("url must be a non-empty string")
            username = arguments.get("username")
            if not username or not isinstance(username, str) or not username.strip():
                raise ValueError("username must be a non-empty string")
            password = arguments.get("password")
            if not password or not isinstance(password, str) or not password.strip():
                raise ValueError("password must be a non-empty string")
            verify = arguments.get("verify", True)
            if not isinstance(verify, bool):
                raise ValueError("verify must be a boolean")

            result = ODSConnectionManager.connect(url=url, auth=(username, password), verify_certificate=verify)
            return ConnectionToolHandler.json_response(result)
        except Exception as e:
            return ConnectionToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def ods_disconnect(arguments: dict[str, Any]) -> list[TextContent]:
        """Close connection to ODS server."""
        try:
            result = ODSConnectionManager.disconnect()
            return ConnectionToolHandler.json_response(result)
        except Exception as e:
            return ConnectionToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def ods_get_connection_info(arguments: dict[str, Any]) -> list[TextContent]:
        """Get current ODS connection information."""
        try:
            info = ODSConnectionManager.get_connection_info()
            return ConnectionToolHandler.json_response(info)
        except Exception as e:
            return ConnectionToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def ods_connect_using_env(arguments: dict[str, Any]) -> list[TextContent]:
        """Establish connection to ASAM ODS server using environment variables.

        By default, this tool reads the following environment variables:
          - ODSBOX_MCP_URL / ODSBOX_MCP_API_URL
          - ODSBOX_MCP_USERNAME / ODSBOX_MCP_USER
          - ODSBOX_MCP_PASSWORD
          - ODSBOX_MCP_VERIFY

        The prefix can be changed using:
          - tool argument `env_prefix`
          - environment variable `ODSBOX_MCP_ENV_PREFIX`

        For backward compatibility, it will also fall back to the legacy:
          - ODS_URL / ODS_API_URL
          - ODS_USERNAME / ODS_USER
          - ODS_PASSWORD
          - ODS_VERIFY
        """
        try:
            env = os.environ
            env_prefix = (
                arguments.get("env_prefix")
                or env.get("ODSBOX_MCP_ENV_PREFIX")
                or "ODSBOX_MCP"
            )

            def _env_get(key: str) -> str | None:
                return env.get(f"{env_prefix}_{key}") or env.get(f"ODS_{key}")

            url = _env_get("URL") or _env_get("API_URL")
            if not url or not isinstance(url, str) or not url.strip():
                raise ValueError(
                    f"Environment variable {env_prefix}_URL (or {env_prefix}_API_URL) must be set to a non-empty string"
                )

            username = _env_get("USERNAME") or _env_get("USER")
            if not username or not isinstance(username, str) or not username.strip():
                raise ValueError(
                    f"Environment variable {env_prefix}_USERNAME (or {env_prefix}_USER) must be set to a non-empty string"
                )

            password = _env_get("PASSWORD") or _env_get("PWD")
            if not password or not isinstance(password, str) or not password.strip():
                raise ValueError(
                    f"Environment variable {env_prefix}_PASSWORD (or {env_prefix}_PWD) must be set to a non-empty string"
                )

            verify = _env_get("VERIFY")
            if verify is None or str(verify).strip() == "":
                verify_bool = True
            else:
                verify_bool = str(verify).strip().lower() in ("1", "true", "yes", "y")

            result = ODSConnectionManager.connect(url=url, auth=(username, password), verify_certificate=verify_bool)
            return ConnectionToolHandler.json_response(result)
        except Exception as e:
            return ConnectionToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def query_execute(arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a Jaquel query on connected ODS server."""
        try:
            query = arguments.get("query", {})
            result = ODSConnectionManager.query(query)

            # Convert non-serializable objects to strings for JSON serialization
            if "result" in result and result["result"] is not None:
                result["result"] = str(result["result"])

            return ConnectionToolHandler.json_response(result)
        except Exception as e:
            return ConnectionToolHandler.error_response(str(e), type(e).__name__)
