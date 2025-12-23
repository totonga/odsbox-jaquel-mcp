"""Query pattern and skeleton tool handlers."""

from __future__ import annotations

from typing import Any

from google.protobuf.json_format import MessageToDict
from mcp.types import TextContent
from odsbox.jaquel import Jaquel
from odsbox.proto import ods

from ..connection import ODSConnectionManager
from ..queries import JaquelExamples
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
        if select_statement.columns:
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
        if select_statement.columns:
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
                    where_parts.append(f"{c_entity.name}.{c_attribute} {c_operator} {c_value}")
                if condition.conjunction is not None:
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
    def _explain_query(query: dict[str, Any]) -> str:
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
        explanation_parts.append("SQL-like Representation:")
        explanation_parts.append("=" * 50)

        sql_representation = QueryToolHandler._generate_sql_representation(select_statement, mc)
        explanation_parts.append(sql_representation)

        return "\n".join(explanation_parts)
