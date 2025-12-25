"""Data preparation utilities for measurement comparison notebooks.

Provides helpers for extracting metadata, formatting labels with units,
and preparing data for visualization.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


class MeasurementMetadataExtractor:
    """Extract and format metadata for measurements."""

    @staticmethod
    def extract_unit_lookup(
        local_columns_df: pd.DataFrame,
    ) -> dict[int, str]:
        """
        Create a lookup dictionary mapping local column IDs to unit names.

        Args:
            local_columns_df: DataFrame with columns 'id' and 'measurement_quantity.unit:OUTER.name'

        Returns:
            Dictionary mapping column ID to unit name
        """
        if local_columns_df.empty:
            return {}

        return dict(
            zip(
                local_columns_df["id"],
                local_columns_df.get("measurement_quantity.unit:OUTER.name", "-"),
            )
        )

    @staticmethod
    def build_label_dict(
        local_columns_df: pd.DataFrame,
        unit_lookup: dict[int, str],
    ) -> dict[str, str]:
        """
        Build a dictionary mapping column names to formatted labels with units.

        Args:
            local_columns_df: DataFrame with columns 'id', 'name'
            unit_lookup: Dictionary mapping column ID to unit

        Returns:
            Dictionary mapping column name to formatted label "[name] [unit]"
        """
        if local_columns_df.empty:
            return {}

        return {
            row["name"]: f"{row['name']} [{unit_lookup.get(row['id'], '-')}]" for _, row in local_columns_df.iterrows()
        }

    @staticmethod
    def build_submatrix_title_lookup(
        submatrices_df: pd.DataFrame,
        measurements_df: pd.DataFrame,
    ) -> dict[int, str]:
        """
        Build a lookup dictionary mapping submatrix IDs to descriptive titles.

        Titles are formatted as: "Project - Campaign - Profile"

        Args:
            submatrices_df: DataFrame with columns 'id', 'measurement'
            measurements_df: DataFrame with columns containing:
                - 'MeaResult.Id'
                - 'MeaResult.Name'
                - 'Test.Name'
                - 'Project.Name'

        Returns:
            Dictionary mapping submatrix ID to title string
        """
        if submatrices_df.empty or measurements_df.empty:
            return {}

        title_lookup = {}

        for _, submatrix_row in submatrices_df.iterrows():
            submatrix_id = submatrix_row["id"]
            measurement_id = submatrix_row["measurement"]

            # Find matching measurement
            measurement_info = measurements_df[measurements_df["MeaResult.Id"] == measurement_id]

            if not measurement_info.empty:
                project = measurement_info["Project.Name"].values[0]
                profile = measurement_info["MeaResult.Name"].values[0]
                campaign = measurement_info["Test.Name"].values[0]
                title_lookup[submatrix_id] = f"{project} - {campaign} - {profile}"
            else:
                title_lookup[submatrix_id] = f"Submatrix {submatrix_id}"

        return title_lookup

    @staticmethod
    def get_independent_column_info(
        local_columns_df: pd.DataFrame,
        unit_lookup: dict[int, str],
    ) -> tuple[str | None, str]:
        """
        Extract independent column information.

        Args:
            local_columns_df: DataFrame with columns 'name', 'independent', 'id'
            unit_lookup: Dictionary mapping column ID to unit

        Returns:
            Tuple of (column_name, unit_name). Returns ("Index", "-") if no independent column found.
        """
        if local_columns_df.empty:
            return "Index", "-"

        independent_rows = local_columns_df[local_columns_df["independent"] == 1]

        if independent_rows.empty:
            return "Index", "-"

        col_name = independent_rows["name"].iloc[0]
        col_id = independent_rows["id"].iloc[0]
        col_unit = unit_lookup.get(col_id, "-")

        return col_name, col_unit


class MeasurementDataPreparator:
    """Prepare measurement data for plotting."""

    @staticmethod
    def prepare_submatrix_dataframe(
        submatrix_signals_df: pd.DataFrame,
        measurement_quantity_names: list[str],
    ) -> tuple[pd.DataFrame | None, str | None]:
        """
        Prepare a DataFrame from submatrix signals for plotting.

        Args:
            submatrix_signals_df: DataFrame with columns 'name', 'values', 'independent'
            measurement_quantity_names: List of measurement quantity names to include

        Returns:
            Tuple of (DataFrame, error_message). Returns (None, error_message) if preparation fails.
            The DataFrame has measurement quantities as columns and independent column as index.
        """
        if submatrix_signals_df.empty:
            return None, "No signals provided"

        try:
            # Create DataFrame from signals
            data_dict = {row["name"]: row["values"] for _, row in submatrix_signals_df.iterrows()}
            df = pd.DataFrame(data_dict)

            # Check if all required quantities are present
            missing_cols = [col for col in measurement_quantity_names if col not in df.columns]
            if missing_cols:
                return None, f"Missing required columns: {missing_cols}"

            # Set independent column as index
            independent_rows = submatrix_signals_df[submatrix_signals_df["independent"] == 1]
            if not independent_rows.empty:
                independent_name = independent_rows["name"].iloc[0]
                if independent_name in df.columns:
                    df.set_index(independent_name, inplace=True)

            return df, None

        except Exception as e:
            return None, str(e)

    @staticmethod
    def prepare_measurement_data_items(
        submatrix_signals_by_id: dict[int, pd.DataFrame],
        submatrices_df: pd.DataFrame,
        measurements_df: pd.DataFrame,
        local_columns_df: pd.DataFrame,
        measurement_quantity_names: list[str],
        unit_lookup: dict[int, str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Prepare all measurement data items for visualization.

        Args:
            submatrix_signals_by_id: Dictionary mapping submatrix ID to signals DataFrame
            submatrices_df: DataFrame with submatrix metadata
            measurements_df: DataFrame with measurement metadata
            local_columns_df: DataFrame with local column metadata
            measurement_quantity_names: List of measurement quantity names to plot
            unit_lookup: Optional pre-computed unit lookup dictionary

        Returns:
            List of dictionaries with keys: 'title', 'data', 'labels', 'independent_info'
        """
        if unit_lookup is None:
            unit_lookup = MeasurementMetadataExtractor.extract_unit_lookup(local_columns_df)

        title_lookup = MeasurementMetadataExtractor.build_submatrix_title_lookup(submatrices_df, measurements_df)
        label_dict = MeasurementMetadataExtractor.build_label_dict(local_columns_df, unit_lookup)

        measurement_data_items = []

        for submatrix_id, signals_df in submatrix_signals_by_id.items():
            df, error = MeasurementDataPreparator.prepare_submatrix_dataframe(signals_df, measurement_quantity_names)

            if error:
                continue

            independent_name, independent_unit = MeasurementMetadataExtractor.get_independent_column_info(
                signals_df, unit_lookup
            )

            title = (
                f"{title_lookup.get(submatrix_id, 'Unknown')}\n" f"(Color: {independent_name} [{independent_unit}])"
            )
            measurement_data_items.append(
                {
                    "title": title,
                    "data": df,
                    "labels": label_dict,
                    "independent_info": {
                        "name": independent_name,
                        "unit": independent_unit,
                    },
                }
            )

        # Sort by title for consistent output
        measurement_data_items.sort(key=lambda x: str(x["title"]))

        return measurement_data_items
