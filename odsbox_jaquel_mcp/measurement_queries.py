"""Measurement hierarchy and discovery utilities.

Provides tools for exploring ODS measurement structure, finding measurements
by criteria, and extracting metadata from queries.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class MeasurementHierarchyExplorer:
    """Explore measurement hierarchies and structures in ODS."""

    @staticmethod
    def extract_measurements_from_query_result(
        query_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Extract measurement metadata from ODS query result.

        Args:
            query_result: Result from ODS query execution

        Returns:
            List of measurement dictionaries with metadata
        """
        try:
            measurements = []

            if not isinstance(query_result, dict):
                return measurements

            # Handle direct measurement list
            if "measurements" in query_result:
                measurements_data = query_result["measurements"]
                if isinstance(measurements_data, list):
                    measurements.extend(measurements_data)

            # Handle AoMeasurement results
            if "AoMeasurement" in query_result:
                meas_data = query_result["AoMeasurement"]
                if isinstance(meas_data, list):
                    for m in meas_data:
                        if isinstance(m, dict):
                            measurements.append(m)
                elif isinstance(meas_data, dict):
                    measurements.append(meas_data)

            # Handle test hierarchy results
            if "AoTest" in query_result:
                test_data = query_result["AoTest"]
                if isinstance(test_data, list):
                    for t in test_data:
                        if isinstance(t, dict) and "measurements" in t:
                            meas_list = t.get("measurements", [])
                            if isinstance(meas_list, list):
                                measurements.extend(meas_list)

            return measurements

        except Exception as e:
            raise ValueError(f"Failed to extract measurements: {e}") from e

    @staticmethod
    def build_measurement_hierarchy(
        measurements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build hierarchical view of measurements.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Hierarchical structure organized by test/campaign
        """
        try:
            hierarchy: Dict[str, Any] = {
                "by_test": {},
                "by_date_range": {},
                "by_status": {},
                "total_measurements": len(measurements),
            }

            for meas in measurements:
                if not isinstance(meas, dict):
                    continue

                # Organize by test
                test_name = meas.get("TestName") or meas.get("Test", {}).get("Name")
                if test_name:
                    if test_name not in hierarchy["by_test"]:
                        hierarchy["by_test"][test_name] = []
                    hierarchy["by_test"][test_name].append(meas)

                # Organize by status
                status = meas.get("Status", "Unknown")
                if status not in hierarchy["by_status"]:
                    hierarchy["by_status"][status] = []
                hierarchy["by_status"][status].append(meas)

            return hierarchy

        except Exception as e:
            raise ValueError(f"Failed to build hierarchy: {e}") from e

    @staticmethod
    def get_available_quantities_for_measurement(
        measurement: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Get list of available quantities for a measurement.

        Args:
            measurement: Measurement dictionary from ODS

        Returns:
            List of quantity dictionaries
        """
        try:
            quantities = []

            if not isinstance(measurement, dict):
                return quantities

            # Try multiple possible keys for quantities
            qty_sources = [
                "quantities",
                "MeasurementQuantities",
                "measurement_quantities",
                "AoMeasurementQuantity",
                "Quantities",
            ]

            for source_key in qty_sources:
                if source_key in measurement:
                    qty_data = measurement[source_key]
                    if isinstance(qty_data, list):
                        quantities.extend(qty_data)
                    elif isinstance(qty_data, dict):
                        quantities.append(qty_data)

            # If no quantities found, try to extract from submatrices
            if not quantities:
                submatrix_sources = [
                    "submatrices",
                    "AoSubmatrix",
                    "Submatrices",
                    "SubMatrices",
                ]
                for source_key in submatrix_sources:
                    if source_key in measurement:
                        submatrix_data = measurement[source_key]
                        if isinstance(submatrix_data, list):
                            for sm in submatrix_data:
                                if isinstance(sm, dict):
                                    cols = sm.get("LocalColumns") or sm.get("AoLocalColumn")
                                    if isinstance(cols, list):
                                        for col in cols:
                                            if isinstance(col, dict):
                                                qty_name = col.get("Name")
                                                if qty_name:
                                                    quantities.append(
                                                        {
                                                            "name": qty_name,
                                                            "source": "submatrix_column",
                                                        }
                                                    )

            return quantities

        except Exception as e:
            raise ValueError(f"Failed to get quantities for measurement: {e}") from e

    @staticmethod
    def filter_measurements_by_criteria(
        measurements: List[Dict[str, Any]],
        test_name: Optional[str] = None,
        status: Optional[str] = None,
        name_pattern: Optional[str] = None,
        has_quantities: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Filter measurements by various criteria.

        Args:
            measurements: List of measurement dictionaries
            test_name: Filter by test name (exact match)
            status: Filter by status
            name_pattern: Filter by name pattern (substring match)
            has_quantities: Filter measurements containing all these quantities

        Returns:
            Filtered list of measurements
        """
        try:
            filtered = measurements

            # Filter by test name
            if test_name:
                filtered = [
                    m
                    for m in filtered
                    if (m.get("TestName") == test_name or m.get("Test", {}).get("Name") == test_name)
                ]

            # Filter by status
            if status:
                filtered = [m for m in filtered if m.get("Status") == status]

            # Filter by name pattern
            if name_pattern:
                filtered = [
                    m
                    for m in filtered
                    if (
                        name_pattern.lower() in str(m.get("Name", "")).lower()
                        or name_pattern.lower() in str(m.get("Id", "")).lower()
                    )
                ]

            # Filter by quantities
            if has_quantities:

                def has_all_quantities(meas: Dict[str, Any]) -> bool:
                    meas_quantities = MeasurementHierarchyExplorer.get_available_quantities_for_measurement(meas)
                    meas_qty_names = {q.get("name", q.get("Name", "")) for q in meas_quantities}
                    return all(qty in meas_qty_names for qty in has_quantities)

                filtered = [m for m in filtered if has_all_quantities(m)]

            return filtered

        except Exception as e:
            raise ValueError(f"Failed to filter measurements: {e}") from e

    @staticmethod
    def get_measurement_summary(
        measurement: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Get summary information for a measurement.

        Args:
            measurement: Measurement dictionary

        Returns:
            Summary dictionary with key metadata
        """
        try:
            summary = {
                "id": measurement.get("Id"),
                "name": measurement.get("Name"),
                "status": measurement.get("Status"),
                "date": measurement.get("Date"),
                "test_name": measurement.get("TestName") or measurement.get("Test", {}).get("Name"),
                "num_submatrices": 0,
                "num_quantities": 0,
                "metadata": {},
            }

            # Count submatrices
            submatrix_sources = [
                "submatrices",
                "AoSubmatrix",
                "Submatrices",
            ]
            for source_key in submatrix_sources:
                if source_key in measurement:
                    sm_data = measurement[source_key]
                    if isinstance(sm_data, list):
                        summary["num_submatrices"] = len(sm_data)
                        break

            # Get quantities
            quantities = MeasurementHierarchyExplorer.get_available_quantities_for_measurement(measurement)
            summary["num_quantities"] = len(quantities)
            summary["quantity_names"] = [q.get("name") or q.get("Name") for q in quantities]

            # Extract other metadata
            metadata_keys = [
                "Description",
                "Comment",
                "Campaign",
                "UserComment",
                "CreatedDate",
                "ModifiedDate",
            ]
            for key in metadata_keys:
                if key in measurement:
                    summary["metadata"][key] = measurement[key]

            return summary

        except Exception as e:
            raise ValueError(f"Failed to get measurement summary: {e}") from e

    @staticmethod
    def query_measurements_by_hierarchy(
        query_result: Dict[str, Any],
        path_filter: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Query measurements following ODS hierarchy structure.

        Args:
            query_result: Result from ODS query
            path_filter: Path through hierarchy (e.g., ["Test1", "SubTest1"])

        Returns:
            List of matching measurements
        """
        try:
            measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)

            if not path_filter:
                return measurements

            # Apply hierarchy path filtering
            filtered = measurements
            for path_component in path_filter:
                filtered = [
                    m
                    for m in filtered
                    if (
                        path_component.lower() in str(m.get("TestName", "")).lower()
                        or path_component.lower() in str(m.get("Test", {}).get("Name", "")).lower()
                    )
                ]

            return filtered

        except Exception as e:
            raise ValueError(f"Failed to query by hierarchy: {e}") from e

    @staticmethod
    def build_measurement_index(
        measurements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build an index of measurements for fast lookup.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Index dictionary with multiple lookup methods
        """
        try:
            index = {
                "by_id": {},
                "by_name": {},
                "by_test": {},
                "by_status": {},
                "total_measurements": len(measurements),
            }

            for meas in measurements:
                if not isinstance(meas, dict):
                    continue

                # Index by ID
                meas_id = meas.get("Id")
                if meas_id:
                    index["by_id"][str(meas_id)] = meas

                # Index by name
                meas_name = meas.get("Name")
                if meas_name:
                    if meas_name not in index["by_name"]:
                        index["by_name"][meas_name] = []
                    index["by_name"][meas_name].append(meas)

                # Index by test
                test_name = meas.get("TestName") or meas.get("Test", {}).get("Name")
                if test_name:
                    if test_name not in index["by_test"]:
                        index["by_test"][test_name] = []
                    index["by_test"][test_name].append(meas)

                # Index by status
                status = meas.get("Status", "Unknown")
                if status not in index["by_status"]:
                    index["by_status"][status] = []
                index["by_status"][status].append(meas)

            return index

        except Exception as e:
            raise ValueError(f"Failed to build measurement index: {e}") from e

    @staticmethod
    def get_measurements_by_test(
        measurements: List[Dict[str, Any]],
        test_name: str,
    ) -> List[Dict[str, Any]]:
        """Get all measurements for a specific test.

        Args:
            measurements: List of measurement dictionaries
            test_name: Name of test to find

        Returns:
            List of measurements for that test
        """
        return [
            m for m in measurements if (m.get("TestName") == test_name or m.get("Test", {}).get("Name") == test_name)
        ]

    @staticmethod
    def get_unique_tests(
        measurements: List[Dict[str, Any]],
    ) -> List[str]:
        """Get list of unique test names in measurements.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Sorted list of unique test names
        """
        test_names = set()
        for m in measurements:
            test_name = m.get("TestName") or m.get("Test", {}).get("Name")
            if test_name:
                test_names.add(test_name)
        return sorted(test_names)

    @staticmethod
    def get_unique_quantities(
        measurements: List[Dict[str, Any]],
    ) -> List[str]:
        """Get list of unique quantity names across all measurements.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Sorted list of unique quantity names
        """
        quantity_names = set()
        for m in measurements:
            quantities = MeasurementHierarchyExplorer.get_available_quantities_for_measurement(m)
            for q in quantities:
                qty_name = q.get("name") or q.get("Name")
                if qty_name:
                    quantity_names.add(qty_name)
        return sorted(quantity_names)
