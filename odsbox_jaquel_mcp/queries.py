"""Jaquel query examples and debugging for ASAM ODS Jaquel MCP Server."""

from __future__ import annotations

from typing import Any


class JaquelExamples:
    """Provides Jaquel query examples and templates."""

    BASIC_PATTERNS = {
        "get_all_instances": {
            "template": """{
    "EntityName": {},
    "$options": {
        "$rowlimit": 5
    }
}""",
            "description": "Get all instances (limited to 5)",
            "explanation": ("Empty {} means no filter. " "$rowlimit prevents large result sets."),
        },
        "get_by_id": {
            "template": '{"EntityName": 123}',
            "description": "Get instance by ID (shorthand)",
            "explanation": 'Full: {"EntityName": {"id": 123}}',
        },
        "get_by_name": {
            "template": """{
    "EntityName": {
        "name": "SearchName"
    },
    "$attributes": {
        "id": 1,
        "name": 1
    }
}""",
            "description": "Get instances by name",
            "explanation": "1 means include attribute",
        },
        "case_insensitive_search": {
            "template": """{
    "EntityName": {
        "name": {
            "$like": "Search*",
            "$options": "i"
        }
    }
}""",
            "description": "Case-insensitive wildcard search",
            "explanation": ("$like uses * and ? wildcards. " "$options: 'i' = case-insensitive"),
        },
        "time_range": {
            "template": """{
    "AoMeasurement": {
        "measurement_begin": {
            "$between": [
                "2023-01-01T00:00:00Z",
                "2023-12-31T23:59:59Z"
            ]
        }
    }
}""",
            "description": "Query time range",
            "explanation": "Use ISO 8601 or ODS time format",
        },
        "inner_join": {
            "template": """{
    "AoMeasurementQuantity": {},
    "$attributes": {
        "name": 1,
        "unit.name": 1,
        "quantity.name": 1
    }
}""",
            "description": "Inner join with related entities",
            "explanation": ("Use dot notation. Related record must exist."),
        },
        "outer_join": {
            "template": """{
    "AoMeasurementQuantity": {},
    "$attributes": {
        "name": 1,
        "unit:OUTER.name": 1,
        "quantity:OUTER.name": 1
    }
}""",
            "description": "Outer join",
            "explanation": ("Use :OUTER suffix. Handles sparse data."),
        },
        "aggregates": {
            "template": """{
    "AoUnit": {},
    "$attributes": {
        "factor": {
            "$min": 1,
            "$max": 1,
            "$avg": 1
        },
        "description": {
            "$distinct": 1,
            "$dcount": 1
        }
    }
}""",
            "description": "Aggregate functions",
            "explanation": ("$min/$max/$avg for numeric. " "$distinct for unique values."),
        },
    }

    @staticmethod
    def get_pattern(pattern_name: str) -> dict[str, Any]:
        """Get a specific query pattern."""
        if pattern_name not in JaquelExamples.BASIC_PATTERNS:
            return {"error": f"Unknown pattern: {pattern_name}"}
        return JaquelExamples.BASIC_PATTERNS[pattern_name]

    @staticmethod
    def list_patterns() -> list[str]:
        """list all available patterns."""
        return list(JaquelExamples.BASIC_PATTERNS.keys())

    @staticmethod
    def generate_query_skeleton(entity_name: str, operation: str = "get_all") -> dict[str, Any]:
        """Generate a query skeleton for an entity.

        Args:
            entity_name: Name of the entity
            operation: Type of query
        """
        skeletons = {
            "get_all": {entity_name: {}, "$attributes": {"id": 1, "name": 1}, "$options": {"$rowlimit": 5}},
            "get_by_id": {entity_name: 123, "$attributes": {"*": 1}},
            "get_by_name": {entity_name: {"name": "SearchName"}, "$attributes": {"*": 1}},
            "search_and_select": {
                entity_name: {"name": {"$like": "Search*"}},
                "$attributes": {"id": 1, "name": 1},
                "$orderby": {"name": 1},
                "$options": {"$rowlimit": 10},
            },
        }

        if operation not in skeletons:
            return {"error": f"Unknown operation: {operation}"}

        return skeletons[operation]


