"""Unit tests for measurement_queries module."""

import pytest
from odsbox_jaquel_mcp.measurement_queries import MeasurementHierarchyExplorer


class TestExtractMeasurementsFromQueryResult:
    """Test extract_measurements_from_query_result method."""

    def test_extract_measurements_direct_list(self):
        """Test extracting from direct measurements list."""
        query_result = {
            "measurements": [
                {"Id": 1, "Name": "Test1"},
                {"Id": 2, "Name": "Test2"},
            ]
        }
        result = MeasurementHierarchyExplorer.extract_measurements_from_query_result(
            query_result
        )
        assert len(result) == 2
        assert result[0]["Name"] == "Test1"

    def test_extract_measurements_from_aomeasurement(self):
        """Test extracting from AoMeasurement key."""
        query_result = {
            "AoMeasurement": [
                {"Id": 1, "Name": "Test1"},
                {"Id": 2, "Name": "Test2"},
            ]
        }
        result = MeasurementHierarchyExplorer.extract_measurements_from_query_result(
            query_result
        )
        assert len(result) == 2

    def test_extract_measurements_from_test_hierarchy(self):
        """Test extracting from test hierarchy."""
        query_result = {
            "AoTest": [
                {
                    "Name": "Test1",
                    "measurements": [
                        {"Id": 1, "Name": "Meas1"},
                        {"Id": 2, "Name": "Meas2"},
                    ],
                }
            ]
        }
        result = MeasurementHierarchyExplorer.extract_measurements_from_query_result(
            query_result
        )
        assert len(result) == 2

    def test_extract_measurements_empty_result(self):
        """Test with empty query result."""
        result = MeasurementHierarchyExplorer.extract_measurements_from_query_result({})
        assert len(result) == 0

    def test_extract_measurements_invalid_input(self):
        """Test with non-dict input."""
        result = MeasurementHierarchyExplorer.extract_measurements_from_query_result(
            "invalid"
        )
        assert len(result) == 0

    def test_extract_measurements_single_aomeasurement(self):
        """Test extracting single AoMeasurement dict."""
        query_result = {
            "AoMeasurement": {"Id": 1, "Name": "Test1"}
        }
        result = MeasurementHierarchyExplorer.extract_measurements_from_query_result(
            query_result
        )
        assert len(result) == 1


class TestBuildMeasurementHierarchy:
    """Test build_measurement_hierarchy method."""

    def test_build_hierarchy_by_test(self):
        """Test building hierarchy organized by test."""
        measurements = [
            {"Id": 1, "TestName": "Test1"},
            {"Id": 2, "TestName": "Test1"},
            {"Id": 3, "TestName": "Test2"},
        ]
        hierarchy = MeasurementHierarchyExplorer.build_measurement_hierarchy(
            measurements
        )
        assert "Test1" in hierarchy["by_test"]
        assert "Test2" in hierarchy["by_test"]
        assert len(hierarchy["by_test"]["Test1"]) == 2

    def test_build_hierarchy_by_status(self):
        """Test building hierarchy organized by status."""
        measurements = [
            {"Id": 1, "Status": "Complete"},
            {"Id": 2, "Status": "Complete"},
            {"Id": 3, "Status": "Incomplete"},
        ]
        hierarchy = MeasurementHierarchyExplorer.build_measurement_hierarchy(
            measurements
        )
        assert "Complete" in hierarchy["by_status"]
        assert len(hierarchy["by_status"]["Complete"]) == 2

    def test_build_hierarchy_total_count(self):
        """Test total measurement count in hierarchy."""
        measurements = [
            {"Id": 1, "TestName": "Test1"},
            {"Id": 2, "TestName": "Test2"},
        ]
        hierarchy = MeasurementHierarchyExplorer.build_measurement_hierarchy(
            measurements
        )
        assert hierarchy["total_measurements"] == 2

    def test_build_hierarchy_empty_measurements(self):
        """Test with empty measurements list."""
        hierarchy = MeasurementHierarchyExplorer.build_measurement_hierarchy([])
        assert hierarchy["total_measurements"] == 0

    def test_build_hierarchy_nested_test_structure(self):
        """Test with nested test structure."""
        measurements = [
            {"Id": 1, "Test": {"Name": "Test1"}},
            {"Id": 2, "Test": {"Name": "Test1"}},
        ]
        hierarchy = MeasurementHierarchyExplorer.build_measurement_hierarchy(
            measurements
        )
        assert "Test1" in hierarchy["by_test"]


