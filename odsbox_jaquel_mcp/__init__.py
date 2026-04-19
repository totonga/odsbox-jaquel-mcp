"""ASAM ODS Jaquel MCP Server - A Model Context Protocol server for Jaquel queries."""

try:
    from importlib.metadata import version

    __version__ = version("odsbox-jaquel-mcp")
except Exception:
    __version__ = "0.0.0.dev0"

__author__ = "Assistant"

from .connection import ODSConnectionManager
from .notebook_generator import NotebookGenerator
from .queries import JaquelExamples
from .schemas import EntityDescriptions, SchemaInspector
from .schemas_types import AttributeSchema, ConnectionInfo, ConnectResult, EntitySchema, RelationshipSchema
from .submatrix import SubmatrixDataReader
from .validators import JaquelValidator
from .visualization_templates import VisualizationTemplateGenerator

__all__ = [
    "ODSConnectionManager",
    "JaquelValidator",
    "JaquelExamples",
    "EntityDescriptions",
    "SchemaInspector",
    "AttributeSchema",
    "RelationshipSchema",
    "EntitySchema",
    "ConnectionInfo",
    "ConnectResult",
    "SubmatrixDataReader",
    "VisualizationTemplateGenerator",
    "NotebookGenerator",
]
