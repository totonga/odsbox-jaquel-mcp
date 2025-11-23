"""Filter condition tool handlers."""

from __future__ import annotations

from typing import Any

from mcp.types import TextContent

from ..validators import JaquelValidator
from .base_handler import BaseToolHandler


class FilterToolHandler(BaseToolHandler):
    """Handles filter condition building tools."""

    @staticmethod
    def build_filter_condition(arguments: dict[str, Any]) -> list[TextContent]:
        """Build a filter condition for WHERE clause."""
        try:
            field = arguments.get("field")
            if not field or not isinstance(field, str) or not field.strip():
                raise ValueError("field must be a non-empty string")
            operator = arguments.get("operator")
            value = arguments.get("value")

            # Validate operator
            if not operator or not isinstance(operator, str) or not operator.strip():
                raise ValueError("operator must be a non-empty string")
            if operator not in JaquelValidator.ALL_OPERATORS:
                raise ValueError(f"Unknown operator: {operator}")

            result = {field: {operator: value}}
            return FilterToolHandler.json_response(result)
        except Exception as e:
            return FilterToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def merge_filter_conditions(arguments: dict[str, Any]) -> list[TextContent]:
        """Merge multiple filter conditions with AND/OR logic."""
        try:
            conditions = arguments.get("conditions", [])
            operator = arguments.get("operator", "$and")

            if not operator or not isinstance(operator, str) or not operator.strip():
                raise ValueError("operator must be a non-empty string")
            if not conditions:
                raise ValueError("No conditions to merge")

            result = {operator: conditions}
            return FilterToolHandler.json_response(result)
        except Exception as e:
            return FilterToolHandler.error_response(str(e), type(e).__name__)
