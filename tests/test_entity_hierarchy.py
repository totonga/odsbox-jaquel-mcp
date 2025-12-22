"""Tests for entity hierarchy functions."""

from unittest.mock import Mock, patch

from odsbox_jaquel_mcp.schemas import EntityDescriptions, SchemaInspector


class TestGetTestToMeasurementHierarchy:
    """Test cases for get_test_to_measurement_hierarchy."""

    def setup_method(self):
        """Reset singleton instance before each test."""
        from odsbox_jaquel_mcp.connection import ODSConnectionManager

        ODSConnectionManager._instance = None
        ODSConnectionManager._con_i = None
        ODSConnectionManager._model_cache = None
        ODSConnectionManager._model = None
        ODSConnectionManager._connection_info = {}

    def test_hierarchy_no_connection(self):
        """Test hierarchy retrieval without connection."""
        result = SchemaInspector.get_test_to_measurement_hierarchy()

        assert "error" in result
        assert "Model not loaded" in result["error"]
        assert "Connect to ODS server" in result["hint"]

    @patch("odsbox_jaquel_mcp.connection.ConI")
    def test_hierarchy_simple_chain(self, mock_coni_class):
        """Test hierarchy with simple AoTest -> AoMeasurement chain."""
        from odsbox_jaquel_mcp.connection import ODSConnectionManager

        # Create mock entities
        mock_ao_test = Mock()
        mock_ao_test.name = "Test"
        mock_ao_test.base_name = "AoTest"
        mock_ao_test.relations = {}

        mock_ao_measurement = Mock()
        mock_ao_measurement.name = "Measurement"
        mock_ao_measurement.base_name = "AoMeasurement"
        mock_ao_measurement.relations = {}

        # Setup ConI mock
        mock_coni = Mock()
        mock_coni.con_i_url.return_value = "http://test:8087/api"
        mock_coni.mc = Mock()

        # Mock model cache methods
        mock_model_cache = Mock()
        mock_model_cache.entity_by_base_name.side_effect = lambda name: (
            mock_ao_test if name == "AoTest" else mock_ao_measurement
        )
        mock_model_cache.relation_no_throw.return_value = None
        mock_model_cache.entity.return_value = mock_ao_measurement

        mock_coni.mc = mock_model_cache

        mock_model = Mock()
        mock_model.entities = {"Test": mock_ao_test, "Measurement": mock_ao_measurement}
        mock_coni.model.return_value = mock_model
        mock_coni_class.return_value = mock_coni

        # Connect to establish model cache
        ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        # Get hierarchy
        result = SchemaInspector.get_test_to_measurement_hierarchy()

        assert result["success"] is True
        assert result["depth"] == 1
        assert len(result["hierarchy_chain"]) == 1
        assert result["hierarchy_chain"][0]["name"] == "Test"
        assert result["hierarchy_chain"][0]["base_name"] == "AoTest"
        assert "Test" in result["hierarchy_chain"][0]["query_example"]
        assert "$attributes" in result["hierarchy_chain"][0]["query_example"]
        assert "$options" in result["hierarchy_chain"][0]["query_example"]

    @patch("odsbox_jaquel_mcp.connection.ConI")
    def test_hierarchy_three_level_chain(self, mock_coni_class):
        """Test hierarchy with AoTest -> AoSubTest -> AoMeasurement chain."""
        from odsbox_jaquel_mcp.connection import ODSConnectionManager

        # Create mock entities
        mock_ao_test = Mock()
        mock_ao_test.name = "Test"
        mock_ao_test.base_name = "AoTest"

        mock_ao_subtest = Mock()
        mock_ao_subtest.name = "SubTest"
        mock_ao_subtest.base_name = "AoSubTest"

        mock_ao_measurement = Mock()
        mock_ao_measurement.name = "Measurement"
        mock_ao_measurement.base_name = "AoMeasurement"

        # Setup relations
        mock_children_relation_1 = Mock()
        mock_children_relation_1.entity_name = "SubTest"
        mock_children_relation_1.inverse_name = "parent_test"

        mock_children_relation_2 = Mock()
        mock_children_relation_2.entity_name = "Measurement"
        mock_children_relation_2.inverse_name = "parent_test"

        mock_ao_test.relations = {}
        mock_ao_subtest.relations = {}
        mock_ao_measurement.relations = {}

        # Setup ConI mock
        mock_coni = Mock()
        mock_coni.con_i_url.return_value = "http://test:8087/api"

        # Mock model cache
        mock_model_cache = Mock()

        def entity_by_base_name(name):
            if name == "AoTest":
                return mock_ao_test
            elif name == "AoSubTest":
                return mock_ao_subtest
            else:
                return mock_ao_measurement

        def relation_no_throw(entity, rel_name):
            if entity == mock_ao_test and rel_name == "children":
                return mock_children_relation_1
            elif entity == mock_ao_subtest and rel_name == "children":
                return mock_children_relation_2
            return None

        def entity(entity_name):
            if entity_name == "SubTest":
                return mock_ao_subtest
            else:
                return mock_ao_measurement

        mock_model_cache.entity_by_base_name.side_effect = entity_by_base_name
        mock_model_cache.relation_no_throw.side_effect = relation_no_throw
        mock_model_cache.entity.side_effect = entity

        mock_coni.mc = mock_model_cache

        mock_model = Mock()
        mock_model.entities = {
            "Test": mock_ao_test,
            "SubTest": mock_ao_subtest,
            "Measurement": mock_ao_measurement,
        }
        mock_coni.model.return_value = mock_model
        mock_coni_class.return_value = mock_coni

        # Connect to establish model cache
        ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        # Get hierarchy
        result = SchemaInspector.get_test_to_measurement_hierarchy()

        assert result["success"] is True
        assert result["depth"] == 3
        assert len(result["hierarchy_chain"]) == 3
        assert result["hierarchy_chain"][0]["base_name"] == "AoTest"
        assert result["hierarchy_chain"][1]["base_name"] == "AoSubTest"
        assert result["hierarchy_chain"][1]["parent_relation"] == "parent_test"
        assert result["hierarchy_chain"][2]["base_name"] == "AoMeasurement"

    @patch("odsbox_jaquel_mcp.connection.ConI")
    def test_hierarchy_exception_handling(self, mock_coni_class):
        """Test hierarchy with exception during traversal."""
        from odsbox_jaquel_mcp.connection import ODSConnectionManager

        # Setup ConI mock
        mock_coni = Mock()
        mock_coni.con_i_url.return_value = "http://test:8087/api"

        # Mock model cache that throws exception
        mock_model_cache = Mock()
        mock_model_cache.entity_by_base_name.side_effect = Exception("Connection failed")

        mock_coni.mc = mock_model_cache

        mock_model = Mock()
        mock_model.entities = {}
        mock_coni.model.return_value = mock_model
        mock_coni_class.return_value = mock_coni

        # Connect to establish model cache
        ODSConnectionManager.connect(url="http://test:8087/api", auth=("user", "pass"))

        # Get hierarchy
        result = SchemaInspector.get_test_to_measurement_hierarchy()

        assert result["success"] is False
        assert "error" in result
        assert result["error_type"] == "Exception"
        assert result["hierarchy_chain"] == []

    def test_hierarchy_with_descriptions(self):
        """Test that entity descriptions are included in hierarchy."""
        # Verify descriptions exist for key entities
        assert EntityDescriptions.has_description("AoTest")
        assert EntityDescriptions.has_description("AoSubTest")
        assert EntityDescriptions.has_description("AoMeasurement")

        # Verify descriptions are not empty
        assert len(EntityDescriptions.get_description("AoTest")) > 0
        assert len(EntityDescriptions.get_description("AoSubTest")) > 0
        assert len(EntityDescriptions.get_description("AoMeasurement")) > 0
