"""Tests for ODSConnectionManager."""

from unittest.mock import Mock, patch

from odsbox_jaquel_mcp import ODSConnectionManager


class TestODSConnectionManager:
    """Test cases for ODSConnectionManager singleton."""

    def setup_method(self):
        """Reset singleton instance before each test."""
        ODSConnectionManager._instance = None
        ODSConnectionManager._con_i = None
        ODSConnectionManager._model_cache = None
        ODSConnectionManager._model = None
        ODSConnectionManager._connection_info = {}

    def test_get_instance_creates_singleton(self):
        """Test that get_instance creates a singleton."""
        instance1 = ODSConnectionManager.get_instance()
        instance2 = ODSConnectionManager.get_instance()

        assert instance1 is instance2
        assert isinstance(instance1, ODSConnectionManager)

    def test_initial_state(self):
        """Test initial state of connection manager."""
        instance = ODSConnectionManager.get_instance()

        assert instance._con_i is None
        assert instance._model_cache is None
        assert instance._model is None
        assert instance._connection_info == {}
        assert not ODSConnectionManager.is_connected()

    @patch("odsbox_jaquel_mcp.connection.ODSBOX_AVAILABLE", True)
    @patch("odsbox_jaquel_mcp.connection.ConI")
    def test_connect_success(self, mock_coni_class):
        """Test successful connection to ODS server."""
        # Mock ConI instance
        mock_coni = Mock()
        mock_coni.con_i_url.return_value = "http://test:8087/api"
        mock_coni.mc = Mock()
        mock_model = Mock()
        mock_model.entities = {"Measurement": Mock(), "Unit": Mock(), "Test": Mock()}
        mock_coni.model.return_value = mock_model
        mock_coni_class.return_value = mock_coni

        result = ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        assert result["success"] is True
        assert "Connected to ODS server" in result["message"]
        assert result["connection"]["url"] == "http://test:8087/api"
        assert result["connection"]["username"] == "user"
        assert result["connection"]["status"] == "connected"
        assert result["connection"]["available_entities"] == ["Measurement", "Unit", "Test"]
        assert ODSConnectionManager.is_connected()

    @patch("odsbox_jaquel_mcp.connection.ODSBOX_AVAILABLE", False)
    def test_connect_odsbox_not_available(self):
        """Test connection when odsbox is not available."""
        result = ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        assert result["success"] is False
        assert result["error"] == "odsbox not installed"
        assert not ODSConnectionManager.is_connected()

    @patch("odsbox_jaquel_mcp.connection.ODSBOX_AVAILABLE", True)
    @patch("odsbox_jaquel_mcp.connection.ConI")
    def test_connect_failure(self, mock_coni_class):
        """Test connection failure."""
        mock_coni_class.side_effect = Exception("Connection failed")

        result = ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        assert result["success"] is False
        assert result["error"] == "Connection failed"
        assert result["error_type"] == "Exception"
        assert not ODSConnectionManager.is_connected()

    @patch("odsbox_jaquel_mcp.connection.ODSBOX_AVAILABLE", True)
    @patch("odsbox_jaquel_mcp.connection.ConI")
    def test_disconnect_success(self, mock_coni_class):
        """Test successful disconnection."""
        # First connect
        mock_coni = Mock()
        mock_coni.close.return_value = None
        mock_coni_class.return_value = mock_coni

        ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        # Then disconnect
        result = ODSConnectionManager.disconnect()

        assert result["success"] is True
        assert "Disconnected from ODS server" in result["message"]
        assert not ODSConnectionManager.is_connected()
        mock_coni.close.assert_called_once()

    def test_disconnect_when_not_connected(self):
        """Test disconnect when not connected."""
        result = ODSConnectionManager.disconnect()

        assert result["success"] is True
        assert "Disconnected from ODS server" in result["message"]

    @patch("odsbox_jaquel_mcp.connection.ODSBOX_AVAILABLE", True)
    @patch("odsbox_jaquel_mcp.connection.ConI")
    def test_disconnect_failure(self, mock_coni_class):
        """Test disconnect failure."""
        # First connect
        mock_coni = Mock()
        mock_coni.close.side_effect = Exception("Close failed")
        mock_coni_class.return_value = mock_coni

        ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        # Then disconnect
        result = ODSConnectionManager.disconnect()

        assert result["success"] is False
        assert result["error"] == "Close failed"

    def test_get_connection_info(self):
        """Test getting connection info."""
        info = ODSConnectionManager.get_connection_info()
        assert info == {}

        # Set some connection info
        instance = ODSConnectionManager.get_instance()
        instance._connection_info = {"test": "data"}

        info = ODSConnectionManager.get_connection_info()
        assert info == {"test": "data"}

    def test_get_model_cache_and_model(self):
        """Test getting model cache and model."""
        assert ODSConnectionManager.get_model_cache() is None
        assert ODSConnectionManager.get_model() is None

        # Set mock objects
        instance = ODSConnectionManager.get_instance()
        mock_cache = Mock()
        mock_model = Mock()
        instance._model_cache = mock_cache
        instance._model = mock_model

        assert ODSConnectionManager.get_model_cache() is mock_cache
        assert ODSConnectionManager.get_model() is mock_model

    @patch("odsbox_jaquel_mcp.connection.ODSBOX_AVAILABLE", True)
    @patch("odsbox_jaquel_mcp.connection.ConI")
    def test_query_success(self, mock_coni_class):
        """Test successful query execution."""
        # Setup connection
        mock_coni = Mock()
        mock_result = Mock()
        mock_result.dataMatrices = [Mock(), Mock()]  # 2 entities
        mock_coni.query_data.return_value = mock_result
        mock_coni_class.return_value = mock_coni

        ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        # Execute query
        query = {"TestEntity": {}}
        result = ODSConnectionManager.query(query)

        assert result["success"] is True
        assert result["result"] is mock_result
        assert result["entity_count"] == 2
        mock_coni.query_data.assert_called_once_with(query)

    def test_query_not_connected(self):
        """Test query when not connected."""
        query = {"TestEntity": {}}
        result = ODSConnectionManager.query(query)

        assert "error" in result
        assert "Not connected to ODS server" in result["error"]

    @patch("odsbox_jaquel_mcp.connection.ODSBOX_AVAILABLE", True)
    @patch("odsbox_jaquel_mcp.connection.ConI")
    def test_query_failure(self, mock_coni_class):
        """Test query execution failure."""
        # Setup connection
        mock_coni = Mock()
        mock_coni.query_data.side_effect = Exception("Query failed")
        mock_coni_class.return_value = mock_coni

        ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        # Execute query
        query = {"TestEntity": {}}
        result = ODSConnectionManager.query(query)

        assert "error" in result
        assert result["error"] == "Query failed"
        assert result["error_type"] == "Exception"
