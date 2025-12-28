"""MCP Resources for ODS connection and workflow guidance.

This module provides reference materials about:
- Connecting to ASAM ODS servers
- Common workflows and patterns
- Entity hierarchy understanding
- Query execution best practices
- Connection troubleshooting
- Dynamic entity schema templates
"""

from __future__ import annotations

from pathlib import Path

from mcp.types import Resource, ResourceTemplate
from pydantic import AnyUrl


class ResourceLibrary:
    """Collection of reference resources for ODS operations."""

    @staticmethod
    def _get_resource_dir() -> Path:
        """Get the path to the resource files directory."""
        return Path(__file__).parent / "resource_files"

    @staticmethod
    def get_all_resources() -> list[Resource]:
        """Return all available reference resources."""
        return [
            Resource(
                uri=AnyUrl("file:///odsbox/ods-connection-guide"),
                name="ODS Connection Setup Guide",
                description="Complete guide for connecting to ASAM ODS servers and managing connections",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/ods-workflow-reference"),
                name="Common ODS Workflows",
                description="Step-by-step workflows for typical ODS operations and data access patterns",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/ods-entity-hierarchy"),
                name="ODS Entity Hierarchy Reference",
                description="Understanding ASAM ODS entity relationships (AoTest, AoMeasurement, etc.)",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/query-execution-patterns"),
                name="Query Execution Patterns",
                description="Best practices and patterns for executing Jaquel queries against ODS servers",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/query-operators-reference"),
                name="Query Operators Reference",
                description="Complete reference of all Jaquel query operators with examples and use cases",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/jaquel-syntax-guide"),
                name="Jaquel Syntax Guide",
                description="Complete Jaquel query language syntax reference with examples and best practices",
                mimeType="text/markdown",
            ),
            Resource(
                uri=AnyUrl("file:///odsbox/connection-troubleshooting"),
                name="ODS Connection Troubleshooting",
                description="Common connection issues and solutions for working with ASAM ODS servers",
                mimeType="text/markdown",
            ),
        ]

    @staticmethod
    def get_all_resource_templates() -> list[ResourceTemplate]:
        """Return all available resource templates for dynamic content."""
        return [
            ResourceTemplate(
                name="entity_schema",
                uriTemplate="file:///odsbox/schema/entity/{entity_name}",
                title="Entity Schema",
                description="Get detailed schema information for any ODS entity (requires active ODS connection)",
                mimeType="text/markdown",
            ),
        ]

    @staticmethod
    def get_resource_content(uri: str) -> str:
        """Get the content for a specific resource.

        Args:
            uri: Resource URI (e.g., 'file:///odsbox/ods-connection-guide' or 'file:///odsbox/schema/AoTest')

        Returns:
            Resource content as markdown
        """
        # Handle dynamic entity schema template
        if uri.startswith("file:///odsbox/schema/entity/"):
            from .schemas import SchemaInspector

            entity_name = uri.replace("file:///odsbox/schema/entity/", "")
            try:
                return SchemaInspector.format_entity_schema_as_markdown(entity_name)
            except Exception as e:
                return f"""# Entity Schema: {entity_name}

**Error retrieving schema**: {str(e)}

Ensure:
1. You are connected to an ODS server via `ods_connect` tool
2. The entity name is correct (try `schema_list_entities` to see available entities)
3. The entity exists in the ODS model
"""

        # Map URIs to resource file names
        uri_to_resource = {
            "file:///odsbox/ods-connection-guide": "resource_ods_connection_guide.md",
            "file:///odsbox/ods-workflow-reference": "resource_ods_workflow_reference.md",
            "file:///odsbox/ods-entity-hierarchy": "resource_ods_entity_hierarchy.md",
            "file:///odsbox/query-execution-patterns": "resource_query_execution_patterns.md",
            "file:///odsbox/connection-troubleshooting": "resource_connection_troubleshooting.md",
            "file:///odsbox/query-operators-reference": "resource_query_operators_reference.md",
            "file:///odsbox/jaquel-syntax-guide": "resource_jaquel_syntax_guide.md",
        }

        if uri in uri_to_resource:
            resource_path = ResourceLibrary._get_resource_dir() / uri_to_resource[uri]
            try:
                return resource_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                return f"Resource file not found: {resource_path}"

        return f"Unknown resource: {uri}"
