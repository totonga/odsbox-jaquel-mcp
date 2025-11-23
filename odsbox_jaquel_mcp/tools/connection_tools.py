"""ODS connection tool handlers."""

from __future__ import annotations

from typing import Any

from mcp.types import TextContent

from ..connection import ODSConnectionManager
from .base_handler import BaseToolHandler


class ConnectionToolHandler(BaseToolHandler):
    """Handles ODS connection management tools."""

    @staticmethod
    def connect_ods_server(arguments: dict[str, Any]) -> list[TextContent]:
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

            result = ODSConnectionManager.connect(url=url, auth=(username, password))
            return ConnectionToolHandler.json_response(result)
        except Exception as e:
            return ConnectionToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def disconnect_ods_server(arguments: dict[str, Any]) -> list[TextContent]:
        """Close connection to ODS server."""
        try:
            result = ODSConnectionManager.disconnect()
            return ConnectionToolHandler.json_response(result)
        except Exception as e:
            return ConnectionToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def get_ods_connection_info(arguments: dict[str, Any]) -> list[TextContent]:
        """Get current ODS connection information."""
        try:
            info = ODSConnectionManager.get_connection_info()
            return ConnectionToolHandler.json_response(info)
        except Exception as e:
            return ConnectionToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def execute_ods_query(arguments: dict[str, Any]) -> list[TextContent]:
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