class QueryDebugger:
    """Debug and explain queries in detail."""

    @staticmethod
    def explain_filter(filter_condition: dict[str, Any]) -> str:
        """Convert filter to English explanation."""
        explanations = []

        for field, condition in filter_condition.items():
            if isinstance(condition, dict):
                for op, value in condition.items():
                    if op == "$eq":
                        explanations.append(f"{field} equals {value}")
                    elif op == "$neq":
                        explanations.append(f"{field} not equals {value}")
                    elif op == "$like":
                        explanations.append(f"{field} matches pattern " f"'{value}'")
                    elif op == "$gt":
                        explanations.append(f"{field} greater than {value}")
                    elif op == "$lt":
                        explanations.append(f"{field} less than {value}")
                    elif op == "$between":
                        explanations.append(f"{field} between " f"{value[0]} and {value[1]}")
                    elif op == "$in":
                        explanations.append(f"{field} in {value}")
                    elif op == "$null":
                        explanations.append(f"{field} is null")
                    elif op == "$notnull":
                        explanations.append(f"{field} is not null")
            else:
                explanations.append(f"{field} equals {condition}")

        return " AND ".join(explanations)

    @staticmethod
    def debug_query_step_by_step(query: dict[str, Any]) -> dict[str, Any]:
        """Break down query into steps."""
        steps = []

        # Step 1: Entity
        entity = [k for k in query.keys() if not k.startswith("$")]
        if entity:
            steps.append({"step": 1, "name": "Entity Selection", "description": f"Query entity: {entity[0]}"})

        # Step 2: Filter
        if entity and query.get(entity[0]):
            filter_cond = query[entity[0]]
            steps.append(
                {
                    "step": 2,
                    "name": "Filtering",
                    "description": (
                        QueryDebugger.explain_filter(filter_cond) if filter_cond else "No filter " "(all records)"
                    ),
                }
            )

        # Step 3: Attributes/Projection
        if "$attributes" in query:
            attr_count = len(query["$attributes"])
            steps.append(
                {
                    "step": 3,
                    "name": "Column Selection",
                    "description": (f"Select {attr_count} attributes: " f"{list(query['$attributes'].keys())}"),
                }
            )

        # Step 4: Ordering
        if "$orderby" in query:
            steps.append({"step": 4, "name": "Sorting", "description": (f"Order by: {query['$orderby']}")})

        # Step 5: Options
        if "$options" in query:
            steps.append({"step": 5, "name": "Options", "description": (f"Options: {query['$options']}")})

        return {"query": query, "steps": steps, "total_steps": len(steps)}

    @staticmethod
    def suggest_fixes_for_issue(issue: str, query: dict[str, Any]) -> list[str]:
        """Suggest fixes for common issues."""
        suggestions = []

        if "no results" in issue.lower():
            suggestions.append("Try removing the filter to get all " "records")
            suggestions.append("Check if filter fields exist in " "schema")
            suggestions.append("Verify filter values match data " "types")
            suggestions.append("Use $like with wildcards instead of " "exact match")

        if "unknown field" in issue.lower():
            suggestions.append("Check available fields with " "check_entity_schema tool")
            suggestions.append("Verify field name spelling and " "casing")

        if "relationship" in issue.lower():
            suggestions.append("Use :OUTER suffix for optional " "relationships")
            suggestions.append("Use dot notation for required " "relationships")
            suggestions.append("Check if relationship target " "has data")

        if "empty" in issue.lower():
            suggestions.append("Add $rowlimit to see some results")
            suggestions.append("Remove filters to test entity access")
            suggestions.append("Use debug_query tool to trace " "each step")

        return (
            suggestions
            if suggestions
            else [
                "Check query syntax with " "validate_jaquel_query",
                "Explain query with explain_jaquel_query",
                "Debug step-by-step with " "generate_debug_query",
            ]
        )