class TestGetAvailableQuantities:
    """Test get_available_quantities_for_measurement method."""

    def test_get_quantities_from_quantities_key(self):
        """Test getting quantities from 'quantities' key."""
        measurement = {
            "quantities": [
                {"name": "Speed"},
                {"name": "Torque"},
            ]
        }
        quantities = (
            MeasurementHierarchyExplorer.get_available_quantities_for_measurement(
                measurement
            )
        )
        assert len(quantities) == 2
        assert quantities[0]["name"] == "Speed"

    def test_get_quantities_from_measurement_quantities(self):
        """Test getting from MeasurementQuantities."""
        measurement = {
            "MeasurementQuantities": [
                {"name": "Speed"},
            ]
        }
        quantities = (
            MeasurementHierarchyExplorer.get_available_quantities_for_measurement(
                measurement
            )
        )
        assert len(quantities) == 1

    def test_get_quantities_from_submatrix_columns(self):
        """Test extracting from submatrix local columns."""
        measurement = {
            "submatrices": [
                {
                    "LocalColumns": [
                        {"Name": "Speed"},
                        {"Name": "Torque"},
                    ]
                }
            ]
        }
        quantities = (
            MeasurementHierarchyExplorer.get_available_quantities_for_measurement(
                measurement
            )
        )
        assert len(quantities) == 2
        assert quantities[0]["name"] == "Speed"

    def test_get_quantities_empty_measurement(self):
        """Test with measurement having no quantities."""
        quantities = (
            MeasurementHierarchyExplorer.get_available_quantities_for_measurement({})
        )
        assert len(quantities) == 0

    def test_get_quantities_invalid_input(self):
        """Test with invalid input."""
        quantities = (
            MeasurementHierarchyExplorer.get_available_quantities_for_measurement(
                "invalid"
            )
        )
        assert len(quantities) == 0

    def test_get_quantities_dict_instead_of_list(self):
        """Test with dict instead of list."""
        measurement = {
            "quantities": {"name": "Speed"}
        }
        quantities = (
            MeasurementHierarchyExplorer.get_available_quantities_for_measurement(
                measurement
            )
        )
        assert len(quantities) == 1


class TestFilterMeasurementsByCriteria:
    """Test filter_measurements_by_criteria method."""

    def test_filter_by_test_name(self):
        """Test filtering by test name."""
        measurements = [
            {"TestName": "Test1", "Id": 1},
            {"TestName": "Test1", "Id": 2},
            {"TestName": "Test2", "Id": 3},
        ]
        filtered = MeasurementHierarchyExplorer.filter_measurements_by_criteria(
            measurements, test_name="Test1"
        )
        assert len(filtered) == 2
        assert all(m["TestName"] == "Test1" for m in filtered)

    def test_filter_by_status(self):
        """Test filtering by status."""
        measurements = [
            {"Status": "Complete", "Id": 1},
            {"Status": "Incomplete", "Id": 2},
            {"Status": "Complete", "Id": 3},
        ]
        filtered = MeasurementHierarchyExplorer.filter_measurements_by_criteria(
            measurements, status="Complete"
        )
        assert len(filtered) == 2

    def test_filter_by_name_pattern(self):
        """Test filtering by name pattern."""
        measurements = [
            {"Name": "Profile_001", "Id": 1},
            {"Name": "Profile_002", "Id": 2},
            {"Name": "Baseline", "Id": 3},
        ]
        filtered = MeasurementHierarchyExplorer.filter_measurements_by_criteria(
            measurements, name_pattern="Profile"
        )
        assert len(filtered) == 2

    def test_filter_by_multiple_criteria(self):
        """Test filtering by multiple criteria."""
        measurements = [
            {"TestName": "Test1", "Status": "Complete", "Name": "Profile_001"},
            {"TestName": "Test1", "Status": "Incomplete", "Name": "Profile_002"},
            {"TestName": "Test2", "Status": "Complete", "Name": "Profile_003"},
        ]
        filtered = MeasurementHierarchyExplorer.filter_measurements_by_criteria(
            measurements,
            test_name="Test1",
            status="Complete",
        )
        assert len(filtered) == 1
        assert filtered[0]["Name"] == "Profile_001"

    def test_filter_by_quantities(self):
        """Test filtering by required quantities."""
        measurements = [
            {
                "Id": 1,
                "quantities": [
                    {"name": "Speed"},
                    {"name": "Torque"},
                ]
            },
            {
                "Id": 2,
                "quantities": [
                    {"name": "Speed"},
                ]
            },
        ]
        filtered = MeasurementHierarchyExplorer.filter_measurements_by_criteria(
            measurements, has_quantities=["Speed", "Torque"]
        )
        assert len(filtered) == 1
        assert filtered[0]["Id"] == 1

    def test_filter_empty_measurements(self):
        """Test filtering empty measurement list."""
        filtered = MeasurementHierarchyExplorer.filter_measurements_by_criteria(
            [], test_name="Test1"
        )
        assert len(filtered) == 0


