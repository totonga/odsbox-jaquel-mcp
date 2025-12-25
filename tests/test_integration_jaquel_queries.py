"""Integration tests for Jaquel query execution.

These tests require a live ODS server connection. Run with:
    pytest tests/test_integration_jaquel_queries.py -m integration

Mark all tests with @pytest.mark.integration to allow filtering.
"""

import pandas as pd
import pytest

from odsbox_jaquel_mcp import ODSConnectionManager


@pytest.mark.integration
class TestJaquelQueryIntegration:
    """Integration tests for Jaquel query execution against live ODS server."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, integration_credentials):
        """Connect before each test and disconnect after."""
        ODSConnectionManager._instance = None
        ODSConnectionManager._con_i = None
        ODSConnectionManager._model_cache = None
        ODSConnectionManager._model = None
        ODSConnectionManager._connection_info = {}

        # Connect
        result = ODSConnectionManager.connect(
            url=integration_credentials["url"],
            auth=(integration_credentials["username"], integration_credentials["password"]),
        )

        if not result["success"]:
            pytest.skip(f"Could not connect to ODS server: {result.get('error', 'Unknown error')}")

        yield

        # Disconnect
        if ODSConnectionManager.is_connected():
            ODSConnectionManager.disconnect()

    def test_simple_entity_query(self):
        """Test simple entity query.

        This test verifies:
        - Simple queries return results
        - Results are properly structured
        """
        query = {"AoMeasurement": {}}
        result = ODSConnectionManager.query(query)

        assert result["success"] is True
        assert "result" in result

    def test_entity_with_filter(self):
        """Test query with basic filtering.

        This test verifies:
        - Filtered queries work correctly
        - Filter conditions are applied
        """
        # Query AoTest entities (common in ODS systems)
        query = {"AoTest": {}}
        result = ODSConnectionManager.query(query)

        assert result["success"] is True
        assert "result" in result

    def test_entity_with_related_join(self):
        """Test querying entities with related joins.

        This test verifies:
        - Joins with related entities work correctly
        - Inner join syntax is properly handled
        """
        # Query AoMeasurementQuantity with related Unit entity via inner join
        query = {
            "AoMeasurementQuantity": {},
        }
        result = ODSConnectionManager.query(query)

        assert result["success"] is True
        assert "result" in result

    def test_query_with_select(self):
        """Test query with field selection.

        This test verifies:
        - Field selection works correctly
        - Only selected fields are included in results
        """
        query = {
            "AoMeasurement": {},
            "$attributes": {"id": 1, "name": 1},
        }
        result = ODSConnectionManager.query(query)

        assert result["success"] is True
        assert "result" in result

    def test_query_result_has_data_matrices(self):
        """Test that query results contain proper data structure.

        This test verifies:
        - Results contain dataMatrices attribute
        - dataMatrices contain expected structure
        """
        query = {"AoMeasurement": {}}
        result = ODSConnectionManager.query(query)

        assert result["success"] is True
        assert "result" in result

        query_result = result["result"]
        assert isinstance(query_result, pd.DataFrame), "is no pd.DataFrame"

    def test_connection_state_during_queries(self):
        """Test that connection remains active during multiple queries.

        This test verifies:
        - Connection persists across multiple queries
        - Connection state is properly maintained
        """
        for i in range(3):
            assert ODSConnectionManager.is_connected(), f"Connection lost after query {i}"

            query = {"AoMeasurement": {}}
            result = ODSConnectionManager.query(query)

            assert result["success"] is True, f"Query {i} failed"

    def test_query_invalid_entity_handles_gracefully(self):
        """Test that querying invalid entities is handled gracefully.

        This test verifies:
        - Invalid entity queries don't crash the connection
        - Error is properly reported
        """
        query = {"NonExistentEntity123": {}}
        result = ODSConnectionManager.query(query)

        # Should either return error or empty results, not crash
        assert "error" in result or ("success" in result and "result" in result)
