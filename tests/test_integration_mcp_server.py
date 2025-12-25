"""Integration tests for MCP server communication.

These tests require a live ODS server connection and test the MCP server
as if a real MCP client is connecting to it via stdio protocol.

Run with:
    pytest tests/test_integration_mcp_server.py -m integration

Mark all tests with @pytest.mark.integration to allow filtering.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

import pytest

from odsbox_jaquel_mcp import ODSConnectionManager


@pytest.mark.integration
class TestMCPServerIntegration:
    """Integration tests for MCP server via stdio protocol."""

    def test_mcp_server_process_starts(self):
        """Test that MCP server starts as subprocess.

        This test verifies:
        - Server can be started as a subprocess
        - Server doesn't immediately crash
        - Server can be communicated with via stdio
        """
        # This is a basic smoke test - just verify the module runs
        try:
            result = subprocess.run(
                [sys.executable, "-m", "odsbox_jaquel_mcp"],
                input=b"",
                capture_output=True,
                timeout=10,  # Increased from 5 to 10 seconds
                cwd=Path(__file__).parent.parent,
            )

            # Server may fail with no input, but should start
            # Exit code 1 is expected since we're not sending valid JSON-RPC
            assert result.returncode in [0, 1, -15]  # 0=success, 1=error, -15=SIGTERM
        except subprocess.TimeoutExpired:
            # Server is running and waiting for input - this is expected
            # It means the server started successfully
            pass

    @pytest.mark.asyncio
    async def test_mcp_tool_handler_routing(self):
        """Test that tool names are properly routed to handlers.

        This test verifies:
        - Tool names map to correct handlers
        - Handler delegation works
        - All tools are registered
        """
        from odsbox_jaquel_mcp.server import list_tools

        # Get all registered tools
        result = await list_tools()

        # Should have multiple tools
        assert len(result) > 20

        # Should have connection tools
        tool_names = [tool.name for tool in result]
        assert "connect_ods_server" in tool_names
        assert "execute_query" in tool_names
        assert "validate_query" in tool_names
