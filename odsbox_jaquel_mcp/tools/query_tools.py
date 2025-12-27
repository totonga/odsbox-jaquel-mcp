"""Query pattern and skeleton tool handlers."""

from __future__ import annotations

from typing import Any

from mcp.types import TextContent

from ..queries import JaquelExamples, JaquelExplain
from .base_handler import BaseToolHandler


class QueryToolHandler(BaseToolHandler):
    """Handles query pattern and skeleton tools."""

    @staticmethod
    def query_get_pattern(arguments: dict[str, Any]) -> list[TextContent]:
        """Get a specific query pattern."""
        try:
            pattern = arguments.get("pattern")
            if not pattern or not isinstance(pattern, str) or not pattern.strip():
                raise ValueError("pattern must be a non-empty string")
            result = JaquelExamples.get_pattern(pattern)
            return QueryToolHandler.json_response(result)
        except Exception as e:
            return QueryToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def query_list_patterns(arguments: dict[str, Any]) -> list[TextContent]:
        """List all available query patterns."""
        try:
            patterns = JaquelExamples.list_patterns()
            result = {"available_patterns": patterns, "description": "Available query patterns"}
            return QueryToolHandler.json_response(result)
        except Exception as e:
            return QueryToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def query_generate_skeleton(arguments: dict[str, Any]) -> list[TextContent]:
        """Generate a query skeleton for an entity."""
        try:
            entity_name = arguments.get("entity_name")
            if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
                raise ValueError("entity_name must be a non-empty string")
            operation = arguments.get("operation", "get_all")
            result = JaquelExamples.query_generate_skeleton(entity_name, operation)
            return QueryToolHandler.json_response(result)
        except Exception as e:
            return QueryToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def query_describe(arguments: dict[str, Any]) -> list[TextContent]:
        """Describe what a Jaquel query does."""
        try:
            query = arguments.get("query", {})
            explanation = JaquelExplain.query_describe(query)
            return QueryToolHandler.text_response(explanation)
        except Exception as e:
            return QueryToolHandler.error_response(str(e), type(e).__name__)
