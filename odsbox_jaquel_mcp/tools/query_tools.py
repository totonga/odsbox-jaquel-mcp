"""Query pattern and skeleton tool handlers."""

from __future__ import annotations

from typing import Any

from mcp.types import TextContent

from ..queries import JaquelExamples, QueryDebugger
from .base_handler import BaseToolHandler


class QueryToolHandler(BaseToolHandler):
    """Handles query pattern and skeleton tools."""

    @staticmethod
    def get_query_pattern(arguments: dict[str, Any]) -> list[TextContent]:
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
    def list_query_patterns(arguments: dict[str, Any]) -> list[TextContent]:
        """List all available query patterns."""
        try:
            patterns = JaquelExamples.list_patterns()
            result = {"available_patterns": patterns, "description": "Available query patterns"}
            return QueryToolHandler.json_response(result)
        except Exception as e:
            return QueryToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def generate_query_skeleton(arguments: dict[str, Any]) -> list[TextContent]:
        """Generate a query skeleton for an entity."""
        try:
            entity_name = arguments.get("entity_name")
            if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
                raise ValueError("entity_name must be a non-empty string")
            operation = arguments.get("operation", "get_all")
            result = JaquelExamples.generate_query_skeleton(entity_name, operation)
            return QueryToolHandler.json_response(result)
        except Exception as e:
            return QueryToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def explain_jaquel_query(arguments: dict[str, Any]) -> list[TextContent]:
        """Explain what a Jaquel query does."""
        try:
            query = arguments.get("query", {})
            explanation = QueryToolHandler._explain_query(query)
            return QueryToolHandler.text_response(explanation)
        except Exception as e:
            return QueryToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def debug_query_steps(arguments: dict[str, Any]) -> list[TextContent]:
        """Break down a query into steps for debugging."""
        try:
            query = arguments.get("query", {})
            result = QueryDebugger.debug_query_step_by_step(query)
            return QueryToolHandler.json_response(result)
        except Exception as e:
            return QueryToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def suggest_error_fixes(arguments: dict[str, Any]) -> list[TextContent]:
        """Suggest fixes for query errors."""
        try:
            issue = arguments.get("issue", "Unknown issue")
            query = arguments.get("query")
            suggestions = QueryDebugger.suggest_fixes_for_issue(issue, query)
            result = {"issue": issue, "suggestions": suggestions}
            return QueryToolHandler.json_response(result)
        except Exception as e:
            return QueryToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def _explain_query(query: dict[str, Any]) -> str:
        """Generate human-readable explanation of a query."""
        if not query:
            return "Empty query"

        explanation_parts = []

        for entity_name, entity_spec in query.items():
            explanation_parts.append(f"Query for entity: {entity_name}")

            if isinstance(entity_spec, dict):
                if entity_spec.get("$where"):
                    where_clause = entity_spec["$where"]
                    explanation_parts.append(f"  Filter: {QueryDebugger.explain_filter(where_clause)}")

                if entity_spec.get("$select"):
                    select_fields = entity_spec["$select"]
                    explanation_parts.append(f"  Select: {', '.join(select_fields)}")

                if entity_spec.get("$orderby"):
                    order_fields = entity_spec["$orderby"]
                    explanation_parts.append(f"  Order by: {', '.join(order_fields)}")

                if entity_spec.get("$limit"):
                    limit = entity_spec["$limit"]
                    explanation_parts.append(f"  Limit: {limit} results")

        return "\n".join(explanation_parts)
