"""Submatrix data reader for ASAM ODS Jaquel MCP Server."""

from __future__ import annotations

from typing import Any, Literal, cast

import pandas as pd

from ..connection import ODSConnectionManager


def _resample_dataframe_uniform(df: pd.DataFrame, target_size: int) -> pd.DataFrame:
    """Resample DataFrame uniformly by selecting evenly spaced rows.

    Args:
        df: DataFrame to resample
        target_size: Target number of rows

    Returns:
        Resampled DataFrame
    """
    if len(df) <= target_size:
        return df

    # Calculate indices for uniform sampling
    indices = [int(i * len(df) / target_size) for i in range(target_size)]
    return df.iloc[indices].copy()


def _resample_dataframe_time_aware(df: pd.DataFrame, target_size: int) -> pd.DataFrame:
    """Resample DataFrame considering temporal distribution in the index.

    This method attempts to preserve temporal distribution by using pandas resample
    for datetime indices, or falls back to uniform sampling.

    Args:
        df: DataFrame to resample
        target_size: Target number of rows

    Returns:
        Resampled DataFrame
    """
    if len(df) <= target_size:
        return df

    # Check if index is datetime-like
    if isinstance(df.index, pd.DatetimeIndex):
        # Calculate appropriate frequency based on target size
        total_duration = df.index[-1] - df.index[0]
        target_freq = total_duration / target_size

        # Use pandas resample with mean aggregation for numeric columns
        # For string columns, use first value
        agg_dict: dict[str, Any] = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                agg_dict[col] = "mean"
            else:
                agg_dict[col] = "first"

        try:
            resampled = df.resample(target_freq).agg(cast(Any, agg_dict))
            # Limit to target size
            if len(resampled) > target_size:
                return resampled.iloc[:: len(resampled) // target_size][:target_size]
            return resampled
        except Exception:
            # Fall back to uniform sampling if resample fails
            return _resample_dataframe_uniform(df, target_size)

    # For non-datetime indices, fall back to uniform sampling
    return _resample_dataframe_uniform(df, target_size)


def _resample_dataframe_random(df: pd.DataFrame, target_size: int) -> pd.DataFrame:
    """Resample DataFrame using random sampling.

    Args:
        df: DataFrame to resample
        target_size: Target number of rows

    Returns:
        Resampled DataFrame
    """
    if len(df) <= target_size:
        return df

    return df.sample(n=target_size, random_state=42).sort_index()


def _resample_dataframe_stratified(df: pd.DataFrame, target_size: int) -> pd.DataFrame:
    """Resample DataFrame using stratified sampling to preserve distribution.

    This method divides the data into bins and samples from each bin proportionally.

    Args:
        df: DataFrame to resample
        target_size: Target number of rows

    Returns:
        Resampled DataFrame
    """
    if len(df) <= target_size:
        return df

    # Use stratified sampling based on quantiles
    # Divide into bins equal to target_size or fewer
    n_bins = min(target_size, 10)  # Use at most 10 bins
    samples_per_bin = target_size // n_bins

    # Create bins based on first numeric column or index
    numeric_col = None
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_col = col
            break

    if numeric_col is not None:
        # Stratify based on numeric column
        df_temp = df.copy()
        df_temp["_bin"] = pd.qcut(df_temp[numeric_col], q=n_bins, labels=False, duplicates="drop")
        sampled_indices = []

        for bin_val in df_temp["_bin"].unique():
            bin_df = df_temp[df_temp["_bin"] == bin_val]
            n_samples = min(samples_per_bin, len(bin_df))
            sampled_indices.extend(bin_df.sample(n=n_samples, random_state=42).index.tolist())

        # Limit to target size
        return df.loc[sorted(sampled_indices)[:target_size]]

    # Fall back to uniform sampling if no numeric column
    return _resample_dataframe_uniform(df, target_size)


def _resample_dataframe_minmax(df: pd.DataFrame, target_size: int) -> pd.DataFrame:
    """Resample DataFrame using min-max sampling to preserve extremes.

    This method keeps first, last, min, and max values, then fills with uniform sampling.

    Args:
        df: DataFrame to resample
        target_size: Target number of rows

    Returns:
        Resampled DataFrame
    """
    if len(df) <= target_size:
        return df

    sampled_indices = set()

    # Always include first and last
    sampled_indices.add(0)
    sampled_indices.add(len(df) - 1)

    # For each numeric column, include min and max indices
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and len(sampled_indices) < target_size:
            # Skip columns with all NaN
            if not df[col].isna().all():
                sampled_indices.add(int(df[col].idxmin()))
                sampled_indices.add(int(df[col].idxmax()))

    # Fill remaining with uniform sampling
    if len(sampled_indices) < target_size:
        remaining_size = target_size - len(sampled_indices)
        all_indices = set(range(len(df)))
        available_indices = list(all_indices - sampled_indices)

        if available_indices:
            step = len(available_indices) // remaining_size
            if step > 0:
                uniform_indices = available_indices[::step][:remaining_size]
                sampled_indices.update(uniform_indices)

    # Convert index positions to actual DataFrame indices
    result_indices = [df.index[i] if isinstance(i, int) and i < len(df) else i for i in sorted(sampled_indices)]
    return df.loc[result_indices]


def _resample_dataframe(
    df: pd.DataFrame,
    target_size: int,
    method: Literal["auto", "uniform", "time_aware", "random", "stratified", "minmax"] = "auto",
) -> pd.DataFrame:
    """Resample DataFrame to target size using specified method.

    Args:
        df: DataFrame to resample
        target_size: Target number of rows
        method: Resampling method to use:
            - "auto": Choose method based on data characteristics
            - "uniform": Evenly spaced sampling
            - "time_aware": Temporal distribution-aware sampling
            - "random": Random sampling
            - "stratified": Stratified sampling preserving distribution
            - "minmax": Min-max sampling preserving extremes

    Returns:
        Resampled DataFrame
    """
    if len(df) <= target_size:
        return df

    if method == "auto":
        # Choose method based on data characteristics
        if isinstance(df.index, pd.DatetimeIndex):
            method = "time_aware"
        else:
            # Check if data has high variance (preserve extremes)
            has_high_variance = False
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]) and not df[col].isna().all():
                    cv = df[col].std() / df[col].mean() if df[col].mean() != 0 else 0
                    if abs(cv) > 0.5:  # Coefficient of variation > 0.5
                        has_high_variance = True
                        break

            method = "minmax" if has_high_variance else "uniform"

    # Apply selected method
    if method == "uniform":
        return _resample_dataframe_uniform(df, target_size)
    elif method == "time_aware":
        return _resample_dataframe_time_aware(df, target_size)
    elif method == "random":
        return _resample_dataframe_random(df, target_size)
    elif method == "stratified":
        return _resample_dataframe_stratified(df, target_size)
    elif method == "minmax":
        return _resample_dataframe_minmax(df, target_size)
    else:
        # Default to uniform if unknown method
        return _resample_dataframe_uniform(df, target_size)


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
                    "measurement_quantity.datatype": 1,
                    "measurement_quantity.unit:OUTER.name": 1,
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
                                row.get("measurement_quantity.datatype", 0)
                                if hasattr(row, "get")
                                else row["measurement_quantity.datatype"]
                            ),
                            "measurement_quantity": (
                                row.get("measurement_quantity.name", "Unknown")
                                if hasattr(row, "get")
                                else row["measurement_quantity.name"]
                            ),
                            "unit": (
                                row.get("measurement_quantity.unit:OUTER.name", "")
                                if hasattr(row, "get")
                                else row["measurement_quantity.unit:OUTER.name"]
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
    def data_read_submatrix(
        submatrix_id: int,
        measurement_quantity_patterns: list[str] | None = None,
        case_insensitive: bool = False,
        date_as_timestamp: bool = True,
        set_independent_as_index: bool = True,
        max_preview_size: int = 100,
        preview_sampling_method: Literal["auto", "uniform", "time_aware", "random", "stratified", "minmax"] = "auto",
    ) -> dict[str, Any]:
        """Read timeseries data from a submatrix.

        Args:
            submatrix_id: ID of the submatrix
            measurement_quantity_patterns: Column patterns to include
            case_insensitive: Case-insensitive pattern matching
            date_as_timestamp: Convert dates to timestamps
            set_independent_as_index: Set independent column as index
            max_preview_size: Maximum number of rows in data preview (default: 100)
            preview_sampling_method: Method for resampling preview data:
                - "auto": Automatic selection based on data characteristics
                - "uniform": Evenly spaced sampling
                - "time_aware": Temporal distribution-aware sampling
                - "random": Random sampling
                - "stratified": Stratified sampling preserving distribution
                - "minmax": Min-max sampling preserving extremes

        Returns:
            Dict with data information including resampled preview
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

            # Resample for preview if needed
            if len(df) > max_preview_size:
                df_preview = _resample_dataframe(df, max_preview_size, preview_sampling_method)
                preview_note = (
                    f"Preview resampled from {len(df)} to {len(df_preview)} rows using"
                    f" '{preview_sampling_method}' method"
                )
            else:
                df_preview = df
                preview_note = f"Full data shown ({len(df)} rows)"

            # Convert DataFrame to dict for JSON serialization
            result = {
                "submatrix_id": submatrix_id,
                "columns": list(df.columns),
                "row_count": len(df),
                "preview_row_count": len(df_preview),
                "data_preview": df_preview.to_dict(orient="records") if len(df_preview) > 0 else [],
                "sampling_method": preview_sampling_method,
                "note": preview_note,
            }

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to read submatrix data: {e}") from e
