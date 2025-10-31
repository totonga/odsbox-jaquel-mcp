"""Jaquel query validators and optimizers for ASAM ODS Jaquel MCP Server."""

from __future__ import annotations

from typing import Any


class JaquelValidator:
    """Validates and analyzes Jaquel query structures."""

    # Valid operators in Jaquel
    COMPARISON_OPERATORS = {
        "$eq",
        "$neq",
        "$lt",
        "$gt",
        "$lte",
        "$gte",
        "$in",
        "$notinset",
        "$like",
        "$notlike",
        "$null",
        "$notnull",
        "$between",
    }

    LOGICAL_OPERATORS = {"$and", "$or", "$not"}

    AGGREGATE_FUNCTIONS = {
        "$none",
        "$count",
        "$dcount",
        "$min",
        "$max",
        "$avg",
        "$stddev",
        "$sum",
        "$distinct",
        "$point",
        "$ia",
    }

    SPECIAL_KEYS = {
        "$attributes",
        "$orderby",
        "$groupby",
        "$options",
        "$unit",
        "$nested",
        "$rowlimit",
        "$rowskip",
        "$seqlimit",
        "$seqskip",
    }

    ALL_OPERATORS = COMPARISON_OPERATORS | LOGICAL_OPERATORS | AGGREGATE_FUNCTIONS | SPECIAL_KEYS

    @staticmethod
    def validate_query(query: dict[str, Any]) -> dict[str, Any]:
        """Validate a Jaquel query structure.

        Returns:
            dict with 'valid', 'errors', 'warnings',
            'suggestions'.
        """
        errors = []
        warnings = []
        suggestions = []

        if not isinstance(query, dict):
            return {"valid": False, "errors": ["Query must be a dictionary"], "warnings": [], "suggestions": []}

        # Find entity name (first non-$ key)
        entity_name = None
        for key in query.keys():
            if not key.startswith("$"):
                entity_name = key
                break

        if not entity_name:
            msg = "Query must contain an entity name (non-$ key)"
            errors.append(msg)
            return {"valid": False, "errors": errors, "warnings": warnings, "suggestions": suggestions}

        # Validate entity query value
        entity_query = query[entity_name]
        if entity_query is None:
            msg = f"Entity '{entity_name}' query value cannot be None"
            errors.append(msg)
        elif not isinstance(entity_query, (dict, int, str)):
            msg = f"Entity '{entity_name}' query value must be " "dict, int, or string"
            errors.append(msg)

        # Validate special keys
        for key in query.keys():
            if key.startswith("$"):
                if key not in JaquelValidator.SPECIAL_KEYS:
                    warnings.append(f"Unknown special key: {key}")

        # Check for common patterns
        if "$attributes" in query:
            attrs = query["$attributes"]
            if not isinstance(attrs, dict):
                errors.append("$attributes must be a dictionary")
            else:
                if len(attrs) == 0:
                    msg = "$attributes is empty - consider " "removing it or adding attributes"
                    suggestions.append(msg)

        if "$orderby" in query:
            orderby = query["$orderby"]
            if not isinstance(orderby, dict):
                msg = "$orderby must be a dictionary with " "attribute names as keys and 0/1 as values"
                errors.append(msg)

        if "$groupby" in query:
            groupby = query["$groupby"]
            if not isinstance(groupby, dict):
                errors.append("$groupby must be a dictionary")

        if "$options" in query:
            opts = query["$options"]
            if isinstance(opts, dict):
                rowlimit = opts.get("$rowlimit")
                if rowlimit is not None:
                    if not isinstance(rowlimit, int):
                        msg = "$rowlimit must be an integer"
                        errors.append(msg)
                rowskip = opts.get("$rowskip")
                if rowskip is not None:
                    if not isinstance(rowskip, int):
                        msg = "$rowskip must be an integer"
                        errors.append(msg)

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "suggestions": suggestions}

    @staticmethod
    def validate_filter_condition(condition: dict[str, Any], field_name: str = "condition") -> dict[str, Any]:
        """Validate a filter condition (WHERE clause).

        Returns:
            dict with 'valid', 'errors', 'issues'.
        """
        errors = []
        issues = []

        if not isinstance(condition, dict):
            return {"valid": False, "errors": ["Condition must be a dictionary"], "issues": []}

        def validate_operator_dict(op_dict: dict[str, Any], path: str = "") -> None:
            """Recursively validate an operator dictionary."""
            for key, value in op_dict.items():
                if key.startswith("$"):
                    if key not in JaquelValidator.ALL_OPERATORS:
                        errors.append(f"Unknown operator: {key}{path}")
                    elif key in JaquelValidator.LOGICAL_OPERATORS:
                        if key == "$not":
                            if not isinstance(value, dict):
                                msg = f"{key} must contain expression{path}"
                                errors.append(msg)
                            else:
                                validate_operator_dict(value, f"{path}.{key}")
                        else:  # $and, $or
                            if not isinstance(value, list):
                                msg = f"{key} must contain an array{path}"
                                errors.append(msg)
                            else:
                                for i, item in enumerate(value):
                                    if isinstance(item, dict):
                                        validate_operator_dict(item, f"{path}.{key}[{i}]")
                    elif key in JaquelValidator.COMPARISON_OPERATORS:
                        if key in ["$null", "$notnull"]:
                            if value != 1:
                                msg = f"{key} should have value 1{path}"
                                issues.append(msg)
                        elif key in ["$between", "$in", "$notinset"]:
                            if not isinstance(value, list):
                                msg = f"{key} requires a list value{path}"
                                errors.append(msg)
                elif isinstance(value, dict):
                    # This is a field condition like {"field": {"$eq": "value"}}
                    validate_operator_dict(value, f" for field '{key}'")

        validate_operator_dict(condition)

        return {"valid": len(errors) == 0, "errors": errors, "issues": issues}

    @staticmethod
    def get_operator_info(operator: str) -> dict[str, Any]:
        """Get information about a Jaquel operator."""
        operator_docs = {
            "$eq": {
                "category": "comparison",
                "description": "Equal comparison",
                "example": '{"name": {"$eq": "MyTest"}}',
                "options": "Use $options: 'i' for case-insensitive",
            },
            "$neq": {
                "category": "comparison",
                "description": "Not equal comparison",
                "example": '{"status": {"$neq": "active"}}',
            },
            "$lt": {
                "category": "comparison",
                "description": "Less than",
                "example": '{"value": {"$lt": 100}}',
            },
            "$gt": {
                "category": "comparison",
                "description": "Greater than",
                "example": '{"value": {"$gt": 0}}',
            },
            "$lte": {
                "category": "comparison",
                "description": "Less than or equal",
                "example": '{"value": {"$lte": 100}}',
            },
            "$gte": {
                "category": "comparison",
                "description": "Greater than or equal",
                "example": '{"value": {"$gte": 0}}',
            },
            "$in": {
                "category": "comparison",
                "description": "Value in array",
                "example": '{"id": {"$in": [1, 2, 3]}}',
            },
            "$like": {
                "category": "comparison",
                "description": "Wildcard match (* and ?)",
                "example": '{"name": {"$like": "Test*"}}',
                "options": "Use $options: 'i' for case-insensitive",
            },
            "$between": {
                "category": "comparison",
                "description": "Value between two values",
                "example": '{"date": {"$between": ' '["2023-01-01", "2023-12-31"]}}',
            },
            "$null": {
                "category": "comparison",
                "description": "Is null value",
                "example": '{"field": {"$null": 1}}',
            },
            "$notnull": {
                "category": "comparison",
                "description": "Is not null value",
                "example": '{"field": {"$notnull": 1}}',
            },
            "$and": {
                "category": "logical",
                "description": "Logical AND - all must be true",
                "example": '{"$and": [{"status": "active"},' ' {"value": {"$gt": 0}}]}',
            },
            "$or": {
                "category": "logical",
                "description": "Logical OR - at least one true",
                "example": '{"$or": [{"status": "active"},' ' {"status": "pending"}]}',
            },
            "$not": {
                "category": "logical",
                "description": "Logical NOT",
                "example": '{"$not": {"status": "inactive"}}',
            },
            "$distinct": {
                "category": "aggregate",
                "description": "Get distinct values",
                "example": '{"$attributes": ' '{"name": {"$distinct": 1}}}',
            },
            "$min": {
                "category": "aggregate",
                "description": "Get minimum value",
                "example": '{"$attributes": ' '{"value": {"$min": 1}}}',
            },
            "$max": {
                "category": "aggregate",
                "description": "Get maximum value",
                "example": '{"$attributes": ' '{"value": {"$max": 1}}}',
            },
        }

        if operator not in operator_docs:
            return {"error": f"Unknown operator: {operator}"}

        return operator_docs[operator]


