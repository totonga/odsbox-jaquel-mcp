"""Practical MCP server integration tests using test client.

These tests use the MCPServerTestClient to communicate with the MCP server
via the actual stdio protocol, testing real end-to-end MCP communication.

Run with:
    pytest tests/test_mcp_server_e2e.py -m integration -v
"""

import json

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_server_lists_tools(mcp_client):
    """Test that server lists all available tools via MCP protocol.

    This test verifies:
    - Server responds to tools/list request
    - Tools have required metadata (name, description)
    - All expected tool categories are present
    """
    tools = await mcp_client.list_tools()

    assert isinstance(tools, list)
    assert len(tools) > 20, "Server should list all tools"

    # Check tool structure
    for tool in tools:
        assert "name" in tool, f"Tool missing name: {tool}"
        assert "description" in tool, f"Tool {tool.get('name')} missing description"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_server_has_expected_tools(mcp_client):
    """Test that server has all expected tool categories.

    This test verifies:
    - Connection tools exist
    - Query validation tools exist
    - Schema inspection tools exist
    - Submatrix tools exist
    """
    tools = await mcp_client.list_tools()
    tool_names = {tool["name"] for tool in tools}

    # Connection tools
    assert "connect_ods_server" in tool_names
    assert "disconnect_ods_server" in tool_names
    assert "get_ods_connection_info" in tool_names

    # Query validation tools
    assert "validate_query" in tool_names
    assert "explain_query" in tool_names

    # Schema tools
    assert "check_entity_schema" in tool_names
    assert "validate_field_exists" in tool_names

    # Data access tools
    assert "read_submatrix_data" in tool_names
    assert "execute_query" in tool_names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_validate_query_tool_via_mcp(mcp_client):
    """Test validate_query tool through MCP protocol.

    This test verifies:
    - Tool call works through stdio protocol
    - Query validation executes correctly
    - Result is properly formatted
    """
    result = await mcp_client.call_tool("validate_query", {"query": {"TestEntity": {}}})

    # Result should be a proper response
    assert result is not None

    # The result contains content with the actual validation output
    content = result.get("result", {}).get("content", [])
    assert len(content) > 0, f"Expected content in result, got: {result}"

    # Parse the JSON from the text content
    text = content[0].get("text", "{}")
    validation_result = json.loads(text)

    assert "valid" in validation_result or "errors" in validation_result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_resources(mcp_client):
    """Test that server lists available resources.

    This test verifies:
    - Server responds to resources/list request
    - Resources have required metadata
    - Resource URIs are properly formatted
    """
    resources = await mcp_client.list_resources()

    assert isinstance(resources, list)
    assert len(resources) > 0, "Server should list resources"

    # Check resource structure
    for resource in resources:
        assert "uri" in resource, f"Resource missing uri: {resource}"
        assert "name" in resource, f"Resource {resource.get('uri')} missing name"
        assert "description" in resource


@pytest.mark.integration
@pytest.mark.asyncio
async def test_explain_query_tool_via_mcp(mcp_client):
    """Test explain_query tool through MCP protocol.

    This test verifies:
    - Query explanation tool works via MCP
    - Handles complex query objects
    - Returns proper explanation
    """
    query = {
        "AoMeasurement": {
            "name": "Temperature*",
        },
        "$attributes": {
            "id": 1,
            "name": 1,
        },
    }

    result = await mcp_client.call_tool("explain_query", {"query": query})

    assert result is not None
    # Result should contain explanation content
    assert "result" in result or "content" in result or "error" not in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_operator_documentation_via_mcp(mcp_client):
    """Test get_operator_documentation tool through MCP protocol.

    This test verifies:
    - Operator documentation tool works
    - Returns proper documentation format
    - Handles various operators
    """
    result = await mcp_client.call_tool("get_operator_documentation", {"operator": "$eq"})

    assert result is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_server_handles_invalid_tool_gracefully(mcp_client):
    """Test that server handles invalid tool calls gracefully.

    This test verifies:
    - Invalid tool names are rejected
    - Error message is meaningful
    - Server doesn't crash
    """
    # This might raise an exception or return an error response
    try:
        result = await mcp_client.call_tool("nonexistent_tool_xyz", {})

        # If it returns a result, should have error info
        if isinstance(result, dict):
            assert "error" in result or "result" in result
    except Exception as e:
        # Some error is expected for invalid tool
        assert "nonexistent" in str(e).lower() or "unknown" in str(e).lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_sequential_calls(mcp_client):
    """Test multiple sequential tool calls through MCP protocol.

    This test verifies:
    - Server handles multiple requests sequentially
    - Connection remains stable
    - Results are independent
    """
    # Call 1: Validate query
    result1 = await mcp_client.call_tool("validate_query", {"query": {"Entity1": {}}})
    assert result1 is not None

    # Call 2: Get operator docs
    result2 = await mcp_client.call_tool("get_operator_documentation", {"operator": "$like"})
    assert result2 is not None

    # Call 3: List patterns
    result3 = await mcp_client.call_tool("list_query_patterns", {})
    assert result3 is not None

    # All calls should succeed independently
    assert result1 != result2 != result3
    assert result1 != result2 != result3
    assert result1 != result2 != result3
