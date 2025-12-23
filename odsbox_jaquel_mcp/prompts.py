"""Starting prompts for the ASAM ODS Jaquel MCP Server.

This module provides helpful starting prompts to guide users on how to use
the server's tools for Jaquel query creation, validation, and ODS data access.
"""

from __future__ import annotations

from mcp.types import Prompt, PromptArgument, TextContent


class PromptLibrary:
    """Collection of starting prompts for the MCP server."""

    @staticmethod
    def get_all_prompts() -> list[Prompt]:
        """Return all available starting prompts."""
        return [
            PromptLibrary._query_validation_prompt(),
            PromptLibrary._query_pattern_prompt(),
            PromptLibrary._ods_connection_prompt(),
            PromptLibrary._bulk_api_guide_prompt(),
            PromptLibrary._measurement_analysis_prompt(),
        ]

    @staticmethod
    def _query_validation_prompt() -> Prompt:
        """Prompt for validating a Jaquel query."""
        return Prompt(
            name="validate_query",
            title="Validate a Jaquel Query",
            description=(
                "Learn how to validate a Jaquel query for syntax errors and best practices. "
                "Provides detailed feedback on query structure and suggestions for improvement."
            ),
            arguments=[
                PromptArgument(
                    name="query_example",
                    description="(Optional) A sample Jaquel query to validate",
                    required=False,
                )
            ],
        )

    @staticmethod
    def _query_pattern_prompt() -> Prompt:
        """Prompt for exploring Jaquel query patterns."""
        return Prompt(
            name="explore_patterns",
            title="Explore Jaquel Query Patterns",
            description=(
                "Discover common Jaquel query patterns and templates for tasks like: "
                "getting all instances, filtering by ID or name, case-insensitive search, "
                "time range queries, joins, and aggregations."
            ),
            arguments=[
                PromptArgument(
                    name="pattern_type",
                    description=(
                        "Type of pattern: get_all_instances, get_by_id, get_by_name, "
                        "case_insensitive_search, time_range, inner_join, outer_join, aggregates"
                    ),
                    required=False,
                )
            ],
        )

    @staticmethod
    def _ods_connection_prompt() -> Prompt:
        """Prompt for connecting to an ODS server."""
        return Prompt(
            name="setup_ods_connection",
            title="Set Up ODS Server Connection",
            description=(
                "Learn how to establish a connection to an ASAM ODS server for live model inspection, "
                "schema validation, and direct query execution. Includes connection management and "
                "entity listing."
            ),
            arguments=[
                PromptArgument(
                    name="server_details",
                    description="(Optional) Your ODS server URL, username, and password",
                    required=False,
                )
            ],
        )

    @staticmethod
    def _bulk_api_guide_prompt() -> Prompt:
        """Prompt for bulk API and submatrix data access."""
        return Prompt(
            name="bulk_data_access",
            title="Bulk Data Access & Submatrix Reading",
            description=(
                "Master the 3-step Bulk API workflow for efficient timeseries data access. "
                "Learn how to read submatrix data, generate fetcher scripts, and handle large datasets. "
                "Includes patterns, best practices, and common mistakes to avoid."
            ),
            arguments=[
                PromptArgument(
                    name="use_case",
                    description=(
                        "Your data access scenario: "
                        "basic reading, advanced analysis, batch processing, or generating scripts"
                    ),
                    required=False,
                )
            ],
        )

    @staticmethod
    def _measurement_analysis_prompt() -> Prompt:
        """Prompt for measurement analysis and comparison."""
        return Prompt(
            name="analyze_measurements",
            title="Measurement Analysis & Comparison",
            description=(
                "Learn how to analyze and compare measurements across quantities with statistical analysis. "
                "Generate Jupyter notebooks for measurement comparison, create visualization code, "
                "and explore measurement hierarchies."
            ),
            arguments=[
                PromptArgument(
                    name="analysis_type",
                    description=(
                        "Type of analysis: comparison, visualization, hierarchy exploration, " "or notebook generation"
                    ),
                    required=False,
                )
            ],
        )

    @staticmethod
    def get_prompt_content(prompt_name: str, arguments: dict | None = None) -> str:
        """Generate content for a specific prompt.

        Args:
            prompt_name: Name of the prompt
            arguments: Optional arguments for customizing the prompt content

        Returns:
            Prompt content as a formatted string
        """
        arguments = arguments or {}

        if prompt_name == "setup_ods_connection":
            server_details = arguments.get("server_details", "")
            content = (
                "# Setting Up ODS Server Connection\n\n"
                "Connect to your ASAM ODS server to enable live data model inspection and query data execution.\n\n"
                "## Connection Steps:\n"
                "1. Use `connect_ods_server` with your server URL, username, and password\n"
                "2. Verify connection with `get_ods_connection_info`\n"
                "3. Use `get_test_to_measurement_hierarchy` to explore hierarchy entity relations\n"
                "4. List entities with `list_ods_entities` to explore the entity relationship model\n"
                "5. Generate query templates with `generate_query_skeleton` for specific entity\n"
                "6. Execute queries directly with `execute_ods_query`\n\n"
                "## Available ODS Connection Tools:\n"
                "- `connect_ods_server` - Establish connection\n"
                "- `disconnect_ods_server` - Close connection\n"
                "- `get_ods_connection_info` - Check current connection status\n"
                "- `get_test_to_measurement_hierarchy` - Explore test-measurement relationships\n"
                "- `list_ods_entities` - List available entities in the data model\n"
                "- `generate_query_skeleton` - Create query templates for entity\n"
                "- `execute_ods_query` - Run queries on live server\n\n"
            )
            if server_details:
                content += f"**Your server details:** {server_details}\n"
            return content

        elif prompt_name == "validate_query":
            query_example = arguments.get("query_example", "")
            content = (
                "# Validating Jaquel Queries\n\n"
                "Use the `validate_query` tool to check your Jaquel queries for:\n"
                "- Syntax errors and structural issues\n"
                "- Missing required fields\n"
                "- Invalid operators or comparisons\n"
                "- Best practice violations\n\n"
                "## How to use:\n"
                "1. Call `validate_query` with your query object\n"
                "2. Review the validation report\n"
                "3. Use suggestions to fix any issues\n\n"
            )
            if query_example:
                content += f"**Your query:**\n```json\n{query_example}\n```\n"
            return content

        elif prompt_name == "explore_patterns":
            pattern_type = arguments.get("pattern_type", "")
            content = (
                "# Jaquel Query Patterns\n\n"
                "The MCP server provides templates for common query patterns:\n\n"
                "**Available patterns:**\n"
                "- `get_all_instances` - Retrieve all instances of an entity\n"
                "- `get_by_id` - Get a specific instance by ID\n"
                "- `get_by_name` - Filter by name field\n"
                "- `case_insensitive_search` - Pattern matching without case sensitivity\n"
                "- `time_range` - Filter by date/time ranges\n"
                "- `inner_join` - Join related entities\n"
                "- `outer_join` - Outer join for optional relationships\n"
                "- `aggregates` - Aggregate functions like count, sum, avg\n\n"
                "## How to use:\n"
                "1. Call `list_query_patterns` to see all available patterns\n"
                "2. Use `get_query_pattern` with a specific pattern name\n"
                "3. Adapt the template to your entity and requirements\n"
                "4. Use `generate_query_skeleton` for entity-specific starting points\n\n"
            )
            if pattern_type:
                content += f"**Pattern of interest:** {pattern_type}\n"
            return content

        elif prompt_name == "bulk_data_access":
            use_case = arguments.get("use_case", "")
            content = (
                "# Bulk API & Submatrix Data Access\n\n"
                "Efficiently access large timeseries datasets from ODS using the 3-step Bulk API workflow.\n\n"
                "## The 3-Step Workflow:\n"
                "1. **Locate** - Find the submatrix ID you need\n"
                "2. **Access** - Use Bulk API to read the data efficiently\n"
                "3. **Process** - Transform and analyze the data\n\n"
                "## Key Tools:\n"
                "- `read_submatrix_data` - Read data with pattern matching\n"
                "- `get_submatrix_measurement_quantities` - List available quantities\n"
                "- `generate_submatrix_fetcher_script` - Generate reusable scripts\n"
                "- `get_bulk_api_help` - Get detailed guidance\n\n"
                "## Script Generation Types:\n"
                "- `basic` - Simple data fetching\n"
                "- `advanced` - With analysis and visualization\n"
                "- `batch` - For processing multiple submatrices\n"
                "- `analysis` - Statistical analysis included\n\n"
                "## Quick Start:\n"
                "1. Get measurement quantities: `get_submatrix_measurement_quantities`\n"
                "2. Read data: `read_submatrix_data` with patterns\n"
                "3. Generate script for reuse: `generate_submatrix_fetcher_script`\n\n"
            )
            if use_case:
                content += f"**Your use case:** {use_case}\n"
            return content

        elif prompt_name == "analyze_measurements":
            analysis_type = arguments.get("analysis_type", "")
            content = (
                "# Measurement Analysis & Comparison\n\n"
                "Analyze and compare measurements with statistical analysis and visualization.\n\n"
                "## Analysis Tools:\n"
                "- `compare_measurements` - Statistical comparison across quantities\n"
                "- `query_measurement_hierarchy` - Explore measurement structure\n"
                "- `generate_measurement_comparison_notebook` - Create Jupyter notebooks\n"
                "- `generate_plotting_code` - Generate matplotlib visualization code\n\n"
                "## Hierarchy Operations:\n"
                "- `extract_measurements` - Get measurements from query results\n"
                "- `build_hierarchy` - Create hierarchical structure\n"
                "- `get_unique_tests` - Find all unique test names\n"
                "- `get_unique_quantities` - List available quantities\n"
                "- `build_index` - Create searchable measurement index\n\n"
                "## Plot Types:\n"
                "- `scatter` - Scatter plot for 2+ quantities\n"
                "- `line` - Line plot for trends\n"
                "- `subplots` - Individual subplot per measurement\n\n"
                "## Workflow:\n"
                "1. Execute a query to get measurements\n"
                "2. Use `query_measurement_hierarchy` to explore\n"
                "3. Generate notebooks or plots\n"
                "4. Perform statistical comparisons\n\n"
            )
            if analysis_type:
                content += f"**Analysis type:** {analysis_type}\n"
            return content

        else:
            return f"Prompt '{prompt_name}' not found."
