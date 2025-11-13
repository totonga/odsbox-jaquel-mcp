"""ASAM ODS Jaquel MCP Server.

A Model Context Protocol server for helping create and validate
ASAM ODS Jaquel queries. Provides tools for building, validating,
and optimizing Jaquel queries for ODS data access.

This server can establish its own connection to ODS servers to provide
live model inspection and schema validation features.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import mcp.server.stdio
from mcp.server import Server, InitializationOptions
from mcp import ServerCapabilities, ToolsCapability
from mcp.types import Tool, TextContent

from .connection import ODSConnectionManager
from .validators import JaquelValidator, JaquelOptimizer
from .schemas import SchemaInspector
from .queries import JaquelExamples, QueryDebugger
from .submatrix import SubmatrixDataReader
from .submatrix.scripts import (
    generate_basic_fetcher_script,
    generate_advanced_fetcher_script,
    generate_batch_fetcher_script,
    generate_analysis_fetcher_script,
)
from .notebook_generator import NotebookGenerator
from .visualization_templates import VisualizationTemplateGenerator

# ============================================================================
# MCP SERVER SETUP
# ============================================================================

server = Server("odsbox-jaquel-mcp")


# ============================================================================
# MCP TOOLS
# ============================================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="validate_jaquel_query",
            description="Validate a Jaquel query structure for syntax errors and best practices",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": "The Jaquel query to validate",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="validate_filter_condition",
            description="Validate a WHERE clause filter condition in a Jaquel query",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "object",
                        "description": "The filter condition to validate",
                    }
                },
                "required": ["condition"],
            },
        ),
        Tool(
            name="get_operator_documentation",
            description="Get documentation and examples for a Jaquel operator",
            inputSchema={
                "type": "object",
                "properties": {
                    "operator": {
                        "type": "string",
                        "description": "The operator to get documentation for",
                    }
                },
                "required": ["operator"],
            },
        ),
        Tool(
            name="suggest_optimizations",
            description="Suggest optimizations and simplifications for a Jaquel query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": "The Jaquel query to optimize",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_query_pattern",
            description="Get a template for a common Jaquel query pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": (
                            "Pattern name: get_all_instances, get_by_id, "
                            "get_by_name, case_insensitive_search, time_range, "
                            "inner_join, outer_join, aggregates"
                        ),
                    }
                },
                "required": ["pattern"],
            },
        ),
        Tool(
            name="list_query_patterns",
            description="list all available Jaquel query patterns and templates",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="generate_query_skeleton",
            description="Generate a query skeleton for a specific entity and operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {
                        "type": "string",
                        "description": "Name of the entity",
                    },
                    "operation": {
                        "type": "string",
                        "description": "Type of query: get_all, get_by_id, get_by_name, search_and_select",
                    },
                },
                "required": ["entity_name"],
            },
        ),
        Tool(
            name="build_filter_condition",
            description="Build a filter condition for WHERE clause",
            inputSchema={
                "type": "object",
                "properties": {
                    "field": {"type": "string", "description": "Field name to filter on"},
                    "operator": {"type": "string", "description": "Comparison operator"},
                    "value": {"description": "Value to compare against"},
                },
                "required": ["field", "operator", "value"],
            },
        ),
        Tool(
            name="explain_jaquel_query",
            description="Explain what a Jaquel query does",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": "The Jaquel query",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="merge_filter_conditions",
            description="Merge multiple filter conditions with AND/OR logic",
            inputSchema={
                "type": "object",
                "properties": {
                    "conditions": {
                        "type": "array",
                        "description": "list of filter conditions",
                        "items": {"type": "object"},
                    },
                    "operator": {
                        "type": "string",
                        "description": "How to combine conditions",
                        "enum": ["$and", "$or"],
                    },
                },
                "required": ["conditions", "operator"],
            },
        ),
        Tool(
            name="check_entity_schema",
            description="Get available fields for an entity from ODS model",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {
                        "type": "string",
                        "description": "Entity name (e.g., 'StructureLevel')",
                    }
                },
                "required": ["entity_name"],
            },
        ),
        Tool(
            name="validate_field_exists",
            description="Check if a field exists in entity schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {"type": "string", "description": "Entity name"},
                    "field_name": {"type": "string", "description": "Field to check"},
                },
                "required": ["entity_name", "field_name"],
            },
        ),
        Tool(
            name="validate_filter_against_schema",
            description="Validate filter against actual entity schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {"type": "string", "description": "Entity name"},
                    "filter_condition": {
                        "type": "object",
                        "description": "Filter to validate",
                    },
                },
                "required": ["entity_name", "filter_condition"],
            },
        ),
        Tool(
            name="debug_query_steps",
            description="Break down a query into steps for debugging",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": "Query to break down",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="suggest_error_fixes",
            description="Get suggestions to fix query errors",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue": {"type": "string", "description": "Description of issue"},
                    "query": {
                        "type": "object",
                        "description": "The problematic query",
                    },
                },
                "required": ["issue"],
            },
        ),
        Tool(
            name="connect_ods_server",
            description="Establish connection to ASAM ODS server for live model inspection",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "ODS API URL (e.g., http://localhost:8087/api)",
                    },
                    "username": {"type": "string", "description": "Username for auth"},
                    "password": {"type": "string", "description": "Password for auth"},
                },
                "required": ["url", "username", "password"],
            },
        ),
        Tool(
            name="disconnect_ods_server",
            description="Close connection to ODS server",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_ods_connection_info",
            description="Get current ODS connection information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_ods_entities",
            description="Return a list of existing entities from the ODS server ModelCache",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="execute_ods_query",
            description="Execute a Jaquel query directly on connected ODS server",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": "Jaquel query to execute",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_submatrix_measurement_quantities",
            description="Get available measurement quantities for a submatrix",
            inputSchema={
                "type": "object",
                "properties": {
                    "submatrix_id": {
                        "type": "integer",
                        "description": "ID of the submatrix",
                    }
                },
                "required": ["submatrix_id"],
            },
        ),
        Tool(
            name="read_submatrix_data",
            description="Read timeseries data from a submatrix using bulk data access",
            inputSchema={
                "type": "object",
                "properties": {
                    "submatrix_id": {
                        "type": "integer",
                        "description": "ID of the submatrix to read",
                    },
                    "measurement_quantity_patterns": {
                        "type": "array",
                        "description": "List of measurement quantity name patterns to include",
                        "items": {"type": "string"},
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "Whether pattern matching should be case insensitive",
                    },
                    "date_as_timestamp": {
                        "type": "boolean",
                        "description": "Convert date columns to pandas timestamps",
                    },
                    "set_independent_as_index": {
                        "type": "boolean",
                        "description": "Set the independent column as DataFrame index",
                    },
                },
                "required": ["submatrix_id"],
            },
        ),
        Tool(
            name="generate_submatrix_fetcher_script",
            description=(
                "Generate Python scripts for fetching submatrix data "
                "with error handling and data processing"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "submatrix_id": {
                        "type": "integer",
                        "description": "ID of the submatrix to fetch data from",
                    },
                    "script_type": {
                        "type": "string",
                        "description": "Type of script: basic, advanced, batch, analysis",
                        "enum": ["basic", "advanced", "batch", "analysis"],
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Desired output format for the data",
                        "enum": ["csv", "json", "parquet", "excel", "dataframe"],
                    },
                    "measurement_quantity_patterns": {
                        "type": "array",
                        "description": "List of measurement quantity patterns to include",
                        "items": {"type": "string"},
                    },
                    "include_analysis": {
                        "type": "boolean",
                        "description": "Include basic data analysis examples",
                    },
                    "include_visualization": {
                        "type": "boolean",
                        "description": "Include matplotlib visualization code",
                    },
                },
                "required": ["submatrix_id", "script_type"],
            },
        ),
        Tool(
            name="generate_measurement_comparison_notebook",
            description="Generate a Jupyter notebook for comparing measurements",
            inputSchema={
                "type": "object",
                "properties": {
                    "measurement_query_conditions": {
                        "type": "object",
                        "description": "Filter conditions for measurements",
                    },
                    "measurement_quantity_names": {
                        "type": "array",
                        "description": "Names of quantities to plot",
                        "items": {"type": "string"},
                    },
                    "ods_url": {
                        "type": "string",
                        "description": "ODS server URL",
                    },
                    "ods_username": {
                        "type": "string",
                        "description": "ODS username",
                    },
                    "ods_password": {
                        "type": "string",
                        "description": "ODS password",
                    },
                    "available_quantities": {
                        "type": "array",
                        "description": "List of all available quantities (for documentation)",
                        "items": {"type": "string"},
                    },
                    "plot_type": {
                        "type": "string",
                        "description": 'Type of plot ("scatter", "line", or "subplots")',
                        "enum": ["scatter", "line", "subplots"],
                    },
                    "title": {
                        "type": "string",
                        "description": "Notebook title",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional path to save notebook (.ipynb file)",
                    },
                },
                "required": [
                    "measurement_query_conditions",
                    "measurement_quantity_names",
                    "ods_url",
                    "ods_username",
                    "ods_password",
                ],
            },
        ),
        Tool(
            name="generate_plotting_code",
            description="Generate Python plotting code for measurement comparison",
            inputSchema={
                "type": "object",
                "properties": {
                    "measurement_quantity_names": {
                        "type": "array",
                        "description": "List of quantity names to plot",
                        "items": {"type": "string"},
                    },
                    "submatrices_count": {
                        "type": "integer",
                        "description": "Number of submatrices to plot",
                    },
                    "plot_type": {
                        "type": "string",
                        "description": 'Type of plot ("scatter", "line", or "subplots")',
                        "enum": ["scatter", "line", "subplots"],
                    },
                },
                "required": [
                    "measurement_quantity_names",
                    "submatrices_count",
                    "plot_type",
                ],
            },
        ),
    ]


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


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle MCP tool calls."""
    try:
        # ====================================================================
        # VALIDATION TOOLS
        # ====================================================================

        if name == "validate_jaquel_query":
            query = arguments.get("query", {})
            result = JaquelValidator.validate_query(query)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "validate_filter_condition":
            condition = arguments.get("condition", {})
            result = JaquelValidator.validate_filter_condition(condition)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_operator_documentation":
            operator = arguments.get("operator")
            result = JaquelValidator.get_operator_info(operator)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "suggest_optimizations":
            query = arguments.get("query", {})
            suggestions = JaquelOptimizer.suggest_simplifications(query)
            result = {
                "query_summary": str(query),
                "suggestions": suggestions,
                "suggestion_count": len(suggestions),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # ====================================================================
        # QUERY PATTERN TOOLS
        # ====================================================================

        elif name == "get_query_pattern":
            pattern = arguments.get("pattern")
            result = JaquelExamples.get_pattern(pattern)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_query_patterns":
            patterns = JaquelExamples.list_patterns()
            result = {"available_patterns": patterns, "description": "Available query patterns"}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "generate_query_skeleton":
            entity_name = arguments.get("entity_name")
            operation = arguments.get("operation", "get_all")
            result = JaquelExamples.generate_query_skeleton(entity_name, operation)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # ====================================================================
        # FILTER BUILDING TOOLS
        # ====================================================================

        elif name == "build_filter_condition":
            field = arguments.get("field")
            operator = arguments.get("operator")
            value = arguments.get("value")

            # Validate operator
            if operator not in JaquelValidator.ALL_OPERATORS:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": f"Unknown operator: {operator}"}, indent=2),
                    )
                ]

            result = {field: {operator: value}}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "merge_filter_conditions":
            conditions = arguments.get("conditions", [])
            operator = arguments.get("operator", "$and")

            if not conditions:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": "No conditions to merge"}, indent=2),
                    )
                ]

            result = {operator: conditions}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # ====================================================================
        # QUERY EXPLANATION & DEBUGGING TOOLS
        # ====================================================================

        elif name == "explain_jaquel_query":
            query = arguments.get("query", {})
            explanation = _explain_query(query)
            return [TextContent(type="text", text=explanation)]

        elif name == "debug_query_steps":
            query = arguments.get("query", {})
            result = QueryDebugger.debug_query_step_by_step(query)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "suggest_error_fixes":
            issue = arguments.get("issue", "Unknown issue")
            query = arguments.get("query")
            suggestions = QueryDebugger.suggest_fixes_for_issue(issue, query)
            result = {"issue": issue, "suggestions": suggestions}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # ====================================================================
        # SCHEMA VALIDATION TOOLS
        # ====================================================================

        elif name == "check_entity_schema":
            entity_name = arguments.get("entity_name")
            result = SchemaInspector.get_entity_schema(entity_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "validate_field_exists":
            entity_name = arguments.get("entity_name")
            field_name = arguments.get("field_name")
            result = SchemaInspector.validate_field_exists(entity_name, field_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "validate_filter_against_schema":
            entity_name = arguments.get("entity_name")
            filter_condition = arguments.get("filter_condition")
            result = SchemaInspector.validate_filter_against_schema(entity_name, filter_condition)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # ====================================================================
        # CONNECTION MANAGEMENT TOOLS
        # ====================================================================

        elif name == "connect_ods_server":
            url = arguments.get("url")
            username = arguments.get("username")
            password = arguments.get("password")

            result = ODSConnectionManager.connect(url=url, auth=(username, password))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "disconnect_ods_server":
            result = ODSConnectionManager.disconnect()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_ods_connection_info":
            info = ODSConnectionManager.get_connection_info()
            return [TextContent(type="text", text=json.dumps(info, indent=2))]

        # ====================================================================
        # ODS QUERY EXECUTION TOOLS
        # ====================================================================

        elif name == "list_ods_entities":
            model = ODSConnectionManager.get_model()
            if not model:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": "Not connected to ODS server"}, indent=2),
                    )
                ]

            entities = []
            for entity_name, entity in model.entities.items():
                entities.append(
                    {
                        "name": entity.name,
                        "basename": entity.base_name,
                        "relations": list(entity.relations.keys()),
                    }
                )

            result = {"count": len(entities), "entities": entities}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "execute_ods_query":
            query = arguments.get("query", {})
            result = ODSConnectionManager.query(query)

            # Convert non-serializable objects to strings for JSON serialization
            if "result" in result and result["result"] is not None:
                result["result"] = str(result["result"])

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # ====================================================================
        # SUBMATRIX DATA ACCESS TOOLS
        # ====================================================================

        elif name == "get_submatrix_measurement_quantities":
            submatrix_id = arguments.get("submatrix_id")

            try:
                quantities = SubmatrixDataReader.get_measurement_quantities(submatrix_id)
                result = {
                    "submatrix_id": submatrix_id,
                    "measurement_quantities": quantities,
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2),
                    )
                ]

        elif name == "read_submatrix_data":
            submatrix_id = arguments.get("submatrix_id")
            measurement_quantity_patterns = arguments.get("measurement_quantity_patterns", [])
            case_insensitive = arguments.get("case_insensitive", False)
            date_as_timestamp = arguments.get("date_as_timestamp", True)
            set_independent_as_index = arguments.get("set_independent_as_index", True)

            try:
                result = SubmatrixDataReader.read_submatrix_data(
                    submatrix_id=submatrix_id,
                    measurement_quantity_patterns=measurement_quantity_patterns,
                    case_insensitive=case_insensitive,
                    date_as_timestamp=date_as_timestamp,
                    set_independent_as_index=set_independent_as_index,
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2),
                    )
                ]

        elif name == "generate_submatrix_fetcher_script":
            submatrix_id = arguments.get("submatrix_id")
            script_type = arguments.get("script_type", "basic")
            output_format = arguments.get("output_format", "csv")
            measurement_quantity_patterns = arguments.get("measurement_quantity_patterns", [])
            include_analysis = arguments.get("include_analysis", False)
            include_visualization = arguments.get("include_visualization", False)

            try:
                # Get available measurement quantities
                quantities = SubmatrixDataReader.get_measurement_quantities(submatrix_id)

                # Use provided patterns or all quantities
                if measurement_quantity_patterns:
                    mq_list = measurement_quantity_patterns
                else:
                    mq_list = [q["name"] for q in quantities]

                # Generate script based on type
                if script_type == "basic":
                    script = generate_basic_fetcher_script(submatrix_id, mq_list, output_format)
                elif script_type == "advanced":
                    script = generate_advanced_fetcher_script(
                        submatrix_id,
                        mq_list,
                        output_format,
                        include_visualization,
                        include_analysis,
                    )
                elif script_type == "batch":
                    script = generate_batch_fetcher_script(submatrix_id, mq_list, output_format)
                elif script_type == "analysis":
                    script = generate_analysis_fetcher_script(
                        submatrix_id, mq_list, output_format, include_visualization
                    )
                else:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {"error": f"Unknown script type: {script_type}"}, indent=2
                            ),
                        )
                    ]

                result = {
                    "submatrix_id": submatrix_id,
                    "script_type": script_type,
                    "output_format": output_format,
                    "script": script,
                    "instructions": [
                        "1. Update the configuration section with your ODS server details",
                        "2. Install required packages: pip install odsbox pandas",
                        f"3. Run the script: python submatrix_{submatrix_id}_fetcher.py",
                        f"4. Check output: submatrix_{submatrix_id}_data.{output_format}",
                    ],
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2),
                    )
                ]

        elif name == "generate_measurement_comparison_notebook":
            measurement_query_conditions = arguments.get("measurement_query_conditions", {})
            measurement_quantity_names = arguments.get("measurement_quantity_names", [])
            ods_url = arguments.get("ods_url", "")
            ods_username = arguments.get("ods_username", "")
            ods_password = arguments.get("ods_password", "")
            available_quantities = arguments.get("available_quantities", None)
            plot_type = arguments.get("plot_type", "scatter")
            title = arguments.get("title", "Measurement Comparison")
            output_path = arguments.get("output_path", None)

            try:
                notebook = NotebookGenerator.generate_measurement_comparison_notebook(
                    measurement_query_conditions=measurement_query_conditions,
                    measurement_quantity_names=measurement_quantity_names,
                    ods_url=ods_url,
                    ods_username=ods_username,
                    ods_password=ods_password,
                    available_quantities=available_quantities,
                    plot_type=plot_type,
                    title=title,
                )

                result = {
                    "title": title,
                    "plot_type": plot_type,
                    "measurement_quantities": measurement_quantity_names,
                    "num_cells": len(notebook["cells"]),
                }

                if output_path:
                    NotebookGenerator.save_notebook(notebook, output_path)
                    result["saved_to"] = output_path
                    result["status"] = "Notebook saved successfully"
                else:
                    result["status"] = "Notebook generated successfully"
                    result["notebook"] = notebook

                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2),
                    )
                ]

        elif name == "generate_plotting_code":
            measurement_quantity_names = arguments.get("measurement_quantity_names", [])
            submatrices_count = arguments.get("submatrices_count", 0)
            plot_type = arguments.get("plot_type", "scatter")

            try:
                if plot_type == "scatter":
                    if len(measurement_quantity_names) < 2:
                        raise ValueError(
                            "Scatter plot requires at least 2 measurement quantities"
                        )
                    code = VisualizationTemplateGenerator.generate_scatter_plot_code(
                        measurement_quantity_names=measurement_quantity_names,
                        submatrices_count=submatrices_count,
                    )
                elif plot_type == "line":
                    code = VisualizationTemplateGenerator.generate_line_plot_code(
                        measurement_quantity_names=measurement_quantity_names,
                        submatrices_count=submatrices_count,
                    )
                elif plot_type == "subplots":
                    code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
                        measurement_quantity_names=measurement_quantity_names,
                        submatrices_count=submatrices_count,
                    )
                else:
                    raise ValueError(f"Unknown plot type: {plot_type}")

                result = {
                    "plot_type": plot_type,
                    "measurement_quantities": measurement_quantity_names,
                    "submatrices_count": submatrices_count,
                    "code": code,
                    "description": (
                        f"Generated {plot_type} plot code for "
                        f"{len(measurement_quantity_names)} quantities and "
                        f"{submatrices_count} submatrices"
                    ),
                }

                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2),
                    )
                ]

        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2),
                )
            ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": str(e), "error_type": type(e).__name__}, indent=2),
            )
        ]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="odsbox-jaquel",
                server_version="1.0.0",
                capabilities=ServerCapabilities(tools=ToolsCapability(listChanged=True)),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
