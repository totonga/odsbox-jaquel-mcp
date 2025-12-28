"""Visualization template generators for measurement comparison notebooks.

Generates Python code for creating matplotlib plots with various configurations.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

from jinja2 import Environment, FileSystemLoader


class VisualizationTemplateGenerator:
    """Generate plotting code templates."""

    @staticmethod
    def _get_jinja_env() -> Environment:
        """Get configured Jinja2 environment for visualization templates."""
        template_dir = Path(__file__).parent / "templates"
        return Environment(loader=FileSystemLoader(str(template_dir)), trim_blocks=True, lstrip_blocks=True)

    @staticmethod
    def generate_scatter_plot_code(
        measurement_quantity_names: list[str],
        submatrices_count: int,
        subplots_per_row: int = 3,
        figsize_width: float = 15.0,
        figsize_height_per_row: float = 5.0,
    ) -> str:
        """
        Generate code for creating scatter plots with multiple submatrices.

        Args:
            measurement_quantity_names: List of quantity names to plot (must have exactly 2)
            submatrices_count: Number of submatrices to plot
            subplots_per_row: Number of plots per row (default: 3)
            figsize_width: Figure width in inches
            figsize_height_per_row: Figure height per row in inches

        Returns:
            Python code string for plotting
        """
        if len(measurement_quantity_names) < 2:
            raise ValueError("At least 2 measurement quantities required for scatter plot")

        env = VisualizationTemplateGenerator._get_jinja_env()
        template = env.get_template("visualization_scatter.j2")

        return cast(
            str,
            template.render(
                x_qty=measurement_quantity_names[0],
                y_qty=measurement_quantity_names[1],
                submatrices_count=submatrices_count,
                subplots_per_row=subplots_per_row,
                figsize_width=figsize_width,
                figsize_height_per_row=figsize_height_per_row,
            ),
        )

    @staticmethod
    def generate_line_plot_code(
        measurement_quantity_names: list[str],
        submatrices_count: int,
        subplots_per_row: int = 3,
        figsize_width: float = 15.0,
        figsize_height_per_row: float = 5.0,
    ) -> str:
        """
        Generate code for creating line plots with multiple submatrices.

        Args:
            measurement_quantity_names: List of quantity names to plot
            submatrices_count: Number of submatrices to plot
            subplots_per_row: Number of plots per row (default: 3)
            figsize_width: Figure width in inches
            figsize_height_per_row: Figure height per row in inches

        Returns:
            Python code string for plotting
        """
        env = VisualizationTemplateGenerator._get_jinja_env()
        template = env.get_template("visualization_line.j2")

        return cast(
            str,
            template.render(
                measurement_quantity_names=measurement_quantity_names,
                submatrices_count=submatrices_count,
                subplots_per_row=subplots_per_row,
                figsize_width=figsize_width,
                figsize_height_per_row=figsize_height_per_row,
            ),
        )

    @staticmethod
    def generate_subplots_per_measurement_code(
        measurement_quantity_names: list[str],
        submatrices_count: int,
    ) -> str:
        """
        Generate code for creating separate subplots for each quantity.

        Args:
            measurement_quantity_names: List of quantity names to plot
            submatrices_count: Number of submatrices to plot

        Returns:
            Python code string for plotting
        """
        env = VisualizationTemplateGenerator._get_jinja_env()
        template = env.get_template("visualization_subplots.j2")

        return cast(
            str,
            template.render(
                measurement_quantity_names=measurement_quantity_names,
                submatrices_count=submatrices_count,
            ),
        )
