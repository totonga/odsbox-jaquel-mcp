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
            name="validate_query",
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
            name="get_operator_documentation",
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
            name="suggest_optimizations",
            title="Suggest Query Optimizations",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="⚡")],
        ),
        Tool(
            name="get_query_pattern",
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
            name="list_query_patterns",
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
            name="generate_query_skeleton",
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
            name="explain_query",
            title="Explain Jaquel Query",
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
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="💡")],
        ),
        Tool(
            name="check_entity_schema",
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
            name="validate_field_exists",
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
            name="connect_ods_server",
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
            name="disconnect_ods_server",
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
            name="get_ods_connection_info",
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
            name="list_ods_entities",
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
            name="execute_ods_query",
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
            name="get_submatrix_measurement_quantities",
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
            name="read_submatrix_data",
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
            name="generate_submatrix_fetcher_script",
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
            name="generate_measurement_comparison_notebook",
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
            name="generate_plotting_code",
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
            name="compare_measurements",
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
            name="query_measurement_hierarchy",
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
            name="get_bulk_api_help",
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
                            "(e.g., read_submatrix_data, connect_ods_server)"
                        ),
                    },
                },
                "required": ["topic"],
            },
            annotations=ToolAnnotations(readOnlyHint=True),
            icons=[Icon(src="❓")],
        ),
        Tool(
            name="get_test_to_measurement_hierarchy",
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
    if name == "validate_query":
        return ValidationToolHandler.validate_query(arguments)

    elif name == "get_operator_documentation":
        return ValidationToolHandler.get_operator_documentation(arguments)

    elif name == "suggest_optimizations":
        return ValidationToolHandler.suggest_optimizations(arguments)

    # ========================================================================
    # QUERY PATTERN TOOLS
    # ========================================================================
    elif name == "get_query_pattern":
        return QueryToolHandler.get_query_pattern(arguments)

    elif name == "list_query_patterns":
        return QueryToolHandler.list_query_patterns(arguments)

    elif name == "generate_query_skeleton":
        return QueryToolHandler.generate_query_skeleton(arguments)

    # ========================================================================
    # QUERY EXPLANATION & DEBUGGING TOOLS
    # ========================================================================
    elif name == "explain_query":
        return QueryToolHandler.explain_query(arguments)

    # ========================================================================
    # SCHEMA VALIDATION TOOLS
    # ========================================================================
    elif name == "check_entity_schema":
        return SchemaToolHandler.check_entity_schema(arguments)

    elif name == "validate_field_exists":
        return SchemaToolHandler.validate_field_exists(arguments)

    # ========================================================================
    # CONNECTION MANAGEMENT TOOLS
    # ========================================================================
    elif name == "connect_ods_server":
        return ConnectionToolHandler.connect_ods_server(arguments)

    elif name == "disconnect_ods_server":
        return ConnectionToolHandler.disconnect_ods_server(arguments)

    elif name == "get_ods_connection_info":
        return ConnectionToolHandler.get_ods_connection_info(arguments)

    # ========================================================================
    # ODS QUERY EXECUTION TOOLS
    # ========================================================================
    elif name == "list_ods_entities":
        return SchemaToolHandler.list_ods_entities(arguments)

    elif name == "execute_ods_query":
        return ConnectionToolHandler.execute_ods_query(arguments)

    # ========================================================================
    # SUBMATRIX DATA ACCESS TOOLS
    # ========================================================================
    elif name == "get_submatrix_measurement_quantities":
        return SubmatrixToolHandler.get_submatrix_measurement_quantities(arguments)

    elif name == "read_submatrix_data":
        return SubmatrixToolHandler.read_submatrix_data(arguments)

    elif name == "generate_submatrix_fetcher_script":
        return SubmatrixToolHandler.generate_submatrix_fetcher_script(arguments)

    # ========================================================================
    # MEASUREMENT & VISUALIZATION TOOLS
    # ========================================================================
    elif name == "generate_measurement_comparison_notebook":
        return MeasurementToolHandler.generate_measurement_comparison_notebook(arguments)

    elif name == "generate_plotting_code":
        return MeasurementToolHandler.generate_plotting_code(arguments)

    elif name == "compare_measurements":
        return MeasurementToolHandler.compare_measurements(arguments)

    elif name == "query_measurement_hierarchy":
        return MeasurementToolHandler.query_measurement_hierarchy(arguments)

    # ========================================================================
    # HELP & DOCUMENTATION TOOLS
    # ========================================================================
    elif name == "get_bulk_api_help":
        return HelpToolHandler.get_bulk_api_help(arguments)

    elif name == "get_test_to_measurement_hierarchy":
        return SchemaToolHandler.get_test_to_measurement_hierarchy(arguments)

    else:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2),
            )
        ]


