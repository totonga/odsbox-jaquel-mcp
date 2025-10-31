"""Submatrix data reader for ASAM ODS Jaquel MCP Server."""

from __future__ import annotations

from typing import Any

from ..connection import ODSConnectionManager


class SubmatrixDataReader:
    """Reader for submatrix timeseries data."""

    @staticmethod
    def get_measurement_quantities(submatrix_id: int) -> list[dict[str, Any]]:
        """Get available measurement quantities for a submatrix.

        Args:
            submatrix_id: ID of the submatrix

        Returns:
            List of measurement quantity dicts
        """
        instance = ODSConnectionManager.get_instance()

        if not instance._con_i:
            raise ConnectionError("Not connected to ODS server")

        try:
            # Query for local columns in the submatrix
            query = {
                "AoLocalColumn": {"submatrix": submatrix_id},
                "$attributes": {
                    "name": 1,
                    "id": 1,
                    "sequence_representation": 1,
                    "independent": 1,
                    "measurement_quantity.name": 1,
                    "measurement_quantity.data_type": 1,
                    "unit.name": 1,
                },
            }

            result = instance._con_i.query(query)

            # Convert to list of dicts for JSON serialization
            quantities = []
            for _, row in result.iterrows():
                try:
                    quantities.append(
                        {
                            "id": int(row.get("id", 0)) if hasattr(row, "get") else int(row["id"]),
                            "name": row.get("name", "Unknown") if hasattr(row, "get") else row["name"],
                            "data_type": (
                                row.get("measurement_quantity.data_type", 0)
                                if hasattr(row, "get")
                                else row["measurement_quantity.data_type"]
                            ),
                            "measurement_quantity": (
                                row.get("measurement_quantity.name", "Unknown")
                                if hasattr(row, "get")
                                else row["measurement_quantity.name"]
                            ),
                            "unit": (
                                row.get("unit.name", "")
                                if hasattr(row, "get")
                                else row["unit.name"]
                            ),
                            "sequence_representation": (
                                int(row.get("sequence_representation", 0))
                                if hasattr(row, "get")
                                else int(row["sequence_representation"])
                            ),
                            "independent": (
                                bool(row.get("independent", False))
                                if hasattr(row, "get")
                                else bool(row["independent"])
                            ),
                        }
                    )
                except (KeyError, TypeError, ValueError):
                    # Skip rows with missing or invalid data
                    continue

            return quantities

        except Exception as e:
            raise RuntimeError(f"Failed to get measurement quantities: {e}") from e

    @staticmethod
    def read_submatrix_data(
        submatrix_id: int,
        measurement_quantity_patterns: list[str] | None = None,
        case_insensitive: bool = False,
        date_as_timestamp: bool = True,
        set_independent_as_index: bool = True,
    ) -> dict[str, Any]:
        """Read timeseries data from a submatrix.

        Args:
            submatrix_id: ID of the submatrix
            measurement_quantity_patterns: Column patterns to include
            case_insensitive: Case-insensitive pattern matching
            date_as_timestamp: Convert dates to timestamps
            set_independent_as_index: Set independent column as index

        Returns:
            Dict with data information
        """
        instance = ODSConnectionManager.get_instance()

        if not instance._con_i:
            raise ConnectionError("Not connected to ODS server")

        try:
            # Use bulk.data_read to get the data
            df = instance._con_i.bulk.data_read(
                submatrix_iid=submatrix_id,
                column_patterns=measurement_quantity_patterns if measurement_quantity_patterns else None,
                column_patterns_case_insensitive=case_insensitive,
                date_as_timestamp=date_as_timestamp,
                set_independent_as_index=set_independent_as_index,
            )

            # Convert DataFrame to dict for JSON serialization
            result = {
                "submatrix_id": submatrix_id,
                "columns": list(df.columns),
                "row_count": len(df),
                "data_preview": df.head(10).to_dict(orient="records") if len(df) > 0 else [],
                "note": "Full DataFrame returned (may be large)",
            }

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to read submatrix data: {e}") from e
