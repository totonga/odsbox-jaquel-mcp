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
            "validate_filter_condition",
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
            "validate_filter_against_schema",
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
    async def test_call_tool_validate_filter_condition(self):
        """Test calling validate_filter_condition tool."""
        condition = {"name": {"$eq": "test"}}
        arguments = {"condition": condition}

        result = await call_tool("validate_filter_condition", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert "valid" in response_data
        assert "errors" in response_data
        assert "issues" in response_data

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

        # Should return plain text explanation
        explanation = result[0].text
        assert "Query for entity: TestEntity" in explanation

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

    @patch("odsbox_jaquel_mcp.server.SchemaInspector.get_entity_schema")
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

    @patch("odsbox_jaquel_mcp.server.SchemaInspector.validate_field_exists")
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

    @patch("odsbox_jaquel_mcp.server.SchemaInspector.validate_filter_against_schema")
    @pytest.mark.asyncio
    async def test_call_tool_validate_filter_against_schema(self, mock_validate):
        """Test calling validate_filter_against_schema tool."""
        mock_validate.return_value = {"valid": True}
        arguments = {"entity_name": "TestEntity", "filter_condition": {"name": "test"}}

        result = await call_tool("validate_filter_against_schema", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_validate.assert_called_once_with("TestEntity", {"name": "test"})

    @patch("odsbox_jaquel_mcp.server.QueryDebugger.debug_query_step_by_step")
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

    @patch("odsbox_jaquel_mcp.server.QueryDebugger.suggest_fixes_for_issue")
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

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.connect")
    @pytest.mark.asyncio
    async def test_call_tool_connect_ods_server(self, mock_connect):
        """Test calling connect_ods_server tool."""
        mock_connect.return_value = {"success": True}
        arguments = {"url": "http://test:8087/api", "username": "user", "password": "pass"}

        result = await call_tool("connect_ods_server", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        mock_connect.assert_called_once_with(url="http://test:8087/api", auth=("user", "pass"))

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.disconnect")
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

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.get_connection_info")
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

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.get_model")
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

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.query")
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

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.get_instance")
    @pytest.mark.asyncio
    async def test_call_tool_get_submatrix_measurement_quantities(self, mock_get_instance):
        """Test calling get_submatrix_measurement_quantities tool."""
        from unittest.mock import MagicMock

        # Mock the connection instance
        mock_instance = mock_get_instance.return_value
        mock_con_i = MagicMock()
        mock_instance._con_i = mock_con_i

        # Mock the query result as a DataFrame-like object
        class MockRow:
            def __getitem__(self, key):
                return {
                    "id": 1,
                    "name": "Time",
                    "measurement_quantity.name": "Time",
                    "measurement_quantity.datatype": 2,  # DT_DOUBLE
                    "measurement_quantity.unit:OUTER.name": "s",
                    "sequence_representation": 1,
                    "independent": True,
                }[key]

        class MockDF:
            def iterrows(self):
                return [(0, MockRow())]

        mock_con_i.query.return_value = MockDF()

        arguments = {"submatrix_id": 123}

        result = await call_tool("get_submatrix_measurement_quantities", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert response_data["submatrix_id"] == 123
        assert "measurement_quantities" in response_data
        assert len(response_data["measurement_quantities"]) == 1
        assert response_data["measurement_quantities"][0]["name"] == "Time"
        assert response_data["measurement_quantities"][0]["measurement_quantity"] == "Time"
        assert response_data["measurement_quantities"][0]["unit"] == "s"

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.get_instance")
    @pytest.mark.asyncio
    async def test_call_tool_read_submatrix_data(self, mock_get_instance):
        """Test calling read_submatrix_data tool."""
        from unittest.mock import MagicMock

        # Mock the connection instance
        mock_instance = mock_get_instance.return_value
        mock_con_i = MagicMock()
        mock_bulk = MagicMock()
        mock_con_i.bulk = mock_bulk
        mock_instance._con_i = mock_con_i

        # Mock the DataFrame result
        class MockDF:
            def __init__(self):
                self.columns = ["Time", "Temperature"]

            def __len__(self):
                return 100

            def head(self, n):
                # Return a DataFrame-like object that has to_dict
                class MockHeadDF:
                    def to_dict(self, orient):
                        return [{"Time": 1.0, "Temperature": 25.0}]

                return MockHeadDF()

            def to_dict(self, orient):
                return [{"Time": 1.0, "Temperature": 25.0}]

        mock_bulk.data_read.return_value = MockDF()

        arguments = {"submatrix_id": 123, "measurement_quantity_patterns": ["Time", "Temp*"]}

        result = await call_tool("read_submatrix_data", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert response_data["submatrix_id"] == 123
        assert response_data["columns"] == ["Time", "Temperature"]
        assert response_data["row_count"] == 100

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.get_instance")
    @pytest.mark.asyncio
    async def test_call_tool_generate_submatrix_fetcher_script(self, mock_get_instance):
        """Test calling generate_submatrix_fetcher_script tool."""
        from unittest.mock import MagicMock

        # Mock the connection instance
        mock_instance = mock_get_instance.return_value
        mock_con_i = MagicMock()
        mock_instance._con_i = mock_con_i

        # Mock the query result as a DataFrame-like object
        class MockRow:
            def __getitem__(self, key):
                return {"name": "Temperature", "measurement_quantity.name": "Temperature", "independent": False}[key]

        class MockDF:
            def iterrows(self):
                return [(0, MockRow())]

        mock_con_i.query.return_value = MockDF()

        arguments = {"submatrix_id": 123, "script_type": "basic", "output_format": "csv"}

        result = await call_tool("generate_submatrix_fetcher_script", arguments)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        response_data = json.loads(result[0].text)
        assert response_data["submatrix_id"] == 123
        assert response_data["script_type"] == "basic"
        assert response_data["output_format"] == "csv"
        assert "script" in response_data
        assert "instructions" in response_data
        assert "submatrix_123_data.csv" in response_data["script"]

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
