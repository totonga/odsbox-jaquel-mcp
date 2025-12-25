"""Entity descriptions for ASAM ODS model."""

from __future__ import annotations

from odsbox.proto import ods


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
