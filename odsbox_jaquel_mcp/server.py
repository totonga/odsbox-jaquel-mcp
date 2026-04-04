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
from .measurement_analysis import ComparisonResult, MeasurementAnalyzer
from .measurement_queries import MeasurementHierarchyExplorer
from .monitoring import ToolStatsMiddleware
from .notebook_generator import NotebookGenerator
from .prompts import PromptLibrary
from .queries import JaquelExamples, JaquelExplain
from .resources import ResourceLibrary
from .schemas import SchemaInspector
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
    _instructions = (
        "# ASAM ODS Jaquel MCP Server\n\n" "See documentation at https://github.com/totonga/odsbox-jaquel-mcp"
    )

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
    annotations={"readOnlyHint": True},
    tags={"validation"},
)
def query_validate(query: dict) -> dict:
    """Validate a Jaquel query structure for syntax errors and best practices."""
    return JaquelValidator.query_validate(query)


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"validation"},
)
def query_get_operator_docs(operator: str) -> dict:
    """Get documentation and examples for a Jaquel operator."""
    if not operator or not isinstance(operator, str) or not operator.strip():
        raise ValueError("operator must be a non-empty string")
    return JaquelValidator.get_operator_info(operator)


# ============================================================================
# QUERY PATTERN TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": True},
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
    annotations={"readOnlyHint": True},
    tags={"query"},
)
def query_list_patterns() -> dict:
    """List all available Jaquel query patterns and templates."""
    patterns = JaquelExamples.list_patterns()
    return {"available_patterns": patterns, "description": "Available query patterns"}


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"query"},
)
def query_generate_skeleton(
    entity_name: str,
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
    annotations={"readOnlyHint": True},
    tags={"query"},
)
def query_describe(query: dict) -> str:
    """Describe what a Jaquel query does."""
    return JaquelExplain.query_describe(query)


# ============================================================================
# SCHEMA TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"schema"},
)
def schema_get_entity(
    entity_name: Annotated[str, Field(description="Entity name (e.g., 'StructureLevel')")],
) -> dict:
    """Get available fields for an entity from ODS model."""
    if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
        raise ValueError("entity_name must be a non-empty string")
    return SchemaInspector.get_entity_schema(entity_name)


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"schema"},
)
def schema_field_exists(entity_name: str, field_name: str) -> dict:
    """Check if a field exists in entity schema."""
    if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
        raise ValueError("entity_name must be a non-empty string")
    if not field_name or not isinstance(field_name, str) or not field_name.strip():
        raise ValueError("field_name must be a non-empty string")
    return SchemaInspector.schema_field_exists(entity_name, field_name)


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"schema"},
)
def schema_list_entities() -> dict:
    """Return a list of existing entities from the ODS server ModelCache."""
    return SchemaInspector.schema_list_entities()


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"schema"},
)
def schema_test_to_measurement_hierarchy() -> dict:
    """Get hierarchical entity chain from AoTest to AoMeasurement via 'children' relation."""
    return SchemaInspector.schema_test_to_measurement_hierarchy()


