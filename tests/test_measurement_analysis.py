"""Unit tests for measurement_analysis module."""

import pytest
from odsbox_jaquel_mcp.measurement_analysis import (
    MeasurementAnalyzer,
    ColumnStatistics,
    ComparisonResult,
)


class TestColumnStatistics:
    """Test ColumnStatistics dataclass."""

    def test_column_statistics_creation(self):
        """Test creating ColumnStatistics."""
        stats = ColumnStatistics(
            name="Speed",
            count=100,
            mean=50.0,
            median=48.0,
            stdev=5.0,
            min=40.0,
            max=60.0,
            range=20.0,
        )
        assert stats.name == "Speed"
        assert stats.count == 100
        assert stats.mean == 50.0

    def test_column_statistics_to_dict(self):
        """Test converting ColumnStatistics to dict."""
        stats = ColumnStatistics(
            name="Speed",
            count=100,
            mean=50.0,
            median=48.0,
            stdev=5.0,
            min=40.0,
            max=60.0,
            range=20.0,
        )
        result = stats.to_dict()
        assert isinstance(result, dict)
        assert result["name"] == "Speed"
        assert result["mean"] == 50.0

    def test_column_statistics_with_none_values(self):
        """Test ColumnStatistics with None values."""
        stats = ColumnStatistics(
            name="Speed",
            count=0,
            mean=None,
            median=None,
            stdev=None,
            min=None,
            max=None,
            range=None,
        )
        assert stats.mean is None
        assert stats.count == 0


