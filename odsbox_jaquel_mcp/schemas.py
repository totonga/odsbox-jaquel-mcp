"""Entity descriptions and schema inspection for ASAM ODS Jaquel MCP Server."""

from __future__ import annotations

from typing import Any

try:
    from odsbox.proto import ods
    from odsbox.model_cache import ModelCache

    ODSBOX_AVAILABLE = True
except ImportError:
    ODSBOX_AVAILABLE = False

from .connection import ODSConnectionManager


class EntityDescriptions:
    """Entity descriptions for ASAM ODS model."""

    DESCRIPTIONS = {
        "AoEnvironment": (
            "The main entry point to the ASAM ODS storage, used to "
            "describe the environment and store global information like "
            "the base model version and timezone data. Only one "
            "instance is allowed."
        ),
        "AoNameMap": (
            "Used to store lists of alias names for Application "
            "Elements, primarily supporting multi-language environments."
        ),
        "AoAttributeMap": ("Used to store lists of alias names for application attributes and relations."),
        "AoFile": (
            "Represents an external file in the ODS server namespace that is under the control of the ODS server."
        ),
        "AoMimetypeMap": ("Used to manage multiple MIME types that can be associated with an instance."),
        "AoQuantity": (
            "Describes a physical quantity (e.g., force, temperature). "
            "It serves as a base for measurement quantities and relates "
            "to a physical dimension."
        ),
        "AoUnit": ("Represents information about a specific physical unit (e.g., Newton, Kelvin)."),
        "AoPhysicalDimension": (
            "Specifies the physical dimension of a unit based on "
            "characteristics in the SI system (e.g., length, time, "
            "mass)."
        ),
        "AoQuantityGroup": ("Allows for the logical grouping of quantities based on application-specific criteria."),
        "AoUnitGroup": ("Allows for the logical grouping of units."),
        "AoMeasurement": (
            "The primary container for a complete measurement or test case. Represents a single "
            "data acquisition session that contains all measurement data, metadata, and associated "
            "submatrices. Links to the test hierarchy and manages timeseries data through Local Columns."
        ),
        "AoMeasurementQuantity": (
            "Represents a specific measured or set physical quantity used within a measurement case."
        ),
        "AoSubmatrix": (
            "A container used to manage and group related Local Columns "
            "that hold timeseries data corresponding to the same "
            "measurement points."
        ),
        "AoLocalColumn": (
            "Stores the actual mass data (values and flags) for exactly one measurement quantity (column)."
        ),
        "AoExternalComponent": (
            "Describes the location and structure of mass data stored in "
            "an external binary file, as referenced by a Local Column to "
            "store values."
        ),
        "AoTest": (
            "The root entity of the test hierarchy representing test campaigns or programs. "
            "Organizes test activities creating a multi-level "
            "tree structure from AoTest through multiple AoSubTest levels down to individual AoMeasurement instances."
        ),
        "AoSubTest": (
            "An intermediate level in the test hierarchy that enables the organization of complex test scenarios. "
            "Allows for grouping related measurements under logical sub-test categories, creating a multi-level "
            "tree structure from AoTest through multiple AoSubTest levels down to individual AoMeasurement instances. "
            "Supports hierarchical test planning and result organization."
        ),
        "AoUnitUnderTest": ("Represents the complete object undergoing testing (UUT)."),
        "AoUnitUnderTestPart": ("Represents individual parts or components of the Unit Under Test."),
        "AoTestSequence": ("Defines the overall test procedure or plan executed."),
        "AoTestSequencePart": ("Defines parts of a defined test sequence."),
        "AoTestEquipment": ("Represents the primary test equipment used during a test."),
        "AoTestEquipmentPart": ("Represents parts or components of the test equipment."),
        "AoTestDevice": ("A specialized base element primarily intended for representing specific test devices."),
        "AoUser": ("Used for managing and storing user identification data."),
        "AoUserGroup": ("Used for storing definitions of user groups, typically for access control lists (ACLs)."),
        "AoParameter": (
            "Used to define precise properties or characteristics of "
            "other application elements when no real attributes have "
            "been assigned."
        ),
        "AoParameterSet": ("A container used to group multiple instances of AoParameter."),
        "AoLog": ("Used for storing various types of log data. This entity is almost never used in practice."),
        "AoAny": (
            "A generic base element serving as a template from which "
            "application elements can be derived freely and arbitrarily "
            "often to model non-standard application data."
        ),
    }

    @staticmethod
    def get_entity_description(entity: ods.Model.Entity) -> str | None:
        """Get description for an entity.

        Args:
            entity: The entity object
        Returns:
            Description string or None if not found
        """
        if entity.base_name == "AoAny":
            if entity.name.startswith("Tpl"):
                return "openMDM Template Entity. Used for administration."
            if entity.name.startswith("Cat"):
                return "openMDM Catalog Entity. Used for administration."

        return EntityDescriptions.get_description(entity.base_name)

    @staticmethod
    def get_description(entity_base_name: str) -> str | None:
        """Get description for an entity.

        Args:
            entity_base_name: The entity name

        Returns:
            Description string or None if not found
        """
        # Try direct lookup first
        if entity_base_name in EntityDescriptions.DESCRIPTIONS:
            return EntityDescriptions.DESCRIPTIONS[entity_base_name]

        # Fall back to case-insensitive lookup
        for key, value in EntityDescriptions.DESCRIPTIONS.items():
            if key.lower() == entity_base_name.lower():
                return value
        return None

    @staticmethod
    def has_description(entity_base_name: str) -> bool:
        """Check if entity has a description.

        Args:
            entity_name: The entity name

        Returns:
            True if description exists, False otherwise
        """
        # Try direct lookup first
        if entity_base_name in EntityDescriptions.DESCRIPTIONS:
            return True

        # Fall back to case-insensitive lookup
        for key in EntityDescriptions.DESCRIPTIONS.keys():
            if key.lower() == entity_base_name.lower():
                return True
        return False

    @staticmethod
    def list_base_entities() -> list[str]:
        """Get list of all entities with descriptions.

        Returns:
            list of entity names
        """
        return sorted(EntityDescriptions.DESCRIPTIONS.keys())


