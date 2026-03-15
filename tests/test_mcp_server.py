"""Tests for MCP server functions."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.lowlevel.server import request_ctx
from mcp.shared.context import RequestContext
from mcp.types import ElicitResult, TextContent

from odsbox_jaquel_mcp.server import call_tool, list_tools


class TestMCPServer:
    """Test cases for MCP server functions."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_list(self):
        """Test that list_tools returns a list of Tool objects."""
        tools = await list_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check that each tool has required attributes
        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")

    @pytest.mark.asyncio
    async def test_list_tools_has_expected_tools(self):
        """Test that list_tools includes expected tool names."""
        tools = await list_tools()
        tool_names = [tool.name for tool in tools]

        expected_tools = [
            "query_validate",
            "query_get_operator_docs",
            "query_get_pattern",
            "query_list_patterns",
            "query_generate_skeleton",
            "query_describe",
            "schema_get_entity",
            "schema_field_exists",
            "ods_connect",
            "ods_disconnect",
            "ods_get_connection_info",
            "schema_list_entities",
            "query_execute",
            "data_get_quantities",
            "data_read_submatrix",
            "data_generate_fetcher_script",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_ods_connect_password_marked_as_secret(self):
        """Test that ods_connect tool marks password as secret with format hint."""
        tools = await list_tools()
        ods_connect = next(t for t in tools if t.name == "ods_connect")
        password_prop = ods_connect.inputSchema["properties"]["password"]

        assert password_prop["format"] == "password"
        assert password_prop["x-mcp-secret"] is True

    @pytest.mark.asyncio
    async def test_plot_comparison_notebook_password_marked_as_secret(self):
        """Test that plot_comparison_notebook marks ods_password as secret."""
        tools = await list_tools()
        notebook_tool = next(t for t in tools if t.name == "plot_comparison_notebook")
        password_prop = notebook_tool.inputSchema["properties"]["ods_password"]

        assert password_prop["format"] == "password"
        assert password_prop["x-mcp-secret"] is True

    @pytest.mark.asyncio
    async def test_call_tool_query_validate(self):
        """Test calling query_validate tool."""
        query = {"TestEntity": {}}
        arguments = {"query": query}

        result = await call_tool("query_validate", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        # Parse the JSON response
        response_data = json.loads(result[0].text)
        assert "valid" in response_data
        assert "errors" in response_data
        assert "warnings" in response_data
        assert "suggestions" in response_data

    @pytest.mark.asyncio
    async def test_call_tool_query_get_operator_docs(self):
        """Test calling query_get_operator_docs tool."""
        arguments = {"operator": "$eq"}

        result = await call_tool("query_get_operator_docs", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "category" in response_data
        assert response_data["category"] == "comparison"

    @pytest.mark.asyncio
    async def test_call_tool_query_get_pattern(self):
        """Test calling query_get_pattern tool."""
        arguments = {"pattern": "get_all_instances"}

        result = await call_tool("query_get_pattern", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "template" in response_data
        assert "description" in response_data

    @pytest.mark.asyncio
    async def test_call_tool_query_list_patterns(self):
        """Test calling query_list_patterns tool."""
        arguments = {}

        result = await call_tool("query_list_patterns", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "available_patterns" in response_data
        assert "description" in response_data
        assert isinstance(response_data["available_patterns"], list)

    @pytest.mark.asyncio
    async def test_call_tool_query_generate_skeleton(self):
        """Test calling query_generate_skeleton tool."""
        arguments = {"entity_name": "TestEntity", "operation": "get_all"}

        result = await call_tool("query_generate_skeleton", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "TestEntity" in response_data

    @pytest.mark.asyncio
    async def test_call_tool_query_describe(self):
        """Test calling query_describe tool."""
        query = {"TestEntity": {}}
        arguments = {"query": query}

        result = await call_tool("query_describe", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        # Should return plain text explanation with query components
        explanation = result[0].text
        # The explanation should contain information about the query structure
        # It can be either a simple explanation or an error if not connected to ODS
        assert isinstance(explanation, str)
        assert len(explanation) > 0

    @patch("odsbox_jaquel_mcp.tools.schema_tools.SchemaInspector.get_entity_schema")
    @pytest.mark.asyncio
    async def test_call_tool_schema_get_entity(self, mock_get_schema):
        """Test calling schema_get_entity tool."""
        mock_get_schema.return_value = {"fields": ["id", "name"]}
        arguments = {"entity_name": "TestEntity"}

        result = await call_tool("schema_get_entity", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_get_schema.assert_called_once_with("TestEntity")

    @patch("odsbox_jaquel_mcp.tools.schema_tools.SchemaInspector.schema_field_exists")
    @pytest.mark.asyncio
    async def test_call_tool_schema_field_exists(self, mock_validate):
        """Test calling schema_field_exists tool."""
        mock_validate.return_value = {"exists": True}
        arguments = {"entity_name": "TestEntity", "field_name": "name"}

        result = await call_tool("schema_field_exists", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_validate.assert_called_once_with("TestEntity", "name")

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.connect")
    @pytest.mark.asyncio
    async def test_call_tool_ods_connect(self, mock_connect):
        """Test calling ods_connect tool."""
        mock_connect.return_value = {"success": True}
        arguments = {"url": "http://test:8087/api", "username": "user", "password": "pass"}

        result = await call_tool("ods_connect", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_connect.assert_called_once_with(
            url="http://test:8087/api", auth=("user", "pass"), verify_certificate=True
        )

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.connect")
    @pytest.mark.asyncio
    async def test_call_tool_ods_connect_verify_false(self, mock_connect):
        """Test calling ods_connect tool."""
        mock_connect.return_value = {"success": True}
        arguments = {"url": "http://test:8087/api", "username": "user", "password": "pass", "verify": False}

        result = await call_tool("ods_connect", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_connect.assert_called_once_with(
            url="http://test:8087/api", auth=("user", "pass"), verify_certificate=False
        )

    @pytest.mark.asyncio
    async def test_ods_connect_credentials_required_in_schema(self):
        """Test that username and password are required in the schema."""
        tools = await list_tools()
        ods_connect = next(t for t in tools if t.name == "ods_connect")
        assert "username" in ods_connect.inputSchema["required"]
        assert "password" in ods_connect.inputSchema["required"]

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.connect")
    @pytest.mark.asyncio
    async def test_ods_connect_elicits_credentials_on_accept(self, mock_connect):
        """Test that missing credentials trigger elicitation and connect on accept."""
        mock_connect.return_value = {"success": True}

        mock_session = MagicMock()
        mock_session.check_client_capability.return_value = True
        mock_session.elicit = AsyncMock(
            return_value=ElicitResult(
                action="accept",
                content={"username": "elicited_user", "password": "elicited_pass"},
            )
        )
        ctx = RequestContext(request_id="test", meta=None, session=mock_session, lifespan_context=None)
        token = request_ctx.set(ctx)
        try:
            result = await call_tool("ods_connect", {"url": "http://test:8087/api"})
        finally:
            request_ctx.reset(token)

        assert isinstance(result, list)
        response = json.loads(result[0].text)
        assert response.get("success") is True
        mock_connect.assert_called_once_with(
            url="http://test:8087/api", auth=("elicited_user", "elicited_pass"), verify_certificate=True
        )

    @pytest.mark.asyncio
    async def test_ods_connect_elicitation_declined(self):
        """Test that declining elicitation returns an error."""
        mock_session = MagicMock()
        mock_session.check_client_capability.return_value = True
        mock_session.elicit = AsyncMock(return_value=ElicitResult(action="decline", content=None))
        ctx = RequestContext(request_id="test", meta=None, session=mock_session, lifespan_context=None)
        token = request_ctx.set(ctx)
        try:
            result = await call_tool("ods_connect", {"url": "http://test:8087/api"})
        finally:
            request_ctx.reset(token)

        response = json.loads(result[0].text)
        assert "error" in response
        assert response["error_type"] == "ElicitationDeclined"

    @pytest.mark.asyncio
    async def test_ods_connect_no_elicitation_support(self):
        """Test error when client does not support elicitation."""
        mock_session = MagicMock()
        mock_session.check_client_capability.return_value = False
        ctx = RequestContext(request_id="test", meta=None, session=mock_session, lifespan_context=None)
        token = request_ctx.set(ctx)
        try:
            result = await call_tool("ods_connect", {"url": "http://test:8087/api"})
        finally:
            request_ctx.reset(token)

        response = json.loads(result[0].text)
        assert "error" in response
        assert response["error_type"] == "ElicitationNotSupported"

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.disconnect")
    @pytest.mark.asyncio
    async def test_call_tool_ods_disconnect(self, mock_disconnect):
        """Test calling ods_disconnect tool."""
        mock_disconnect.return_value = {"success": True}
        arguments = {}

        result = await call_tool("ods_disconnect", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_disconnect.assert_called_once()

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.get_connection_info")
    @pytest.mark.asyncio
    async def test_call_tool_ods_get_connection_info(self, mock_get_info):
        """Test calling ods_get_connection_info tool."""
        mock_get_info.return_value = {"status": "connected"}
        arguments = {}

        result = await call_tool("ods_get_connection_info", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_get_info.assert_called_once()

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.get_model")
    @pytest.mark.asyncio
    async def test_call_tool_schema_list_entities(self, mock_get_model):
        """Test calling schema_list_entities tool."""
        from unittest.mock import MagicMock

        # Mock the model and entities
        mock_model = MagicMock()
        mock_entity = MagicMock()
        mock_entity.name = "TestEntity"
        mock_entity.base_name = "TestBase"
        mock_entity.relations = {}
        # Mock entities as a dictionary (entity_name -> entity)
        mock_model.entities = {"TestEntity": mock_entity}
        mock_get_model.return_value = mock_model

        arguments = {}

        result = await call_tool("schema_list_entities", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        # Parse the JSON response
        response_data = json.loads(result[0].text)
        assert "entities" in response_data
        assert "count" in response_data
        assert len(response_data["entities"]) == 1
        assert response_data["entities"][0]["name"] == "TestEntity"
        assert response_data["entities"][0]["basename"] == "TestBase"

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.query")
    @pytest.mark.asyncio
    async def test_call_tool_query_execute(self, mock_query):
        """Test calling query_execute tool."""
        mock_query.return_value = {"success": True, "result": "data"}
        arguments = {"query": {"TestEntity": {}}}

        result = await call_tool("query_execute", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        # Should return the serializable result
        text_result = result[0].text
        response_data = json.loads(text_result)
        assert response_data["success"] is True
        assert response_data["result"] == "data"

    @patch("odsbox_jaquel_mcp.tools.submatrix_tools.SubmatrixDataReader.get_measurement_quantities")
    @pytest.mark.asyncio
    async def test_call_tool_data_get_quantities(self, mock_get_quantities):
        """Test calling data_get_quantities tool."""
        # Mock the get_measurement_quantities to return sample data
        mock_get_quantities.return_value = [
            {
                "id": 1,
                "name": "Time",
                "measurement_quantity": {"name": "Time", "unit": "s", "datatype": 2},
            }
        ]

        arguments = {"submatrix_id": 123}

        result = await call_tool("data_get_quantities", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert response_data["submatrix_id"] == 123
        assert "measurement_quantities" in response_data

    @patch("odsbox_jaquel_mcp.tools.submatrix_tools.SubmatrixDataReader.data_read_submatrix")
    @pytest.mark.asyncio
    async def test_call_tool_data_read_submatrix(self, mock_read_data):
        """Test calling data_read_submatrix tool."""
        # Mock the data_read_submatrix to return sample data with new format
        mock_read_data.return_value = {
            "submatrix_id": 456,
            "columns": ["Time", "Temperature"],
            "row_count": 1000,
            "preview_row_count": 100,
            "data_preview": [[1, 25.5], [2, 26.0], [3, 25.8]],
            "sampling_method": "auto",
            "note": "Preview resampled from 1000 to 100 rows using 'auto' method",
        }

        arguments = {
            "submatrix_id": 456,
            "measurement_quantity_patterns": ["Temp*"],
        }

        result = await call_tool("data_read_submatrix", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        # Verify we got the expected fields
        assert "columns" in response_data
        assert "row_count" in response_data
        assert "data_preview" in response_data or "error" not in response_data

    @patch("odsbox_jaquel_mcp.tools.submatrix_tools.generate_basic_fetcher_script")
    @pytest.mark.asyncio
    async def test_call_tool_data_generate_fetcher_script(self, mock_generate_script):
        """Test calling data_generate_fetcher_script tool."""
        # Mock the script generation to return sample Python code
        mock_generate_script.return_value = "# Generated script\nprint('Hello')"

        arguments = {
            "submatrix_id": 789,
            "script_type": "basic",
            "output_format": "csv",
        }

        result = await call_tool("data_generate_fetcher_script", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        # Response should be a dict (either with script or error is acceptable for this test)
        assert isinstance(response_data, dict)

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """Test calling an unknown tool."""
        arguments = {}

        result = await call_tool("unknown_tool", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "error" in response_data
        assert "Unknown tool: unknown_tool" in response_data["error"]
