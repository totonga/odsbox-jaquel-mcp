"""Base handler for tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent


class BaseToolHandler:
    """Base class for tool handlers providing common utilities."""

    @staticmethod
    def error_response(error: str, error_type: str) -> list[TextContent]:
        """Generate error response with consistent formatting."""
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": error, "error_type": error_type}, indent=2),
            )
        ]

    @staticmethod
    def json_response(data: dict[str, Any]) -> list[TextContent]:
        """Generate JSON response."""
        return [TextContent(type="text", text=json.dumps(data, indent=2))]

    @staticmethod
    def text_response(text: str) -> list[TextContent]:
        """Generate text response."""
        return [TextContent(type="text", text=text)]
