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
from pathlib import Path

import mcp.server.stdio
from mcp.server import InitializationOptions, Server
from mcp.types import (
    GetPromptResult,
    Icon,
    PromptMessage,
    PromptsCapability,
    Resource,
    ResourcesCapability,
    ServerCapabilities,
    TextContent,
    Tool,
    ToolAnnotations,
    ToolsCapability,
)
from pydantic import AnyUrl

from . import __version__
from .prompts import PromptLibrary
from .resources import ResourceLibrary
from .tools import (
    ConnectionToolHandler,
    HelpToolHandler,
    MeasurementToolHandler,
    QueryToolHandler,
    SchemaToolHandler,
    SubmatrixToolHandler,
    ValidationToolHandler,
)

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
            name="query_validate",
            title="Validate Jaquel Query",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="✅")],
        ),
        Tool(
            name="query_get_operator_docs",
            title="Get Operator Documentation",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="📚")],
        ),
        Tool(
            name="query_get_pattern",
            title="Get Query Pattern Template",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="📋")],
        ),
        Tool(
            name="query_list_patterns",
            title="List Available Query Patterns",
            description="list all available Jaquel query patterns and templates",
            inputSchema={
                "type": "object",
                "properties": {},
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="📑")],
        ),
        Tool(
            name="query_generate_skeleton",
            title="Generate Query Skeleton",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="🦴")],
        ),
        Tool(
            name="query_describe",
            title="Describe JAQueL Query",
            description="Describe what a Jaquel query does",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="💡")],
        ),
        Tool(
            name="schema_get_entity",
            title="Check Entity Schema",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="📊")],
        ),
        Tool(
            name="schema_field_exists",
            title="Validate Field Exists",
            description="Check if a field exists in entity schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_name": {"type": "string", "description": "Entity name"},
                    "field_name": {"type": "string", "description": "Field to check"},
                },
                "required": ["entity_name", "field_name"],
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="🔍")],
        ),
        Tool(
            name="ods_connect",
            title="Connect to ODS Server",
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
                    "verify": {
                        "type": "boolean",
                        "description": "Verify SSL certificates (default: true)",
                        "default": True,
                    },
                },
                "required": ["url", "username", "password"],
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="🔌")],
        ),
        Tool(
            name="ods_disconnect",
            title="Disconnect from ODS Server",
            description="Close connection to ODS server",
            inputSchema={
                "type": "object",
                "properties": {},
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="🔓")],
        ),
        Tool(
            name="ods_get_connection_info",
            title="Get ODS Connection Information",
            description="Get current ODS connection information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="ℹ️")],
        ),
        Tool(
            name="schema_list_entities",
            title="List ODS Entities",
            description="Return a list of existing entities from the ODS server ModelCache",
            inputSchema={
                "type": "object",
                "properties": {},
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="📋")],
        ),
        Tool(
            name="query_execute",
            title="Execute ODS Query",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="⚙️")],
        ),
        Tool(
            name="data_get_quantities",
            title="Get Submatrix Measurement Quantities",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="📈")],
        ),
        Tool(
            name="data_read_submatrix",
            title="Read Submatrix Data",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="📖")],
        ),
        Tool(
            name="data_generate_fetcher_script",
            title="Generate Submatrix Fetcher Script",
            description=(
                "Generate Python scripts for fetching submatrix data " "with error handling and data processing"
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="🐍")],
        ),
        Tool(
            name="plot_comparison_notebook",
            title="Generate Measurement Comparison Notebook",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="📓")],
        ),
        Tool(
            name="plot_generate_code",
            title="Generate Plotting Code",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="📊")],
        ),
        Tool(
            name="data_compare_measurements",
            title="Compare Measurements",
            description="Compare measurements across quantities with statistical analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "quantity_name": {
                        "type": "string",
                        "description": "Name of quantity to compare",
                    },
                    "measurement_data": {
                        "type": "object",
                        "description": "Dict mapping measurement_id (as string) to list of values",
                    },
                    "measurement_names": {
                        "type": "object",
                        "description": "Optional dict mapping measurement_id to display names",
                    },
                },
                "required": ["quantity_name", "measurement_data"],
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="🔀")],
        ),
        Tool(
            name="data_query_hierarchy",
            title="Query Measurement Hierarchy",
            description="Query and explore ODS measurement hierarchy and structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "query_result": {
                        "type": "object",
                        "description": "ODS query result to explore",
                    },
                    "operation": {
                        "type": "string",
                        "description": "Operation to perform on query result",
                        "enum": [
                            "extract_measurements",
                            "build_hierarchy",
                            "get_unique_tests",
                            "get_unique_quantities",
                            "build_index",
                        ],
                    },
                    "test_name": {
                        "type": "string",
                        "description": "Optional test name for filtering",
                    },
                    "quantity_names": {
                        "type": "array",
                        "description": "Optional list of quantities to search for",
                        "items": {"type": "string"},
                    },
                },
                "required": ["query_result", "operation"],
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="🌳")],
        ),
        Tool(
            name="help_bulk_api",
            title="Get Bulk API Help",
            description=(
                "Get help and guidance on using the Bulk API for loading timeseries data. "
                "Use this to understand the 3-step workflow and common patterns."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": (
                            "Help topic. Options: 3-step-rule, quick-start, bulk-vs-jaquel, "
                            "patterns, decision-tree, mistakes, step-by-step, "
                            "response-template, troubleshooting, tool-patterns, all"
                        ),
                        "enum": [
                            "3-step-rule",
                            "quick-start",
                            "bulk-vs-jaquel",
                            "patterns",
                            "decision-tree",
                            "mistakes",
                            "step-by-step",
                            "response-template",
                            "troubleshooting",
                            "tool-patterns",
                            "all",
                        ],
                    },
                    "tool": {
                        "type": "string",
                        "description": (
                            "Optional: Get contextual help for a specific tool "
                            "(e.g., data_read_submatrix, ods_connect)"
                        ),
                    },
                },
                "required": ["topic"],
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="❓")],
        ),
        Tool(
            name="schema_test_to_measurement_hierarchy",
            title="Get Test to Measurement Hierarchy",
            description="Get hierarchical entity chain from AoTest to AoMeasurement via 'children' relation",
            inputSchema={
                "type": "object",
                "properties": {},
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="🔗")],
        ),
    ]


