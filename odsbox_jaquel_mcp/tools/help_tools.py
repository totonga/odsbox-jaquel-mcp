"""Help and documentation tool handlers."""

from __future__ import annotations

from typing import Any

from mcp.types import TextContent

from ..bulk_api_guide import BulkAPIGuide
from .base_handler import BaseToolHandler


class HelpToolHandler(BaseToolHandler):
    """Handles help and documentation tools."""

    @staticmethod
    def get_bulk_api_help(arguments: dict[str, Any]) -> list[TextContent]:
        """Get help on using the Bulk API."""
        try:
            topic = arguments.get("topic", "3-step-rule")
            tool = arguments.get("tool")

            if tool:
                # Get contextual help for a specific tool
                help_text = BulkAPIGuide.get_contextual_help(tool)
                result = {
                    "topic": "contextual-help",
                    "tool": tool,
                    "help": help_text,
                }
            elif topic == "all":
                # Get all help content
                help_text = BulkAPIGuide.get_all_help()
                result = {
                    "topic": topic,
                    "help": help_text,
                }
            else:
                # Get specific topic help
                help_text = BulkAPIGuide.get_help(topic)
                result = {
                    "topic": topic,
                    "help": help_text,
                }

            return HelpToolHandler.json_response(result)
        except Exception as e:
            return HelpToolHandler.error_response(str(e), type(e).__name__)
