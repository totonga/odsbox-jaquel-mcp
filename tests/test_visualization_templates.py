"""Tests for visualization template generators."""

import unittest

from odsbox_jaquel_mcp.visualization_templates import VisualizationTemplateGenerator


class TestVisualizationTemplateGenerator(unittest.TestCase):
    """Test VisualizationTemplateGenerator class."""

    def test_generate_scatter_plot_code_valid(self):
        """Test scatter plot code generation with valid parameters."""
        code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["Speed", "Torque"],
            submatrices_count=6,
            subplots_per_row=3,
        )

        self.assertIsInstance(code, str)
        self.assertIn("plt.subplots", code)
        self.assertIn("scatter", code)
        self.assertIn("Speed", code)
        self.assertIn("Torque", code)
        self.assertIn("viridis", code)

    def test_generate_scatter_plot_code_insufficient_quantities(self):
        """Test with fewer than 2 quantities."""
        with self.assertRaises(ValueError):
            VisualizationTemplateGenerator.generate_scatter_plot_code(
                measurement_quantity_names=["Speed"],
                submatrices_count=6,
            )

    def test_generate_scatter_plot_code_includes_submatrix_count(self):
        """Test that generated code handles correct subplot count."""
        code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["Motor_speed", "Torque"],
            submatrices_count=9,
        )

        self.assertIn("9", code)  # num_of_plots = 9

    def test_generate_scatter_plot_code_custom_figsize(self):
        """Test with custom figure size."""
        code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["Speed", "Torque"],
            submatrices_count=6,
            figsize_width=20.0,
            figsize_height_per_row=7.0,
        )

        self.assertIn("20.0", code)
        self.assertIn("7.0", code)

    def test_generate_line_plot_code_valid(self):
        """Test line plot code generation."""
        code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=["Speed", "Torque", "Temperature"],
            submatrices_count=6,
        )

        self.assertIsInstance(code, str)
        self.assertIn("plt.subplots", code)
        self.assertIn("plot", code)
        self.assertIn("Speed", code)
        self.assertIn("Torque", code)
        self.assertIn("Temperature", code)
        self.assertIn("legend", code)
        self.assertIn("grid", code)

    def test_generate_line_plot_code_single_quantity(self):
        """Test line plot with single quantity."""
        code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=["Speed"],
            submatrices_count=3,
        )

        self.assertIn("Speed", code)
        self.assertIn("for qty in quantity_names", code)

    def test_generate_line_plot_code_custom_subplots(self):
        """Test with custom subplot layout."""
        code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=["Speed", "Torque"],
            submatrices_count=8,
            subplots_per_row=4,
        )

        self.assertIn("4", code)  # subplots_per_row

    def test_generate_subplots_per_measurement_code_valid(self):
        """Test subplot-per-measurement code generation."""
        code = (
            VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
                measurement_quantity_names=["Speed", "Torque"],
                submatrices_count=4,
            )
        )

        self.assertIsInstance(code, str)
        self.assertIn("num_quantities", code)
        self.assertIn("Speed", code)
        self.assertIn("Torque", code)
        self.assertIn("for q_idx, qty in enumerate", code)

    def test_generate_subplots_per_measurement_code_multiple_quantities(self):
        """Test with multiple quantities."""
        code = (
            VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
                measurement_quantity_names=[
                    "Speed",
                    "Torque",
                    "Temperature",
                    "Current",
                ],
                submatrices_count=6,
            )
        )

        self.assertIn("Speed", code)
        self.assertIn("Torque", code)
        self.assertIn("Temperature", code)
        self.assertIn("Current", code)

    def test_scatter_plot_code_executable_structure(self):
        """Verify scatter plot code has proper Python structure."""
        code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["A", "B"],
            submatrices_count=3,
        )

        # Check for required imports
        self.assertIn("import matplotlib.pyplot", code)

        # Check for key structure elements
        self.assertIn("fig, axes", code)
        self.assertIn("for i, measurement_data", code)
        self.assertIn("plt.show()", code)

    def test_line_plot_code_executable_structure(self):
        """Verify line plot code has proper Python structure."""
        code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=["A", "B"],
            submatrices_count=3,
        )

        # Check for required imports
        self.assertIn("import matplotlib.pyplot", code)

        # Check for key structure elements
        self.assertIn("fig, axes", code)
        self.assertIn("for qty in quantity_names", code)
        self.assertIn("plt.show()", code)

    def test_subplots_code_handles_edge_cases(self):
        """Verify subplot code handles single plots."""
        code = (
            VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
                measurement_quantity_names=["A"],
                submatrices_count=1,
            )
        )

        # Should handle 1x1 case
        self.assertIn("if num_quantities == 1 and num_of_plots == 1", code)


if __name__ == "__main__":
    unittest.main()
