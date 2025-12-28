"""Jupyter notebook generator for measurement comparison workflows.

Generates complete Jupyter notebooks with measurement comparison workflows
including data retrieval, preparation, and visualization.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


class NotebookGenerator:
    """Generate Jupyter notebooks for measurement comparison."""

    @staticmethod
    def _get_jinja_env() -> Environment:
        """Get configured Jinja2 environment for notebook templates."""
        template_dir = Path(__file__).parent / "templates"
        return Environment(loader=FileSystemLoader(str(template_dir)), trim_blocks=True, lstrip_blocks=True)

    @staticmethod
    def create_markdown_cell(content: str) -> dict[str, Any]:
        """
        Create a markdown cell.

        Args:
            content: Markdown content

        Returns:
            Cell dictionary for notebook
        """
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": content.split("\n"),
        }

    @staticmethod
    def create_code_cell(code: str, description: str = "") -> dict[str, Any]:
        """
        Create a code cell.

        Args:
            code: Python code content
            description: Optional description for the cell

        Returns:
            Cell dictionary for notebook
        """
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": code.split("\n"),
        }

    @staticmethod
    def plot_comparison_notebook(
        measurement_query_conditions: dict[str, Any],
        measurement_quantity_names: list[str],
        ods_url: str,
        ods_username: str,
        ods_password: str,
        available_quantities: list[str] | None = None,
        plot_type: str = "scatter",
        title: str = "Measurement Comparison",
    ) -> dict[str, Any]:
        """
        Generate a complete Jupyter notebook for comparing measurements.

        Args:
            measurement_query_conditions: Filter conditions for measurements
            measurement_quantity_names: Names of quantities to plot
            ods_url: ODS server URL
            ods_username: ODS username
            ods_password: ODS password
            available_quantities: List of all available quantities (for documentation)
            plot_type: Type of plot ("scatter", "line", or "subplots")
            title: Notebook title

        Returns:
            Notebook dictionary (can be saved as .ipynb)
        """

        cells = []

        # Title cell
        cells.append(NotebookGenerator.create_markdown_cell(f"### {title}"))

        # Available quantities documentation
        if available_quantities:
            quantities_str = ", ".join(available_quantities)
            cells.append(
                NotebookGenerator.create_markdown_cell(
                    f"#### Define measurement query and which measurement quantities to plot\n\n"
                    f"##### Available Measurement Quantities\n"
                    f"{quantities_str}"
                )
            )
        else:
            cells.append(
                NotebookGenerator.create_markdown_cell(
                    "#### Define measurement query and which measurement quantities to plot"
                )
            )

        # Query definition cell
        query_conditions_str = NotebookGenerator._format_dict_for_code(measurement_query_conditions)
        quantities_str = ", ".join(f'"{q}"' for q in measurement_quantity_names)

        cells.append(
            NotebookGenerator.create_code_cell(
                f"mea_result_conditions = {query_conditions_str}\n\n" f"mq_names = [{quantities_str}]"
            )
        )

        # Data retrieval section
        cells.append(NotebookGenerator.create_markdown_cell("#### Retrieve content from ASAM ODS service"))

        env = NotebookGenerator._get_jinja_env()
        retrieval_template = env.get_template("notebook_retrieval.j2")
        retrieval_code = retrieval_template.render(
            ods_url=ods_url,
            ods_username=ods_username,
            ods_password=ods_password,
        )
        cells.append(NotebookGenerator.create_code_cell(retrieval_code))

        # Data preparation section
        cells.append(NotebookGenerator.create_markdown_cell("#### Prepare collected data for plotting"))

        preparation_template = env.get_template("notebook_preparation.j2")
        preparation_code = preparation_template.render()
        cells.append(NotebookGenerator.create_code_cell(preparation_code))

        # Visualization section
        cells.append(NotebookGenerator.create_markdown_cell("#### Plot measurements"))

        if plot_type == "scatter" and len(measurement_quantity_names) >= 2:
            plot_template = env.get_template("notebook_plot_scatter.j2")
            plot_code = plot_template.render(measurement_quantity_names=measurement_quantity_names)
        elif plot_type == "line":
            plot_template = env.get_template("notebook_plot_line.j2")
            plot_code = plot_template.render(measurement_quantity_names=measurement_quantity_names)
        else:
            plot_code = "# Plotting code would be generated here"

        cells.append(NotebookGenerator.create_code_cell(plot_code))
        notebook = {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {
                    "name": "python",
                    "version": "3.11.0",
                },
            },
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        return notebook

    @staticmethod
    def save_notebook(
        notebook: dict[str, Any],
        output_path: str,
    ) -> None:
        """
        Save notebook to file.

        Args:
            notebook: Notebook dictionary
            output_path: Path to save .ipynb file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=2)

    @staticmethod
    def _format_dict_for_code(d: dict[str, Any]) -> str:
        """
        Format a dictionary for Python code representation.

        Args:
            d: Dictionary to format

        Returns:
            String representation suitable for Python code
        """
        return json.dumps(d, indent=4)
