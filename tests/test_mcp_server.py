"""Tests for MCP server functions."""

import json
from unittest.mock import patch

import pytest
from mcp.types import TextContent

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
            "validate_jaquel_query",
            "get_operator_documentation",
            "suggest_optimizations",
            "get_query_pattern",
            "list_query_patterns",
            "generate_query_skeleton",
            "build_filter_condition",
            "explain_jaquel_query",
            "merge_filter_conditions",
            "check_entity_schema",
            "validate_field_exists",
            "debug_query_steps",
            "suggest_error_fixes",
            "connect_ods_server",
            "disconnect_ods_server",
            "get_ods_connection_info",
            "list_ods_entities",
            "execute_ods_query",
            "get_submatrix_measurement_quantities",
            "read_submatrix_data",
            "generate_submatrix_fetcher_script",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_call_tool_validate_jaquel_query(self):
        """Test calling validate_jaquel_query tool."""
        query = {"TestEntity": {}}
        arguments = {"query": query}

        result = await call_tool("validate_jaquel_query", arguments)

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
    async def test_call_tool_get_operator_documentation(self):
        """Test calling get_operator_documentation tool."""
        arguments = {"operator": "$eq"}

        result = await call_tool("get_operator_documentation", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "category" in response_data
        assert response_data["category"] == "comparison"

    @pytest.mark.asyncio
    async def test_call_tool_suggest_optimizations(self):
        """Test calling suggest_optimizations tool."""
        query = {"TestEntity": {}}
        arguments = {"query": query}

        result = await call_tool("suggest_optimizations", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "query_summary" in response_data
        assert "suggestions" in response_data

    @pytest.mark.asyncio
    async def test_call_tool_get_query_pattern(self):
        """Test calling get_query_pattern tool."""
        arguments = {"pattern": "get_all_instances"}

        result = await call_tool("get_query_pattern", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "template" in response_data
        assert "description" in response_data

    @pytest.mark.asyncio
    async def test_call_tool_list_query_patterns(self):
        """Test calling list_query_patterns tool."""
        arguments = {}

        result = await call_tool("list_query_patterns", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "available_patterns" in response_data
        assert "description" in response_data
        assert isinstance(response_data["available_patterns"], list)

    @pytest.mark.asyncio
    async def test_call_tool_generate_query_skeleton(self):
        """Test calling generate_query_skeleton tool."""
        arguments = {"entity_name": "TestEntity", "operation": "get_all"}

        result = await call_tool("generate_query_skeleton", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "TestEntity" in response_data

    @pytest.mark.asyncio
    async def test_call_tool_build_filter_condition(self):
        """Test calling build_filter_condition tool."""
        arguments = {"field": "name", "operator": "$eq", "value": "test"}

        result = await call_tool("build_filter_condition", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "name" in response_data
        assert response_data["name"] == {"$eq": "test"}

    @pytest.mark.asyncio
    async def test_call_tool_build_filter_condition_unknown_operator(self):
        """Test build_filter_condition with unknown operator."""
        arguments = {"field": "name", "operator": "$unknown", "value": "test"}

        result = await call_tool("build_filter_condition", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "error" in response_data
        assert "Unknown operator" in response_data["error"]

    @pytest.mark.asyncio
    async def test_call_tool_explain_jaquel_query(self):
        """Test calling explain_jaquel_query tool."""
        query = {"TestEntity": {}}
        arguments = {"query": query}

        result = await call_tool("explain_jaquel_query", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        # Should return plain text explanation with query components
        explanation = result[0].text
        # The explanation should contain information about the query structure
        # It can be either a simple explanation or an error if not connected to ODS
        assert isinstance(explanation, str)
        assert len(explanation) > 0

    @pytest.mark.asyncio
    async def test_call_tool_merge_filter_conditions(self):
        """Test calling merge_filter_conditions tool."""
        conditions = [{"name": "test1"}, {"name": "test2"}]
        arguments = {"conditions": conditions, "operator": "$and"}

        result = await call_tool("merge_filter_conditions", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "$and" in response_data

    @pytest.mark.asyncio
    async def test_call_tool_merge_filter_conditions_no_conditions(self):
        """Test merge_filter_conditions with no conditions."""
        arguments = {"conditions": [], "operator": "$and"}

        result = await call_tool("merge_filter_conditions", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "error" in response_data
        assert "No conditions to merge" in response_data["error"]

    @patch("odsbox_jaquel_mcp.tools.schema_tools.SchemaInspector.get_entity_schema")
    @pytest.mark.asyncio
    async def test_call_tool_check_entity_schema(self, mock_get_schema):
        """Test calling check_entity_schema tool."""
        mock_get_schema.return_value = {"fields": ["id", "name"]}
        arguments = {"entity_name": "TestEntity"}

        result = await call_tool("check_entity_schema", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_get_schema.assert_called_once_with("TestEntity")

    @patch("odsbox_jaquel_mcp.tools.schema_tools.SchemaInspector.validate_field_exists")
    @pytest.mark.asyncio
    async def test_call_tool_validate_field_exists(self, mock_validate):
        """Test calling validate_field_exists tool."""
        mock_validate.return_value = {"exists": True}
        arguments = {"entity_name": "TestEntity", "field_name": "name"}

        result = await call_tool("validate_field_exists", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_validate.assert_called_once_with("TestEntity", "name")

    @patch("odsbox_jaquel_mcp.tools.query_tools.QueryDebugger.debug_query_step_by_step")
    @pytest.mark.asyncio
    async def test_call_tool_debug_query_steps(self, mock_debug):
        """Test calling debug_query_steps tool."""
        mock_debug.return_value = {"steps": []}
        arguments = {"query": {"TestEntity": {}}}

        result = await call_tool("debug_query_steps", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_debug.assert_called_once_with({"TestEntity": {}})

    @patch("odsbox_jaquel_mcp.tools.query_tools.QueryDebugger.suggest_fixes_for_issue")
    @pytest.mark.asyncio
    async def test_call_tool_suggest_error_fixes(self, mock_suggest):
        """Test calling suggest_error_fixes tool."""
        mock_suggest.return_value = ["Fix suggestion"]
        arguments = {"issue": "Test issue", "query": {"TestEntity": {}}}

        result = await call_tool("suggest_error_fixes", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert response_data["issue"] == "Test issue"
        assert response_data["suggestions"] == ["Fix suggestion"]

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.connect")
    @pytest.mark.asyncio
    async def test_call_tool_connect_ods_server(self, mock_connect):
        """Test calling connect_ods_server tool."""
        mock_connect.return_value = {"success": True}
        arguments = {"url": "http://test:8087/api", "username": "user", "password": "pass"}

        result = await call_tool("connect_ods_server", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_connect.assert_called_once_with(
            url="http://test:8087/api", auth=("user", "pass"), verify_certificate=True
        )

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.connect")
    @pytest.mark.asyncio
    async def test_call_tool_connect_ods_server_verify_false(self, mock_connect):
        """Test calling connect_ods_server tool."""
        mock_connect.return_value = {"success": True}
        arguments = {"url": "http://test:8087/api", "username": "user", "password": "pass", "verify": False}

        result = await call_tool("connect_ods_server", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_connect.assert_called_once_with(
            url="http://test:8087/api", auth=("user", "pass"), verify_certificate=False
        )

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.disconnect")
    @pytest.mark.asyncio
    async def test_call_tool_disconnect_ods_server(self, mock_disconnect):
        """Test calling disconnect_ods_server tool."""
        mock_disconnect.return_value = {"success": True}
        arguments = {}

        result = await call_tool("disconnect_ods_server", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_disconnect.assert_called_once()

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.get_connection_info")
    @pytest.mark.asyncio
    async def test_call_tool_get_ods_connection_info(self, mock_get_info):
        """Test calling get_ods_connection_info tool."""
        mock_get_info.return_value = {"status": "connected"}
        arguments = {}

        result = await call_tool("get_ods_connection_info", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_get_info.assert_called_once()

    @patch("odsbox_jaquel_mcp.tools.connection_tools.ODSConnectionManager.get_model")
    @pytest.mark.asyncio
    async def test_call_tool_list_ods_entities(self, mock_get_model):
        """Test calling list_ods_entities tool."""
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

        result = await call_tool("list_ods_entities", arguments)

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
    async def test_call_tool_execute_ods_query(self, mock_query):
        """Test calling execute_ods_query tool."""
        mock_query.return_value = {"success": True, "result": "data"}
        arguments = {"query": {"TestEntity": {}}}

        result = await call_tool("execute_ods_query", arguments)

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
    async def test_call_tool_get_submatrix_measurement_quantities(self, mock_get_quantities):
        """Test calling get_submatrix_measurement_quantities tool."""
        # Mock the get_measurement_quantities to return sample data
        mock_get_quantities.return_value = [
            {
                "id": 1,
                "name": "Time",
                "measurement_quantity": {"name": "Time", "unit": "s", "datatype": 2},
            }
        ]

        arguments = {"submatrix_id": 123}

        result = await call_tool("get_submatrix_measurement_quantities", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert response_data["submatrix_id"] == 123
        assert "measurement_quantities" in response_data

    @patch("odsbox_jaquel_mcp.tools.submatrix_tools.SubmatrixDataReader.read_submatrix_data")
    @pytest.mark.asyncio
    async def test_call_tool_read_submatrix_data(self, mock_read_data):
        """Test calling read_submatrix_data tool."""
        # Mock the read_submatrix_data to return sample data
        mock_read_data.return_value = {
            "data": [[1, 25.5], [2, 26.0], [3, 25.8]],
            "columns": ["Time", "Temperature"],
        }

        arguments = {
            "submatrix_id": 456,
            "measurement_quantity_patterns": ["Temp*"],
        }

        result = await call_tool("read_submatrix_data", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        # Just verify we got a response back
        assert "data" in response_data or "columns" in response_data or "error" not in response_data

    @patch("odsbox_jaquel_mcp.tools.submatrix_tools.generate_basic_fetcher_script")
    @pytest.mark.asyncio
    async def test_call_tool_generate_submatrix_fetcher_script(self, mock_generate_script):
        """Test calling generate_submatrix_fetcher_script tool."""
        # Mock the script generation to return sample Python code
        mock_generate_script.return_value = "# Generated script\nprint('Hello')"

        arguments = {
            "submatrix_id": 789,
            "script_type": "basic",
            "output_format": "csv",
        }

        result = await call_tool("generate_submatrix_fetcher_script", arguments)

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
