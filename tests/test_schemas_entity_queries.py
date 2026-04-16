from pathlib import Path

import pytest
from google.protobuf.json_format import Parse
from odsbox.model_cache import ModelCache
from odsbox.proto.ods_pb2 import Model

from odsbox_jaquel_mcp.schemas_entity_queries import SchemasEntityQueries


@pytest.fixture(scope="module")
def model() -> Model:
    model_file = Path(__file__).parent / "data" / "application_model.json"
    with open(model_file, "r", encoding="utf-8") as f:
        model_json = f.read()
        parsed_model = Parse(model_json, Model())
    return parsed_model


@pytest.fixture(scope="module")
def mc(model: Model) -> ModelCache:
    return ModelCache(model)


class TestSchemasEntityQueries:
    def test_get_important_entity_attributes_ao_measurement(self, mc: ModelCache):
        entity = mc.entity("MeaResult")

        result = SchemasEntityQueries.get_important_entity_attributes(mc, entity)

        assert "Name" in result
        assert "Id" in result
        assert "Description" in result
        assert "MeasurementBegin" in result
        assert "MeasurementEnd" in result
        assert "TestStep" in result

    def test_get_important_entity_attributes_ao_any_with_description(self, mc: ModelCache):
        """AoAny entities include description when present; no version/version_date added."""
        entity = mc.entity("TplUnitUnderTestRoot")

        result = SchemasEntityQueries.get_important_entity_attributes(mc, entity)

        assert "Name" in result
        assert "Id" in result
        assert "Description" in result

    def test_get_important_entity_attributes_ao_unit_under_test_part(self, mc: ModelCache):
        """AoUnitUnderTestPart includes parent relation and application-specific custom attrs."""
        entity = mc.entity("exhaust_piping")

        result = SchemasEntityQueries.get_important_entity_attributes(mc, entity)

        assert "Name" in result
        assert "Id" in result
        assert "UnitUnderTest" in result
        assert "material" in result
        assert "length" in result

    def test_get_important_entity_attributes_all_entities_use_attribute_names(self, model: Model, mc: ModelCache):
        for entity in model.entities.values():
            result = SchemasEntityQueries.get_important_entity_attributes(mc, entity)

            assert len(result) >= 2
            assert "Name" in result
            assert "Id" in result

            # Every key must be a real attribute or relation name on the entity.
            all_fields = set(entity.attributes.keys()) | set(entity.relations.keys())
            for field_name in result:
                assert field_name in all_fields, (
                    f"Entity '{entity.name}': '{field_name}' is neither an attribute nor a relation"
                )

    def test_default_queries_structure(self, mc: ModelCache):
        entity = mc.entity("Status")

        result = SchemasEntityQueries.default_queries(mc, entity)

        assert set(result.keys()) == {"Base Query", "Distinct Names"}

        assert result["Base Query"]["Status"] == {"Name": {"$like": "*"}}
        assert result["Base Query"]["$attributes"] == {"Name": 1, "Id": 1, "Description": 1}

        assert result["Distinct Names"] == {
            "Status": {},
            "$attributes": {"name": {"$distinct": 1}},
        }

    def test_entities(self, model: Model, mc: ModelCache):
        for entity in model.entities.values():
            queries = SchemasEntityQueries.default_queries(mc, entity)
            assert "Base Query" in queries
            assert "Distinct Names" in queries
