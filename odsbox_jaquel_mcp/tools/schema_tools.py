"""Schema validation tool handlers."""

from __future__ import annotations

from typing import Any

from mcp.types import TextContent

from ..schemas import SchemaInspector
from .base_handler import BaseToolHandler


class SchemaToolHandler(BaseToolHandler):
    """Handles schema inspection and validation tools."""

    @staticmethod
    def schema_get_entity(arguments: dict[str, Any]) -> list[TextContent]:
        """Get available fields for an entity."""
        try:
            entity_name = arguments.get("entity_name")
            if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
                raise ValueError("entity_name must be a non-empty string")
            result = SchemaInspector.get_entity_schema(entity_name)
            return SchemaToolHandler.json_response(result)
        except Exception as e:
            return SchemaToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def schema_field_exists(arguments: dict[str, Any]) -> list[TextContent]:
        """Check if a field (attribute or relationship) exists in entity schema."""
        try:
            entity_name = arguments.get("entity_name")
            if not entity_name or not isinstance(entity_name, str) or not entity_name.strip():
                raise ValueError("entity_name must be a non-empty string")
            field_name = arguments.get("field_name")
            if not field_name or not isinstance(field_name, str) or not field_name.strip():
                raise ValueError("field_name must be a non-empty string")
            result = SchemaInspector.schema_field_exists(entity_name, field_name)
            return SchemaToolHandler.json_response(result)
        except Exception as e:
            return SchemaToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def schema_list_entities(arguments: dict[str, Any]) -> list[TextContent]:
        """List all available ODS entities."""
        try:
            result = SchemaInspector.schema_list_entities()
            return SchemaToolHandler.json_response(result)
        except Exception as e:
            return SchemaToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def schema_test_to_measurement_hierarchy(arguments: dict[str, Any]) -> list[TextContent]:
        """Get hierarchical entity chain from AoTest to AoMeasurement."""
        try:
            result = SchemaInspector.schema_test_to_measurement_hierarchy()
            return SchemaToolHandler.json_response(result)
        except Exception as e:
            return SchemaToolHandler.error_response(str(e), type(e).__name__)
