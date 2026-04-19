"""Tests for MCP server functions."""

from unittest.mock import patch

import pytest

from odsbox_jaquel_mcp.schemas_types import ConnectionInfo, ConnectResult
from odsbox_jaquel_mcp.server import (
    data_generate_fetcher_script,
    data_get_quantities,
    data_read_submatrix,
    mcp,
    ods_connect,
    ods_connect_using_env,
    ods_disconnect,
    ods_get_connection_info,
    query_describe,
    query_execute,
    query_generate_skeleton,
    query_get_operator_docs,
    query_get_pattern,
    query_list_patterns,
    query_validate,
    schema_field_exists,
    schema_get_entity,
    schema_list_entities,
)


class TestMCPServer:
    """Test cases for MCP server functions."""

    def test_server_has_tools(self):
        """Test that the FastMCP server has registered tools."""
        # Verify the mcp instance exists and is properly configured
        assert mcp.name == "odsbox-jaquel-mcp"

    def test_call_tool_query_validate(self):
        """Test calling query_validate tool."""
        query = {"TestEntity": {}}

        result = query_validate(query=query)

        assert isinstance(result, dict)
        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "suggestions" in result

    def test_call_tool_query_get_operator_docs(self):
        """Test calling query_get_operator_docs tool."""
        result = query_get_operator_docs(operator="$eq")

        assert isinstance(result, dict)
        assert "category" in result
        assert result["category"] == "comparison"

    def test_call_tool_query_get_pattern(self):
        """Test calling query_get_pattern tool."""
        result = query_get_pattern(pattern="get_all_instances")

        assert isinstance(result, dict)
        assert "template" in result
        assert "description" in result

    def test_call_tool_query_list_patterns(self):
        """Test calling query_list_patterns tool."""
        result = query_list_patterns()

        assert isinstance(result, dict)
        assert "available_patterns" in result
        assert "description" in result
        assert isinstance(result["available_patterns"], list)

    def test_call_tool_query_generate_skeleton(self):
        """Test calling query_generate_skeleton tool."""
        result = query_generate_skeleton(entity_name="TestEntity", operation="get_all")

        assert isinstance(result, dict)
        assert "TestEntity" in result

    @patch("odsbox_jaquel_mcp.server.JaquelExplain.query_describe")
    def test_call_tool_query_describe(self, mock_describe):
        """Test calling query_describe tool."""
        mock_describe.return_value = "Query describes TestEntity"
        query = {"TestEntity": {}}

        result = query_describe(query=query)

        # Should return plain text explanation
        assert isinstance(result, str)
        assert len(result) > 0
        mock_describe.assert_called_once_with(query)

    @patch("odsbox_jaquel_mcp.server.SchemaInspector.get_entity_schema")
    def test_call_tool_schema_get_entity(self, mock_get_schema):
        """Test calling schema_get_entity tool."""
        from odsbox_jaquel_mcp.schemas_types import EntitySchema

        mock_get_schema.return_value = EntitySchema(
            entity="TestEntity",
            derived_from="AoTest",
            attributes={},
            relationships={},
            description=None,
        )

        result = schema_get_entity(entity_name="TestEntity")

        assert isinstance(result, EntitySchema)
        assert result.entity == "TestEntity"
        mock_get_schema.assert_called_once_with("TestEntity")

    @patch("odsbox_jaquel_mcp.server.SchemaInspector.schema_field_exists")
    def test_call_tool_schema_field_exists(self, mock_validate):
        """Test calling schema_field_exists tool."""
        mock_validate.return_value = {"exists": True}

        result = schema_field_exists(entity_name="TestEntity", field_name="name")

        assert isinstance(result, dict)
        mock_validate.assert_called_once_with("TestEntity", "name")

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.connect")
    @pytest.mark.asyncio
    async def test_call_tool_ods_connect(self, mock_connect):
        """Test calling ods_connect tool."""
        mock_connect.return_value = ConnectResult(
            message="Connected to ODS server",
            connection=ConnectionInfo(
                url="http://test:8087/api",
                username="user",
                con_i_url="",
                status="connected",
                available_entities=[],
                initial_query={},
            ),
        )

        result = await ods_connect(url="http://test:8087/api", username="user", password="pass")

        assert isinstance(result, ConnectResult)
        mock_connect.assert_called_once_with(
            url="http://test:8087/api", auth=("user", "pass"), verify_certificate=True
        )

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.connect")
    @pytest.mark.asyncio
    async def test_call_tool_ods_connect_verify_false(self, mock_connect):
        """Test calling ods_connect tool."""
        mock_connect.return_value = ConnectResult(
            message="Connected to ODS server",
            connection=ConnectionInfo(
                url="http://test:8087/api",
                username="user",
                con_i_url="",
                status="connected",
                available_entities=[],
                initial_query={},
            ),
        )

        result = await ods_connect(url="http://test:8087/api", username="user", password="pass", verify=False)

        assert isinstance(result, ConnectResult)
        mock_connect.assert_called_once_with(
            url="http://test:8087/api", auth=("user", "pass"), verify_certificate=False
        )

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.connect_with_factory")
    @pytest.mark.asyncio
    async def test_call_tool_ods_connect_using_env_default_prefix(self, mock_connect, monkeypatch):
        """Test calling ods_connect_using_env tool with default prefix (ODSBOX_MCP)."""
        mock_connect.return_value = ConnectResult(
            message="Connected to ODS server",
            connection=ConnectionInfo(
                url="http://test:8087/api",
                username="user",
                con_i_url="",
                status="connected",
                available_entities=[],
                initial_query={},
            ),
        )

        monkeypatch.setenv("ODSBOX_MCP_URL", "http://test:8087/api")
        monkeypatch.setenv("ODSBOX_MCP_USERNAME", "user")
        monkeypatch.setenv("ODSBOX_MCP_PASSWORD", "pass")
        monkeypatch.setenv("ODSBOX_MCP_VERIFY", "false")

        result = await ods_connect_using_env()

        assert isinstance(result, ConnectResult)
        mock_connect.assert_called_once()
        auth_args = mock_connect.call_args[0][0]
        assert auth_args["mode"] == "basic"
        assert auth_args["url"] == "http://test:8087/api"
        assert auth_args["username"] == "user"
        assert auth_args["password"] == "pass"
        assert auth_args["verify_certificate"] is False

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.connect_with_factory")
    @pytest.mark.asyncio
    async def test_call_tool_ods_connect_using_env_override_prefix(self, mock_connect, monkeypatch):
        """Test calling ods_connect_using_env tool with an explicit env_prefix."""
        mock_connect.return_value = ConnectResult(
            message="Connected to ODS server",
            connection=ConnectionInfo(
                url="http://test:8087/api",
                username="user",
                con_i_url="",
                status="connected",
                available_entities=[],
                initial_query={},
            ),
        )

        monkeypatch.setenv("ODS_URL", "http://test:8087/api")
        monkeypatch.setenv("ODS_USERNAME", "user")
        monkeypatch.setenv("ODS_PASSWORD", "pass")
        monkeypatch.setenv("ODS_VERIFY", "false")

        result = await ods_connect_using_env(env_prefix="ODS")

        assert isinstance(result, ConnectResult)
        mock_connect.assert_called_once()
        auth_args = mock_connect.call_args[0][0]
        assert auth_args["mode"] == "basic"
        assert auth_args["url"] == "http://test:8087/api"
        assert auth_args["username"] == "user"
        assert auth_args["password"] == "pass"
        assert auth_args["verify_certificate"] is False

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.connect_with_factory")
    @pytest.mark.asyncio
    async def test_call_tool_ods_connect_using_env_fallback_to_ods_vars(self, mock_connect, monkeypatch):
        """Test that ods_connect_using_env falls back to legacy ODS_ env vars when ODSBOX_MCP_ vars are absent."""
        mock_connect.return_value = ConnectResult(
            message="Connected to ODS server",
            connection=ConnectionInfo(
                url="http://test:8087/api",
                username="user",
                con_i_url="",
                status="connected",
                available_entities=[],
                initial_query={},
            ),
        )

        monkeypatch.delenv("ODSBOX_MCP_URL", raising=False)
        monkeypatch.delenv("ODSBOX_MCP_USERNAME", raising=False)
        monkeypatch.delenv("ODSBOX_MCP_PASSWORD", raising=False)
        monkeypatch.delenv("ODSBOX_MCP_VERIFY", raising=False)

        monkeypatch.setenv("ODS_URL", "http://test:8087/api")
        monkeypatch.setenv("ODS_USERNAME", "user")
        monkeypatch.setenv("ODS_PASSWORD", "pass")
        monkeypatch.setenv("ODS_VERIFY", "true")

        result = await ods_connect_using_env()

        assert isinstance(result, ConnectResult)
        mock_connect.assert_called_once()
        auth_args = mock_connect.call_args[0][0]
        assert auth_args["mode"] == "basic"
        assert auth_args["url"] == "http://test:8087/api"
        assert auth_args["username"] == "user"
        assert auth_args["password"] == "pass"
        assert auth_args["verify_certificate"] is True

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.connect_with_factory")
    @pytest.mark.asyncio
    async def test_call_tool_ods_connect_using_env_missing_required_env_vars(self, mock_connect, monkeypatch):
        """Test that missing required env vars raises an error."""
        mock_connect.return_value = {"message": "Connected to ODS server", "connection": {}}

        monkeypatch.delenv("ODSBOX_MCP_URL", raising=False)
        monkeypatch.delenv("ODSBOX_MCP_USERNAME", raising=False)
        monkeypatch.delenv("ODSBOX_MCP_PASSWORD", raising=False)

        with pytest.raises(ValueError, match="must be set"):
            await ods_connect_using_env()

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.disconnect")
    def test_call_tool_ods_disconnect(self, mock_disconnect):
        """Test calling ods_disconnect tool."""
        mock_disconnect.return_value = {"message": "Disconnected from ODS server"}

        result = ods_disconnect()

        assert isinstance(result, dict)
        mock_disconnect.assert_called_once()

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.get_connection_info")
    def test_call_tool_ods_get_connection_info(self, mock_get_info):
        """Test calling ods_get_connection_info tool."""
        mock_get_info.return_value = ConnectionInfo(
            url="http://test:8087/api",
            username="user",
            con_i_url="",
            status="connected",
            available_entities=[],
            initial_query={},
        )

        result = ods_get_connection_info()

        assert isinstance(result, ConnectionInfo)
        mock_get_info.assert_called_once()

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.get_model")
    def test_call_tool_schema_list_entities(self, mock_get_model):
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

        result = schema_list_entities()

        assert isinstance(result, dict)
        assert "entities" in result
        assert "count" in result
        assert len(result["entities"]) == 1
        assert result["entities"][0]["name"] == "TestEntity"
        assert result["entities"][0]["basename"] == "TestBase"

    @patch("odsbox_jaquel_mcp.server.ODSConnectionManager.query")
    @pytest.mark.asyncio
    async def test_call_tool_query_execute(self, mock_query):
        """Test calling query_execute tool."""
        mock_query.return_value = {"result": "data"}

        result = await query_execute(query={"TestEntity": {}})

        assert isinstance(result, dict)
        assert result["result"] == "data"

    @patch("odsbox_jaquel_mcp.server.SubmatrixDataReader.get_measurement_quantities")
    def test_call_tool_data_get_quantities(self, mock_get_quantities):
        """Test calling data_get_quantities tool."""
        mock_get_quantities.return_value = [
            {
                "id": 1,
                "name": "Time",
                "measurement_quantity": {"name": "Time", "unit": "s", "datatype": 2},
            }
        ]

        result = data_get_quantities(submatrix_id=123)

        assert isinstance(result, dict)
        assert result["submatrix_id"] == 123
        assert "measurement_quantities" in result

    @patch("odsbox_jaquel_mcp.server.SubmatrixDataReader.data_read_submatrix")
    @pytest.mark.asyncio
    async def test_call_tool_data_read_submatrix(self, mock_read_data):
        """Test calling data_read_submatrix tool."""
        mock_read_data.return_value = {
            "submatrix_id": 456,
            "columns": ["Time", "Temperature"],
            "row_count": 1000,
            "preview_row_count": 100,
            "data_preview": [[1, 25.5], [2, 26.0], [3, 25.8]],
            "sampling_method": "auto",
            "note": "Preview resampled from 1000 to 100 rows using 'auto' method",
        }

        result = await data_read_submatrix(
            submatrix_id=456,
            measurement_quantity_patterns=["Temp*"],
        )

        assert isinstance(result, dict)
        assert "columns" in result
        assert "row_count" in result

    @patch("odsbox_jaquel_mcp.server.SubmatrixDataReader.get_measurement_quantities")
    @patch("odsbox_jaquel_mcp.server.generate_basic_fetcher_script")
    @pytest.mark.asyncio
    async def test_call_tool_data_generate_fetcher_script(self, mock_generate_script, mock_get_mqs):
        """Test calling data_generate_fetcher_script tool."""
        mock_get_mqs.return_value = [{"name": "Temperature"}]
        mock_generate_script.return_value = "# Generated script\nprint('Hello')"

        result = await data_generate_fetcher_script(
            submatrix_id=789,
            script_type="basic",
            output_format="csv",
        )

        assert isinstance(result, dict)
