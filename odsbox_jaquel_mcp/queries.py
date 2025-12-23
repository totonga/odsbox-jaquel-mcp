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
        skeletons: dict[str, dict[str, Any]] = {
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

        return skeletons.get(operation, {"error": f"Unknown operation: {operation}"})
