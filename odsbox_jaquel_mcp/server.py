"""ASAM ODS Jaquel MCP Server.

A Model Context Protocol server for helping create and validate
ASAM ODS Jaquel queries. Provides tools for building, validating,
and optimizing Jaquel queries for ODS data access.

This server can establish its own connection to ODS servers to provide
live model inspection and schema validation features.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from . import __version__
from .auth_factory import resolve_auth_args_from_env
from .bulk_api_guide import BulkAPIGuide
from .connection import ODSConnectionManager
from .monitoring import ToolStatsMiddleware
from .notebook_generator import NotebookGenerator
from .prompts import PromptLibrary
from .queries import JaquelExamples, JaquelExplain
from .resources import ResourceLibrary
from .schemas import SchemaInspector
from .schemas_types import ConnectionInfo, ConnectResult, EntitySchema
from .submatrix import SubmatrixDataReader
from .submatrix.scripts import (
    generate_advanced_fetcher_script,
    generate_analysis_fetcher_script,
    generate_basic_fetcher_script,
    generate_batch_fetcher_script,
)
from .validators import JaquelValidator
from .visualization_templates import VisualizationTemplateGenerator

# ============================================================================
# MCP SERVER SETUP
# ============================================================================

# Load instructions from markdown file
_instructions_path = Path(__file__).parent / "server_instructions.md"
try:
    _instructions = _instructions_path.read_text(encoding="utf-8")
except FileNotFoundError:
    _instructions = "# ASAM ODS Jaquel MCP Server\n\nSee documentation at https://github.com/totonga/odsbox-jaquel-mcp"

mcp = FastMCP(
    name="odsbox-jaquel-mcp",
    instructions=_instructions,
    version=__version__,
)

mcp.add_middleware(ToolStatsMiddleware())


# ============================================================================
# VALIDATION TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"validation"},
)
def query_validate(
    query: Annotated[
        dict,
        Field(
            description=(
                "Jaquel query dict to validate. Top-level key is the entity name "
                "(e.g. 'AoTest'), value is a filter/attribute object. "
                'Example: {"AoTest": {"name": {"$like": "*"}}, '
                '"$attributes": {"id": 1, "name": 1}, '
                '"$options": {"$rowlimit": 100}}'
            )
        ),
    ],
) -> dict:
    """Validate a Jaquel query structure for syntax errors and best practices."""
    return JaquelValidator.query_validate(query)


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"validation"},
)
def query_get_operator_docs(
    operator: Annotated[str, Field(description="Jaquel operator name, e.g. '$like', '$gt', '$in', '$between'")],
) -> dict:
    """Get documentation and examples for a Jaquel operator."""
    if not operator or not isinstance(operator, str) or not operator.strip():
        raise ValueError("operator must be a non-empty string")
    return JaquelValidator.get_operator_info(operator)


# ============================================================================
# QUERY PATTERN TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"query"},
)
def query_get_pattern(
    pattern: Annotated[
        str,
        Field(
            description=(
                "Pattern name: get_all_instances, get_by_id, "
                "get_by_name, case_insensitive_search, time_range, "
                "inner_join, outer_join, aggregates"
            )
        ),
    ],
) -> dict:
    """Get a template for a common Jaquel query pattern."""
    if not pattern or not isinstance(pattern, str) or not pattern.strip():
        raise ValueError("pattern must be a non-empty string")
    return JaquelExamples.get_pattern(pattern)


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"query"},
)
def query_list_patterns() -> dict:
    """List all available Jaquel query patterns and templates."""
    patterns = JaquelExamples.list_patterns()
    return {"available_patterns": patterns, "description": "Available query patterns"}


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"query"},
)
def query_generate_skeleton(
    entity_name: Annotated[str, Field(description="ODS entity name (e.g. 'AoTest', 'AoMeasurement', 'AoSubMatrix')")],
    operation: Annotated[
        str,
        Field(
            default="get_all",
            description="Type of query: get_all, get_by_id, get_by_name, search_and_select",
        ),
    ] = "get_all",
) -> dict:
    """Generate a query skeleton for a specific entity and operation."""
    if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
        raise ValueError("entity_name must be a non-empty string")
    return JaquelExamples.query_generate_skeleton(entity_name, operation)


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"query"},
)
def query_describe(
    query: Annotated[
        dict,
        Field(
            description=(
                "Jaquel query dict to describe. Top-level key is entity name, value is filter/attribute object. "
                'Example: {"AoTest": {"name": {"$like": "*"}}, '
                '"$attributes": {"id": 1, "name": 1}}'
            )
        ),
    ],
) -> str:
    """Describe what a Jaquel query does."""
    return JaquelExplain.query_describe(query)


# ============================================================================
# SCHEMA TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"schema"},
)
def schema_get_entity(
    entity_name: Annotated[str, Field(description="Entity name (e.g., 'StructureLevel')")],
) -> EntitySchema:
    """Get available fields for an entity from ODS model."""
    if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
        raise ValueError("entity_name must be a non-empty string")
    return SchemaInspector.get_entity_schema(entity_name)


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"schema"},
)
def schema_field_exists(
    entity_name: Annotated[str, Field(description="ODS entity name (e.g. 'AoTest', 'AoMeasurement')")],
    field_name: Annotated[str, Field(description="Field/attribute name to check (e.g. 'name', 'id', 'version')")],
) -> dict:
    """Check if a field exists in entity schema."""
    if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
        raise ValueError("entity_name must be a non-empty string")
    if not field_name or not isinstance(field_name, str) or not field_name.strip():
        raise ValueError("field_name must be a non-empty string")
    return SchemaInspector.schema_field_exists(entity_name, field_name)


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"schema"},
)
def schema_list_entities() -> dict:
    """Return a list of existing entities from the ODS server ModelCache."""
    return SchemaInspector.schema_list_entities()


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"schema"},
)
def schema_test_to_measurement_hierarchy() -> dict:
    """Get hierarchical entity chain from AoTest to AoMeasurement via 'children' relation."""
    return SchemaInspector.schema_test_to_measurement_hierarchy()


# ============================================================================
# CONNECTION TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
    tags={"connection"},
)
async def ods_connect(
    url: Annotated[str, Field(description="ODS API URL (e.g., http://localhost:8087/api)")],
    username: Annotated[str, Field(description="ODS username for authentication")],
    password: Annotated[
        str,
        Field(
            json_schema_extra={"format": "password", "x-mcp-secret": True},
        ),
    ],
    verify: Annotated[bool, Field(description="Verify SSL certificates (default: true)")] = True,
    ctx: Context | None = None,
) -> ConnectResult:
    """Establish connection to ASAM ODS server for live model inspection."""
    if not url or not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")
    if not username or not isinstance(username, str) or not username.strip():
        raise ValueError("username must be a non-empty string")
    if not password or not isinstance(password, str) or not password.strip():
        raise ValueError("password must be a non-empty string")
    if ctx:
        await ctx.info(f"Connecting to ODS server: {url} as user '{username}'")
    result = ODSConnectionManager.connect(url=url, auth=(username, password), verify_certificate=verify)
    if ctx:
        await ctx.info("Connection established successfully")
    return result


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
    tags={"connection"},
)
async def ods_connect_using_env(
    env_prefix: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional: override the environment variable prefix (default: ODSBOX_MCP)",
        ),
    ] = None,
    ctx: Context | None = None,
) -> ConnectResult:
    """Establish connection to ASAM ODS server using environment variables.

    Default prefix is ODSBOX_MCP; set ODSBOX_MCP_ENV_PREFIX or pass env_prefix.
    Falls back to legacy ODS_ prefix variables.

    Supports three authentication modes via {prefix}_MODE:
    - basic (default): Username/password. Vars: URL, USERNAME, PASSWORD, VERIFY.
    - m2m: OAuth2 client credentials. Vars: URL, M2M_TOKEN_ENDPOINT, M2M_CLIENT_ID,
      M2M_CLIENT_SECRET, M2M_SCOPE (optional, comma-separated), VERIFY.
    - oidc: OpenID Connect browser login. Vars: URL, OIDC_CLIENT_ID, OIDC_REDIRECT_URI,
      OIDC_CLIENT_SECRET (optional), OIDC_WEBFINGER_PATH_PREFIX, OIDC_AUTHORIZATION_ENDPOINT,
      OIDC_TOKEN_ENDPOINT, OIDC_LOGIN_TIMEOUT, OIDC_REDIRECT_INSECURE, OIDC_SCOPE, VERIFY.

    Secrets (passwords, client_secrets) fall back to keyring when not in env.
    """
    env = os.environ
    resolved_prefix = env_prefix or env.get("ODSBOX_MCP_ENV_PREFIX") or "ODSBOX_MCP"
    if ctx:
        await ctx.info(f"Resolved env prefix: {resolved_prefix}")

    auth_args = resolve_auth_args_from_env(resolved_prefix)
    mode = auth_args["mode"]

    if ctx:
        await ctx.info(f"Authentication mode: {mode}")

    result = ODSConnectionManager.connect_with_factory(auth_args)

    if ctx:
        await ctx.info("Connection established successfully")
    return result


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
    tags={"connection"},
)
def ods_disconnect() -> dict:
    """Close connection to ODS server."""
    return ODSConnectionManager.disconnect()


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"connection"},
)
def ods_get_connection_info() -> ConnectionInfo | None:
    """Get current ODS connection information."""
    return ODSConnectionManager.get_connection_info()


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"connection"},
)
async def query_execute(
    query: Annotated[
        dict,
        Field(
            description=(
                "Jaquel query dict to execute. Top-level key is entity name, value is filter/attribute object. "
                'Example: {"AoTest": {"name": {"$like": "*"}}, '
                '"$attributes": {"id": 1, "name": 1}, '
                '"$options": {"$rowlimit": 100}}'
            )
        ),
    ],
    result_format: Annotated[
        Literal["split", "records"],
        Field(
            default="split",
            description=(
                'Result serialisation format: "split" (default) encodes column names once '
                '— {"columns": [...], "index": [...], "data": [...]}; '
                '"records" repeats all keys per row — [{"col": val, ...}, ...]. '
                '"split" is more token-efficient for wide results.'
            ),
        ),
    ] = "split",
    max_rows: Annotated[
        int,
        Field(
            default=100,
            ge=1,
            le=10000,
            description=(
                "Maximum number of rows to return (default: 100). "
                "Also capped adaptively by max_cells to protect LLM context size. "
                "Use a small value like 10-20 for wide results (many columns)."
            ),
        ),
    ] = 100,
    max_cells: Annotated[
        int,
        Field(
            default=10000,
            ge=100,
            le=100000,
            description=(
                "Adaptive cell budget: effective_rows = min(max_rows, max_cells // col_count). "
                "Default 10 000 ≈ 6 000 LLM tokens for double data. "
                "Increase only if you need more data and understand the context cost."
            ),
        ),
    ] = 10000,
    ctx: Context | None = None,
) -> dict:
    """Execute a Jaquel query directly on connected ODS server."""
    return ODSConnectionManager.query(query, result_format=result_format, max_rows=max_rows, max_cells=max_cells)


# ============================================================================
# SUBMATRIX DATA ACCESS TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"data"},
)
def data_get_quantities(
    submatrix_id: Annotated[int, Field(description="ID of the submatrix")],
) -> dict:
    """Get available measurement quantities for a submatrix."""
    if submatrix_id <= 0:
        raise ValueError("submatrix_id must be a positive integer (> 0)")
    quantities = SubmatrixDataReader.get_measurement_quantities(submatrix_id)
    return {"submatrix_id": submatrix_id, "measurement_quantities": quantities}


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"data"},
)
async def data_read_submatrix(
    submatrix_id: Annotated[int, Field(description="ID of the submatrix to read")],
    measurement_quantity_patterns: Annotated[
        list[str] | None,
        Field(default=None, description="List of measurement quantity name patterns to include"),
    ] = None,
    case_insensitive: Annotated[
        bool, Field(default=False, description="Whether pattern matching should be case insensitive")
    ] = False,
    date_as_timestamp: Annotated[
        bool, Field(default=True, description="Convert date columns to pandas timestamps")
    ] = True,
    set_independent_as_index: Annotated[
        bool, Field(default=True, description="Set the independent column as DataFrame index")
    ] = True,
    max_preview_size: Annotated[
        int, Field(default=100, description="Maximum number of rows in data preview (default: 100)")
    ] = 100,
    preview_sampling_method: Annotated[
        Literal["auto", "uniform", "time_aware", "random", "stratified", "minmax"],
        Field(
            default="auto",
            description="Method for resampling preview data: auto, uniform, time_aware, random, stratified, minmax",
        ),
    ] = "auto",
    ctx: Context | None = None,
) -> dict:
    """Read timeseries data from a submatrix using bulk data access."""
    if submatrix_id <= 0:
        raise ValueError("submatrix_id must be a positive integer (> 0)")
    if ctx:
        await ctx.info(f"Reading submatrix {submatrix_id}...")
    result = SubmatrixDataReader.data_read_submatrix(
        submatrix_id=submatrix_id,
        measurement_quantity_patterns=measurement_quantity_patterns or [],
        case_insensitive=case_insensitive,
        date_as_timestamp=date_as_timestamp,
        set_independent_as_index=set_independent_as_index,
        max_preview_size=max_preview_size,
        preview_sampling_method=preview_sampling_method,
    )
    if ctx:
        await ctx.info(result["note"])
    return result


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"data"},
)
async def data_generate_fetcher_script(
    submatrix_id: Annotated[int, Field(description="ID of the submatrix to fetch data from")],
    script_type: Annotated[
        Literal["basic", "advanced", "batch", "analysis"],
        Field(description="Type of script: basic, advanced, batch, analysis"),
    ],
    output_format: Annotated[
        Literal["csv", "json", "parquet", "excel", "dataframe"],
        Field(default="csv", description="Desired output format for the data"),
    ] = "csv",
    measurement_quantity_patterns: Annotated[
        list[str] | None,
        Field(default=None, description="List of measurement quantity patterns to include"),
    ] = None,
    include_analysis: Annotated[
        bool, Field(default=False, description="Include basic data analysis examples")
    ] = False,
    include_visualization: Annotated[
        bool, Field(default=False, description="Include matplotlib visualization code")
    ] = False,
    ctx: Context | None = None,
) -> dict:
    """Generate Python scripts for fetching submatrix data with error handling and data processing."""
    if submatrix_id <= 0:
        raise ValueError("submatrix_id must be a positive integer (> 0)")

    # Get available measurement quantities
    quantities = SubmatrixDataReader.get_measurement_quantities(submatrix_id)

    # Use provided patterns or all quantities
    if not measurement_quantity_patterns:
        mq_list = [q["name"] for q in quantities]
        if ctx:
            await ctx.warning(f"No patterns specified — including all {len(quantities)} quantities in script")
    else:
        mq_list = measurement_quantity_patterns

    # Generate script based on type
    if script_type == "basic":
        script = generate_basic_fetcher_script(submatrix_id, mq_list, output_format)
    elif script_type == "advanced":
        script = generate_advanced_fetcher_script(
            submatrix_id, mq_list, output_format, include_visualization, include_analysis
        )
    elif script_type == "batch":
        script = generate_batch_fetcher_script(submatrix_id, mq_list, output_format)
    elif script_type == "analysis":
        script = generate_analysis_fetcher_script(submatrix_id, mq_list, output_format, include_visualization)
    else:
        raise ValueError(f"Unknown script type: {script_type}")

    return {
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


# ============================================================================
# MEASUREMENT & VISUALIZATION TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
    tags={"measurement", "visualization"},
)
def plot_comparison_notebook(
    measurement_query_conditions: Annotated[
        dict,
        Field(
            description=(
                "Filter conditions for measurements (MeaResult attributes). "
                'Example: {"Name": {"$like": "Profile_*"}} or '
                '{"TestStep.Test.Name": {"$eq": "MyTest"}}'
            )
        ),
    ],
    measurement_quantity_names: Annotated[list[str], Field(description="Names of quantities to plot")],
    available_quantities: Annotated[
        list[str] | None,
        Field(default=None, description="List of all available quantities (for documentation)"),
    ] = None,
    plot_type: Annotated[
        Literal["scatter", "line", "subplots"],
        Field(default="scatter", description='Type of plot ("scatter", "line", or "subplots")'),
    ] = "scatter",
    title: Annotated[
        str, Field(default="Measurement Comparison", description="Notebook title")
    ] = "Measurement Comparison",
    output_path: Annotated[
        str | None,
        Field(default=None, description="Optional path to save notebook (.ipynb file)"),
    ] = None,
) -> dict:
    """Generate a Jupyter notebook for comparing measurements.

    Uses the active ODS connection (established via ods_connect or ods_connect_using_env).
    The generated notebook reads the password from the ODS_PASSWORD environment variable
    at runtime so no credentials are embedded in the notebook file.
    """
    connection_info = ODSConnectionManager.get_connection_info()
    if connection_info is None or not connection_info.url:
        raise ValueError("No active ODS connection. Use ods_connect or ods_connect_using_env first.")
    ods_url = connection_info.url
    ods_username = connection_info.username

    notebook = NotebookGenerator.plot_comparison_notebook(
        measurement_query_conditions=measurement_query_conditions,
        measurement_quantity_names=measurement_quantity_names,
        ods_url=ods_url,
        ods_username=ods_username,
        available_quantities=available_quantities,
        plot_type=plot_type,
        title=title,
    )

    result: dict = {
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

    return result


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"measurement", "visualization"},
)
def plot_generate_code(
    measurement_quantity_names: Annotated[list[str], Field(description="List of quantity names to plot")],
    submatrices_count: Annotated[int, Field(description="Number of submatrices to plot")],
    plot_type: Annotated[
        Literal["scatter", "line", "subplots"],
        Field(description='Type of plot ("scatter", "line", or "subplots")'),
    ],
) -> dict:
    """Generate Python plotting code for measurement comparison."""
    if plot_type == "scatter":
        if len(measurement_quantity_names) < 2:
            raise ValueError("Scatter plot requires at least 2 measurement quantities")
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

    return {
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


# ============================================================================
# HELP & DOCUMENTATION TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
    tags={"help"},
)
def help_bulk_api(
    topic: Annotated[
        Literal[
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
        Field(description="Help topic"),
    ],
    tool: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional: Get contextual help for a specific tool (e.g., data_read_submatrix, ods_connect)",
        ),
    ] = None,
) -> dict:
    """Get help and guidance on using the Bulk API for loading timeseries data.

    Use this to understand the 3-step workflow and common patterns.
    """
    if tool:
        help_text = BulkAPIGuide.get_contextual_help(tool)
        return {"topic": "contextual-help", "tool": tool, "help": help_text}
    elif topic == "all":
        help_text = BulkAPIGuide.get_all_help()
        return {"topic": topic, "help": help_text}
    else:
        help_text = BulkAPIGuide.get_help(topic)
        return {"topic": topic, "help": help_text}


# ============================================================================
# MCP RESOURCES
# ============================================================================


@mcp.resource("file:///odsbox/ods-connection-guide", name="ODS Connection Setup Guide", mime_type="text/markdown")
def resource_ods_connection_guide() -> str:
    """Complete guide for connecting to ASAM ODS servers and managing connections."""
    return ResourceLibrary.get_resource_content("file:///odsbox/ods-connection-guide")


@mcp.resource("file:///odsbox/ods-workflow-reference", name="Common ODS Workflows", mime_type="text/markdown")
def resource_ods_workflow_reference() -> str:
    """Step-by-step workflows for typical ODS operations and data access patterns."""
    return ResourceLibrary.get_resource_content("file:///odsbox/ods-workflow-reference")


@mcp.resource("file:///odsbox/ods-entity-hierarchy", name="ODS Entity Hierarchy Reference", mime_type="text/markdown")
def resource_ods_entity_hierarchy() -> str:
    """Understanding ASAM ODS entity relationships (AoTest, AoMeasurement, etc.)."""
    return ResourceLibrary.get_resource_content("file:///odsbox/ods-entity-hierarchy")


@mcp.resource("file:///odsbox/query-execution-patterns", name="Query Execution Patterns", mime_type="text/markdown")
def resource_query_execution_patterns() -> str:
    """Best practices and patterns for executing Jaquel queries against ODS servers."""
    return ResourceLibrary.get_resource_content("file:///odsbox/query-execution-patterns")


@mcp.resource("file:///odsbox/query-operators-reference", name="Query Operators Reference", mime_type="text/markdown")
def resource_query_operators_reference() -> str:
    """Complete reference of all Jaquel query operators with examples and use cases."""
    return ResourceLibrary.get_resource_content("file:///odsbox/query-operators-reference")


@mcp.resource("file:///odsbox/jaquel-syntax-guide", name="Jaquel Syntax Guide", mime_type="text/markdown")
def resource_jaquel_syntax_guide() -> str:
    """Complete Jaquel query language syntax reference with examples and best practices."""
    return ResourceLibrary.get_resource_content("file:///odsbox/jaquel-syntax-guide")


@mcp.resource(
    "file:///odsbox/connection-troubleshooting", name="ODS Connection Troubleshooting", mime_type="text/markdown"
)
def resource_connection_troubleshooting() -> str:
    """Common connection issues and solutions for working with ASAM ODS servers."""
    return ResourceLibrary.get_resource_content("file:///odsbox/connection-troubleshooting")


@mcp.resource(
    "file:///odsbox/schema/entity/{entity_name}",
    name="Entity Schema",
    mime_type="text/markdown",
)
def resource_entity_schema(entity_name: str) -> str:
    """Get detailed schema information for any ODS entity (requires active ODS connection)."""
    return ResourceLibrary.get_resource_content(f"file:///odsbox/schema/entity/{entity_name}")


# ============================================================================
# MCP PROMPTS
# ============================================================================


@mcp.prompt()
def prompt_query_validate(query_example: str = "") -> str:
    """Validate a Jaquel Query.

    Learn how to validate a Jaquel query for syntax errors and best practices.
    Provides detailed feedback on query structure and suggestions for improvement.
    """
    return PromptLibrary.get_prompt_content("query_validate", {"query_example": query_example})


@mcp.prompt()
def explore_patterns(pattern_type: str = "") -> str:
    """Explore Jaquel Query Patterns.

    Discover common Jaquel query patterns and templates for tasks like:
    getting all instances, filtering by ID or name, case-insensitive search,
    time range queries, joins, and aggregations.
    """
    return PromptLibrary.get_prompt_content("explore_patterns", {"pattern_type": pattern_type})


@mcp.prompt()
def connect_ods_server(server_details: str = "") -> str:
    """Set Up ODS Server Connection.

    Learn how to establish a connection to an ASAM ODS server for live model inspection,
    schema validation, and direct query execution.
    """
    return PromptLibrary.get_prompt_content("connect_ods_server", {"server_details": server_details})


@mcp.prompt()
def timeseries_access(use_case: str = "") -> str:
    """Bulk Data Access & Submatrix Reading.

    Master the 3-step Bulk API workflow for efficient timeseries data access.
    Learn how to read submatrix data, generate fetcher scripts, and handle large datasets.
    """
    return PromptLibrary.get_prompt_content("timeseries_access", {"use_case": use_case})
