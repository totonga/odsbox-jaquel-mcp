"""Measurement analysis tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from ..measurement_analysis import ComparisonResult, MeasurementAnalyzer
from ..measurement_queries import MeasurementHierarchyExplorer
from ..notebook_generator import NotebookGenerator
from ..visualization_templates import VisualizationTemplateGenerator
from .base_handler import BaseToolHandler


class MeasurementToolHandler(BaseToolHandler):
    """Handles measurement analysis and visualization tools."""

    @staticmethod
    def generate_measurement_comparison_notebook(arguments: dict[str, Any]) -> list[TextContent]:
        """Generate a Jupyter notebook for comparing measurements."""
        try:
            measurement_query_conditions = arguments.get("measurement_query_conditions", {})
            measurement_quantity_names = arguments.get("measurement_quantity_names", [])
            ods_url = arguments.get("ods_url", "")
            ods_username = arguments.get("ods_username", "")
            ods_password = arguments.get("ods_password", "")
            available_quantities = arguments.get("available_quantities", None)
            plot_type = arguments.get("plot_type", "scatter")
            title = arguments.get("title", "Measurement Comparison")
            output_path = arguments.get("output_path", None)

            notebook = NotebookGenerator.generate_measurement_comparison_notebook(
                measurement_query_conditions=measurement_query_conditions,
                measurement_quantity_names=measurement_quantity_names,
                ods_url=ods_url,
                ods_username=ods_username,
                ods_password=ods_password,
                available_quantities=available_quantities,
                plot_type=plot_type,
                title=title,
            )

            result = {
                "title": title,
                "plot_type": plot_type,
                "measurement_quantities": measurement_quantity_names,
                "num_cells": len(notebook["cells"]),
            }

            if output_path:
                NotebookGenerator.save_notebook(notebook, output_path)
                result["saved_to"] = output_path
                result["status"] = "Notebook saved successfully"
            else:
                result["status"] = "Notebook generated successfully"
                result["notebook"] = notebook

            return MeasurementToolHandler.json_response(result)
        except Exception as e:
            return MeasurementToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def generate_plotting_code(arguments: dict[str, Any]) -> list[TextContent]:
        """Generate Python plotting code for measurement comparison."""
        try:
            measurement_quantity_names = arguments.get("measurement_quantity_names", [])
            submatrices_count = arguments.get("submatrices_count", 0)
            plot_type = arguments.get("plot_type", "scatter")

            if plot_type == "scatter":
                if len(measurement_quantity_names) < 2:
                    raise ValueError("Scatter plot requires at least 2 measurement quantities")
                code = VisualizationTemplateGenerator.generate_scatter_plot_code(
                    measurement_quantity_names=measurement_quantity_names,
                    submatrices_count=submatrices_count,
                )
            elif plot_type == "line":
                code = VisualizationTemplateGenerator.generate_line_plot_code(
                    measurement_quantity_names=measurement_quantity_names,
                    submatrices_count=submatrices_count,
                )
            elif plot_type == "subplots":
                code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
                    measurement_quantity_names=measurement_quantity_names,
                    submatrices_count=submatrices_count,
                )
            else:
                raise ValueError(f"Unknown plot type: {plot_type}")

            result = {
                "plot_type": plot_type,
                "measurement_quantities": measurement_quantity_names,
                "submatrices_count": submatrices_count,
                "code": code,
                "description": (
                    f"Generated {plot_type} plot code for "
                    f"{len(measurement_quantity_names)} quantities and "
                    f"{submatrices_count} submatrices"
                ),
            }

            return MeasurementToolHandler.json_response(result)
        except Exception as e:
            return MeasurementToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def compare_measurements(arguments: dict[str, Any]) -> list[TextContent]:
        """Compare measurements across quantities with statistical analysis."""
        try:
            quantity_name = arguments.get("quantity_name", "")
            measurement_data = arguments.get("measurement_data", {})
            measurement_names = arguments.get("measurement_names", {})

            if not quantity_name or not measurement_data:
                raise ValueError("quantity_name and measurement_data are required")

            # Convert string keys to integers for measurement_data
            converted_data: dict[int | str, Any] = {}
            for key, values in measurement_data.items():
                try:
                    meas_id = int(key)
                    converted_data[meas_id] = values
                except (ValueError, TypeError):
                    converted_data[key] = values

            # Perform multi-measurement comparison
            comparison_result = MeasurementAnalyzer.compare_multiple_measurements(quantity_name, converted_data)

            # If measurement_names provided, generate summary
            if measurement_names:
                quantity_names = [quantity_name]
                comparison_results = [
                    ComparisonResult(
                        quantity_name=c["quantity_name"],
                        measurement_1_id=c["measurement_1_id"],
                        measurement_2_id=c["measurement_2_id"],
                        measurement_1_mean=c["measurement_1_mean"],
                        measurement_2_mean=c["measurement_2_mean"],
                        mean_difference=c["mean_difference"],
                        mean_difference_percent=c["mean_difference_percent"],
                        correlation=c["correlation"],
                        notes=c["notes"],
                    )
                    for c in comparison_result.get("pairwise_comparisons", [])
                ]

                summary = MeasurementAnalyzer.generate_comparison_summary(
                    measurement_names, quantity_names, comparison_results
                )
                comparison_result["summary"] = summary

            return MeasurementToolHandler.json_response(comparison_result)
        except Exception as e:
            return MeasurementToolHandler.error_response(str(e), type(e).__name__)

    @staticmethod
    def query_measurement_hierarchy(arguments: dict[str, Any]) -> list[TextContent]:
        """Query and explore ODS measurement hierarchy and structure."""
        try:
            query_result = arguments.get("query_result", {})
            operation = arguments.get("operation", "extract_measurements")

            if operation == "extract_measurements":
                measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
                result = {
                    "operation": operation,
                    "num_measurements": len(measurements),
                    "measurements": measurements[:50],  # Limit output
                }

            elif operation == "build_hierarchy":
                measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
                hierarchy = MeasurementHierarchyExplorer.build_measurement_hierarchy(measurements)
                result = {
                    "operation": operation,
                    "hierarchy_keys": list(hierarchy.keys()),
                    "total_measurements": hierarchy["total_measurements"],
                    "tests": list(hierarchy["by_test"].keys()),
                    "statuses": list(hierarchy["by_status"].keys()),
                }

            elif operation == "get_unique_tests":
                measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
                tests = MeasurementHierarchyExplorer.get_unique_tests(measurements)
                result = {
                    "operation": operation,
                    "unique_tests": tests,
                    "num_tests": len(tests),
                }

            elif operation == "get_unique_quantities":
                measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
                unique_quantities: list[str] = MeasurementHierarchyExplorer.get_unique_quantities(measurements)
                result = {
                    "operation": operation,
                    "unique_quantities": unique_quantities,
                    "num_quantities": len(unique_quantities),
                }

            elif operation == "build_index":
                measurements = MeasurementHierarchyExplorer.extract_measurements_from_query_result(query_result)
                index = MeasurementHierarchyExplorer.build_measurement_index(measurements)
                result = {
                    "operation": operation,
                    "total_measurements": index["total_measurements"],
                    "index_by_id_count": len(index["by_id"]),
                    "index_by_name_count": len(index["by_name"]),
                    "index_by_test_count": len(index["by_test"]),
                    "index_by_status_count": len(index["by_status"]),
                    "available_test_names": list(index["by_test"].keys())[:10],
                }

            else:
                raise ValueError(f"Unknown operation: {operation}")

            return MeasurementToolHandler.json_response(result)
        except Exception as e:
            return MeasurementToolHandler.error_response(str(e), type(e).__name__)