class SchemaInspector:
    """Inspect ODS model schema via ConI/ModelCache."""

    @classmethod
    def _get_model(cls) -> ods.Model:
        """Get model cache from connection manager."""
        return ODSConnectionManager.get_model()

    @classmethod
    def _get_model_cache(cls) -> ModelCache:
        """Get model cache from connection manager."""
        return ODSConnectionManager.get_model_cache()

    @staticmethod
    def _get_entity(mc: ModelCache, entity_name: str) -> ods.Model.Entity:
        """
        Get the entity name.

        :param str entity_name: case insensitive name of an entity.
        :raises ValueError: If the entity does not exist.
        """
        model = mc.model()
        entity = model.entities.get(entity_name)
        if entity is not None:
            return entity
        name_casefold = entity_name.casefold()
        for key, entity in model.entities.items():
            if key.casefold() == name_casefold:
                return entity
            if name_casefold == entity.base_name.casefold():
                # return the first found
                return entity

        raise ValueError(f"No entity named '{entity_name}' found.")

    @classmethod
    def list_ods_entities(cls) -> dict[str, Any]:
        """List all entities in the ODS model."""
        model = cls._get_model()
        if not model:
            return {
                "error": "Model not loaded",
                "hint": ("Connect to ODS server using 'connect_ods_server' tool first"),
            }

        entities = []
        for _entity_name, entity in model.entities.items():
            entities.append(
                {
                    "name": entity.name,
                    "basename": entity.base_name,
                    "relations": list(entity.relations.keys()),
                    "description": EntityDescriptions.get_entity_description(entity),
                }
            )

        result = {"count": len(entities), "entities": entities}
        return result

    @classmethod
    def get_entity_schema(cls, entity_name: str) -> dict[str, Any]:
        """Get schema for an entity from model."""
        model_cache: ModelCache = cls._get_model_cache()

        if not model_cache:
            return {
                "error": "Model not loaded",
                "hint": ("Connect to ODS server using 'connect_ods_server' tool first"),
            }

        try:
            entity: ods.Model.Entity = SchemaInspector._get_entity(model_cache, entity_name)
            if not entity:
                # Try to get available entities
                try:
                    model = ODSConnectionManager.get_model()
                    available = [e.name for e in model.entities][:10] if model else []
                except Exception:
                    available = []

                return {"error": (f"Entity not found: {entity_name}"), "available_entities": available}

            # Get attributes
            attributes = {}
            for attr_name, attr in entity.attributes.items():
                attr_datatype = ods.DataTypeEnum.Name(attr.data_type)
                attr_is_array = True if attr_datatype.startswith("DS_") or attr_datatype == "DT_UNKNOWN" else False
                attributes[attr_name] = {
                    "base_name": attr.base_name,
                    "data_type": ods.DataTypeEnum.Name(attr.data_type)[3:],
                    "is_array": attr_is_array,
                    "nullable": attr.obligatory is False,
                }

            # Get relationships
            relationships = {}
            for rel_name, rel in entity.relations.items():
                rel_type = {
                    (-1, -1): "n:m",
                    (1, -1): "1:n",
                }.get((rel.range_max, rel.inverse_range_max), "n:1")
                rel_nullable = rel.range_min == 0
                relationships[rel_name] = {
                    "base_name": rel.base_name,
                    "target_entity": rel.entity_name,
                    "inverse_name": rel.inverse_name,
                    "inverse_base_name": rel.inverse_base_name,
                    "relationship_type": rel_type,
                    "nullable": rel_nullable,
                    "relationship": ods.Model.RelationshipEnum.Name(rel.relationship)[3:],
                }

            return {
                "entity": entity.name,
                "derived_from": entity.base_name,
                "attributes": attributes,
                "relationships": relationships,
                "description": EntityDescriptions.get_entity_description(entity),
            }

        except Exception as e:
            return {"error": str(e), "entity": entity_name}

    @classmethod
    def validate_field_exists(cls, entity_name: str, field_name: str) -> dict[str, Any]:
        """Check if field exists in entity."""
        schema = cls.get_entity_schema(entity_name)

        if "error" in schema:
            return schema

        # Check attributes
        if field_name in schema["attributes"]:
            return {"exists": True, "type": "attribute", "field_info": schema["attributes"][field_name]}

        # Check relationships
        if field_name in schema["relationships"]:
            return {"exists": True, "type": "relationship", "field_info": schema["relationships"][field_name]}

        # Field doesn't exist
        available = list(schema["attributes"].keys()) + list(schema["relationships"].keys())
        return {
            "exists": False,
            "entity": entity_name,
            "field": field_name,
            "available_fields": available,
            "suggestions": [f for f in available if field_name.lower() in f.lower()][:5],
        }

    @classmethod
    def validate_filter_against_schema(cls, entity_name: str, filter_condition: dict[str, Any]) -> dict[str, Any]:
        """Validate filter against actual schema."""
        from .validators import JaquelValidator

        schema = cls.get_entity_schema(entity_name)

        if "error" in schema:
            return schema

        issues = []
        suggestions = []

        for field, value in filter_condition.items():
            # Check if field exists
            field_check = cls.validate_field_exists(entity_name, field)

            if not field_check.get("exists"):
                issues.append(f"Field '{field}' not found in " f"{entity_name}")
                if field_check.get("suggestions"):
                    suggestions.extend(field_check["suggestions"])
                continue

            # Check data type compatibility
            if isinstance(value, dict):
                for op, _op_value in value.items():
                    if op.startswith("$"):
                        if op not in (JaquelValidator.ALL_OPERATORS):
                            issues.append(f"Unknown operator: {op}")

        return {
            "entity": entity_name,
            "filter": filter_condition,
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
        }

    @classmethod
    def get_test_to_measurement_hierarchy(cls) -> dict[str, Any]:
        """Get hierarchical entity chain from AoTest to AoMeasurement via 'children' relation.

        This traverses the main ASAM ODS hierarchy:
        AoTest -> (children) -> AoSubTest -> (children) -> ... -> AoMeasurement

        Returns:
            Dict containing hierarchy chain and relationships
        """
        model_cache: ModelCache = cls._get_model_cache()
        if not model_cache:
            return {
                "error": "Model not loaded",
                "hint": "Connect to ODS server using 'connect_ods_server' tool first",
            }

        hierarchy_chain = []
        try:
            visited = set()

            # Start with AoTest base entity
            current_entity = model_cache.entity_by_base_name("AoTest")
            current_children_relation = None

            # Traverse from AoTest following 'children' relation
            while current_entity and current_entity.name not in visited:
                visited.add(current_entity.name)
                hierarchy_chain.append(
                    {
                        "name": current_entity.name,
                        "base_name": current_entity.base_name,
                        "parent_relation": (
                            current_children_relation.inverse_name if current_children_relation else None
                        ),
                        "description": EntityDescriptions.get_entity_description(current_entity),
                    }
                )

                # Look for 'children' relation to find next entity
                current_children_relation = model_cache.relation_no_throw(current_entity, "children")
                if current_children_relation:
                    current_entity = model_cache.entity(current_children_relation.entity_name)
                else:
                    # No more children relation
                    break

            hierarchy_queries = []
            parent_id = 4711
            for item in hierarchy_chain:
                condition = {"name": {"$like": "*"}}
                if item["parent_relation"]:
                    condition = {item["parent_relation"]: 4711}
                    parent_id += 1
                query = {item["name"]: condition, "$attributes": {"id": 1, "name": 1}}
                hierarchy_queries.append(query)

            return {
                "success": True,
                "hierarchy_chain": hierarchy_chain,
                "hierarchy_chain_queries": hierarchy_queries,
                "depth": len(hierarchy_chain),
                "note": "This is the main AoTest to AoMeasurement hierarchy in this ASAM ODS server",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "hierarchy_chain": hierarchy_chain,
            }
