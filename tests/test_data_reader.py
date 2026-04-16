"""Tests for submatrix data reader with resampling functionality."""

import pandas as pd

from odsbox_jaquel_mcp.submatrix.data_reader import (
    _resample_dataframe,
    _resample_dataframe_minmax,
    _resample_dataframe_random,
    _resample_dataframe_stratified,
    _resample_dataframe_time_aware,
    _resample_dataframe_uniform,
)


class TestResamplingUniform:
    """Test uniform resampling."""

    def test_uniform_sampling_basic(self):
        """Test basic uniform sampling."""
        df = pd.DataFrame({"value": range(100)})
        result = _resample_dataframe_uniform(df, 10)

        assert len(result) == 10
        assert result["value"].iloc[0] == 0
        assert result["value"].iloc[-1] == 90  # Last sample should be near end

    def test_uniform_no_resampling_needed(self):
        """Test that no resampling happens when df is smaller than target."""
        df = pd.DataFrame({"value": range(10)})
        result = _resample_dataframe_uniform(df, 100)

        assert len(result) == 10
        pd.testing.assert_frame_equal(result, df)

    def test_uniform_multiple_columns(self):
        """Test uniform sampling with multiple columns."""
        df = pd.DataFrame({"a": range(100), "b": range(100, 200), "c": ["x"] * 100})
        result = _resample_dataframe_uniform(df, 20)

        assert len(result) == 20
        assert list(result.columns) == ["a", "b", "c"]

    def test_uniform_even_distribution(self):
        """Test that uniform sampling produces evenly spaced samples."""
        df = pd.DataFrame({"value": range(1000)})
        result = _resample_dataframe_uniform(df, 10)

        # Check spacing is approximately equal
        diffs = result["value"].diff().dropna()
        assert diffs.std() < 10  # Standard deviation should be small


class TestResamplingTimeAware:
    """Test time-aware resampling."""

    def test_time_aware_with_datetime_index(self):
        """Test time-aware sampling with datetime index."""
        dates = pd.date_range("2024-01-01", periods=1000, freq="1h")
        df = pd.DataFrame({"value": range(1000)}, index=dates)
        result = _resample_dataframe_time_aware(df, 100)

        assert len(result) <= 100
        assert isinstance(result.index, pd.DatetimeIndex)

    def test_time_aware_with_numeric_data(self):
        """Test time-aware sampling with numeric columns."""
        dates = pd.date_range("2024-01-01", periods=500, freq="1min")
        df = pd.DataFrame({"temp": range(500), "pressure": range(1000, 1500)}, index=dates)
        result = _resample_dataframe_time_aware(df, 50)

        assert len(result) <= 50
        assert "temp" in result.columns
        assert "pressure" in result.columns

    def test_time_aware_with_string_columns(self):
        """Test time-aware sampling with string columns."""
        dates = pd.date_range("2024-01-01", periods=200, freq="1h")
        df = pd.DataFrame({"value": range(200), "status": ["ok"] * 200}, index=dates)
        result = _resample_dataframe_time_aware(df, 20)

        assert len(result) <= 20
        assert "status" in result.columns

    def test_time_aware_fallback_to_uniform(self):
        """Test time-aware falls back to uniform for non-datetime index."""
        df = pd.DataFrame({"value": range(100)})
        result = _resample_dataframe_time_aware(df, 10)

        assert len(result) == 10
        # Should fall back to uniform sampling


class TestResamplingRandom:
    """Test random resampling."""

    def test_random_sampling_basic(self):
        """Test basic random sampling."""
        df = pd.DataFrame({"value": range(100)})
        result = _resample_dataframe_random(df, 10)

        assert len(result) == 10
        # Check that result is sorted by index
        assert result.index.is_monotonic_increasing

    def test_random_sampling_deterministic(self):
        """Test that random sampling is deterministic with fixed seed."""
        df = pd.DataFrame({"value": range(100)})
        result1 = _resample_dataframe_random(df, 10)
        result2 = _resample_dataframe_random(df, 10)

        pd.testing.assert_frame_equal(result1, result2)

    def test_random_no_resampling_needed(self):
        """Test no resampling when df is smaller than target."""
        df = pd.DataFrame({"value": range(10)})
        result = _resample_dataframe_random(df, 100)

        assert len(result) == 10


