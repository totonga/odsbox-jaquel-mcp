"""Jaquel query examples and debugging for ASAM ODS Jaquel MCP Server."""

from __future__ import annotations

from typing import Any

from odsbox.jaquel import Jaquel
from odsbox.proto import ods

from .connection import ODSConnectionManager


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


class JaquelExplain:
    """Generates explanations for Jaquel queries."""

    @staticmethod
    def _generate_sql_representation(select_statement: ods.SelectStatement, mc) -> str:
        """Generate SQL-like representation of a SelectStatement.

        Args:
            select_statement: Protobuf SelectStatement object
            mc: ModelCache object for entity/attribute lookups

        Returns:
            SQL-like query string
        """
        sql_lines = []

        # SELECT clause
        select_parts = []
        if select_statement.columns and len(select_statement.columns) > 0:
            for column in select_statement.columns:
                col_aggregate = (
                    ods.AggregateEnum.Name(column.aggregate).replace("AG_", "")
                    if column.aggregate != ods.AggregateEnum.AG_NONE
                    else ""
                )
                entity_name = mc.entity_by_aid(column.aid).name
                column_name = f"{entity_name}.{column.attribute}"
                if col_aggregate:
                    select_parts.append(f"{col_aggregate}({column_name})")
                else:
                    select_parts.append(column_name)

        sql_lines.append(f"SELECT {', '.join(select_parts) if select_parts else '*'}")

        # FROM clause
        if select_statement.columns and len(select_statement.columns) > 0:
            main_entity = mc.entity_by_aid(select_statement.columns[0].aid)
            sql_lines.append(f"FROM {main_entity.name}")

        # JOIN clause
        if select_statement.joins:
            for join in select_statement.joins:
                left_entity = mc.entity_by_aid(join.aid_from)
                right_entity = mc.entity_by_aid(join.aid_to)
                join_rel = mc.relation_no_throw(left_entity, join.relation)
                join_id = mc.attribute_by_base_name(right_entity, "id")
                join_type = ods.SelectStatement.JoinItem.JoinTypeEnum.Name(join.join_type).replace("JT_", "")
                if join_type == "DEFAULT":
                    join_type = "INNER"
                sql_lines.append(
                    f"{join_type} JOIN {right_entity.name} ON {left_entity.name}.{join_rel.name} = {right_entity.name}.{join_id.name}"
                )

        # WHERE clause
        if select_statement.where:
            where_parts = []
            for condition in select_statement.where:
                if condition.HasField("condition"):
                    c_entity = mc.entity_by_aid(condition.condition.aid)
                    c_attribute = condition.condition.attribute
                    c_operator = ods.SelectStatement.ConditionItem.Condition.OperatorEnum.Name(
                        condition.condition.operator
                    ).replace("OP_", "")
                    c_value = getattr(condition.condition, condition.condition.WhichOneof("ValueOneOf")).values
                    c_value = c_value[0] if len(c_value) == 1 else c_value
                    if isinstance(c_value, str):
                        c_value = f"'{c_value}'"
                    where_parts.append(f"{c_entity.name}.{c_attribute} {c_operator} {c_value}")
                if condition.HasField("conjunction"):
                    conjunction = ods.SelectStatement.ConditionItem.ConjuctionEnum.Name(condition.conjunction).replace(
                        "CO_", ""
                    )
                    if conjunction == "OPEN":
                        where_parts.append("(")
                    elif conjunction == "CLOSE":
                        where_parts.append(")")
                    elif conjunction in ("AND", "OR"):
                        where_parts.append(conjunction)

            if where_parts:
                # Remove trailing AND/OR if present, but keep parentheses
                while where_parts and where_parts[-1] in ("AND", "OR"):
                    where_parts.pop()
                if where_parts:
                    sql_lines.append("WHERE " + " ".join(where_parts))

        # GROUP BY clause
        if select_statement.group_by:
            group_parts = []
            for group in select_statement.group_by:
                g_entity = mc.entity_by_aid(group.aid)
                g_attribute = group.attribute
                group_parts.append(f"{g_entity.name}.{g_attribute}")
            sql_lines.append("GROUP BY " + ", ".join(group_parts))

        # ORDER BY clause
        if select_statement.order_by:
            order_parts = []
            for order in select_statement.order_by:
                o_entity = mc.entity_by_aid(order.aid)
                o_attribute = order.attribute
                o_direction = ods.SelectStatement.OrderByItem.OrderEnum.Name(order.order).replace("OD_", "")
                order_parts.append(f"{o_entity.name}.{o_attribute} {o_direction}")
            sql_lines.append("ORDER BY " + ", ".join(order_parts))

        # LIMIT clause
        if select_statement.row_limit > 0:
            sql_lines.append(f"LIMIT {select_statement.row_limit}")
        if select_statement.row_start > 0:
            sql_lines.append(f"OFFSET {select_statement.row_start}")

        return "\n".join(sql_lines)

    @staticmethod
    def explain_query(query: dict[str, Any]) -> str:
        """Generate human-readable explanation of a query."""
        if not query:
            return "Empty query"

        explanation_parts = []

        explanation_parts.append("\n" + "=" * 50)
        explanation_parts.append("Textual Representation:")
        explanation_parts.append("=" * 50)

        # Get model cache from ODS connection
        connection = ODSConnectionManager.get_instance()
        if not connection or not connection.is_connected():
            raise RuntimeError("Not connected to ODS server. Cannot access model cache.")

        mc = connection.get_model_cache()
        if not mc:
            raise RuntimeError("Model cache not available. Ensure connection is properly established.")

        select_statement = None
        try:
            select_statement = Jaquel(model=mc.model(), jaquel_query=query).select_statement
        except Exception as e:
            raise RuntimeError(f"Failed to parse query: {str(e)}")
        if select_statement is None:
            raise RuntimeError("Failed to generate SelectStatement from query.")

        if select_statement.columns:
            explanation_parts.append("Select Statement Columns:")
            for column in select_statement.columns:
                col_aggregate = (
                    ods.AggregateEnum.Name(column.aggregate).replace("AG_", "")
                    if column.aggregate != ods.AggregateEnum.AG_NONE
                    else ""
                )
                entity_name = mc.entity_by_aid(column.aid).name
                column_name = f"{entity_name}.{column.attribute}"
                if col_aggregate:
                    explanation_parts.append(f"  - {col_aggregate}({column_name})")
                else:
                    explanation_parts.append(f"  - {column_name}")
        if select_statement.where:
            explanation_parts.append("Where Clause:")
            for condition in select_statement.where:
                if condition.condition is not None:
                    c_entity = mc.entity_by_aid(condition.condition.aid)
                    c_attribute = condition.condition.attribute
                    c_operator = ods.SelectStatement.ConditionItem.Condition.OperatorEnum.Name(
                        condition.condition.operator
                    ).replace("OP_", "")
                    c_value = getattr(condition.condition, condition.condition.WhichOneof("ValueOneOf")).values
                    c_value = c_value[0] if len(c_value) == 1 else c_value
                    if isinstance(c_value, str):
                        c_value = f"'{c_value}'"
                    explanation_parts.append(f"  - Condition: {c_entity.name}.{c_attribute} {c_operator} {c_value}")
                if condition.conjunction is not None:
                    conjunction = ods.SelectStatement.ConditionItem.ConjuctionEnum.Name(condition.conjunction).replace(
                        "CO_", ""
                    )
                    # conjunction OPEN and CLOSE are used as open brackets and close brackets in complex conditions
                    explanation_parts.append(f"  - Conjunction: {conjunction}")
        if select_statement.joins:
            explanation_parts.append("Joins:")
            for join in select_statement.joins:
                left_entity = mc.entity_by_aid(join.aid_from)
                right_entity = mc.entity_by_aid(join.aid_to)
                join_rel = mc.relation_no_throw(left_entity, join.relation)
                right_id = mc.attribute_by_base_name(right_entity, "id")
                join_type = ods.SelectStatement.JoinItem.JoinTypeEnum.Name(join.join_type).replace("JT_", "")
                explanation_parts.append(
                    f"  - {join_type} Join: {left_entity.name}.{join_rel.name} "
                    f"= {right_entity.name}.{right_id.name}"
                )
        if select_statement.order_by:
            explanation_parts.append("Order By:")
            for order in select_statement.order_by:
                o_entity = mc.entity_by_aid(order.aid)
                o_attribute = order.attribute
                o_direction = ods.SelectStatement.OrderByItem.OrderEnum.Name(order.order).replace("OD_", "")
                explanation_parts.append(f"  - {o_entity.name}.{o_attribute} {o_direction}")
        if select_statement.group_by:
            explanation_parts.append("Group By:")
            for group in select_statement.group_by:
                g_entity = mc.entity_by_aid(group.aid)
                g_attribute = group.attribute
                explanation_parts.append(f"  - {g_entity.name}.{g_attribute}")
        if select_statement.row_limit > 0 or select_statement.row_start > 0:
            explanation_parts.append(
                f"Row Limit: {select_statement.row_limit}, Row Offset: {select_statement.row_start}"
            )
        if select_statement.values_limit > 0 or select_statement.values_start > 0:
            explanation_parts.append(
                f"Values Limit: {select_statement.values_limit}, " f"Values Offset: {select_statement.values_start}"
            )

        explanation_parts.append("\n" + "=" * 50)
        try:
            sql_representation = JaquelExplain._generate_sql_representation(select_statement, mc)
            explanation_parts.append("SQL-like Representation:")
            explanation_parts.append("=" * 50)
            explanation_parts.append(sql_representation)
        except Exception as e:
            explanation_parts.append(f"Failed to generate SQL-like representation: {str(e)}")

        return "\n".join(explanation_parts)
