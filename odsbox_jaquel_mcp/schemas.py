"""Entity descriptions and schema inspection for ASAM ODS Jaquel MCP Server."""

from __future__ import annotations

from typing import Any

from odsbox.model_cache import ModelCache
from odsbox.proto import ods

from .connection import ODSConnectionManager
from .schemas_entity_descriptions import EntityDescriptions


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
            entity: ods.Model.Entity = model_cache.entity(entity_name)

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
    def format_entity_schema_as_markdown(cls, entity_name: str) -> str:
        """Format entity schema as markdown for resource template.

        Args:
            entity_name: Name of the entity

        Returns:
            Markdown-formatted schema documentation
        """
        schema = cls.get_entity_schema(entity_name)

        if "error" in schema:
            return f"""# Entity Schema: {entity_name}

**Error**: {schema['error']}

{f"**Available entities**: {', '.join(schema.get('available_entities', []))}" if schema.get('available_entities') else ""}

Use `list_ods_entities` tool to see all available entities.
"""

        entity = schema.get("entity", entity_name)
        description = schema.get("description", "No description available")
        derived_from = schema.get("derived_from", "Unknown")

        md = f"""# Entity Schema: {entity}

**Base Name**: `{derived_from}`

{f"**Description**: {description}" if description else ""}

## Attributes

| Name | Base Name | Data Type | Array | Nullable |
|------|-----------|-----------|-------|----------|
"""

        for attr_name, attr_info in sorted(schema.get("attributes", {}).items()):
            is_array = "✓" if attr_info.get("is_array") else "✗"
            nullable = "✓" if attr_info.get("nullable") else "✗"
            md += f"| `{attr_name}` | `{attr_info['base_name']}` | {attr_info['data_type']} | {is_array} | {nullable} |\n"

        md += "\n## Relationships\n\n"
        md += "| Name | Target Entity | Type | Nullable | Inverse | Inverse Type |\n"
        md += "|------|---------------|------|----------|---------|---------------|\n"

        for rel_name, rel_info in sorted(schema.get("relationships", {}).items()):
            nullable = "✓" if rel_info.get("nullable") else "✗"
            md += (
                f"| `{rel_name}` | `{rel_info['target_entity']}` | "
                f"{rel_info['relationship_type']} | {nullable} | "
                f"`{rel_info['inverse_name']}` | {rel_info['relationship']} |\n"
            )

        return md

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

                condition = {"name": {"$like": "*"}}
                if current_children_relation:
                    condition[current_children_relation.inverse_name] = 4711
                query_example = {
                    current_entity.name: condition,
                    "$attributes": {"id": 1, "name": 1},
                    "$options": {"$rowlimit": 100},
                }

                hierarchy_chain.append(
                    {
                        "name": current_entity.name,
                        "base_name": current_entity.base_name,
                        "parent_relation": (
                            current_children_relation.inverse_name if current_children_relation else None
                        ),
                        "query_example": query_example,
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

            return {
                "success": True,
                "hierarchy_chain": hierarchy_chain,
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
