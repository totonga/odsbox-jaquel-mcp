"""
Create some default queries for entities.
"""

from typing import Any

from odsbox.model_cache import ModelCache
from odsbox.proto import ods


class SchemasEntityQueries:
    @staticmethod
    def get_important_entity_attributes(mc: ModelCache, entity: ods.Model.Entity) -> dict[str, int | dict[str, Any]]:
        """Get the important attributes for an entity."""
        important_attributes: dict[str, int | dict[str, Any]] = {}

        base_names = ["name", "id", "description"]

        if entity.base_name == "AoEnvironment":
            base_names.append("timezone")
            base_names.append("base_model_version")
        if entity.base_name == "AoSubTest":
            base_names.append("parent_test")
        elif entity.base_name == "AoMeasurement":
            base_names.append("measurement_begin")
            base_names.append("measurement_end")
            base_names.append("test")
        elif entity.base_name == "AoSubmatrix":
            base_names.append("number_of_rows")
            base_names.append("measurement")
        elif entity.base_name == "AoMeasurementQuantity":
            base_names.append("datatype")
            base_names.append("measurement")
            base_names.append("unit")
            base_names.append("quantity")
        elif entity.base_name == "AoLocalColumn":
            base_names.append("independent")
            base_names.append("sequence_representation")
            base_names.append("measurement_quantity")
            base_names.append("submatrix")
        elif entity.base_name == "AoUnit":
            base_names.append("factor")
            base_names.append("offset")
            base_names.append("phys_dimension")
        elif entity.base_name == "AoQuantity":
            base_names.append("default_unit")
        elif entity.base_name == "AoTestSequencePart":
            base_names.append("parent_sequence")
        elif entity.base_name == "AoTestEquipmentPart":
            base_names.append("parent_equipment")
        elif entity.base_name == "AoUnitUnderTestPart":
            base_names.append("parent_unit_under_test")

        for base_name in base_names:
            attr_or_rel = mc.attribute_no_throw(entity, base_name) or mc.relation_no_throw(entity, base_name)
            if attr_or_rel is not None:
                important_attributes[attr_or_rel.name] = 1

        if entity.base_name in ["AoUnitUnderTestPart", "AoTestEquipmentPart", "AoTestSequencePart"]:
            for attr in entity.attributes.values():
                if attr.base_name is None or attr.base_name == "":
                    # application attributes added to the part are important for the usage
                    important_attributes[attr.name] = 1

        return important_attributes

    @staticmethod
    def default_queries(mc: ModelCache, entity: ods.Model.Entity) -> dict[str, dict[str, Any]]:
        """Create a default query for an entity."""
        queries: dict[str, dict[str, Any]] = {}
        name_attribute = mc.attribute_by_base_name(entity, "name")

        queries["Base Query"] = {
            entity.name: {name_attribute.name: {"$like": "*"}},
            "$attributes": SchemasEntityQueries.get_important_entity_attributes(mc, entity),
        }
        queries["Distinct Names"] = {entity.name: {}, "$attributes": {"name": {"$distinct": 1}}}

        return queries
