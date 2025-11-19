"""Measurement analysis utilities for comparison and statistical analysis.

Provides tools for comparing multiple measurements, calculating statistics,
and generating comparison reports.
"""

from __future__ import annotations

import statistics
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ColumnStatistics:
    """Statistics for a single measurement quantity."""

    name: str
    count: int
    mean: Optional[float]
    median: Optional[float]
    stdev: Optional[float]
    min: Optional[float]
    max: Optional[float]
    range: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ComparisonResult:
    """Result of comparing two quantities across measurements."""

    quantity_name: str
    measurement_1_id: int
    measurement_2_id: int
    measurement_1_mean: Optional[float]
    measurement_2_mean: Optional[float]
    mean_difference: Optional[float]
    mean_difference_percent: Optional[float]
    correlation: Optional[float]
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MeasurementAnalyzer:
    """Analyze and compare measurement data."""

    @staticmethod
    def calculate_statistics(values: List[float]) -> ColumnStatistics:
        """Calculate statistics for a list of numeric values.

        Args:
            values: List of numeric values

        Returns:
            ColumnStatistics object with calculated statistics
        """
        if not values:
            return ColumnStatistics(
                name="",
                count=0,
                mean=None,
                median=None,
                stdev=None,
                min=None,
                max=None,
                range=None,
            )

        try:
            numeric_values = [v for v in values if isinstance(v, (int, float))]

            if not numeric_values:
                return ColumnStatistics(
                    name="",
                    count=len(values),
                    mean=None,
                    median=None,
                    stdev=None,
                    min=None,
                    max=None,
                    range=None,
                )

            mean = statistics.mean(numeric_values)
            median = statistics.median(numeric_values)
            stdev = statistics.stdev(numeric_values) if len(numeric_values) > 1 else None
            min_val = min(numeric_values)
            max_val = max(numeric_values)
            range_val = max_val - min_val

            return ColumnStatistics(
                name="",
                count=len(values),
                mean=mean,
                median=median,
                stdev=stdev,
                min=min_val,
                max=max_val,
                range=range_val,
            )

        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to calculate statistics: {e}") from e

    @staticmethod
    def compare_quantities(
        quantity_name: str,
        values_1: List[float],
        values_2: List[float],
        measurement_1_id: int = 1,
        measurement_2_id: int = 2,
    ) -> ComparisonResult:
        """Compare a quantity across two measurements.

        Args:
            quantity_name: Name of the quantity being compared
            values_1: Values from first measurement
            values_2: Values from second measurement
            measurement_1_id: ID of first measurement
            measurement_2_id: ID of second measurement

        Returns:
            ComparisonResult with comparison metrics
        """
        notes: List[str] = []

        if not values_1 or not values_2:
            return ComparisonResult(
                quantity_name=quantity_name,
                measurement_1_id=measurement_1_id,
                measurement_2_id=measurement_2_id,
                measurement_1_mean=None,
                measurement_2_mean=None,
                mean_difference=None,
                mean_difference_percent=None,
                correlation=None,
                notes=["Insufficient data for comparison"],
            )

        try:
            numeric_1 = [v for v in values_1 if isinstance(v, (int, float))]
            numeric_2 = [v for v in values_2 if isinstance(v, (int, float))]

            if not numeric_1 or not numeric_2:
                return ComparisonResult(
                    quantity_name=quantity_name,
                    measurement_1_id=measurement_1_id,
                    measurement_2_id=measurement_2_id,
                    measurement_1_mean=None,
                    measurement_2_mean=None,
                    mean_difference=None,
                    mean_difference_percent=None,
                    correlation=None,
                    notes=["No numeric data available"],
                )

            mean_1 = statistics.mean(numeric_1)
            mean_2 = statistics.mean(numeric_2)
            mean_diff = mean_2 - mean_1

            mean_diff_pct = None
            if mean_1 != 0:
                mean_diff_pct = (mean_diff / mean_1) * 100

            # Calculate correlation
            correlation = MeasurementAnalyzer._calculate_correlation(numeric_1, numeric_2)

            if correlation is not None and correlation > 0.95:
                notes.append("Strong positive correlation detected")
            elif correlation is not None and correlation < -0.95:
                notes.append("Strong negative correlation detected")

            if mean_diff_pct is not None and abs(mean_diff_pct) > 10:
                notes.append(f"Significant difference ({mean_diff_pct:.1f}%)")

            if len(numeric_1) != len(numeric_2):
                notes.append(f"Different sample sizes: {len(numeric_1)} vs {len(numeric_2)}")

            return ComparisonResult(
                quantity_name=quantity_name,
                measurement_1_id=measurement_1_id,
                measurement_2_id=measurement_2_id,
                measurement_1_mean=mean_1,
                measurement_2_mean=mean_2,
                mean_difference=mean_diff,
                mean_difference_percent=mean_diff_pct,
                correlation=correlation,
                notes=notes,
            )

        except (ValueError, TypeError) as e:
            return ComparisonResult(
                quantity_name=quantity_name,
                measurement_1_id=measurement_1_id,
                measurement_2_id=measurement_2_id,
                measurement_1_mean=None,
                measurement_2_mean=None,
                mean_difference=None,
                mean_difference_percent=None,
                correlation=None,
                notes=[f"Comparison failed: {str(e)}"],
            )

    @staticmethod
    def _calculate_correlation(values_1: List[float], values_2: List[float]) -> Optional[float]:
        """Calculate Pearson correlation coefficient.

        Args:
            values_1: First list of values
            values_2: Second list of values

        Returns:
            Correlation coefficient (-1 to 1), or None if calculation fails
        """
        try:
            # Both must have same length
            min_len = min(len(values_1), len(values_2))
            if min_len < 2:
                return None

            x = values_1[:min_len]
            y = values_2[:min_len]

            mean_x = statistics.mean(x)
            mean_y = statistics.mean(y)

            cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x))) / len(x)
            std_x = statistics.stdev(x) if len(x) > 1 else 0
            std_y = statistics.stdev(y) if len(y) > 1 else 0

            if std_x == 0 or std_y == 0:
                return None

            correlation = cov / (std_x * std_y)
            return max(-1.0, min(1.0, correlation))

        except (ValueError, ZeroDivisionError, TypeError):
            return None

    @staticmethod
    def compare_multiple_measurements(
        quantity_name: str,
        measurement_data: Dict[int, List[float]],
    ) -> Dict[str, Any]:
        """Compare a quantity across multiple measurements.

        Args:
            quantity_name: Name of quantity to compare
            measurement_data: Dict mapping measurement_id -> values list

        Returns:
            Summary comparison dictionary
        """
        if not measurement_data:
            return {
                "quantity_name": quantity_name,
                "num_measurements": 0,
                "error": "No measurement data provided",
            }

        try:
            stats_by_measurement: Dict[int, Dict[str, Any]] = {}
            measurement_ids = sorted(measurement_data.keys())

            for meas_id, values in measurement_data.items():
                stats = MeasurementAnalyzer.calculate_statistics(values)
                stats.name = quantity_name
                stats_by_measurement[meas_id] = stats.to_dict()

            # Calculate overall statistics
            all_values = [v for vals in measurement_data.values() for v in vals]
            overall_stats = MeasurementAnalyzer.calculate_statistics(all_values)
            overall_stats.name = quantity_name

            # Find pairwise comparisons
            pairwise_comparisons = []
            for i, id1 in enumerate(measurement_ids):
                for id2 in measurement_ids[i + 1 :]:
                    comparison = MeasurementAnalyzer.compare_quantities(
                        quantity_name,
                        measurement_data[id1],
                        measurement_data[id2],
                        measurement_1_id=id1,
                        measurement_2_id=id2,
                    )
                    pairwise_comparisons.append(comparison.to_dict())

            return {
                "quantity_name": quantity_name,
                "num_measurements": len(measurement_data),
                "measurement_ids": measurement_ids,
                "statistics_by_measurement": stats_by_measurement,
                "overall_statistics": overall_stats.to_dict(),
                "pairwise_comparisons": pairwise_comparisons,
                "num_pairwise_comparisons": len(pairwise_comparisons),
            }

        except Exception as e:
            return {
                "quantity_name": quantity_name,
                "error": f"Multi-measurement comparison failed: {str(e)}",
            }

    @staticmethod
    def generate_comparison_summary(
        measurement_names: Dict[int, str],
        quantity_names: List[str],
        comparison_results: List[ComparisonResult],
    ) -> Dict[str, Any]:
        """Generate a summary report of all comparisons.

        Args:
            measurement_names: Dict mapping measurement_id -> name
            quantity_names: List of quantity names being compared
            comparison_results: List of comparison results

        Returns:
            Summary report dictionary
        """
        if not comparison_results:
            return {
                "num_quantities": len(quantity_names),
                "num_comparisons": 0,
                "measurements": measurement_names,
                "summary": "No comparisons to summarize",
            }

        try:
            significant_diffs = [
                c for c in comparison_results if c.mean_difference_percent and abs(c.mean_difference_percent) > 10
            ]

            strong_correlations = [c for c in comparison_results if c.correlation and abs(c.correlation) > 0.95]

            return {
                "num_quantities": len(quantity_names),
                "num_comparisons": len(comparison_results),
                "measurements": measurement_names,
                "quantities": quantity_names,
                "significant_differences_found": len(significant_diffs),
                "significant_differences": [
                    {
                        "quantity": c.quantity_name,
                        "measurements": f"{c.measurement_1_id} vs {c.measurement_2_id}",
                        "difference_percent": c.mean_difference_percent,
                    }
                    for c in significant_diffs
                ],
                "strong_correlations_found": len(strong_correlations),
                "strong_correlations": [
                    {
                        "quantity": c.quantity_name,
                        "measurements": f"{c.measurement_1_id} vs {c.measurement_2_id}",
                        "correlation": c.correlation,
                    }
                    for c in strong_correlations
                ],
                "notes": [note for c in comparison_results for note in c.notes],
            }

        except Exception as e:
            return {
                "error": f"Summary generation failed: {str(e)}",
            }