# ============================================================================
# MCP PROMPTS
# ============================================================================


@server.list_prompts()
async def list_prompts() -> list:
    """List all available starting prompts."""
    return PromptLibrary.get_all_prompts()


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None = None) -> GetPromptResult:
    """Get a specific prompt with optional arguments."""
    # Find the prompt by name
    all_prompts = PromptLibrary.get_all_prompts()
    prompt = next((p for p in all_prompts if p.name == name), None)

    if not prompt:
        raise ValueError(f"Unknown prompt: {name}")

    # Generate the prompt content
    content = PromptLibrary.get_prompt_content(name, arguments or {})

    return GetPromptResult(
        description=prompt.description,
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=content),
            )
        ],
    )


# ============================================================================
# MCP RESOURCES
# ============================================================================


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available reference resources for ODS connection and workflows."""
    return ResourceLibrary.get_all_resources()


@server.list_resource_templates()
async def list_resource_templates():
    """List available resource templates for dynamic content."""
    return ResourceLibrary.get_all_resource_templates()


@server.read_resource()
async def read_resource(uri: AnyUrl):
    """Read reference resources about ODS connection and workflows."""
    content = ResourceLibrary.get_resource_content(str(uri))

    # MCP expects Iterable[ReadResourceContents] where each item has .content and .mime_type
    class ResourceContent:
        def __init__(self, content_text: str, mime_type: str):
            self.content = content_text
            self.mime_type = mime_type

    return [ResourceContent(content, "text/markdown")]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle MCP tool calls by delegating to appropriate tool handlers."""
    # ========================================================================
    # VALIDATION TOOLS
    # ========================================================================
    if name == "query_validate":
        return ValidationToolHandler.query_validate(arguments)

    elif name == "query_get_operator_docs":
        return ValidationToolHandler.query_get_operator_docs(arguments)

    # ========================================================================
    # QUERY PATTERN TOOLS
    # ========================================================================
    elif name == "query_get_pattern":
        return QueryToolHandler.query_get_pattern(arguments)

    elif name == "query_list_patterns":
        return QueryToolHandler.query_list_patterns(arguments)

    elif name == "query_generate_skeleton":
        return QueryToolHandler.query_generate_skeleton(arguments)

    # ========================================================================
    # QUERY EXPLANATION & DEBUGGING TOOLS
    # ========================================================================
    elif name == "query_describe":
        return QueryToolHandler.query_describe(arguments)

    # ========================================================================
    # SCHEMA VALIDATION TOOLS
    # ========================================================================
    elif name == "schema_get_entity":
        return SchemaToolHandler.schema_get_entity(arguments)

    elif name == "schema_field_exists":
        return SchemaToolHandler.schema_field_exists(arguments)

    # ========================================================================
    # CONNECTION MANAGEMENT TOOLS
    # ========================================================================
    elif name == "ods_connect":
        return ConnectionToolHandler.ods_connect(arguments)

    elif name == "ods_disconnect":
        return ConnectionToolHandler.ods_disconnect(arguments)

    elif name == "ods_get_connection_info":
        return ConnectionToolHandler.ods_get_connection_info(arguments)

    # ========================================================================
    # ODS QUERY EXECUTION TOOLS
    # ========================================================================
    elif name == "schema_list_entities":
        return SchemaToolHandler.schema_list_entities(arguments)

    elif name == "query_execute":
        return ConnectionToolHandler.query_execute(arguments)

    # ========================================================================
    # SUBMATRIX DATA ACCESS TOOLS
    # ========================================================================
    elif name == "data_get_quantities":
        return SubmatrixToolHandler.data_get_quantities(arguments)

    elif name == "data_read_submatrix":
        return SubmatrixToolHandler.data_read_submatrix(arguments)

    elif name == "data_generate_fetcher_script":
        return SubmatrixToolHandler.data_generate_fetcher_script(arguments)

    # ========================================================================
    # MEASUREMENT & VISUALIZATION TOOLS
    # ========================================================================
    elif name == "plot_comparison_notebook":
        return MeasurementToolHandler.plot_comparison_notebook(arguments)

    elif name == "plot_generate_code":
        return MeasurementToolHandler.plot_generate_code(arguments)

    elif name == "data_compare_measurements":
        return MeasurementToolHandler.data_compare_measurements(arguments)

    elif name == "data_query_hierarchy":
        return MeasurementToolHandler.data_query_hierarchy(arguments)

    # ========================================================================
    # HELP & DOCUMENTATION TOOLS
    # ========================================================================
    elif name == "help_bulk_api":
        return HelpToolHandler.help_bulk_api(arguments)

    elif name == "schema_test_to_measurement_hierarchy":
        return SchemaToolHandler.schema_test_to_measurement_hierarchy(arguments)

    else:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2),
            )
        ]


async def main():
    """Run the MCP server."""
    # Load instructions from markdown file
    instructions_path = Path(__file__).parent / "server_instructions.md"
    try:
        with open(instructions_path, "r", encoding="utf-8") as f:
            instructions = f.read()
    except FileNotFoundError:
        # Fallback if file not found
        instructions = (
            "# ASAM ODS Jaquel MCP Server\n\n" "See documentation at https://github.com/totonga/odsbox-jaquel-mcp"
        )

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="odsbox-jaquel-mcp",
                server_version=__version__,
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(listChanged=True),
                    prompts=PromptsCapability(listChanged=True),
                    resources=ResourcesCapability(listChanged=True),
                ),
                instructions=instructions,
                website_url="https://github.com/totonga/odsbox-jaquel-mcp/tree/main#readme",
                icons=[Icon(src="📦")],
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
