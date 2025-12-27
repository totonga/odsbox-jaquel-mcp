"""Submatrix data access tool handlers."""

from __future__ import annotations

from typing import Any

from mcp.types import TextContent

from ..submatrix import SubmatrixDataReader
from ..submatrix.scripts import (
    generate_advanced_fetcher_script,
    generate_analysis_fetcher_script,
    generate_basic_fetcher_script,
    generate_batch_fetcher_script,
)
from .base_handler import BaseToolHandler


class SubmatrixToolHandler(BaseToolHandler):
    """Handles submatrix data access tools."""

    @staticmethod
    def data_get_quantities(arguments: dict[str, Any]) -> list[TextContent]:
        """Get available measurement quantities for a submatrix."""
        try:
            submatrix_id_raw = arguments.get("submatrix_id")
            if submatrix_id_raw is None:
                raise ValueError("submatrix_id is required")
            submatrix_id = int(submatrix_id_raw)
            if submatrix_id <= 0:
                raise ValueError("submatrix_id must be a positive integer (> 0)")
            quantities = SubmatrixDataReader.get_measurement_quantities(submatrix_id)
            result = {
                "submatrix_id": submatrix_id,
                "measurement_quantities": quantities,
            }
            return SubmatrixToolHandler.json_response(result)
        except Exception as e:
            return SubmatrixToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def data_read_submatrix(arguments: dict[str, Any]) -> list[TextContent]:
        """Read timeseries data from a submatrix."""
        try:
            submatrix_id_raw = arguments.get("submatrix_id")
            if submatrix_id_raw is None:
                raise ValueError("submatrix_id is required")
            submatrix_id = int(submatrix_id_raw)
            if submatrix_id <= 0:
                raise ValueError("submatrix_id must be a positive integer (> 0)")
            measurement_quantity_patterns = arguments.get("measurement_quantity_patterns", [])
            case_insensitive = arguments.get("case_insensitive", False)
            date_as_timestamp = arguments.get("date_as_timestamp", True)
            set_independent_as_index = arguments.get("set_independent_as_index", True)

            result = SubmatrixDataReader.data_read_submatrix(
                submatrix_id=submatrix_id,
                measurement_quantity_patterns=measurement_quantity_patterns,
                case_insensitive=case_insensitive,
                date_as_timestamp=date_as_timestamp,
                set_independent_as_index=set_independent_as_index,
            )
            return SubmatrixToolHandler.json_response(result)
        except Exception as e:
            return SubmatrixToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def data_generate_fetcher_script(arguments: dict[str, Any]) -> list[TextContent]:
        """Generate Python scripts for fetching submatrix data."""
        try:
            submatrix_id_raw = arguments.get("submatrix_id")
            if submatrix_id_raw is None:
                raise ValueError("submatrix_id is required")
            submatrix_id = int(submatrix_id_raw)
            if submatrix_id <= 0:
                raise ValueError("submatrix_id must be a positive integer (> 0)")
            script_type = arguments.get("script_type", "basic")
            output_format = arguments.get("output_format", "csv")
            measurement_quantity_patterns = arguments.get("measurement_quantity_patterns", [])
            include_analysis = arguments.get("include_analysis", False)
            include_visualization = arguments.get("include_visualization", False)

            # Get available measurement quantities
            quantities = SubmatrixDataReader.get_measurement_quantities(submatrix_id)

            # Use provided patterns or all quantities
            if measurement_quantity_patterns:
                mq_list = measurement_quantity_patterns
            else:
                mq_list = [q["name"] for q in quantities]

            # Generate script based on type
            if script_type == "basic":
                script = generate_basic_fetcher_script(submatrix_id, mq_list, output_format)
            elif script_type == "advanced":
                script = generate_advanced_fetcher_script(
                    submatrix_id,
                    mq_list,
                    output_format,
                    include_visualization,
                    include_analysis,
                )
            elif script_type == "batch":
                script = generate_batch_fetcher_script(submatrix_id, mq_list, output_format)
            elif script_type == "analysis":
                script = generate_analysis_fetcher_script(submatrix_id, mq_list, output_format, include_visualization)
            else:
                raise ValueError(f"Unknown script type: {script_type}")

            result = {
                "submatrix_id": submatrix_id,
                "script_type": script_type,
                "output_format": output_format,
                "script": script,
                "instructions": [
                    "1. Update the configuration section with your ODS server details",
                    "2. Install required packages: pip install odsbox pandas",
                    f"3. Run the script: python submatrix_{submatrix_id}_fetcher.py",
                    f"4. Check output: submatrix_{submatrix_id}_data.{output_format}",
                ],
            }
            return SubmatrixToolHandler.json_response(result)
        except Exception as e:
            return SubmatrixToolHandler.error_response(str(e), type(e).__name__)
