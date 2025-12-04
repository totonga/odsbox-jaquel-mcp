"""Tests for MCP resource handler integration."""

import pytest
from mcp.types import Resource

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
    async def test_read_resource_returns_list(self):
        """Test that read_resource handler returns a list of resource content items."""
        result = await read_resource("file:///odsbox/ods-connection-guide")

        assert isinstance(result, list)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_read_resource_item_has_correct_attributes(self):
        """Test that resource content items have .content and .mime_type attributes."""
        result = await read_resource("file:///odsbox/ods-connection-guide")

        assert len(result) > 0
        content_item = result[0]
        assert hasattr(content_item, "content")
        assert hasattr(content_item, "mime_type")

    @pytest.mark.asyncio
    async def test_read_resource_content_is_not_empty(self):
        """Test that read_resource returns non-empty content."""
        result = await read_resource("file:///odsbox/ods-connection-guide")

        assert len(result) > 0
        content_item = result[0]
        assert isinstance(content_item.content, str)
        assert len(content_item.content) > 0

    @pytest.mark.asyncio
    async def test_read_resource_ods_connection_guide(self):
        """Test reading ODS connection guide resource."""
        result = await read_resource("file:///odsbox/ods-connection-guide")

        content = result[0].content
        assert "ODS Connection" in content
        assert "Prerequisites" in content

    @pytest.mark.asyncio
    async def test_read_resource_ods_workflow_reference(self):
        """Test reading ODS workflow reference resource."""
        result = await read_resource("file:///odsbox/ods-workflow-reference")

        content = result[0].content
        assert "Workflow" in content or "workflow" in content.lower()

    @pytest.mark.asyncio
    async def test_read_resource_ods_entity_hierarchy(self):
        """Test reading ODS entity hierarchy resource."""
        result = await read_resource("file:///odsbox/ods-entity-hierarchy")

        content = result[0].content
        assert "Entity" in content or "entity" in content.lower()
        assert "AoTest" in content

    @pytest.mark.asyncio
    async def test_read_resource_query_execution_patterns(self):
        """Test reading query execution patterns resource."""
        result = await read_resource("file:///odsbox/query-execution-patterns")

        content = result[0].content
        assert "Pattern" in content or "pattern" in content.lower()

    @pytest.mark.asyncio
    async def test_read_resource_query_operators_reference(self):
        """Test reading query operators reference resource."""
        result = await read_resource("file:///odsbox/query-operators-reference")

        content = result[0].content
        assert "Operator" in content or "operator" in content.lower()
        assert "$eq" in content

    @pytest.mark.asyncio
    async def test_read_resource_jaquel_syntax_guide(self):
        """Test reading Jaquel syntax guide resource."""
        result = await read_resource("file:///odsbox/jaquel-syntax-guide")

        content = result[0].content
        assert "Jaquel" in content
        assert "query" in content.lower()

    @pytest.mark.asyncio
    async def test_read_resource_connection_troubleshooting(self):
        """Test reading connection troubleshooting resource."""
        result = await read_resource("file:///odsbox/connection-troubleshooting")

        content = result[0].content
        assert "Troubleshoot" in content or "Issue" in content

    @pytest.mark.asyncio
    async def test_read_resource_invalid_uri_returns_error_message(self):
        """Test that invalid URI returns error message in text content."""
        result = await read_resource("file:///odsbox/nonexistent-resource")

        assert isinstance(result, list)
        assert len(result) > 0
        assert "Unknown resource" in result[0].content

    @pytest.mark.asyncio
    async def test_read_resource_all_resources_accessible(self):
        """Test that all listed resources are accessible via read_resource."""
        resources = await list_resources()

        for resource in resources:
            result = await read_resource(str(resource.uri))

            assert isinstance(result, list)
            assert len(result) > 0
            assert len(result[0].content) > 0
            # Should not be error message
            assert "Unknown resource" not in result[0].content

    @pytest.mark.asyncio
    async def test_read_resource_content_is_markdown(self):
        """Test that resource content is valid markdown."""
        resources = await list_resources()

        for resource in resources:
            result = await read_resource(str(resource.uri))

            content = result[0].content
            # Markdown should have headers
            assert "#" in content, f"No markdown headers in {resource.name}"

    @pytest.mark.asyncio
    async def test_read_resource_content_size_is_reasonable(self):
        """Test that resource content has substantial size."""
        resources = await list_resources()

        for resource in resources:
            result = await read_resource(str(resource.uri))

            content = result[0].content
            # Each resource should have at least some content (not just error message)
            assert len(content) > 100, f"Resource {resource.name} too small"

    @pytest.mark.asyncio
    async def test_read_resource_content_field_not_none(self):
        """Test that content field is never None."""
        resources = await list_resources()

        for resource in resources:
            result = await read_resource(str(resource.uri))

            content_item = result[0]
            assert content_item.content is not None
            assert isinstance(content_item.content, str)

    @pytest.mark.asyncio
    async def test_read_resource_mime_type_always_markdown(self):
        """Test that mime_type field is always 'text/markdown' for resource content."""
        resources = await list_resources()

        for resource in resources:
            result = await read_resource(str(resource.uri))

            content_item = result[0]
            assert content_item.mime_type == "text/markdown"

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

        result1 = await read_resource(uri)
        result2 = await read_resource(uri)

        assert result1[0].content == result2[0].content
        assert result1[0].mime_type == result2[0].mime_type

    @pytest.mark.asyncio
    async def test_read_resource_case_sensitive_uri(self):
        """Test that URI matching is case-sensitive."""
        # Correct URI
        result_correct = await read_resource("file:///odsbox/ods-connection-guide")
        assert "Unknown resource" not in result_correct[0].content

        # Different case - should fail
        result_wrong_case = await read_resource("file:///odsbox/ODS-Connection-Guide")
        assert "Unknown resource" in result_wrong_case[0].content

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
        result = await read_resource("file:///odsbox/ods-connection-guide")

        content = result[0].content
        # Should mention credentials/auth
        lower_text = content.lower()
        assert "credential" in lower_text or "password" in lower_text or "auth" in lower_text

    @pytest.mark.asyncio
    async def test_read_resource_query_operators_has_all_operators(self):
        """Test that operators reference includes all operator categories."""
        result = await read_resource("file:///odsbox/query-operators-reference")

        content = result[0].content
        # Should mention all operator categories
        assert "Comparison" in content
        assert "Logical" in content
        assert "Aggregate" in content

    @pytest.mark.asyncio
    async def test_read_resource_jaquel_syntax_has_examples(self):
        """Test that Jaquel syntax guide includes query examples."""
        result = await read_resource("file:///odsbox/jaquel-syntax-guide")

        content = result[0].content
        # Should have example code
        assert "```" in content or "example" in content.lower()
