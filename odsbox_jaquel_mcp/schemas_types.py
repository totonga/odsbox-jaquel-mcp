"""Typed dataclasses for entity schema representations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AttributeSchema:
    """Schema information for a single entity attribute."""

    base_name: str
    data_type: str
    is_array: bool
    nullable: bool


@dataclass
class RelationshipSchema:
    """Schema information for a single entity relationship."""

    base_name: str
    target_entity: str
    inverse_name: str
    inverse_base_name: str
    relationship_type: str
    nullable: bool
    relationship: str


@dataclass
class EntitySchema:
    """Complete schema for an ODS entity."""

    entity: str
    derived_from: str
    attributes: dict[str, AttributeSchema]
    relationships: dict[str, RelationshipSchema]
    description: str | None
    example_query: dict[str, dict[str, Any]] = field(default_factory=dict)