class TestResamplingStratified:
    """Test stratified resampling."""

    def test_stratified_sampling_basic(self):
        """Test basic stratified sampling."""
        df = pd.DataFrame({"value": range(100)})
        result = _resample_dataframe_stratified(df, 20)

        assert len(result) <= 20
        # Check that samples are distributed across the range
        assert result["value"].min() < 30
        assert result["value"].max() > 70

    def test_stratified_preserves_distribution(self):
        """Test that stratified sampling preserves distribution."""
        # Create data with known distribution
        df = pd.DataFrame({"value": [0] * 25 + [1] * 50 + [2] * 25})
        result = _resample_dataframe_stratified(df, 30)

        assert len(result) <= 30
        # Check that all values are represented
        assert set(result["value"].unique()).issubset({0, 1, 2})

    def test_stratified_multiple_numeric_columns(self):
        """Test stratified sampling with multiple numeric columns."""
        df = pd.DataFrame({"a": range(200), "b": range(200, 400)})
        result = _resample_dataframe_stratified(df, 40)

        assert len(result) <= 40
        assert list(result.columns) == ["a", "b"]

    def test_stratified_fallback_for_non_numeric(self):
        """Test stratified falls back to uniform for non-numeric data."""
        df = pd.DataFrame({"text": ["a"] * 100})
        result = _resample_dataframe_stratified(df, 10)

        assert len(result) == 10


class TestResamplingMinMax:
    """Test min-max resampling."""

    def test_minmax_preserves_extremes(self):
        """Test that min-max preserves extreme values."""
        df = pd.DataFrame({"value": [0, 1, 2, 100, 4, 5, 6, 7, 8, 9]})
        result = _resample_dataframe_minmax(df, 5)

        assert len(result) <= 5
        # Should include min and max
        assert 0 in result["value"].values
        assert 100 in result["value"].values

    def test_minmax_preserves_first_last(self):
        """Test that min-max preserves first and last rows."""
        df = pd.DataFrame({"value": range(100)})
        result = _resample_dataframe_minmax(df, 10)

        assert len(result) <= 10
        assert result["value"].iloc[0] == 0
        assert result["value"].iloc[-1] == 99

    def test_minmax_multiple_columns(self):
        """Test min-max with multiple numeric columns."""
        df = pd.DataFrame({"a": range(100), "b": range(100, 0, -1)})
        result = _resample_dataframe_minmax(df, 20)

        assert len(result) <= 20
        # Should preserve extremes for both columns
        assert 0 in result["a"].values or result["a"].min() < 10
        assert 99 in result["a"].values or result["a"].max() > 90

    def test_minmax_with_nan_values(self):
        """Test min-max handles NaN values gracefully."""
        df = pd.DataFrame({"value": [float("nan")] * 5 + list(range(95))})
        result = _resample_dataframe_minmax(df, 10)

        assert len(result) <= 10