class TestGetMeasurementSummary:
    """Test get_measurement_summary method."""

    def test_get_summary_basic(self):
        """Test getting basic measurement summary."""
        measurement = {
            "Id": 123,
            "Name": "Test_001",
            "Status": "Complete",
            "TestName": "ProfileTest",
        }
        summary = MeasurementHierarchyExplorer.get_measurement_summary(measurement)
        assert summary["id"] == 123
        assert summary["name"] == "Test_001"
        assert summary["status"] == "Complete"

    def test_get_summary_with_quantities(self):
        """Test summary includes quantity count."""
        measurement = {
            "Id": 1,
            "Name": "Test",
            "quantities": [
                {"name": "Speed"},
                {"name": "Torque"},
            ]
        }
        summary = MeasurementHierarchyExplorer.get_measurement_summary(measurement)
        assert summary["num_quantities"] == 2
        assert "Speed" in summary["quantity_names"]

    def test_get_summary_with_metadata(self):
        """Test summary extracts metadata."""
        measurement = {
            "Id": 1,
            "Name": "Test",
            "Description": "Test description",
            "Campaign": "Campaign_01",
        }
        summary = MeasurementHierarchyExplorer.get_measurement_summary(measurement)
        assert summary["metadata"]["Description"] == "Test description"
        assert summary["metadata"]["Campaign"] == "Campaign_01"

    def test_get_summary_invalid_input(self):
        """Test summary with invalid input."""
        with pytest.raises(ValueError):
            MeasurementHierarchyExplorer.get_measurement_summary("invalid")


class TestBuildMeasurementIndex:
    """Test build_measurement_index method."""

    def test_build_index_by_id(self):
        """Test building index by ID."""
        measurements = [
            {"Id": 1, "Name": "Test1"},
            {"Id": 2, "Name": "Test2"},
        ]
        index = MeasurementHierarchyExplorer.build_measurement_index(measurements)
        assert "1" in index["by_id"]
        assert index["by_id"]["1"]["Name"] == "Test1"

    def test_build_index_by_name(self):
        """Test building index by name."""
        measurements = [
            {"Id": 1, "Name": "Test1"},
            {"Id": 2, "Name": "Test1"},
        ]
        index = MeasurementHierarchyExplorer.build_measurement_index(measurements)
        assert len(index["by_name"]["Test1"]) == 2

    def test_build_index_by_test(self):
        """Test building index by test."""
        measurements = [
            {"Id": 1, "TestName": "Test1"},
            {"Id": 2, "TestName": "Test2"},
        ]
        index = MeasurementHierarchyExplorer.build_measurement_index(measurements)
        assert "Test1" in index["by_test"]
        assert "Test2" in index["by_test"]

    def test_build_index_total_count(self):
        """Test index includes total count."""
        measurements = [
            {"Id": 1},
            {"Id": 2},
        ]
        index = MeasurementHierarchyExplorer.build_measurement_index(measurements)
        assert index["total_measurements"] == 2


class TestGetMeasurementsByTest:
    """Test get_measurements_by_test method."""

    def test_get_measurements_by_test(self):
        """Test getting measurements for a test."""
        measurements = [
            {"Id": 1, "TestName": "Test1"},
            {"Id": 2, "TestName": "Test1"},
            {"Id": 3, "TestName": "Test2"},
        ]
        result = MeasurementHierarchyExplorer.get_measurements_by_test(
            measurements, "Test1"
        )
        assert len(result) == 2

    def test_get_measurements_by_test_nested(self):
        """Test with nested test structure."""
        measurements = [
            {"Id": 1, "Test": {"Name": "Test1"}},
            {"Id": 2, "Test": {"Name": "Test1"}},
            {"Id": 3, "Test": {"Name": "Test2"}},
        ]
        result = MeasurementHierarchyExplorer.get_measurements_by_test(
            measurements, "Test1"
        )
        assert len(result) == 2

    def test_get_measurements_by_test_not_found(self):
        """Test when test not found."""
        measurements = [
            {"Id": 1, "TestName": "Test1"},
        ]
        result = MeasurementHierarchyExplorer.get_measurements_by_test(
            measurements, "NonExistent"
        )
        assert len(result) == 0


