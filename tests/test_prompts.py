"""Tests for the starting prompts feature."""

from __future__ import annotations

from odsbox_jaquel_mcp.prompts import PromptLibrary

# Known prompt names for testing
_PROMPT_NAMES = [
    "query_validate",
    "explore_patterns",
    "connect_ods_server",
    "timeseries_access",
]


class TestPromptLibrary:
    """Test the PromptLibrary for starting prompts."""

    def test_prompt_content_generation(self):
        """Test that prompt content can be generated for all prompts."""
        for name in _PROMPT_NAMES:
            content = PromptLibrary.get_prompt_content(name, {})
            assert isinstance(content, str)
            assert len(content) > 0
            assert "#" in content

    def test_query_validate_prompt(self):
        """Test the query_validate prompt."""
        content = PromptLibrary.get_prompt_content("query_validate", {})
        assert "query_validate" in content
        assert "syntax" in content.lower()

    def test_explore_patterns_prompt(self):
        """Test the explore_patterns prompt."""
        content = PromptLibrary.get_prompt_content("explore_patterns", {})
        assert "get_all_instances" in content
        assert "get_by_id" in content

    def test_connect_ods_server_prompt(self):
        """Test the connect_ods_server prompt."""
        content = PromptLibrary.get_prompt_content("connect_ods_server", {})
        assert "ods_connect" in content
        assert "connection" in content.lower()

    def test_timeseries_access_prompt(self):
        """Test the timeseries_access prompt."""
        content = PromptLibrary.get_prompt_content("timeseries_access", {})
        assert "3-step" in content or "Bulk API" in content
        assert "data_read_submatrix" in content

    def test_prompt_content_with_arguments(self):
        """Test that prompt content respects arguments."""
        args = {"query_example": '{"TestEntity": {}}'}
        content = PromptLibrary.get_prompt_content("query_validate", args)
        assert '{"TestEntity": {}}' in content

    def test_unknown_prompt_name(self):
        """Test that unknown prompt names return error content."""
        content = PromptLibrary.get_prompt_content("unknown_prompt", {})
        assert "not found" in content.lower() or "unknown" in content.lower()


class TestPromptIntegration:
    """Test the integration of prompts with the MCP server."""

    def test_import_server_with_prompts(self):
        """Test that the server can be imported with prompts."""
        from odsbox_jaquel_mcp import server

        assert hasattr(server, "mcp")

    def test_prompt_functions_exist(self):
        """Test that prompt functions are available in server."""
        from odsbox_jaquel_mcp.server import (
            connect_ods_server,
            explore_patterns,
            prompt_query_validate,
            timeseries_access,
        )

        assert callable(prompt_query_validate)
        assert callable(explore_patterns)
        assert callable(connect_ods_server)
        assert callable(timeseries_access)
