"""Tests for EntityDescriptions class."""

import pytest

from odsbox_jaquel_mcp.schemas_entity_descriptions import EntityDescriptions


class TestEntityDescriptions:
    """Test cases for EntityDescriptions class."""

    def test_descriptions_dict_not_empty(self):
        """Test that descriptions dictionary is not empty."""
        assert len(EntityDescriptions.DESCRIPTIONS) > 0

    def test_get_description_existing_entity(self):
        """Test getting description for existing entity."""
        desc = EntityDescriptions.get_description("AoTest")
        assert desc is not None
        assert len(desc) > 0
        assert "test" in desc.lower()

    def test_get_description_case_insensitive(self):
        """Test that get_description is case-insensitive."""
        desc_upper = EntityDescriptions.get_description("AOTEST")
        desc_lower = EntityDescriptions.get_description("aotest")
        desc_normal = EntityDescriptions.get_description("AoTest")

        assert desc_upper == desc_normal
        assert desc_lower == desc_normal

    def test_get_description_nonexistent_entity(self):
        """Test getting description for nonexistent entity."""
        desc = EntityDescriptions.get_description("NonexistentEntity")
        assert desc is None

    def test_has_description_existing_entity(self):
        """Test checking if entity has description."""
        assert EntityDescriptions.has_description("AoTest") is True
        assert EntityDescriptions.has_description("AoMeasurement") is True
        assert EntityDescriptions.has_description("AoSubTest") is True

    def test_has_description_case_insensitive(self):
        """Test that has_description is case-insensitive."""
        assert EntityDescriptions.has_description("AOTEST") is True
        assert EntityDescriptions.has_description("aotest") is True
        assert EntityDescriptions.has_description("AoTest") is True

    def test_has_description_nonexistent_entity(self):
        """Test checking description for nonexistent entity."""
        assert EntityDescriptions.has_description("NonexistentEntity") is False

    def test_list_base_entities_returns_sorted_list(self):
        """Test that list_base_entities returns sorted list of entities."""
        entities = EntityDescriptions.list_base_entities()
        assert isinstance(entities, list)
        assert len(entities) > 0
        # Check if list is sorted
        assert entities == sorted(entities)

    def test_list_base_entities_contains_known_entities(self):
        """Test that list contains known entities."""
        entities = EntityDescriptions.list_base_entities()
        assert "AoTest" in entities
        assert "AoMeasurement" in entities
        assert "AoSubTest" in entities
        assert "AoEnvironment" in entities

    def test_all_descriptions_are_strings(self):
        """Test that all descriptions in dictionary are strings."""
        for entity_name, description in EntityDescriptions.DESCRIPTIONS.items():
            assert isinstance(description, str), f"Description for {entity_name} is not a string"
            assert len(description) > 0, f"Description for {entity_name} is empty"

    def test_all_entities_in_list_have_description(self):
        """Test that all entities returned by list_base_entities have descriptions."""
        entities = EntityDescriptions.list_base_entities()
        for entity in entities:
            assert entity in EntityDescriptions.DESCRIPTIONS, f"Entity {entity} not in DESCRIPTIONS"
            desc = EntityDescriptions.get_description(entity)
            assert desc is not None, f"get_description returned None for {entity}"
