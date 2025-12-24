"""Jupyter notebook generator for measurement comparison workflows.

Generates complete Jupyter notebooks with measurement comparison workflows
including data retrieval, preparation, and visualization.
"""

from __future__ import annotations

import json
from typing import Any


class NotebookGenerator:
    """Generate Jupyter notebooks for measurement comparison."""

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
    def generate_measurement_comparison_notebook(
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

        retrieval_code = f"""from odsbox import ConI

with ConI(url="{ods_url}", auth=("{ods_username}", "{ods_password}")) as con_i:
    # Query measurements to compare
    measurements = con_i.query_data({{
            "MeaResult": mea_result_conditions,
            "$attributes": {{
                "Name": 1,
                "Id": 1,
                "TestStep": {{
                    "Name": 1,
                    "Test": {{
                        "Name": 1,
                        "StructureLevel": {{
                            "Name": 1,
                            "Project": {{
                                "Name": 1
                                }}}}}}}},
            }},
        }})
    measurement_ids = measurements["MeaResult.Id"].tolist()

    # Query submatrices of measurements containing the specified measurement quantities
    submatrices = con_i.query({{
            "AoSubMatrix": {{
                "measurement": {{"$in": measurement_ids}},
                "local_columns": {{
                    "name": {{
                        "$in": mq_names
                    }},
                }}
            }},
            "$attributes": {{
                "id": 1,
                "number_of_rows": 1,
                "measurement": 1,
            }},
            "$groupby": {{
                "id": 1,
                "measurement": 1,
                "number_of_rows": 1,
            }}
        }})
    submatrix_ids = submatrices["id"].tolist()
    
    # Get units and other info of local columns in submatrices
    local_columns = con_i.query(
        {{
            "AoLocalColumn": {{
                "submatrix": {{"$in": submatrix_ids}},
                "$or": [
                    {{"name": {{"$in": mq_names}}}},
                    {{"independent": 1}}
                ]
            }},
            "$attributes": {{
                "id": 1,
                "name": 1,
                "independent": 1,
                "measurement_quantity.unit:OUTER.name": 1,
            }}
        }})
    local_column_ids = local_columns["id"].tolist()
    
    # Fetch bulk data for local columns
    local_columns_signals = con_i.bulk.query({{"id":{{"$in": local_column_ids}}}})"""

        cells.append(NotebookGenerator.create_code_cell(retrieval_code))

        # Data preparation section
        cells.append(NotebookGenerator.create_markdown_cell("#### Prepare collected data for plotting"))

        preparation_code = """import pandas as pd
from odsbox_jaquel_mcp.data_preparation import (
    MeasurementMetadataExtractor,
    MeasurementDataPreparator,
)

# lookup for units of local columns
local_column_unit_lookup = dict({row["id"]: row["measurement_quantity.unit:OUTER.name"]
                                 for _, row in local_columns.iterrows()})

# generate title for each submatrix
submatrix_title_lookup = {}
for submatrix_id in submatrix_ids:
    measurement_id = submatrices[submatrices['id'] == submatrix_id]['measurement'].values[0]
    measurement_info = measurements[measurements['MeaResult.Id'] == measurement_id]
    if not measurement_info.empty:
        project = measurement_info['Project.Name'].values[0]
        profile = measurement_info['MeaResult.Name'].values[0]
        campaign = measurement_info['Test.Name'].values[0]
        submatrix_title_lookup[submatrix_id] = f"{project} - {campaign} - {profile}"
    else:
        submatrix_title_lookup[submatrix_id] = f"Submatrix {submatrix_id}"

# Prepare measurement data items using helper functions
submatrix_signals_by_id = local_columns_signals.groupby("submatrix")
measurement_data_items = MeasurementDataPreparator.prepare_measurement_data_items(
    submatrix_signals_by_id=submatrix_signals_by_id,
    submatrices_df=submatrices,
    measurements_df=measurements,
    local_columns_df=local_columns,
    measurement_quantity_names=mq_names,
    unit_lookup=local_column_unit_lookup,
)

print(f"Prepared {len(measurement_data_items)} measurement data items for plotting")"""

        cells.append(NotebookGenerator.create_code_cell(preparation_code))

        # Visualization section
        cells.append(NotebookGenerator.create_markdown_cell("#### Plot measurements"))

        if plot_type == "scatter" and len(measurement_quantity_names) >= 2:
            qty_0 = measurement_quantity_names[0]
            qty_1 = measurement_quantity_names[1]
            plot_code = f"""import matplotlib.pyplot as plt

# Number of submatrices
num_of_plots = len(measurement_data_items)

# Calculate number of rows (3 submatrices per row)
cols = 3
rows = (num_of_plots + cols - 1) // cols  # Ceiling division

fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
axes = axes.flatten()  # Flatten to 1D array for easy indexing

for i, measurement_data in enumerate(measurement_data_items):
    ax = axes[i]
    measurement_data["data"].plot.scatter(
        x="{qty_0}",
        y="{qty_1}",
        c=measurement_data["data"].index,
        colormap="viridis",
        ax=ax,
        alpha=0.7,
        s=20
    )
    ax.set_xlabel(measurement_data["labels"].get("{qty_0}", "{qty_0}"))
    ax.set_ylabel(measurement_data["labels"].get("{qty_1}", "{qty_1}"))
    ax.set_title(measurement_data["title"])

# Hide any unused subplots
for j in range(i + 1, len(axes)):
    axes[j].axis('off')

plt.tight_layout()
plt.show()"""
        elif plot_type == "line":
            quantities_str = ", ".join(f'"{q}"' for q in measurement_quantity_names)
            plot_code = f"""import matplotlib.pyplot as plt

# Number of submatrices
num_of_plots = len(measurement_data_items)

# Calculate number of rows (3 submatrices per row)
cols = 3
rows = (num_of_plots + cols - 1) // cols

fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
axes = axes.flatten()

quantity_names = [{quantities_str}]

for i, measurement_data in enumerate(measurement_data_items):
    ax = axes[i]
    
    for qty in quantity_names:
        if qty in measurement_data["data"].columns:
            ax.plot(
                measurement_data["data"].index,
                measurement_data["data"][qty],
                label=measurement_data["labels"].get(qty, qty),
                marker='o',
                markersize=4
            )
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.set_title(measurement_data["title"])
    ax.legend()
    ax.grid(True, alpha=0.3)

# Hide any unused subplots
for j in range(i + 1, len(axes)):
    axes[j].axis('off')

plt.tight_layout()
plt.show()"""
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