async def main():
    """Run the MCP server."""
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
                instructions="""
# ASAM ODS Jaquel MCP Server

This MCP server helps you work with ASAM ODS data using odsbox Jaquel queries. It provides 29+ tools across 7 categories.

## 🚀 QUICK START - Choose Your Path

**Path 1: Connect to ODS & Execute Queries**
- `connect_ods_server` → `list_ods_entities` → `get_test_to_measurement_hierarchy` → `execute_ods_query`
- Or: `read_submatrix_data` for efficient timeseries access
- Generate reusable scripts: `generate_submatrix_fetcher_script`

**Path 2: Analysis & Visualization**
- Execute queries to get data
- `compare_measurements` for statistical analysis
- `generate_measurement_comparison_notebook` for Jupyter notebooks
- `generate_plotting_code` for matplotlib visualizations

## 📚 TOOL CATEGORIES

**Validation & Debugging (7 tools)**
- Check queries: `validate_query`, `explain_query`
- Check operators: `get_operator_documentation`

**Query Building (9 tools)**
- Skeletons: `generate_query_skeleton`
- Patterns: `list_query_patterns`, `get_query_pattern`

**Schema & Entity Inspection (5 tools)**
- List entities: `list_ods_entities`, `get_test_to_measurement_hierarchy`
- Check fields: `check_entity_schema`, `validate_field_exists`

**ODS Connection (3 tools)**
- Manage: `connect_ods_server`, `disconnect_ods_server`, `get_ods_connection_info`

**Data Access (3 tools)**
- Submatrix: `read_submatrix_data`, `get_submatrix_measurement_quantities`
- Scripts: `generate_submatrix_fetcher_script`

**Analysis & Visualization (4 tools)**
- Compare: `compare_measurements`, `query_measurement_hierarchy`
- Notebooks: `generate_measurement_comparison_notebook`
- Plots: `generate_plotting_code`

**Help & Documentation (1 tool)**
- `get_bulk_api_help` - Comprehensive Bulk API guidance

## 💡 COMMON WORKFLOWS

**Workflow 1: Connect to ODS & Execute Query**
1. `connect_ods_server` - Provide URL, username, password
2. `list_ods_entities` - See available entities
3. `get_test_to_measurement_hierarchy` - Explore test to measurement structure
4. `check_entity_schema` - Inspect entity fields
5. `execute_ods_query` - Run your query
6. Analyze results with measurement tools

**Workflow 2: Read Timeseries Data Efficiently**
1. `get_submatrix_measurement_quantities` - See available data
2. `read_submatrix_data` - Fetch with pattern matching
3. `generate_submatrix_fetcher_script` - Create reusable Python script
4. Use script for automation

**Workflow 3: Compare Multiple Measurements**
1. Execute query to get measurements
2. `query_measurement_hierarchy` - Explore structure (extract_measurements, get_unique_quantities)
3. `generate_measurement_comparison_notebook` - Create Jupyter notebook
4. `compare_measurements` - Statistical analysis
5. `generate_plotting_code` - Matplotlib code for custom plots

## ⚠️ KEY TIPS

- **Connection State**: Connection persists across tool calls. Call `disconnect_ods_server` when done.
- **Bulk API**: For large timeseries data (submatrices), prefer `read_submatrix_data` over `execute_ods_query`
- **Pattern Matching**: `read_submatrix_data` supports wildcards for efficient data filtering (e.g., "Temp*", "*Speed")

## ❓ WHEN TO USE WHICH TOOL

**"How do I...?"**
- "...start building a query?" → `list_query_patterns`
- "...validate query?" → `explain_query`
- "...connect to ODS?" → `connect_ods_server`
- "...connect to ASAM ODS?" → `connect_ods_server`
- "...find entities?" → `list_ods_entities`
- "...understand structure?" → `get_test_to_measurement_hierarchy` or `check_entity_schema`
- "...read measurement data?" → `read_submatrix_data` or `execute_ods_query`
- "...create a reusable script?" → `generate_submatrix_fetcher_script`
- "...compare measurements?" → `compare_measurements` + `generate_measurement_comparison_notebook`
- "...understand submatrix data access?" → `get_bulk_api_help`

## 📖 INTERACTIVE STARTING PROMPTS

Use these for guided workflows:
- `setup_ods_connection` - Learn connection management
- `validate_query` - Validate queries step-by-step
- `explore_patterns` - Discover query patterns
- `bulk_data_access` - Learn Bulk API 3-step workflow
- `analyze_measurements` - Statistical analysis & visualization

## 🔗 DOCUMENTATION & EXAMPLES

- **Tool Guide**: https://github.com/totonga/odsbox-jaquel-mcp/blob/main/TOOLS_GUIDE.md
- **Prompts Guide**: https://github.com/totonga/odsbox-jaquel-mcp/blob/main/PROMPTS.md
- **Full README**: https://github.com/totonga/odsbox-jaquel-mcp

**Pro Tip**: Always review tool descriptions and examples to understand input/output formats!
""",
                website_url="https://github.com/totonga/odsbox-jaquel-mcp/tree/main#readme",
                icons=[Icon(src="📦")],
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