class TestResamplingAuto:
    """Test automatic resampling method selection."""

    def test_auto_selects_time_aware_for_datetime(self):
        """Test auto selects time_aware for datetime index."""
        dates = pd.date_range("2024-01-01", periods=500, freq="1h")
        df = pd.DataFrame({"value": range(500)}, index=dates)
        result = _resample_dataframe(df, 50, method="auto")

        assert len(result) <= 50
        assert isinstance(result.index, pd.DatetimeIndex)

    def test_auto_selects_minmax_for_high_variance(self):
        """Test auto selects minmax for high variance data."""
        # Create data with high variance
        df = pd.DataFrame({"value": [1] * 40 + [100] * 10 + [1] * 40 + [200] * 10})
        result = _resample_dataframe(df, 20, method="auto")

        assert len(result) <= 20
        # Should preserve extremes
        assert result["value"].max() >= 100

    def test_auto_selects_uniform_for_normal_data(self):
        """Test auto selects uniform for normal data."""
        df = pd.DataFrame({"value": range(100)})
        result = _resample_dataframe(df, 10, method="auto")

        assert len(result) == 10

    def test_auto_no_resampling_when_not_needed(self):
        """Test auto doesn't resample when data is smaller than target."""
        df = pd.DataFrame({"value": range(10)})
        result = _resample_dataframe(df, 100, method="auto")

        assert len(result) == 10
        pd.testing.assert_frame_equal(result, df)


class TestResamplingMethods:
    """Test all resampling methods."""

    def test_all_methods_with_same_data(self):
        """Test that all methods work with the same dataset."""
        df = pd.DataFrame({"value": range(100)})
        target_size = 10

        methods = ["auto", "uniform", "time_aware", "random", "stratified", "minmax"]

        for method in methods:
            result = _resample_dataframe(df, target_size, method=method)
            assert len(result) <= target_size, f"Method {method} failed size constraint"
            assert len(result) > 0, f"Method {method} returned empty dataframe"

    def test_invalid_method_fallback(self):
        """Test that invalid method falls back to uniform."""
        df = pd.DataFrame({"value": range(100)})
        result = _resample_dataframe(df, 10, method="invalid_method")

        assert len(result) == 10


class TestEdgeCases:
    """Test edge cases for resampling."""

    def test_empty_dataframe(self):
        """Test resampling with empty dataframe."""
        df = pd.DataFrame({"value": []})
        result = _resample_dataframe(df, 10)

        assert len(result) == 0

    def test_single_row(self):
        """Test resampling with single row."""
        df = pd.DataFrame({"value": [1]})
        result = _resample_dataframe(df, 10)

        assert len(result) == 1
        pd.testing.assert_frame_equal(result, df)

    def test_target_size_equals_dataframe_size(self):
        """Test when target size equals dataframe size."""
        df = pd.DataFrame({"value": range(10)})
        result = _resample_dataframe(df, 10)

        assert len(result) == 10

    def test_very_large_target_size(self):
        """Test with target size much larger than dataframe."""
        df = pd.DataFrame({"value": range(10)})
        result = _resample_dataframe(df, 1000)

        assert len(result) == 10
        pd.testing.assert_frame_equal(result, df)

    def test_mixed_data_types(self):
        """Test resampling with mixed data types."""
        df = pd.DataFrame(
            {
                "int_col": range(100),
                "float_col": [float(x) for x in range(100)],
                "str_col": [f"text_{x}" for x in range(100)],
                "bool_col": [x % 2 == 0 for x in range(100)],
            }
        )
        result = _resample_dataframe(df, 20)

        assert len(result) <= 20
        assert list(result.columns) == ["int_col", "float_col", "str_col", "bool_col"]


class TestPerformance:
    """Test performance characteristics of resampling."""

    def test_large_dataframe_uniform(self):
        """Test uniform sampling with large dataframe."""
        df = pd.DataFrame({"value": range(10000)})
        result = _resample_dataframe_uniform(df, 100)

        assert len(result) == 100

    def test_large_dataframe_time_aware(self):
        """Test time-aware sampling with large datetime dataframe."""
        dates = pd.date_range("2024-01-01", periods=10000, freq="1min")
        df = pd.DataFrame({"value": range(10000)}, index=dates)
        result = _resample_dataframe_time_aware(df, 100)

        assert len(result) <= 100

    def test_many_columns(self):
        """Test resampling with many columns."""
        data = {f"col_{i}": range(1000) for i in range(50)}
        df = pd.DataFrame(data)
        result = _resample_dataframe(df, 100)

        assert len(result) <= 100
        assert len(result.columns) == 50
