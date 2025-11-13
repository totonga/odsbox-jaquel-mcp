"""Tests for data preparation utilities."""

import unittest

import pandas as pd

from odsbox_jaquel_mcp.data_preparation import (
    MeasurementDataPreparator,
    MeasurementMetadataExtractor,
)


class TestMeasurementMetadataExtractor(unittest.TestCase):
    """Test MeasurementMetadataExtractor class."""

    def test_extract_unit_lookup_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result = MeasurementMetadataExtractor.extract_unit_lookup(df)
        self.assertEqual(result, {})

    def test_extract_unit_lookup_valid_data(self):
        """Test with valid data."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "measurement_quantity.unit:OUTER.name": ["m/s", "N", "°C"],
            }
        )
        result = MeasurementMetadataExtractor.extract_unit_lookup(df)
        expected = {1: "m/s", 2: "N", 3: "°C"}
        self.assertEqual(result, expected)

    def test_build_label_dict_empty_dataframe(self):
        """Test label dict with empty DataFrame."""
        df = pd.DataFrame()
        unit_lookup = {}
        result = MeasurementMetadataExtractor.build_label_dict(df, unit_lookup)
        self.assertEqual(result, {})

    def test_build_label_dict_with_units(self):
        """Test label dict creation with units."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Motor_speed", "Torque", "Temperature"],
            }
        )
        unit_lookup = {1: "rpm", 2: "N·m", 3: "°C"}
        result = MeasurementMetadataExtractor.build_label_dict(df, unit_lookup)
        expected = {
            "Motor_speed": "Motor_speed [rpm]",
            "Torque": "Torque [N·m]",
            "Temperature": "Temperature [°C]",
        }
        self.assertEqual(result, expected)

    def test_build_label_dict_missing_units(self):
        """Test label dict with missing units."""
        df = pd.DataFrame(
            {
                "id": [1, 2],
                "name": ["Speed", "Distance"],
            }
        )
        unit_lookup = {1: "m/s"}  # Missing unit for id 2
        result = MeasurementMetadataExtractor.build_label_dict(df, unit_lookup)
        expected = {
            "Speed": "Speed [m/s]",
            "Distance": "Distance [-]",
        }
        self.assertEqual(result, expected)

    def test_build_submatrix_title_lookup_empty_dataframes(self):
        """Test with empty DataFrames."""
        submatrices_df = pd.DataFrame()
        measurements_df = pd.DataFrame()
        result = MeasurementMetadataExtractor.build_submatrix_title_lookup(
            submatrices_df, measurements_df
        )
        self.assertEqual(result, {})

    def test_build_submatrix_title_lookup_valid_data(self):
        """Test with valid data."""
        submatrices_df = pd.DataFrame(
            {
                "id": [1, 2],
                "measurement": [100, 101],
            }
        )
        measurements_df = pd.DataFrame(
            {
                "MeaResult.Id": [100, 101],
                "MeaResult.Name": ["Profile_1", "Profile_2"],
                "Test.Name": ["Campaign_01", "Campaign_02"],
                "Project.Name": ["Project_A", "Project_B"],
            }
        )
        result = (
            MeasurementMetadataExtractor.build_submatrix_title_lookup(
                submatrices_df, measurements_df
            )
        )
        expected = {
            1: "Project_A - Campaign_01 - Profile_1",
            2: "Project_B - Campaign_02 - Profile_2",
        }
        self.assertEqual(result, expected)

    def test_build_submatrix_title_lookup_missing_measurement(self):
        """Test with missing measurement info."""
        submatrices_df = pd.DataFrame(
            {
                "id": [1, 2],
                "measurement": [100, 999],  # 999 doesn't exist
            }
        )
        measurements_df = pd.DataFrame(
            {
                "MeaResult.Id": [100],
                "MeaResult.Name": ["Profile_1"],
                "Test.Name": ["Campaign_01"],
                "Project.Name": ["Project_A"],
            }
        )
        result = (
            MeasurementMetadataExtractor.build_submatrix_title_lookup(
                submatrices_df, measurements_df
            )
        )
        expected = {
            1: "Project_A - Campaign_01 - Profile_1",
            2: "Submatrix 2",
        }
        self.assertEqual(result, expected)

    def test_get_independent_column_info_empty(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        unit_lookup = {}
        col_name, unit = (
            MeasurementMetadataExtractor.get_independent_column_info(df, unit_lookup)
        )
        self.assertEqual(col_name, "Index")
        self.assertEqual(unit, "-")

    def test_get_independent_column_info_no_independent(self):
        """Test with no independent column."""
        df = pd.DataFrame(
            {
                "name": ["Speed", "Torque"],
                "independent": [0, 0],
                "id": [1, 2],
            }
        )
        unit_lookup = {1: "m/s", 2: "N·m"}
        col_name, unit = (
            MeasurementMetadataExtractor.get_independent_column_info(df, unit_lookup)
        )
        self.assertEqual(col_name, "Index")
        self.assertEqual(unit, "-")

    def test_get_independent_column_info_found(self):
        """Test with independent column found."""
        df = pd.DataFrame(
            {
                "name": ["Time", "Speed", "Torque"],
                "independent": [1, 0, 0],
                "id": [0, 1, 2],
            }
        )
        unit_lookup = {0: "s", 1: "m/s", 2: "N·m"}
        col_name, unit = (
            MeasurementMetadataExtractor.get_independent_column_info(df, unit_lookup)
        )
        self.assertEqual(col_name, "Time")
        self.assertEqual(unit, "s")


class TestMeasurementDataPreparator(unittest.TestCase):
    """Test MeasurementDataPreparator class."""

    def test_prepare_submatrix_dataframe_empty(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result_df, error = (
            MeasurementDataPreparator.prepare_submatrix_dataframe(df, ["Speed"])
        )
        self.assertIsNone(result_df)
        self.assertIsNotNone(error)

    def test_prepare_submatrix_dataframe_valid(self):
        """Test with valid data."""
        df = pd.DataFrame(
            {
                "name": ["Time", "Speed", "Torque"],
                "values": [
                    [0, 1, 2, 3],
                    [10, 20, 30, 40],
                    [100, 110, 120, 130],
                ],
                "independent": [1, 0, 0],
            }
        )
        result_df, error = (
            MeasurementDataPreparator.prepare_submatrix_dataframe(
                df, ["Speed", "Torque"]
            )
        )
        self.assertIsNone(error)
        self.assertIsNotNone(result_df)
        self.assertIn("Speed", result_df.columns)
        self.assertIn("Torque", result_df.columns)
        self.assertEqual(result_df.index.name, "Time")

    def test_prepare_submatrix_dataframe_missing_columns(self):
        """Test with missing required columns."""
        df = pd.DataFrame(
            {
                "name": ["Time", "Speed"],
                "values": [[0, 1, 2], [10, 20, 30]],
                "independent": [1, 0],
            }
        )
        result_df, error = (
            MeasurementDataPreparator.prepare_submatrix_dataframe(
                df, ["Speed", "Torque"]  # Torque missing
            )
        )
        self.assertIsNone(result_df)
        self.assertIn("Missing", error)

    def test_prepare_measurement_data_items_empty(self):
        """Test with empty inputs."""
        result = MeasurementDataPreparator.prepare_measurement_data_items(
            submatrix_signals_by_id={},
            submatrices_df=pd.DataFrame(),
            measurements_df=pd.DataFrame(),
            local_columns_df=pd.DataFrame(),
            measurement_quantity_names=["Speed"],
        )
        self.assertEqual(result, [])

    def test_prepare_measurement_data_items_valid(self):
        """Test with valid data."""
        signals_df = pd.DataFrame(
            {
                "name": ["Time", "Speed", "Torque"],
                "values": [
                    [0, 1, 2, 3],
                    [10, 20, 30, 40],
                    [100, 110, 120, 130],
                ],
                "independent": [1, 0, 0],
                "id": [0, 1, 2],
            }
        )

        submatrices_df = pd.DataFrame(
            {
                "id": [1],
                "measurement": [100],
            }
        )

        measurements_df = pd.DataFrame(
            {
                "MeaResult.Id": [100],
                "MeaResult.Name": ["Profile_1"],
                "Test.Name": ["Campaign_01"],
                "Project.Name": ["Project_A"],
            }
        )

        local_columns_df = pd.DataFrame(
            {
                "id": [0, 1, 2],
                "name": ["Time", "Speed", "Torque"],
                "independent": [1, 0, 0],
                "measurement_quantity.unit:OUTER.name": ["s", "m/s", "N·m"],
            }
        )

        submatrix_signals_by_id = {1: signals_df}

        result = (
            MeasurementDataPreparator.prepare_measurement_data_items(
                submatrix_signals_by_id=submatrix_signals_by_id,
                submatrices_df=submatrices_df,
                measurements_df=measurements_df,
                local_columns_df=local_columns_df,
                measurement_quantity_names=["Speed", "Torque"],
            )
        )

        self.assertEqual(len(result), 1)
        self.assertIn("title", result[0])
        self.assertIn("data", result[0])
        self.assertIn("labels", result[0])
        self.assertIn("independent_info", result[0])
        self.assertIn("Project_A", result[0]["title"])


if __name__ == "__main__":
    unittest.main()