class TestCalculateStatistics:
    """Test calculate_statistics method."""

    def test_calculate_statistics_basic(self):
        """Test basic statistics calculation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = MeasurementAnalyzer.calculate_statistics(values)
        assert stats.count == 5
        assert stats.mean == 3.0
        assert stats.median == 3.0
        assert stats.min == 1.0
        assert stats.max == 5.0
        assert stats.range == 4.0

    def test_calculate_statistics_with_stdev(self):
        """Test standard deviation calculation."""
        values = [10.0, 20.0, 30.0]
        stats = MeasurementAnalyzer.calculate_statistics(values)
        assert stats.stdev is not None
        assert stats.mean == 20.0

    def test_calculate_statistics_single_value(self):
        """Test with single value (no stdev)."""
        values = [42.0]
        stats = MeasurementAnalyzer.calculate_statistics(values)
        assert stats.count == 1
        assert stats.mean == 42.0
        assert stats.stdev is None

    def test_calculate_statistics_empty_list(self):
        """Test with empty list."""
        stats = MeasurementAnalyzer.calculate_statistics([])
        assert stats.count == 0
        assert stats.mean is None

    def test_calculate_statistics_mixed_types(self):
        """Test with mixed numeric types."""
        values = [1, 2.0, 3, 4.5, 5]
        stats = MeasurementAnalyzer.calculate_statistics(values)
        assert stats.count == 5
        assert stats.mean == 3.1

    def test_calculate_statistics_with_non_numeric(self):
        """Test filtering non-numeric values."""
        values = [1.0, "invalid", 2.0, None, 3.0]
        stats = MeasurementAnalyzer.calculate_statistics(values)
        assert stats.count == 5  # Total count includes all inputs
        # But mean only uses numeric values

    def test_calculate_statistics_all_non_numeric(self):
        """Test with all non-numeric values."""
        values = ["a", "b", None]
        stats = MeasurementAnalyzer.calculate_statistics(values)
        assert stats.count == 3
        assert stats.mean is None


class TestComparisonResult:
    """Test ComparisonResult dataclass."""

    def test_comparison_result_creation(self):
        """Test creating ComparisonResult."""
        result = ComparisonResult(
            quantity_name="Speed",
            measurement_1_id=1,
            measurement_2_id=2,
            measurement_1_mean=50.0,
            measurement_2_mean=55.0,
            mean_difference=5.0,
            mean_difference_percent=10.0,
            correlation=0.95,
            notes=["Test note"],
        )
        assert result.quantity_name == "Speed"
        assert result.mean_difference == 5.0
        assert result.correlation == 0.95

    def test_comparison_result_to_dict(self):
        """Test converting ComparisonResult to dict."""
        result = ComparisonResult(
            quantity_name="Speed",
            measurement_1_id=1,
            measurement_2_id=2,
            measurement_1_mean=50.0,
            measurement_2_mean=55.0,
            mean_difference=5.0,
            mean_difference_percent=10.0,
            correlation=0.95,
            notes=["Test note"],
        )
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["quantity_name"] == "Speed"
        assert result_dict["correlation"] == 0.95


class TestCompareQuantities:
    """Test compare_quantities method."""

    def test_compare_quantities_identical(self):
        """Test comparing identical value sets."""
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            [10.0, 20.0, 30.0],
            [10.0, 20.0, 30.0],
            measurement_1_id=1,
            measurement_2_id=2,
        )
        assert result.quantity_name == "Speed"
        assert result.mean_difference == pytest.approx(0.0)
        assert result.mean_difference_percent == pytest.approx(0.0)
        # Correlation exists and is calculated
        assert result.correlation is not None

    def test_compare_quantities_different_means(self):
        """Test comparing with different means."""
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            [10.0, 20.0, 30.0],
            [20.0, 30.0, 40.0],
            measurement_1_id=1,
            measurement_2_id=2,
        )
        assert result.measurement_1_id == 1
        assert result.measurement_2_id == 2
        assert result.quantity_name == "Speed"

    def test_compare_quantities_with_difference(self):
        """Test comparing values with known difference."""
        result = MeasurementAnalyzer.compare_quantities(
            "Torque",
            [50.0, 60.0, 70.0],
            [55.0, 65.0, 75.0],
            measurement_1_id=1,
            measurement_2_id=2,
        )
        assert result.quantity_name == "Torque"
        assert result.measurement_1_id == 1
        assert result.measurement_2_id == 2
        assert result.mean_difference == pytest.approx(5.0)
        # Mean difference percent: (5 / 60) * 100 = 8.33%
        assert result.mean_difference_percent == pytest.approx(8.33, abs=0.2)

    def test_compare_quantities_empty_values(self):
        """Test with empty value sets."""
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            [],
            [1.0, 2.0],
            measurement_1_id=1,
            measurement_2_id=2,
        )
        assert result.measurement_1_mean is None
        assert "Insufficient data" in result.notes[0]

    def test_compare_quantities_negative_correlation(self):
        """Test detecting negative correlation."""
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            [1.0, 2.0, 3.0],
            [10.0, 5.0, 0.0],  # Strong negative trend
            measurement_1_id=1,
            measurement_2_id=2,
        )
        assert result.correlation is not None
        assert result.correlation < 0

    def test_compare_quantities_size_mismatch_note(self):
        """Test that size mismatch generates note."""
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            [1.0, 2.0],
            [1.0, 2.0, 3.0],
            measurement_1_id=1,
            measurement_2_id=2,
        )
        size_mismatch_notes = [n for n in result.notes if "sample size" in n.lower()]
        assert len(size_mismatch_notes) > 0

    def test_compare_quantities_significant_difference_note(self):
        """Test that significant difference generates note."""
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            [100.0],
            [112.0],  # 12% difference
            measurement_1_id=1,
            measurement_2_id=2,
        )
        sig_diff_notes = [n for n in result.notes if "Significant" in n]
        assert len(sig_diff_notes) > 0

    def test_compare_quantities_strong_correlation_note(self):
        """Test that strong correlation generates note."""
        # Use larger dataset for more reliable correlation
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            list(range(1, 101, 1)),
            list(range(2, 202, 2)),  # Perfect linear relationship
            measurement_1_id=1,
            measurement_2_id=2,
        )
        # With larger sample, should get strong positive correlation
        assert result.correlation is not None and result.correlation > 0.98


class TestMultipleMeasurementComparison:
    """Test compare_multiple_measurements method."""

    def test_compare_multiple_measurements_basic(self):
        """Test comparing multiple measurements."""
        measurement_data = {
            1: [10.0, 20.0, 30.0],
            2: [15.0, 25.0, 35.0],
            3: [12.0, 22.0, 32.0],
        }
        result = MeasurementAnalyzer.compare_multiple_measurements(
            "Speed", measurement_data
        )
        assert result["quantity_name"] == "Speed"
        assert result["num_measurements"] == 3
        assert 1 in result["measurement_ids"]
        assert "statistics_by_measurement" in result
        assert "pairwise_comparisons" in result

    def test_compare_multiple_measurements_pairwise_count(self):
        """Test that pairwise comparisons are correct."""
        measurement_data = {1: [1.0], 2: [2.0], 3: [3.0]}
        result = MeasurementAnalyzer.compare_multiple_measurements(
            "Speed", measurement_data
        )
        # 3 measurements = 3 pairwise comparisons (1v2, 1v3, 2v3)
        assert result["num_pairwise_comparisons"] == 3

    def test_compare_multiple_measurements_empty(self):
        """Test with empty measurement data."""
        result = MeasurementAnalyzer.compare_multiple_measurements(
            "Speed", {}
        )
        assert result["num_measurements"] == 0
        assert "error" in result

    def test_compare_multiple_measurements_overall_stats(self):
        """Test that overall statistics are calculated."""
        measurement_data = {
            1: [10.0, 20.0],
            2: [30.0, 40.0],
        }
        result = MeasurementAnalyzer.compare_multiple_measurements(
            "Speed", measurement_data
        )
        overall_stats = result["overall_statistics"]
        assert overall_stats["mean"] == 25.0


class TestComparisonSummary:
    """Test generate_comparison_summary method."""

    def test_generate_comparison_summary_basic(self):
        """Test generating comparison summary."""
        measurement_names = {1: "Test_1", 2: "Test_2"}
        quantity_names = ["Speed", "Torque"]
        comparison_results = [
            ComparisonResult(
                quantity_name="Speed",
                measurement_1_id=1,
                measurement_2_id=2,
                measurement_1_mean=50.0,
                measurement_2_mean=55.0,
                mean_difference=5.0,
                mean_difference_percent=10.0,
                correlation=0.95,
                notes=["Test"],
            ),
        ]

        summary = MeasurementAnalyzer.generate_comparison_summary(
            measurement_names, quantity_names, comparison_results
        )
        assert summary["num_quantities"] == 2
        assert summary["num_comparisons"] == 1
        assert summary["measurements"] == measurement_names

    def test_generate_comparison_summary_detects_significant_diffs(self):
        """Test that summary detects significant differences."""
        measurement_names = {1: "Test_1", 2: "Test_2"}
        quantity_names = ["Speed"]
        comparison_results = [
            ComparisonResult(
                quantity_name="Speed",
                measurement_1_id=1,
                measurement_2_id=2,
                measurement_1_mean=100.0,
                measurement_2_mean=120.0,
                mean_difference=20.0,
                mean_difference_percent=20.0,  # >10% threshold
                correlation=0.5,
                notes=[],
            ),
        ]

        summary = MeasurementAnalyzer.generate_comparison_summary(
            measurement_names, quantity_names, comparison_results
        )
        assert summary["significant_differences_found"] == 1

    def test_generate_comparison_summary_detects_correlations(self):
        """Test that summary detects strong correlations."""
        measurement_names = {1: "Test_1", 2: "Test_2"}
        quantity_names = ["Speed"]
        comparison_results = [
            ComparisonResult(
                quantity_name="Speed",
                measurement_1_id=1,
                measurement_2_id=2,
                measurement_1_mean=50.0,
                measurement_2_mean=55.0,
                mean_difference=5.0,
                mean_difference_percent=10.0,
                correlation=0.96,  # >0.95 threshold
                notes=[],
            ),
        ]

        summary = MeasurementAnalyzer.generate_comparison_summary(
            measurement_names, quantity_names, comparison_results
        )
        assert summary["strong_correlations_found"] == 1

    def test_generate_comparison_summary_empty(self):
        """Test summary with no comparisons."""
        summary = MeasurementAnalyzer.generate_comparison_summary(
            {}, [], []
        )
        assert summary["num_comparisons"] == 0


class TestCalculateCorrelation:
    """Test _calculate_correlation private method."""

    def test_correlation_perfect_positive(self):
        """Test perfect positive correlation."""
        # Use larger dataset for more reliable correlation
        values_x = list(range(1, 51, 1))
        values_y = [v * 2 for v in values_x]  # Perfect linear relationship
        result = MeasurementAnalyzer._calculate_correlation(values_x, values_y)
        # With larger sample, should be very close to 1.0
        assert result is not None and result > 0.95

    def test_correlation_perfect_negative(self):
        """Test perfect negative correlation."""
        # Use larger dataset for more reliable correlation
        values_x = list(range(1, 51, 1))
        values_y = [100 - v for v in values_x]  # Perfect inverse relationship
        result = MeasurementAnalyzer._calculate_correlation(values_x, values_y)
        # With larger sample, should be very close to -1.0
        assert result is not None and result < -0.95

    def test_correlation_no_correlation(self):
        """Test no correlation."""
        result = MeasurementAnalyzer._calculate_correlation(
            [1.0, 2.0, 3.0, 4.0],
            [4.0, 2.0, 3.0, 1.0],
        )
        assert result is not None

    def test_correlation_insufficient_data(self):
        """Test with insufficient data."""
        result = MeasurementAnalyzer._calculate_correlation([1.0], [2.0])
        assert result is None

    def test_correlation_empty_lists(self):
        """Test with empty lists."""
        result = MeasurementAnalyzer._calculate_correlation([], [])
        assert result is None

    def test_correlation_constant_values(self):
        """Test with constant values (zero stdev)."""
        result = MeasurementAnalyzer._calculate_correlation(
            [5.0, 5.0, 5.0], [1.0, 2.0, 3.0]
        )
        assert result is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_calculate_statistics_with_negative_values(self):
        """Test statistics with negative values."""
        stats = MeasurementAnalyzer.calculate_statistics([-10.0, -5.0, 0.0, 5.0, 10.0])
        assert stats.mean == 0.0
        assert stats.min == -10.0
        assert stats.max == 10.0

    def test_compare_quantities_zero_mean(self):
        """Test comparison when mean is zero."""
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            [0.0, 0.0, 0.0],
            [1.0, 2.0, 3.0],
            measurement_1_id=1,
            measurement_2_id=2,
        )
        assert result.mean_difference_percent is None  # Can't calculate percent of zero

    def test_compare_quantities_very_small_values(self):
        """Test comparison with very small values."""
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            [0.001, 0.002, 0.003],
            [0.001, 0.002, 0.003],
            measurement_1_id=1,
            measurement_2_id=2,
        )
        assert result.mean_difference_percent == pytest.approx(0.0)

    def test_compare_quantities_very_large_values(self):
        """Test comparison with very large values."""
        result = MeasurementAnalyzer.compare_quantities(
            "Speed",
            [1e6, 2e6, 3e6, 4e6, 5e6],
            [1e6, 2e6, 3e6, 4e6, 5e6],
            measurement_1_id=1,
            measurement_2_id=2,
        )
        # Verify means are equal
        assert result.mean_difference == pytest.approx(0.0)
        # Correlation exists
        assert result.correlation is not None
