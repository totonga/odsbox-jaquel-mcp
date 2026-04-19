from pathlib import Path
from unittest.mock import patch

import pytest
from google.protobuf.json_format import Parse
from odsbox.model_cache import ModelCache
from odsbox.proto.ods_pb2 import Model

from odsbox_jaquel_mcp.schemas import SchemaInspector
from odsbox_jaquel_mcp.schemas_entity_queries import SchemasEntityQueries
from odsbox_jaquel_mcp.schemas_types import AttributeSchema, EntitySchema, RelationshipSchema


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


class TestSchemaInspector:
    """Tests for SchemaInspector using real application model fixtures."""

    def test_get_entity_schema_returns_entity_schema(self, model: Model, mc: ModelCache):
        with (
            patch.object(SchemaInspector, "_get_model_cache", return_value=mc),
            patch.object(SchemaInspector, "_get_model", return_value=model),
        ):
            result = SchemaInspector.get_entity_schema("MeaResult")

        assert isinstance(result, EntitySchema)
        assert result.entity == "MeaResult"
        assert result.derived_from == "AoMeasurement"

    def test_get_entity_schema_attributes_are_typed(self, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            result = SchemaInspector.get_entity_schema("MeaResult")

        assert "Name" in result.attributes
        attr = result.attributes["Name"]
        assert isinstance(attr, AttributeSchema)
        assert attr.base_name == "name"
        assert attr.data_type == "STRING"
        assert attr.is_array is False
        assert attr.nullable is False

    def test_get_entity_schema_relationships_are_typed(self, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            result = SchemaInspector.get_entity_schema("MeaResult")

        assert "TestStep" in result.relationships
        rel = result.relationships["TestStep"]
        assert isinstance(rel, RelationshipSchema)
        assert rel.target_entity == "TestStep"
        assert rel.inverse_name == "MeaResults"
        assert rel.relationship_type in ("n:1", "1:n", "n:m")

    def test_get_entity_schema_has_description(self, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            result = SchemaInspector.get_entity_schema("MeaResult")

        assert result.description is not None
        assert "measurement" in result.description.lower()

    def test_get_entity_schema_has_example_query(self, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            result = SchemaInspector.get_entity_schema("MeaResult")

        assert "Base Query" in result.example_query
        assert "Distinct Names" in result.example_query

    def test_get_entity_schema_unknown_entity_raises(self, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            with pytest.raises(ValueError, match="Schema lookup failed"):
                SchemaInspector.get_entity_schema("NonExistentEntity")

    def test_get_entity_schema_all_entities(self, model: Model, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            for entity_name in model.entities:
                result = SchemaInspector.get_entity_schema(entity_name)

                assert isinstance(result, EntitySchema)
                assert result.entity == entity_name
                assert len(result.attributes) > 0

    def test_schema_list_entities(self, model: Model, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model", return_value=model):
            result = SchemaInspector.schema_list_entities()

        assert result["count"] == len(model.entities)
        assert len(result["entities"]) == len(model.entities)
        names = {e["name"] for e in result["entities"]}
        assert "MeaResult" in names
        assert "TestStep" in names

    def test_schema_field_exists_attribute(self, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            result = SchemaInspector.schema_field_exists("MeaResult", "Name")

        assert result["exists"] is True
        assert result["type"] == "attribute"
        assert isinstance(result["field_info"], AttributeSchema)

    def test_schema_field_exists_relationship(self, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            result = SchemaInspector.schema_field_exists("MeaResult", "TestStep")

        assert result["exists"] is True
        assert result["type"] == "relationship"
        assert isinstance(result["field_info"], RelationshipSchema)

    def test_schema_field_exists_not_found(self, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            result = SchemaInspector.schema_field_exists("MeaResult", "nonexistent_field")

        assert result["exists"] is False
        assert "available_fields" in result

    def test_format_entity_schema_as_markdown(self, mc: ModelCache):
        with patch.object(SchemaInspector, "_get_model_cache", return_value=mc):
            md = SchemaInspector.format_entity_schema_as_markdown("MeaResult")

        assert "# Entity Schema: MeaResult" in md
        assert "AoMeasurement" in md
        assert "## Attributes" in md
        assert "## Relationships" in md
        assert "`Name`" in md
        assert "`TestStep`" in md

    def test_schema_test_to_measurement_hierarchy(self, model: Model, mc: ModelCache):
        with (
            patch.object(SchemaInspector, "_get_model_cache", return_value=mc),
            patch.object(SchemaInspector, "_get_model", return_value=model),
        ):
            result = SchemaInspector.schema_test_to_measurement_hierarchy()

        assert result["depth"] >= 2
        base_names = [e["base_name"] for e in result["hierarchy_chain"]]
        assert "AoTest" in base_names
        assert "AoMeasurement" in base_names
