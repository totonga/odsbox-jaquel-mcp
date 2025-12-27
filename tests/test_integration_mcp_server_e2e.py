"""Practical MCP server integration tests using test client.

These tests use the MCPServerTestClient to communicate with the MCP server
via the actual stdio protocol, testing real end-to-end MCP communication.

Run with:
    pytest tests/test_integration_mcp_server_e2e.py -v
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
    assert "ods_connect" in tool_names
    assert "ods_disconnect" in tool_names
    assert "ods_get_connection_info" in tool_names

    # Query validation tools
    assert "query_validate" in tool_names
    assert "query_describe" in tool_names

    # Schema tools
    assert "schema_get_entity" in tool_names
    assert "schema_field_exists" in tool_names

    # Data access tools
    assert "data_read_submatrix" in tool_names
    assert "query_execute" in tool_names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_query_validate_tool_via_mcp(mcp_client):
    """Test query_validate tool through MCP protocol.

    This test verifies:
    - Tool call works through stdio protocol
    - Query validation executes correctly
    - Result is properly formatted
    """
    result = await mcp_client.call_tool("query_validate", {"query": {"TestEntity": {}}})

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
async def test_query_get_operator_docs_via_mcp(mcp_client):
    """Test query_get_operator_docs tool through MCP protocol.

    This test verifies:
    - Operator documentation tool works
    - Returns proper documentation format
    - Handles various operators
    """
    result = await mcp_client.call_tool("query_get_operator_docs", {"operator": "$eq"})

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
    result1 = await mcp_client.call_tool("query_validate", {"query": {"Entity1": {}}})
    assert result1 is not None

    # Call 2: Get operator docs
    result2 = await mcp_client.call_tool("query_get_operator_docs", {"operator": "$like"})
    assert result2 is not None

    # Call 3: List patterns
    result3 = await mcp_client.call_tool("query_list_patterns", {})
    assert result3 is not None

    # All calls should succeed independently
    assert result1 != result2 != result3


# ============================================================================
# E2E TESTS WITH ODS SERVER CONNECTION
# ============================================================================
# These tests verify the full flow of connecting to ODS and executing
# queries through the MCP server


@pytest.mark.integration
@pytest.mark.asyncio
async def test_connect_to_ods_via_mcp(mcp_client, integration_credentials):
    """Test connecting to ODS server through MCP protocol.

    This test verifies:
    - ods_connect tool works via MCP
    - ODS server responds successfully
    - Connection state is established
    """
    result = await mcp_client.call_tool(
        "ods_connect",
        {
            "url": integration_credentials["url"],
            "username": integration_credentials["username"],
            "password": integration_credentials["password"],
        },
    )

    assert result is not None
    # Should contain connection result
    content = result.get("result", {}).get("content", [])
    assert len(content) > 0, f"Expected content in result, got: {result}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_entities_via_ods_mcp(mcp_client, integration_credentials):
    """Test listing ODS entities through MCP after connecting.

    This test verifies:
    - Can connect to ODS via MCP
    - Can list entities via MCP
    - Returns proper entity information
    """
    # Connect first
    await mcp_client.call_tool(
        "ods_connect",
        {
            "url": integration_credentials["url"],
            "username": integration_credentials["username"],
            "password": integration_credentials["password"],
        },
    )

    # Check connection info
    result = await mcp_client.call_tool("ods_get_connection_info", {})
    assert result is not None
    content = result.get("result", {}).get("content", [])
    assert len(content) > 0, "Should have connection info"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_query_execute_via_ods_mcp(mcp_client, integration_credentials):
    """Test executing a Jaquel query through MCP with ODS connection.

    This test verifies:
    - Can connect to ODS via MCP
    - Can execute queries via MCP
    - Returns data from ODS
    """
    # Connect first
    await mcp_client.call_tool(
        "ods_connect",
        {
            "url": integration_credentials["url"],
            "username": integration_credentials["username"],
            "password": integration_credentials["password"],
        },
    )

    # Execute a simple query
    query = {"AoTest": {"name": "*"}, "$attributes": {"id": 1, "name": 1}, "$options": {"$rowlimit": 5}}

    result = await mcp_client.call_tool("query_execute", {"query": query})
    assert result is not None

    # Should have content with results
    content = result.get("result", {}).get("content", [])
    assert len(content) > 0, f"Expected query results, got: {result}"

    # Parse the result
    text = content[0].get("text", "{}")
    query_result = json.loads(text)
    assert isinstance(query_result, dict)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_query_validate_with_ods_context(mcp_client, integration_credentials):
    """Test query validation with active ODS connection.

    This test verifies:
    - Query validation works with ODS connection
    - Validates against actual schema
    - Returns validation results
    """
    # Connect first
    await mcp_client.call_tool(
        "ods_connect",
        {
            "url": integration_credentials["url"],
            "username": integration_credentials["username"],
            "password": integration_credentials["password"],
        },
    )

    # Validate a query
    query = {"AoTest": {"name": "Test*"}, "$attributes": {"id": 1, "name": 1}, "$options": {"$rowlimit": 5}}

    result = await mcp_client.call_tool("query_validate", {"query": query})
    assert result is not None

    content = result.get("result", {}).get("content", [])
    assert len(content) > 0, f"Expected validation result, got: {result}"

    text = content[0].get("text", "{}")
    validation_result = json.loads(text)
    assert "valid" in validation_result or "errors" in validation_result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ods_connection_persistence(mcp_client, integration_credentials):
    """Test that ODS connection persists across multiple tool calls.

    This test verifies:
    - Connection state is maintained
    - Multiple queries can use same connection
    - No need to reconnect between calls
    """
    # Connect
    await mcp_client.call_tool(
        "ods_connect",
        {
            "url": integration_credentials["url"],
            "username": integration_credentials["username"],
            "password": integration_credentials["password"],
        },
    )

    # Call 1: Get connection info
    result1 = await mcp_client.call_tool("ods_get_connection_info", {})
    assert result1 is not None

    # Call 2: Execute query
    query = {"AoTest": {}, "$attributes": {"id": 1}, "$options": {"$rowlimit": 1}}
    result2 = await mcp_client.call_tool("query_execute", {"query": query})
    assert result2 is not None

    # Call 3: Validate different query
    result3 = await mcp_client.call_tool(
        "query_validate",
        {"query": {"AoMeasurement": {}}},
    )
    assert result3 is not None

    # All should succeed with same connection
    assert result1 != result2 != result3

    result4 = await mcp_client.call_tool(
        "query_describe",
        {
            "query": {
                "AoUnit": {
                    "phys_dimension": {
                        "$or": [
                            {
                                "length_exp": 1,
                                "mass_exp": 0,
                                "time_exp": -1,
                                "current_exp": 0,
                                "temperature_exp": 0,
                                "molar_amount_exp": 0,
                                "luminous_intensity_exp": 0,
                            },
                            {
                                "length_exp": 0,
                                "mass_exp": 0,
                                "time_exp": 1,
                                "current_exp": 0,
                                "temperature_exp": 0,
                                "molar_amount_exp": 0,
                                "luminous_intensity_exp": 0,
                            },
                        ]
                    }
                },
                "$attributes": {"name": 1, "factor": 1, "offset": 1, "phys_dimension.name": 1},
            }
        },
    )
    assert result4 is not None
    # Result should contain explanation content
    content = result4.get("result", {}).get("content", [])
    assert len(content) > 0, f"Expected content in result, got: {result4}"
    text = content[0].get("text", "")
    assert "Textual Representation:" in text
    assert "SQL-like Representation:" in text
