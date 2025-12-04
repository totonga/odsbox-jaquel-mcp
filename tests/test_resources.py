"""Tests for MCP resource functionality."""

import pytest
from mcp.types import Resource

from odsbox_jaquel_mcp.resources import ResourceLibrary


class TestResourceLibrary:
    """Test cases for ResourceLibrary."""

    def test_get_all_resources_returns_list(self):
        """Test that get_all_resources returns a list of Resource objects."""
        resources = ResourceLibrary.get_all_resources()

        assert isinstance(resources, list)
        assert len(resources) > 0
        assert len(resources) == 7

        # Check that each resource has required attributes
        for resource in resources:
            assert isinstance(resource, Resource)
            assert hasattr(resource, "uri")
            assert hasattr(resource, "name")
            assert hasattr(resource, "description")
            assert hasattr(resource, "mimeType")

    def test_resource_uris_are_valid(self):
        """Test that all resources have valid file:///odsbox/ URIs."""
        resources = ResourceLibrary.get_all_resources()
        expected_uris = {
            "file:///odsbox/ods-connection-guide",
            "file:///odsbox/ods-workflow-reference",
            "file:///odsbox/ods-entity-hierarchy",
            "file:///odsbox/query-execution-patterns",
            "file:///odsbox/query-operators-reference",
            "file:///odsbox/jaquel-syntax-guide",
            "file:///odsbox/connection-troubleshooting",
        }

        resource_uris = {str(resource.uri) for resource in resources}
        assert resource_uris == expected_uris

    def test_resource_names_are_unique(self):
        """Test that all resources have unique names."""
        resources = ResourceLibrary.get_all_resources()
        names = [resource.name for resource in resources]

        assert len(names) == len(set(names))

    def test_resource_descriptions_are_not_empty(self):
        """Test that all resources have descriptions."""
        resources = ResourceLibrary.get_all_resources()

        for resource in resources:
            assert resource.description
            assert len(resource.description) > 0

    def test_resource_mime_type_is_markdown(self):
        """Test that all resources have markdown MIME type."""
        resources = ResourceLibrary.get_all_resources()

        for resource in resources:
            assert resource.mimeType == "text/markdown"

    def test_get_resource_content_ods_connection_guide(self):
        """Test accessing ODS connection guide content."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/ods-connection-guide")

        assert isinstance(content, str)
        assert len(content) > 0
        assert "# ODS Connection Setup Guide" in content
        assert "connect_ods_server" in content
        assert "SSL" in content or "Certificate" in content

    def test_get_resource_content_ods_workflow_reference(self):
        """Test accessing ODS workflow reference content."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/ods-workflow-reference")

        assert isinstance(content, str)
        assert len(content) > 0
        assert "# Common ODS Workflows" in content
        assert "Workflow 1" in content or "Connect and Explore" in content

    def test_get_resource_content_ods_entity_hierarchy(self):
        """Test accessing ODS entity hierarchy content."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/ods-entity-hierarchy")

        assert isinstance(content, str)
        assert len(content) > 0
        assert "# ODS Entity Hierarchy" in content
        assert "AoTest" in content
        assert "AoMeasurement" in content

    def test_get_resource_content_query_execution_patterns(self):
        """Test accessing query execution patterns content."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/query-execution-patterns")

        assert isinstance(content, str)
        assert len(content) > 0
        assert "# Query Execution Patterns" in content
        assert "Pattern 1" in content or "Simple Data Fetch" in content

    def test_get_resource_content_query_operators_reference(self):
        """Test accessing query operators reference content."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/query-operators-reference")

        assert isinstance(content, str)
        assert len(content) > 0
        assert "# Jaquel Query Operators Reference" in content
        # Check for operator categories
        assert "Comparison Operators" in content
        assert "Logical Operators" in content
        assert "Aggregate Functions" in content
        assert "Special Keys" in content
        # Check for specific operators
        assert "$eq" in content
        assert "$and" in content
        assert "$count" in content
        assert "$rowlimit" in content

    def test_get_resource_content_jaquel_syntax_guide(self):
        """Test accessing Jaquel syntax guide content."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/jaquel-syntax-guide")

        assert isinstance(content, str)
        assert len(content) > 0
        assert "# Jaquel Syntax Guide" in content
        assert "Query Structure" in content
        assert "Query Examples" in content
        assert "Get All Instances" in content
        assert "Logical Operators" in content

    def test_get_resource_content_connection_troubleshooting(self):
        """Test accessing connection troubleshooting content."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/connection-troubleshooting")

        assert isinstance(content, str)
        assert len(content) > 0
        assert "# ODS Connection Troubleshooting" in content
        assert "Connection Refused" in content or "Issue 1" in content

    def test_get_resource_content_invalid_uri_returns_error_message(self):
        """Test that invalid URI returns error message."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/nonexistent")

        assert isinstance(content, str)
        assert "Unknown resource" in content

    def test_all_resources_have_content(self):
        """Test that all resources return non-empty content."""
        resources = ResourceLibrary.get_all_resources()

        for resource in resources:
            content = ResourceLibrary.get_resource_content(str(resource.uri))

            assert isinstance(content, str)
            assert len(content) > 0
            assert "Unknown resource" not in content

    def test_query_operators_reference_has_all_categories(self):
        """Test that operators resource includes all 4 operator categories."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/query-operators-reference")

        # Verify all 4 main categories are present
        assert "## Comparison Operators" in content
        assert "## Logical Operators" in content
        assert "## Aggregate Functions" in content
        assert "## Special Keys & Query Options" in content

    def test_query_operators_reference_has_comparison_operators(self):
        """Test that operators resource includes all comparison operators."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/query-operators-reference")

        comparison_ops = [
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
        ]

        for op in comparison_ops:
            assert op in content, f"Missing operator {op} in operators reference"

    def test_query_operators_reference_has_logical_operators(self):
        """Test that operators resource includes all logical operators."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/query-operators-reference")

        logical_ops = ["$and", "$or", "$not"]

        for op in logical_ops:
            assert op in content, f"Missing operator {op} in operators reference"

    def test_query_operators_reference_has_aggregate_functions(self):
        """Test that operators resource includes all aggregate functions."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/query-operators-reference")

        aggregate_funcs = [
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
        ]

        for func in aggregate_funcs:
            assert func in content, f"Missing aggregate function {func} in operators reference"

    def test_query_operators_reference_has_special_keys(self):
        """Test that operators resource includes all special keys."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/query-operators-reference")

        special_keys = [
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
        ]

        for key in special_keys:
            assert key in content, f"Missing special key {key} in operators reference"

    def test_query_operators_reference_has_examples(self):
        """Test that operators resource includes usage examples."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/query-operators-reference")

        # Check for example sections
        assert "Example" in content
        assert "```jaquel" in content or "```" in content

    def test_ods_connection_guide_has_credentials_section(self):
        """Test that connection guide covers credentials."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/ods-connection-guide")

        assert "credential" in content.lower() or "auth" in content.lower()

    def test_ods_workflow_reference_has_multiple_workflows(self):
        """Test that workflow reference covers multiple workflows."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/ods-workflow-reference")

        # Check for at least 3 workflows
        workflow_count = content.count("## Workflow")
        assert workflow_count >= 3

    def test_connection_troubleshooting_has_solutions(self):
        """Test that troubleshooting guide provides solutions."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/connection-troubleshooting")

        # Should have multiple issues and solutions
        assert "Issue" in content or "Problem" in content
        assert "Solution" in content or "solution" in content.lower()

    def test_entity_hierarchy_explains_relationships(self):
        """Test that entity hierarchy explains relationships."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/ods-entity-hierarchy")

        # Should explain relationships between entities
        assert "AoSubTest" in content
        assert "AoMeasurementQuantity" in content
        assert "->" in content or "└" in content or "Relationship" in content.lower()

    def test_query_patterns_has_performance_tips(self):
        """Test that query patterns resource includes performance tips."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/query-execution-patterns")

        assert "Performance" in content or "performance" in content.lower()
        assert "Tip" in content or "tip" in content.lower()

    def test_resource_content_is_markdown(self):
        """Test that all resource content is valid markdown format."""
        resources = ResourceLibrary.get_all_resources()

        for resource in resources:
            content = ResourceLibrary.get_resource_content(str(resource.uri))

            # All resources should have markdown headers
            assert "#" in content, f"Resource {resource.name} missing markdown headers"

    def test_resource_content_length(self):
        """Test that all resources have substantial content."""
        resources = ResourceLibrary.get_all_resources()

        for resource in resources:
            content = ResourceLibrary.get_resource_content(str(resource.uri))

            # Each resource should have at least 500 characters of content
            assert len(content) > 500, f"Resource {resource.name} has insufficient content ({len(content)} chars)"

    def test_jaquel_syntax_guide_has_basic_structure(self):
        """Test that Jaquel syntax guide explains basic query structure."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/jaquel-syntax-guide")

        assert "Basic Query Structure" in content
        assert "JSON" in content

    def test_jaquel_syntax_guide_has_examples(self):
        """Test that Jaquel syntax guide includes query examples."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/jaquel-syntax-guide")

        # Check for various example sections
        assert "Get All Instances" in content
        assert "Access by ID" in content
        assert "Get Children" in content
        assert "Search by Multiple Conditions" in content

    def test_jaquel_syntax_guide_covers_operators(self):
        """Test that Jaquel syntax guide covers all operator categories."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/jaquel-syntax-guide")

        assert "Comparison Operators" in content
        assert "Logical Operators" in content
        assert "Units and Aggregates" in content
        assert "$and" in content
        assert "$or" in content
        assert "$not" in content

    def test_jaquel_syntax_guide_explains_joins(self):
        """Test that Jaquel syntax guide explains joins."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/jaquel-syntax-guide")

        assert "Joins" in content
        assert "Outer Join" in content or "outer join" in content.lower()

    def test_jaquel_syntax_guide_covers_result_naming(self):
        """Test that Jaquel syntax guide covers result naming modes."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/jaquel-syntax-guide")

        assert "result_naming_mode" in content
        assert "query" in content.lower()
        assert "model" in content.lower()

    def test_jaquel_syntax_guide_includes_remarks(self):
        """Test that Jaquel syntax guide includes important remarks."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/jaquel-syntax-guide")

        assert "Remarks" in content or "Important" in content
        assert "Enum" in content or "enum" in content.lower()

    def test_jaquel_syntax_guide_covers_pagination(self):
        """Test that Jaquel syntax guide covers pagination options."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/jaquel-syntax-guide")

        assert "$rowlimit" in content
        assert "$rowskip" in content
        assert "$seqlimit" in content
        assert "$seqskip" in content
