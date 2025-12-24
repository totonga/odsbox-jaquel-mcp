"""Integration tests for ODS connection and queries.

These tests require a live ODS server connection. Run with:
    pytest tests/test_integration_ods_connection.py -m integration

Mark all tests with @pytest.mark.integration to allow filtering.
"""

import pytest

from odsbox_jaquel_mcp import ODSConnectionManager


@pytest.mark.integration
class TestODSIntegration:
    """Integration tests against live ODS server."""

    def setup_method(self):
        """Reset singleton before each test."""
        ODSConnectionManager._instance = None
        ODSConnectionManager._con_i = None
        ODSConnectionManager._model_cache = None
        ODSConnectionManager._model = None
        ODSConnectionManager._connection_info = {}

    def teardown_method(self):
        """Clean up connection after each test."""
        if ODSConnectionManager.is_connected():
            ODSConnectionManager.disconnect()

    def test_connect_to_ods_server(self, integration_credentials):
        """Test connecting to live ODS server.

        This test verifies:
        - Connection can be established with valid credentials
        - Connection status is properly tracked
        - Server information is available
        """
        result = ODSConnectionManager.connect(
            url=integration_credentials["url"],
            auth=(integration_credentials["username"], integration_credentials["password"]),
        )

        assert result["success"] is True, f"Connection failed: {result.get('error', 'Unknown error')}"
        assert ODSConnectionManager.is_connected()
        assert result["connection"]["status"] == "connected"
        assert result["connection"]["url"] == integration_credentials["url"]
        assert result["connection"]["username"] == integration_credentials["username"]

    def test_list_entities(self, integration_credentials):
        """Test retrieving available entities from ODS server.

        This test verifies:
        - Entity list can be retrieved after connection
        - Common ODS entities are present (Measurement, Unit, Test, etc.)
        - Entity count is reasonable
        """
        ODSConnectionManager.connect(
            url=integration_credentials["url"],
            auth=(integration_credentials["username"], integration_credentials["password"]),
        )

        model = ODSConnectionManager.get_model()
        assert model is not None
        assert hasattr(model, "entities")

        entities = model.entities
        entity_names = list(entities.keys()) if hasattr(entities, "keys") else [e.name for e in entities]

        # Check for common ODS entities
        common_entities = {"Measurement", "Unit", "AoTest", "AoMeasurement"}
        available_common = common_entities.intersection(set(entity_names))

        assert len(entity_names) > 0, "No entities found in ODS server"
        assert len(available_common) > 0, f"No common ODS entities found. Available: {entity_names[:10]}"

    def test_get_model_cache(self, integration_credentials):
        """Test that model cache is properly initialized.

        This test verifies:
        - Model cache is created after connection
        - Model cache contains expected content
        """
        ODSConnectionManager.connect(
            url=integration_credentials["url"],
            auth=(integration_credentials["username"], integration_credentials["password"]),
        )

        model_cache = ODSConnectionManager.get_model_cache()
        assert model_cache is not None

    def test_query_measurements(self, integration_credentials):
        """Test executing a query for measurements.

        This test verifies:
        - Queries can be executed after connection
        - Query results are returned properly
        - Result contains expected structure
        """
        ODSConnectionManager.connect(
            url=integration_credentials["url"],
            auth=(integration_credentials["username"], integration_credentials["password"]),
        )

        # Simple query to get first few measurements
        query = {"AoMeasurement": {}}

        result = ODSConnectionManager.query(query)

        assert result["success"] is True, f"Query failed: {result.get('error', 'Unknown error')}"
        assert "result" in result
        assert result.get("entity_count", 0) >= 0

    def test_disconnect_from_ods_server(self, integration_credentials):
        """Test disconnecting from ODS server.

        This test verifies:
        - Connection can be closed properly
        - Connection state is updated
        - Cleanup is performed
        """
        ODSConnectionManager.connect(
            url=integration_credentials["url"],
            auth=(integration_credentials["username"], integration_credentials["password"]),
        )

        assert ODSConnectionManager.is_connected()

        result = ODSConnectionManager.disconnect()

        assert result["success"] is True
        assert not ODSConnectionManager.is_connected()

    def test_connection_reuse(self, integration_credentials):
        """Test that singleton connection can be reused across operations.

        This test verifies:
        - Connection is reused across multiple operations
        - Singleton pattern works correctly
        """
        # First connection
        result1 = ODSConnectionManager.connect(
            url=integration_credentials["url"],
            auth=(integration_credentials["username"], integration_credentials["password"]),
        )
        assert result1["success"] is True

        instance1 = ODSConnectionManager.get_instance()

        # Second get_instance should return same object
        instance2 = ODSConnectionManager.get_instance()
        assert instance1 is instance2

        # Connection should still be active
        assert ODSConnectionManager.is_connected()

        # Model should be accessible
        model = ODSConnectionManager.get_model()
        assert model is not None
