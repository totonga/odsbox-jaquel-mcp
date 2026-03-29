"""Tests for MCP resource handler integration."""

from odsbox_jaquel_mcp.resources import ResourceLibrary
from odsbox_jaquel_mcp.server import (
    resource_connection_troubleshooting,
    resource_jaquel_syntax_guide,
    resource_ods_connection_guide,
    resource_ods_entity_hierarchy,
    resource_ods_workflow_reference,
    resource_query_execution_patterns,
    resource_query_operators_reference,
)

# Map of URI -> resource function for iteration
_RESOURCE_FUNCTIONS = {
    "file:///odsbox/ods-connection-guide": resource_ods_connection_guide,
    "file:///odsbox/ods-workflow-reference": resource_ods_workflow_reference,
    "file:///odsbox/ods-entity-hierarchy": resource_ods_entity_hierarchy,
    "file:///odsbox/query-execution-patterns": resource_query_execution_patterns,
    "file:///odsbox/query-operators-reference": resource_query_operators_reference,
    "file:///odsbox/jaquel-syntax-guide": resource_jaquel_syntax_guide,
    "file:///odsbox/connection-troubleshooting": resource_connection_troubleshooting,
}


class TestResourceHandlers:
    """Test cases for MCP resource handlers."""

    def test_resource_count(self):
        """Test that we have exactly 7 static resource functions."""
        assert len(_RESOURCE_FUNCTIONS) == 7

    def test_read_resource_content_is_not_empty(self):
        """Test that each resource function returns non-empty content."""
        for uri, fn in _RESOURCE_FUNCTIONS.items():
            content = fn()
            assert isinstance(content, str), f"Resource {uri} did not return str"
            assert len(content) > 0, f"Resource {uri} is empty"

    def test_read_resource_ods_connection_guide(self):
        """Test reading ODS connection guide resource."""
        content = resource_ods_connection_guide()
        assert "ODS Connection" in content
        assert "Prerequisites" in content

    def test_read_resource_ods_workflow_reference(self):
        """Test reading ODS workflow reference resource."""
        content = resource_ods_workflow_reference()
        assert "Workflow" in content or "workflow" in content.lower()

    def test_read_resource_ods_entity_hierarchy(self):
        """Test reading ODS entity hierarchy resource."""
        content = resource_ods_entity_hierarchy()
        assert "Entity" in content or "entity" in content.lower()
        assert "AoTest" in content

    def test_read_resource_query_execution_patterns(self):
        """Test reading query execution patterns resource."""
        content = resource_query_execution_patterns()
        assert "Pattern" in content or "pattern" in content.lower()

    def test_read_resource_query_operators_reference(self):
        """Test reading query operators reference resource."""
        content = resource_query_operators_reference()
        assert "Operator" in content or "operator" in content.lower()
        assert "$eq" in content

    def test_read_resource_jaquel_syntax_guide(self):
        """Test reading Jaquel syntax guide resource."""
        content = resource_jaquel_syntax_guide()
        assert "Jaquel" in content
        assert "query" in content.lower()

    def test_read_resource_connection_troubleshooting(self):
        """Test reading connection troubleshooting resource."""
        content = resource_connection_troubleshooting()
        assert "Troubleshoot" in content or "Issue" in content

    def test_read_resource_invalid_uri_returns_error_message(self):
        """Test that invalid URI returns error message in text content."""
        content = ResourceLibrary.get_resource_content("file:///odsbox/nonexistent-resource")
        assert "Unknown resource" in content

    def test_read_resource_all_resources_accessible(self):
        """Test that all resource functions return accessible content."""
        for uri, fn in _RESOURCE_FUNCTIONS.items():
            content = fn()
            assert len(content) > 0
            assert "Unknown resource" not in content

    def test_read_resource_content_is_markdown(self):
        """Test that resource content is valid markdown."""
        for uri, fn in _RESOURCE_FUNCTIONS.items():
            content = fn()
            assert "#" in content, f"No markdown headers in resource for {uri}"

    def test_read_resource_content_size_is_reasonable(self):
        """Test that resource content has substantial size."""
        for uri, fn in _RESOURCE_FUNCTIONS.items():
            content = fn()
            assert len(content) > 100, f"Resource for {uri} too small"

    def test_read_resource_same_uri_returns_same_content(self):
        """Test that reading same resource multiple times returns same content."""
        content1 = resource_ods_connection_guide()
        content2 = resource_ods_connection_guide()
        assert content1 == content2

    def test_read_resource_case_sensitive_uri(self):
        """Test that URI matching is case-sensitive."""
        # Correct URI
        content_correct = ResourceLibrary.get_resource_content("file:///odsbox/ods-connection-guide")
        assert "Unknown resource" not in content_correct

        # Different case - should fail
        content_wrong_case = ResourceLibrary.get_resource_content("file:///odsbox/ODS-Connection-Guide")
        assert "Unknown resource" in content_wrong_case

    def test_read_resource_ods_connection_guide_has_credentials_info(self):
        """Test that connection guide covers credentials."""
        content = resource_ods_connection_guide()
        lower_text = content.lower()
        assert "credential" in lower_text or "password" in lower_text or "auth" in lower_text

    def test_read_resource_query_operators_has_all_operators(self):
        """Test that operators reference includes all operator categories."""
        content = resource_query_operators_reference()
        assert "Comparison" in content
        assert "Logical" in content
        assert "Aggregate" in content

    def test_read_resource_jaquel_syntax_has_examples(self):
        """Test that Jaquel syntax guide includes query examples."""
        content = resource_jaquel_syntax_guide()
        assert "```" in content or "example" in content.lower()
