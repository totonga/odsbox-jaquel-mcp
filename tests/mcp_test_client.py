"""MCP Server Test Client for integration testing.

This module provides a test client to communicate with the MCP server
via the stdio protocol, allowing end-to-end testing of MCP functionality.

Usage:
    client = MCPServerTestClient()
    await client.start()
    result = await client.call_tool("validate_query", {"query": {...}})
    await client.stop()
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


class MCPServerTestClient:
    """Test client for communicating with MCP server via stdio."""

    def __init__(self, timeout: float = 30.0):
        """Initialize MCP test client.

        Args:
            timeout: Timeout for server communication
        """
        self.timeout = timeout
        self.session = None
        self._context_managers = []

    async def start(self) -> None:
        """Start MCP server and establish connection."""
        # Get path to MCP server module - use -m to ensure proper package context
        mcp_module = Path(__file__).parent.parent

        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "odsbox_jaquel_mcp"],
            cwd=str(mcp_module),
        )

        try:
            # Connect to server via stdio protocol
            client_context = stdio_client(server_params)
            read_stream, write_stream = await client_context.__aenter__()
            self._context_managers.append(client_context)

            # Create MCP client session and initialize
            session_context = ClientSession(read_stream, write_stream)
            self.session = await session_context.__aenter__()
            self._context_managers.append(session_context)

            # Initialize protocol
            await self.session.initialize()

            print(f"✓ Connected to MCP server")

        except Exception as e:
            # Clean up on failure
            await self.stop()
            raise RuntimeError(f"Failed to start MCP server: {e}") from e

    async def stop(self) -> None:
        """Stop MCP server and close connection."""
        # Clean up in reverse order
        for ctx in reversed(self._context_managers):
            try:
                await ctx.__aexit__(None, None, None)
            except Exception as e:
                print(f"Error closing connection: {e}")
        self._context_managers.clear()
        self.session = None

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result as dict
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server. Call start() first.")

        try:
            # Call tool via session
            result = await asyncio.wait_for(
                self.session.call_tool(tool_name, arguments),
                timeout=self.timeout,
            )

            # Convert CallResult to dict with content
            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": c.text if hasattr(c, "text") else str(c),
                        }
                        for c in result.content
                    ],
                    "isError": result.isError if hasattr(result, "isError") else False,
                }
            }
        except asyncio.TimeoutError:
            raise TimeoutError(f"Tool call '{tool_name}' timed out after {self.timeout}s")

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all available tools on the server.

        Returns:
            List of tool definitions as dicts
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server. Call start() first.")

        try:
            result = await asyncio.wait_for(
                self.session.list_tools(),
                timeout=self.timeout,
            )

            # Convert Tool objects to dicts
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema if hasattr(tool, "inputSchema") else {},
                }
                for tool in result.tools
            ]
        except asyncio.TimeoutError:
            raise TimeoutError(f"List tools timed out after {self.timeout}s")

    async def list_resources(self) -> list[dict[str, Any]]:
        """List all available resources on the server.

        Returns:
            List of resource definitions as dicts
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server. Call start() first.")

        try:
            result = await asyncio.wait_for(
                self.session.list_resources(),
                timeout=self.timeout,
            )

            # Convert Resource objects to dicts
            return [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description if hasattr(resource, "description") else "",
                }
                for resource in result.resources
            ]
        except asyncio.TimeoutError:
            raise TimeoutError(f"List resources timed out after {self.timeout}s")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


# Example usage
async def example():
    """Example of using the test client."""
    async with MCPServerTestClient() as client:
        # List tools
        tools = await client.list_tools()
        print(f"\nAvailable tools: {len(tools)}")
        for tool in tools[:5]:
            print(f"  - {tool.get('name')}: {tool.get('description')}")

        # Call a tool
        result = await client.call_tool("validate_query", {"query": {"TestEntity": {}}})
        print(f"\nValidation result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(example())
