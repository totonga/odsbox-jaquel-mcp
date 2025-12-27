"""Validation tool handlers."""

from __future__ import annotations

from typing import Any

from mcp.types import TextContent

from ..validators import JaquelValidator
from .base_handler import BaseToolHandler


class ValidationToolHandler(BaseToolHandler):
    """Handles query validation tools."""

    @staticmethod
    def query_validate(arguments: dict[str, Any]) -> list[TextContent]:
        """Validate a Jaquel query structure."""
        try:
            query = arguments.get("query", {})
            result = JaquelValidator.query_validate(query)
            return ValidationToolHandler.json_response(result)
        except Exception as e:
            return ValidationToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def query_get_operator_docs(arguments: dict[str, Any]) -> list[TextContent]:
        """Get documentation for a Jaquel operator."""
        try:
            operator = arguments.get("operator")
            if not operator or not isinstance(operator, str) or not operator.strip():
                raise ValueError("operator must be a non-empty string")
            result = JaquelValidator.get_operator_info(operator)
            return ValidationToolHandler.json_response(result)
        except Exception as e:
            return ValidationToolHandler.error_response(str(e), type(e).__name__)