class TestGetUniqueMethods:
    """Test get_unique_tests and get_unique_quantities methods."""

    def test_get_unique_tests(self):
        """Test getting unique test names."""
        measurements = [
            {"TestName": "Test1"},
            {"TestName": "Test1"},
            {"TestName": "Test2"},
            {"TestName": "Test3"},
        ]
        tests = MeasurementHierarchyExplorer.get_unique_tests(measurements)
        assert len(tests) == 3
        assert tests == ["Test1", "Test2", "Test3"]  # Sorted

    def test_get_unique_tests_empty(self):
        """Test with empty measurements."""
        tests = MeasurementHierarchyExplorer.get_unique_tests([])
        assert len(tests) == 0

    def test_get_unique_quantities(self):
        """Test getting unique quantities."""
        measurements = [
            {
                "quantities": [
                    {"name": "Speed"},
                    {"name": "Torque"},
                ]
            },
            {
                "quantities": [
                    {"name": "Speed"},
                    {"name": "Temperature"},
                ]
            },
        ]
        quantities = MeasurementHierarchyExplorer.get_unique_quantities(measurements)
        assert len(quantities) == 3
        assert "Speed" in quantities
        assert "Torque" in quantities
        assert "Temperature" in quantities


class TestQueryMeasurementsByHierarchy:
    """Test query_measurements_by_hierarchy method."""

    def test_query_with_path_filter(self):
        """Test querying with path filter."""
        query_result = {
            "measurements": [
                {"Id": 1, "TestName": "Test1"},
                {"Id": 2, "TestName": "Test2"},
            ]
        }
        result = MeasurementHierarchyExplorer.query_measurements_by_hierarchy(
            query_result, path_filter=["Test1"]
        )
        assert len(result) == 1
        assert result[0]["TestName"] == "Test1"

    def test_query_without_path_filter(self):
        """Test querying without path filter."""
        query_result = {
            "measurements": [
                {"Id": 1, "TestName": "Test1"},
                {"Id": 2, "TestName": "Test2"},
            ]
        }
        result = MeasurementHierarchyExplorer.query_measurements_by_hierarchy(
            query_result
        )
        assert len(result) == 2

    def test_query_case_insensitive_matching(self):
        """Test case insensitive path matching."""
        query_result = {
            "measurements": [
                {"Id": 1, "TestName": "MyTest"},
            ]
        }
        result = MeasurementHierarchyExplorer.query_measurements_by_hierarchy(
            query_result, path_filter=["mytest"]
        )
        assert len(result) == 1


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_extract_measurements_multiple_sources(self):
        """Test when result has multiple measurement sources."""
        query_result = {
            "measurements": [{"Id": 1}],
            "AoMeasurement": [{"Id": 2}],
        }
        result = MeasurementHierarchyExplorer.extract_measurements_from_query_result(
            query_result
        )
        # Both sources should be extracted
        assert len(result) >= 1

    def test_filter_measurements_case_sensitive_test_name(self):
        """Test that test name filtering is case sensitive."""
        measurements = [
            {"TestName": "Test1"},
        ]
        filtered = MeasurementHierarchyExplorer.filter_measurements_by_criteria(
            measurements, test_name="test1"
        )
        # Should not match due to case sensitivity
        assert len(filtered) == 0

    def test_get_measurements_by_test_with_missing_test_field(self):
        """Test measurements missing TestName field."""
        measurements = [
            {"Id": 1},
            {"Id": 2, "TestName": "Test1"},
        ]
        result = MeasurementHierarchyExplorer.get_measurements_by_test(
            measurements, "Test1"
        )
        assert len(result) == 1

    def test_build_hierarchy_with_missing_fields(self):
        """Test building hierarchy with missing optional fields."""
        measurements = [
            {"Id": 1},  # Missing TestName and Status
        ]
        hierarchy = MeasurementHierarchyExplorer.build_measurement_hierarchy(
            measurements
        )
        assert hierarchy["total_measurements"] == 1
        assert "Unknown" in hierarchy["by_status"]  # Default status