# ============================================================================
# CONNECTION TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"connection"},
)
async def ods_connect(
    url: Annotated[str, Field(description="ODS API URL (e.g., http://localhost:8087/api)")],
    username: str,
    password: Annotated[
        str,
        Field(
            json_schema_extra={"format": "password", "x-mcp-secret": True},
        ),
    ],
    verify: Annotated[bool, Field(description="Verify SSL certificates (default: true)")] = True,
    ctx: Context | None = None,
) -> dict:
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
    annotations={"readOnlyHint": True},
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
) -> dict:
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
    annotations={"readOnlyHint": True},
    tags={"connection"},
)
def ods_disconnect() -> dict:
    """Close connection to ODS server."""
    return ODSConnectionManager.disconnect()


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"connection"},
)
def ods_get_connection_info() -> dict:
    """Get current ODS connection information."""
    return ODSConnectionManager.get_connection_info()


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"connection"},
)
async def query_execute(
    query: Annotated[dict, Field(description="Jaquel query to execute")],
    ctx: Context | None = None,
) -> dict:
    """Execute a Jaquel query directly on connected ODS server."""
    return ODSConnectionManager.query(query)


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
    annotations={"readOnlyHint": True},
    tags={"measurement", "visualization"},
)
def plot_comparison_notebook(
    measurement_query_conditions: Annotated[dict, Field(description="Filter conditions for measurements")],
    measurement_quantity_names: Annotated[list[str], Field(description="Names of quantities to plot")],
    ods_url: Annotated[str, Field(description="ODS server URL")],
    ods_username: Annotated[str, Field(description="ODS username")],
    ods_password: Annotated[
        str,
        Field(
            description="ODS password",
            json_schema_extra={"format": "password", "x-mcp-secret": True},
        ),
    ],
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
    """Generate a Jupyter notebook for comparing measurements."""
    notebook = NotebookGenerator.plot_comparison_notebook(
        measurement_query_conditions=measurement_query_conditions,
        measurement_quantity_names=measurement_quantity_names,
        ods_url=ods_url,
        ods_username=ods_username,
        ods_password=ods_password,
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
    annotations={"readOnlyHint": True},
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


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"measurement"},
)
async def data_compare_measurements(
    quantity_name: Annotated[str, Field(description="Name of quantity to compare")],
    measurement_data: Annotated[dict, Field(description="Dict mapping measurement_id (as string) to list of values")],
    measurement_names: Annotated[
        dict | None,
        Field(default=None, description="Optional dict mapping measurement_id to display names"),
    ] = None,
    ctx: Context | None = None,
) -> dict:
    """Compare measurements across quantities with statistical analysis."""
    if not quantity_name or not measurement_data:
        raise ValueError("quantity_name and measurement_data are required")

    # Convert string keys to integers for measurement_data
    converted_data: dict[int, list[float]] = {}  # type: ignore
    for key, values in measurement_data.items():
        try:
            meas_id = int(key)
            converted_data[meas_id] = values  # type: ignore
        except (ValueError, TypeError):
            if ctx:
                await ctx.warning(f"Could not convert measurement key '{key}' to int, using as-is")
            converted_data[key] = values  # type: ignore

    # Perform multi-measurement comparison
    comparison_result = MeasurementAnalyzer.compare_multiple_measurements(quantity_name, converted_data)

    # If measurement_names provided, generate summary
    if measurement_names:
        quantity_names = [quantity_name]
        comparison_results = [
            ComparisonResult(
                quantity_name=c["quantity_name"],
                measurement_1_id=c["measurement_1_id"],
                measurement_2_id=c["measurement_2_id"],
                measurement_1_mean=c["measurement_1_mean"],
                measurement_2_mean=c["measurement_2_mean"],
                mean_difference=c["mean_difference"],
                mean_difference_percent=c["mean_difference_percent"],
                correlation=c["correlation"],
                notes=c["notes"],
            )
            for c in comparison_result.get("pairwise_comparisons", [])
        ]

        summary = MeasurementAnalyzer.generate_comparison_summary(
            measurement_names, quantity_names, comparison_results
        )
        comparison_result["summary"] = summary

    return comparison_result


@mcp.tool(
    annotations={"readOnlyHint": True},
    tags={"measurement"},
)
def data_query_hierarchy(
    query_result: Annotated[dict, Field(description="ODS query result to explore")],
    operation: Annotated[
        Literal[
            "extract_measurements",
            "build_hierarchy",
            "get_unique_tests",
            "get_unique_quantities",
            "build_index",
        ],
        Field(description="Operation to perform on query result"),
    ],
    test_name: Annotated[str | None, Field(default=None, description="Optional test name for filtering")] = None,
    quantity_names: Annotated[
        list[str] | None,
        Field(default=None, description="Optional list of quantities to search for"),
    ] = None,
) -> dict:
    """Query and explore ODS measurement hierarchy and structure."""
    if operation == "extract_measurements":
        measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
        return {
            "operation": operation,
            "num_measurements": len(measurements),
            "measurements": measurements[:50],  # Limit output
        }

    elif operation == "build_hierarchy":
        measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
        hierarchy = MeasurementHierarchyExplorer.build_measurement_hierarchy(measurements)
        return {
            "operation": operation,
            "hierarchy_keys": list(hierarchy.keys()),
            "total_measurements": hierarchy["total_measurements"],
            "tests": list(hierarchy["by_test"].keys()),
            "statuses": list(hierarchy["by_status"].keys()),
        }

    elif operation == "get_unique_tests":
        measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
        tests = MeasurementHierarchyExplorer.get_unique_tests(measurements)
        return {
            "operation": operation,
            "unique_tests": tests,
            "num_tests": len(tests),
        }

    elif operation == "get_unique_quantities":
        measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
        unique_quantities: list[str] = MeasurementHierarchyExplorer.get_unique_quantities(measurements)
        return {
            "operation": operation,
            "unique_quantities": unique_quantities,
            "num_quantities": len(unique_quantities),
        }

    elif operation == "build_index":
        measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
        index = MeasurementHierarchyExplorer.build_measurement_index(measurements)
        return {
            "operation": operation,
            "total_measurements": index["total_measurements"],
            "index_by_id_count": len(index["by_id"]),
            "index_by_name_count": len(index["by_name"]),
            "index_by_test_count": len(index["by_test"]),
            "index_by_status_count": len(index["by_status"]),
            "available_test_names": list(index["by_test"].keys())[:10],
        }

    else:
        raise ValueError(f"Unknown operation: {operation}")


# ============================================================================
# HELP & DOCUMENTATION TOOLS
# ============================================================================


@mcp.tool(
    annotations={"readOnlyHint": True},
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


@mcp.prompt()
def analyze_measurements(analysis_type: str = "") -> str:
    """Measurement Analysis & Comparison.

    Learn how to analyze and compare measurements across quantities with statistical analysis.
    Generate Jupyter notebooks for measurement comparison, create visualization code,
    and explore measurement hierarchies.
    """
    return PromptLibrary.get_prompt_content("analyze_measurements", {"analysis_type": analysis_type})
