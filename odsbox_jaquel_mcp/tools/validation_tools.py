"""Validation tool handlers."""

from __future__ import annotations

from typing import Any

from mcp.types import TextContent

from ..validators import JaquelOptimizer, JaquelValidator
from .base_handler import BaseToolHandler


class ValidationToolHandler(BaseToolHandler):
    """Handles query validation tools."""

    @staticmethod
    def validate_jaquel_query(arguments: dict[str, Any]) -> list[TextContent]:
        """Validate a Jaquel query structure."""
        try:
            query = arguments.get("query", {})
            result = JaquelValidator.validate_query(query)
            return ValidationToolHandler.json_response(result)
        except Exception as e:
            return ValidationToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def validate_filter_condition(arguments: dict[str, Any]) -> list[TextContent]:
        """Validate a WHERE clause filter condition."""
        try:
            condition = arguments.get("condition", {})
            result = JaquelValidator.validate_filter_condition(condition)
            return ValidationToolHandler.json_response(result)
        except Exception as e:
            return ValidationToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def get_operator_documentation(arguments: dict[str, Any]) -> list[TextContent]:
        """Get documentation for a Jaquel operator."""
        try:
            operator = arguments.get("operator")
            if not operator or not isinstance(operator, str) or not operator.strip():
                raise ValueError("operator must be a non-empty string")
            result = JaquelValidator.get_operator_info(operator)
            return ValidationToolHandler.json_response(result)
        except Exception as e:
            return ValidationToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def suggest_optimizations(arguments: dict[str, Any]) -> list[TextContent]:
        """Suggest query optimizations."""
        try:
            query = arguments.get("query", {})
            suggestions = JaquelOptimizer.suggest_simplifications(query)
            result = {
                "query_summary": str(query),
                "suggestions": suggestions,
                "suggestion_count": len(suggestions),
            }
            return ValidationToolHandler.json_response(result)
        except Exception as e:
            return ValidationToolHandler.error_response(str(e), type(e).__name__)
