"""Tests for visualization template generators."""

import ast
import unittest

from jinja2 import Environment

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
        code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=["Speed", "Torque"],
            submatrices_count=4,
        )

        self.assertIsInstance(code, str)
        self.assertIn("num_quantities", code)
        self.assertIn("Speed", code)
        self.assertIn("Torque", code)
        self.assertIn("for q_idx, qty in enumerate", code)

    def test_generate_subplots_per_measurement_code_multiple_quantities(self):
        """Test with multiple quantities."""
        code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=[
                "Speed",
                "Torque",
                "Temperature",
                "Current",
            ],
            submatrices_count=6,
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
        code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=["A"],
            submatrices_count=1,
        )

        # Should handle 1x1 case
        self.assertIn("if num_quantities == 1 and num_of_plots == 1", code)


class TestVisualizationTemplateRendering(unittest.TestCase):
    """Test Jinja2 template rendering in visualization generator."""

    def test_jinja_environment_setup(self):
        """Test that Jinja2 environment is properly configured."""
        env = VisualizationTemplateGenerator._get_jinja_env()
        self.assertIsInstance(env, Environment)

    def test_visualization_templates_exist(self):
        """Test that all required visualization templates exist."""
        env = VisualizationTemplateGenerator._get_jinja_env()

        required_templates = [
            "visualization_scatter.j2",
            "visualization_line.j2",
            "visualization_subplots.j2",
        ]

        for template_name in required_templates:
            with self.subTest(template=template_name):
                template = env.get_template(template_name)
                self.assertIsNotNone(template)

    def test_scatter_plot_template_renders_valid_python(self):
        """Test that scatter plot template generates syntactically valid Python."""
        code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["Speed", "Torque"],
            submatrices_count=6,
        )

        # Should be valid Python
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Scatter plot template generated invalid Python: {e}")

    def test_line_plot_template_renders_valid_python(self):
        """Test that line plot template generates syntactically valid Python."""
        code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=["Speed", "Torque", "Temperature"],
            submatrices_count=6,
        )

        # Should be valid Python
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Line plot template generated invalid Python: {e}")

    def test_subplots_template_renders_valid_python(self):
        """Test that subplots template generates syntactically valid Python."""
        code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=["Speed", "Torque"],
            submatrices_count=4,
        )

        # Should be valid Python
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Subplots template generated invalid Python: {e}")

    def test_scatter_plot_includes_parameters(self):
        """Test that scatter plot code includes correct parameters."""
        figsize_width = 20.0
        figsize_height = 7.0
        submatrices = 9

        code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["Speed", "Torque"],
            submatrices_count=submatrices,
            subplots_per_row=4,
            figsize_width=figsize_width,
            figsize_height_per_row=figsize_height,
        )

        self.assertIn("Speed", code)
        self.assertIn("Torque", code)
        self.assertIn(str(submatrices), code)
        self.assertIn(str(figsize_width), code)
        self.assertIn(str(figsize_height), code)

    def test_line_plot_includes_all_quantities(self):
        """Test that line plot includes all quantities in the list."""
        quantities = ["Speed", "Torque", "Temperature", "Current"]
        code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=quantities,
            submatrices_count=3,
        )

        for qty in quantities:
            self.assertIn(qty, code)

    def test_subplots_includes_all_quantities(self):
        """Test that subplots code includes all quantities."""
        quantities = ["Speed", "Torque", "Ambient"]
        code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=quantities,
            submatrices_count=5,
        )

        for qty in quantities:
            self.assertIn(qty, code)

    def test_scatter_plot_uses_first_two_quantities(self):
        """Test that scatter plot correctly uses first two quantities only."""
        code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["Speed", "Torque", "Temperature"],
            submatrices_count=6,
        )

        # Should use first two
        self.assertIn("Speed", code)
        self.assertIn("Torque", code)
        # Third one should not be in plot definition (but might be in comments)
        # Check for x/y axis setting
        self.assertIn('x="Speed"', code)
        self.assertIn('y="Torque"', code)

    def test_line_plot_with_special_characters(self):
        """Test line plot with quantities containing special characters."""
        quantities = ["Motor_Speed", "Torque-Value", "Ambient Temp"]
        code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=quantities,
            submatrices_count=2,
        )

        for qty in quantities:
            self.assertIn(f'"{qty}"', code)

        # Should still be valid Python
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Special characters in quantities caused syntax error: {e}")

    def test_scatter_plot_respects_figure_dimensions(self):
        """Test that scatter plot respects figure dimension parameters."""
        code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["A", "B"],
            submatrices_count=12,
            subplots_per_row=4,
            figsize_width=25.0,
            figsize_height_per_row=8.0,
        )

        self.assertIn("25.0", code)
        self.assertIn("8.0", code)
        self.assertIn("4", code)  # subplots_per_row

    def test_subplots_handles_single_quantity(self):
        """Test that subplots code handles single quantity case."""
        code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=["Speed"],
            submatrices_count=3,
        )

        self.assertIn("Speed", code)
        self.assertIn("num_quantities", code)
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Single quantity subplots caused syntax error: {e}")

    def test_subplots_handles_many_quantities(self):
        """Test that subplots code handles many quantities."""
        quantities = [f"Qty_{i}" for i in range(10)]
        code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=quantities,
            submatrices_count=5,
        )

        for qty in quantities:
            self.assertIn(qty, code)

        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Many quantities subplots caused syntax error: {e}")


