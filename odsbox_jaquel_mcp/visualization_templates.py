"""Visualization template generators for measurement comparison notebooks.

Generates Python code for creating matplotlib plots with various configurations.
"""

from __future__ import annotations

from typing import List


class VisualizationTemplateGenerator:
    """Generate plotting code templates."""

    @staticmethod
    def generate_scatter_plot_code(
        measurement_quantity_names: List[str],
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

        x_qty = measurement_quantity_names[0]
        y_qty = measurement_quantity_names[1]

        code = f"""import matplotlib.pyplot as plt

# Number of submatrices
num_of_plots = {submatrices_count}

# Calculate number of rows
cols = {subplots_per_row}
rows = (num_of_plots + cols - 1) // cols  # Ceiling division

fig, axes = plt.subplots(
    rows, cols,
    figsize=({figsize_width}, {figsize_height_per_row} * rows)
)
axes = axes.flatten()  # Flatten to 1D array for easy indexing

for i, measurement_data in enumerate(measurement_data_items):
    ax = axes[i]
    measurement_data["data"].plot.scatter(
        x="{x_qty}",
        y="{y_qty}",
        c=measurement_data["data"].index,
        colormap="viridis",
        ax=ax,
        alpha=0.7,
        s=20
    )
    ax.set_xlabel(measurement_data["labels"].get("{x_qty}", "{x_qty}"))
    ax.set_ylabel(measurement_data["labels"].get("{y_qty}", "{y_qty}"))
    ax.set_title(measurement_data["title"])

# Hide any unused subplots
for j in range(i + 1, len(axes)):
    axes[j].axis('off')

plt.tight_layout()
plt.show()
"""
        return code

    @staticmethod
    def generate_line_plot_code(
        measurement_quantity_names: List[str],
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
        quantities_str = ", ".join(f'"{q}"' for q in measurement_quantity_names)

        code = f"""import matplotlib.pyplot as plt

# Number of submatrices
num_of_plots = {submatrices_count}

# Calculate number of rows
cols = {subplots_per_row}
rows = (num_of_plots + cols - 1) // cols  # Ceiling division

fig, axes = plt.subplots(
    rows, cols,
    figsize=({figsize_width}, {figsize_height_per_row} * rows)
)
axes = axes.flatten()  # Flatten to 1D array for easy indexing

quantity_names = [{quantities_str}]

for i, measurement_data in enumerate(measurement_data_items):
    ax = axes[i]
    
    # Plot each quantity as a line
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
plt.show()
"""
        return code

    @staticmethod
    def generate_subplots_per_measurement_code(
        measurement_quantity_names: List[str],
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
        quantities_str = ", ".join(f'"{q}"' for q in measurement_quantity_names)

        code = f"""import matplotlib.pyplot as plt
import numpy as np

# Create a subplot for each measurement quantity
quantity_names = [{quantities_str}]
num_quantities = len(quantity_names)
num_of_plots = {submatrices_count}

fig, axes = plt.subplots(
    num_quantities, num_of_plots,
    figsize=(5 * num_of_plots, 5 * num_quantities)
)

# Handle case when there's only one row or column
if num_quantities == 1 and num_of_plots == 1:
    axes = [[axes]]
elif num_quantities == 1:
    axes = [axes]
elif num_of_plots == 1:
    axes = [[ax] for ax in axes]

for q_idx, qty in enumerate(quantity_names):
    for m_idx, measurement_data in enumerate(measurement_data_items):
        ax = axes[q_idx][m_idx] if isinstance(axes[0], list) else axes[q_idx]
        
        if qty in measurement_data["data"].columns:
            ax.plot(
                measurement_data["data"].index,
                measurement_data["data"][qty],
                marker='o',
                markersize=4
            )
            ax.set_ylabel(measurement_data["labels"].get(qty, qty))
            ax.set_title(f"{{qty}} - {{measurement_data['title'].split(chr(10))[0]}}")
            ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
"""
        return code
