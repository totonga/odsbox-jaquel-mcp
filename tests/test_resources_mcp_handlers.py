"""Tests for MCP resource handler integration."""

import pytest
from mcp.types import Resource, TextContent

from odsbox_jaquel_mcp.server import list_resources, read_resource


class TestResourceHandlers:
    """Test cases for MCP resource handlers."""

    @pytest.mark.asyncio
    async def test_list_resources_returns_resource_list(self):
        """Test that list_resources handler returns list of Resource objects."""
        resources = await list_resources()

        assert isinstance(resources, list)
        assert len(resources) == 7

        for resource in resources:
            assert isinstance(resource, Resource)
            assert hasattr(resource, "uri")
            assert hasattr(resource, "name")
            assert hasattr(resource, "description")
            assert hasattr(resource, "mimeType")

    @pytest.mark.asyncio
    async def test_list_resources_all_have_valid_uris(self):
        """Test that all resources have valid file:///odsbox/ URIs."""
        resources = await list_resources()

        valid_uris = {
            "file:///odsbox/ods-connection-guide",
            "file:///odsbox/ods-workflow-reference",
            "file:///odsbox/ods-entity-hierarchy",
            "file:///odsbox/query-execution-patterns",
            "file:///odsbox/query-operators-reference",
            "file:///odsbox/jaquel-syntax-guide",
            "file:///odsbox/connection-troubleshooting",
        }

        resource_uris = {str(resource.uri) for resource in resources}
        assert resource_uris == valid_uris

    @pytest.mark.asyncio
    async def test_read_resource_returns_text_content(self):
        """Test that read_resource handler returns TextContent object."""
        content = await read_resource("file:///odsbox/ods-connection-guide")

        assert isinstance(content, TextContent)
        assert hasattr(content, "type")
        assert hasattr(content, "text")
        assert content.type == "text"

    @pytest.mark.asyncio
    async def test_read_resource_content_is_not_empty(self):
        """Test that read_resource returns non-empty content."""
        content = await read_resource("file:///odsbox/ods-connection-guide")

        assert isinstance(content.text, str)
        assert len(content.text) > 0

    @pytest.mark.asyncio
    async def test_read_resource_ods_connection_guide(self):
        """Test reading ODS connection guide resource."""
        content = await read_resource("file:///odsbox/ods-connection-guide")

        assert content.type == "text"
        assert "ODS Connection" in content.text
        assert "Prerequisites" in content.text

    @pytest.mark.asyncio
    async def test_read_resource_ods_workflow_reference(self):
        """Test reading ODS workflow reference resource."""
        content = await read_resource("file:///odsbox/ods-workflow-reference")

        assert content.type == "text"
        assert "Workflow" in content.text or "workflow" in content.text.lower()

    @pytest.mark.asyncio
    async def test_read_resource_ods_entity_hierarchy(self):
        """Test reading ODS entity hierarchy resource."""
        content = await read_resource("file:///odsbox/ods-entity-hierarchy")

        assert content.type == "text"
        assert "Entity" in content.text or "entity" in content.text.lower()
        assert "AoTest" in content.text

    @pytest.mark.asyncio
    async def test_read_resource_query_execution_patterns(self):
        """Test reading query execution patterns resource."""
        content = await read_resource("file:///odsbox/query-execution-patterns")

        assert content.type == "text"
        assert "Pattern" in content.text or "pattern" in content.text.lower()

    @pytest.mark.asyncio
    async def test_read_resource_query_operators_reference(self):
        """Test reading query operators reference resource."""
        content = await read_resource("file:///odsbox/query-operators-reference")

        assert content.type == "text"
        assert "Operator" in content.text or "operator" in content.text.lower()
        assert "$eq" in content.text

    @pytest.mark.asyncio
    async def test_read_resource_jaquel_syntax_guide(self):
        """Test reading Jaquel syntax guide resource."""
        content = await read_resource("file:///odsbox/jaquel-syntax-guide")

        assert content.type == "text"
        assert "Jaquel" in content.text
        assert "query" in content.text.lower()

    @pytest.mark.asyncio
    async def test_read_resource_connection_troubleshooting(self):
        """Test reading connection troubleshooting resource."""
        content = await read_resource("file:///odsbox/connection-troubleshooting")

        assert content.type == "text"
        assert "Troubleshoot" in content.text or "Issue" in content.text

    @pytest.mark.asyncio
    async def test_read_resource_invalid_uri_returns_error_message(self):
        """Test that invalid URI returns error message in text content."""
        content = await read_resource("file:///odsbox/nonexistent-resource")

        assert isinstance(content, TextContent)
        assert content.type == "text"
        assert "Unknown resource" in content.text

    @pytest.mark.asyncio
    async def test_read_resource_all_resources_accessible(self):
        """Test that all listed resources are accessible via read_resource."""
        resources = await list_resources()

        for resource in resources:
            content = await read_resource(str(resource.uri))

            assert isinstance(content, TextContent)
            assert content.type == "text"
            assert len(content.text) > 0
            # Should not be error message
            assert "Unknown resource" not in content.text

    @pytest.mark.asyncio
    async def test_read_resource_content_is_markdown(self):
        """Test that resource content is valid markdown."""
        resources = await list_resources()

        for resource in resources:
            content = await read_resource(str(resource.uri))

            # Markdown should have headers
            assert "#" in content.text, f"No markdown headers in {resource.name}"

    @pytest.mark.asyncio
    async def test_read_resource_content_size_is_reasonable(self):
        """Test that resource content has substantial size."""
        resources = await list_resources()

        for resource in resources:
            content = await read_resource(str(resource.uri))

            # Each resource should have at least some content (not just error message)
            assert len(content.text) > 100, f"Resource {resource.name} too small"

    @pytest.mark.asyncio
    async def test_read_resource_text_field_not_none(self):
        """Test that text field is never None."""
        resources = await list_resources()

        for resource in resources:
            content = await read_resource(str(resource.uri))

            assert content.text is not None
            assert isinstance(content.text, str)

    @pytest.mark.asyncio
    async def test_read_resource_type_always_text(self):
        """Test that type field is always 'text' for resource content."""
        resources = await list_resources()

        for resource in resources:
            content = await read_resource(str(resource.uri))

            assert content.type == "text"

    @pytest.mark.asyncio
    async def test_list_resources_multiple_calls_consistent(self):
        """Test that multiple calls to list_resources return same resources."""
        resources1 = await list_resources()
        resources2 = await list_resources()

        assert len(resources1) == len(resources2)

        uris1 = {str(r.uri) for r in resources1}
        uris2 = {str(r.uri) for r in resources2}

        assert uris1 == uris2

    @pytest.mark.asyncio
    async def test_read_resource_same_uri_returns_same_content(self):
        """Test that reading same resource multiple times returns same content."""
        uri = "file:///odsbox/ods-connection-guide"

        content1 = await read_resource(uri)
        content2 = await read_resource(uri)

        assert content1.text == content2.text
        assert content1.type == content2.type

    @pytest.mark.asyncio
    async def test_read_resource_case_sensitive_uri(self):
        """Test that URI matching is case-sensitive."""
        # Correct URI
        content_correct = await read_resource("file:///odsbox/ods-connection-guide")
        assert "Unknown resource" not in content_correct.text

        # Different case - should fail
        content_wrong_case = await read_resource("file:///odsbox/ODS-Connection-Guide")
        assert "Unknown resource" in content_wrong_case.text

    @pytest.mark.asyncio
    async def test_list_resources_count_matches_implementation(self):
        """Test that list_resources returns expected number of resources."""
        resources = await list_resources()

        # Should have exactly 7 resources
        assert len(resources) == 7

        # All should have names
        names = [r.name for r in resources]
        assert len(names) == 7
        assert len(set(names)) == 7  # All unique

    @pytest.mark.asyncio
    async def test_read_resource_ods_connection_guide_has_credentials_info(self):
        """Test that connection guide covers credentials."""
        content = await read_resource("file:///odsbox/ods-connection-guide")

        # Should mention credentials/auth
        lower_text = content.text.lower()
        assert "credential" in lower_text or "password" in lower_text or "auth" in lower_text

    @pytest.mark.asyncio
    async def test_read_resource_query_operators_has_all_operators(self):
        """Test that operators reference includes all operator categories."""
        content = await read_resource("file:///odsbox/query-operators-reference")

        # Should mention all operator categories
        assert "Comparison" in content.text
        assert "Logical" in content.text
        assert "Aggregate" in content.text

    @pytest.mark.asyncio
    async def test_read_resource_jaquel_syntax_has_examples(self):
        """Test that Jaquel syntax guide includes query examples."""
        content = await read_resource("file:///odsbox/jaquel-syntax-guide")

        # Should have example code
        assert "```" in content.text or "example" in content.text.lower()
