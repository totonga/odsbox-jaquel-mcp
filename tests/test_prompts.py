"""Tests for the starting prompts feature."""

from __future__ import annotations

import pytest

from odsbox_jaquel_mcp.prompts import PromptLibrary


class TestPromptLibrary:
    """Test the PromptLibrary for starting prompts."""

    def test_get_all_prompts_returns_list(self):
        """Test that get_all_prompts returns a list of prompts."""
        prompts = PromptLibrary.get_all_prompts()
        assert isinstance(prompts, list)
        assert len(prompts) > 0

    def test_prompts_have_required_fields(self):
        """Test that all prompts have required fields."""
        prompts = PromptLibrary.get_all_prompts()
        for prompt in prompts:
            assert hasattr(prompt, "name")
            assert hasattr(prompt, "title")
            assert hasattr(prompt, "description")
            assert prompt.name
            assert prompt.title
            assert prompt.description

    def test_all_prompt_names_are_unique(self):
        """Test that all prompt names are unique."""
        prompts = PromptLibrary.get_all_prompts()
        names = [p.name for p in prompts]
        assert len(names) == len(set(names))

    def test_prompt_content_generation(self):
        """Test that prompt content can be generated for all prompts."""
        prompts = PromptLibrary.get_all_prompts()
        for prompt in prompts:
            content = PromptLibrary.get_prompt_content(prompt.name, {})
            assert isinstance(content, str)
            assert len(content) > 0
            assert prompt.title in content or "#" in content

    def test_validate_query_prompt(self):
        """Test the validate_query prompt."""
        content = PromptLibrary.get_prompt_content("validate_query", {})
        assert "validate_query" in content
        assert "syntax" in content.lower()

    def test_explore_patterns_prompt(self):
        """Test the explore_patterns prompt."""
        content = PromptLibrary.get_prompt_content("explore_patterns", {})
        assert "get_all_instances" in content
        assert "get_by_id" in content

    def test_setup_ods_connection_prompt(self):
        """Test the setup_ods_connection prompt."""
        content = PromptLibrary.get_prompt_content("setup_ods_connection", {})
        assert "connect_ods_server" in content
        assert "connection" in content.lower()

    def test_bulk_data_access_prompt(self):
        """Test the bulk_data_access prompt."""
        content = PromptLibrary.get_prompt_content("bulk_data_access", {})
        assert "3-step" in content or "Bulk API" in content
        assert "read_submatrix_data" in content

    def test_analyze_measurements_prompt(self):
        """Test the analyze_measurements prompt."""
        content = PromptLibrary.get_prompt_content("analyze_measurements", {})
        assert "compare_measurements" in content or "measurement" in content.lower()

    def test_prompt_content_with_arguments(self):
        """Test that prompt content respects arguments."""
        args = {"query_example": '{"TestEntity": {}}'}
        content = PromptLibrary.get_prompt_content("validate_query", args)
        assert '{"TestEntity": {}}' in content

    def test_unknown_prompt_name(self):
        """Test that unknown prompt names return error content."""
        content = PromptLibrary.get_prompt_content("unknown_prompt", {})
        assert "not found" in content.lower() or "unknown" in content.lower()

    def test_prompt_descriptions_are_informative(self):
        """Test that prompt descriptions are helpful."""
        prompts = PromptLibrary.get_all_prompts()
        for prompt in prompts:
            assert len(prompt.description) > 20  # Minimum length
            assert "." in prompt.description or ":" in prompt.description


class TestPromptIntegration:
    """Test the integration of prompts with the MCP server."""

    def test_import_server_with_prompts(self):
        """Test that the server can be imported with prompts."""
        from odsbox_jaquel_mcp import server

        assert hasattr(server, "server")

    def test_list_prompts_returns_prompts(self):
        """Test that list_prompts is available."""
        from odsbox_jaquel_mcp.server import list_prompts

        assert callable(list_prompts)

    def test_get_prompt_handler_exists(self):
        """Test that get_prompt handler is available."""
        from odsbox_jaquel_mcp.server import get_prompt

        assert callable(get_prompt)

    @pytest.mark.asyncio
    async def test_server_capabilities_include_prompts(self):
        """Test that server capabilities include prompts."""
        from odsbox_jaquel_mcp.server import server

        # The server should have prompts capability
        assert hasattr(server, "list_prompts")
        assert hasattr(server, "get_prompt")