class JaquelOptimizer:
    """Optimizes and simplifies Jaquel queries."""

    @staticmethod
    def suggest_simplifications(query: dict[str, Any]) -> list[str]:
        """Suggest simplifications for a Jaquel query.

        Returns:
            list of optimization suggestions.
        """
        suggestions = []

        # Get entity name
        entity_name = None
        entity_query = None
        for key, value in query.items():
            if not key.startswith("$"):
                entity_name = key
                entity_query = value
                break

        if not entity_name or entity_query is None:
            return suggestions

        # Suggest ID shorthand
        if isinstance(entity_query, dict):
            if len(entity_query) == 1 and "id" in entity_query:
                id_val = entity_query["id"]
                if isinstance(id_val, (int, str)):
                    msg = (
                        f'Can simplify: {{"id": {id_val}}} → '
                        f"{id_val}\n"
                        f'  Shortened: {{"{entity_name}": {id_val}}}'
                    )
                    suggestions.append(msg)
                elif isinstance(id_val, dict) and "$eq" in id_val:
                    val = id_val["$eq"]
                    msg = f'Can simplify: {{"id": {{"$eq": {val}}}}} ' f"→ {val}"
                    suggestions.append(msg)

            # Suggest nested attribute shorthand
            if "test" in entity_query and isinstance(entity_query["test"], dict):
                nested = entity_query["test"]
                if len(nested) == 1 and "id" in nested:
                    test_id = nested["id"]
                    msg = f"Can simplify nested: " f'{{"test": {{"id": {test_id}}}}} → ' f'{{"test.id": {test_id}}}'
                    suggestions.append(msg)

        # Check for empty $attributes
        if "$attributes" in query and query["$attributes"] == {}:
            msg = "$attributes is empty - consider removing it " "to get all attributes"
            suggestions.append(msg)

        # Check for verbose $eq
        if "$attributes" in query:
            attrs = query["$attributes"]
            for attr_name, attr_val in attrs.items():
                if isinstance(attr_val, dict) and "$eq" in attr_val and len(attr_val) == 1:
                    val = attr_val["$eq"]
                    msg = (
                        f"Can simplify attribute: "
                        f'{{"{attr_name}": {{"$eq": {val}}}}} → '
                        f'{{"{attr_name}": {val}}}'
                    )
                    suggestions.append(msg)

        return suggestions