class TestVisualizationTemplateEdgeCases(unittest.TestCase):
    """Test edge cases in visualization template generation."""

    def test_scatter_plot_minimum_requirements(self):
        """Test scatter plot with minimum requirements."""
        code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["A", "B"],
            submatrices_count=1,
        )

        self.assertIn("A", code)
        self.assertIn("B", code)
        self.assertIn("matplotlib.pyplot", code)

    def test_line_plot_many_submatrices(self):
        """Test line plot with many submatrices."""
        code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=["Speed"],
            submatrices_count=100,
        )

        self.assertIn("100", code)
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Many submatrices caused syntax error: {e}")

    def test_subplots_large_grid(self):
        """Test subplots with large grid dimensions."""
        quantities = [f"Q{i}" for i in range(12)]
        code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=quantities,
            submatrices_count=15,
        )

        # Check that all quantities are included
        for qty in quantities:
            self.assertIn(qty, code)
        self.assertIn("15", code)  # num_of_plots
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Large grid caused syntax error: {e}")

    def test_all_plot_types_have_required_imports(self):
        """Test that all plot types include required matplotlib imports."""
        scatter_code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["A", "B"],
            submatrices_count=2,
        )
        line_code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=["A"],
            submatrices_count=2,
        )
        subplots_code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=["A"],
            submatrices_count=2,
        )

        for code in [scatter_code, line_code]:
            self.assertIn("import matplotlib.pyplot", code)

        self.assertIn("import matplotlib.pyplot", subplots_code)
        self.assertIn("import numpy", subplots_code)

    def test_all_plot_types_have_final_show_call(self):
        """Test that all plot types end with plt.show()."""
        scatter_code = VisualizationTemplateGenerator.generate_scatter_plot_code(
            measurement_quantity_names=["A", "B"],
            submatrices_count=2,
        )
        line_code = VisualizationTemplateGenerator.generate_line_plot_code(
            measurement_quantity_names=["A"],
            submatrices_count=2,
        )
        subplots_code = VisualizationTemplateGenerator.generate_subplots_per_measurement_code(
            measurement_quantity_names=["A"],
            submatrices_count=2,
        )

        for code in [scatter_code, line_code, subplots_code]:
            self.assertIn("plt.show()", code)


if __name__ == "__main__":
    unittest.main()
