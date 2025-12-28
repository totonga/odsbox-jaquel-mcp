"""Tests for notebook generator."""

import ast
import json
import tempfile
import unittest
from pathlib import Path

from jinja2 import Environment

from odsbox_jaquel_mcp.notebook_generator import NotebookGenerator


class TestNotebookGenerator(unittest.TestCase):
    """Test NotebookGenerator class."""

    def test_create_markdown_cell(self):
        """Test markdown cell creation."""
        content = "# Title\n\nSome markdown content"
        cell = NotebookGenerator.create_markdown_cell(content)

        self.assertEqual(cell["cell_type"], "markdown")
        self.assertEqual(cell["metadata"], {})
        self.assertIsInstance(cell["source"], list)
        self.assertEqual(cell["source"][0], "# Title")

    def test_create_code_cell(self):
        """Test code cell creation."""
        code = "x = 1\ny = 2\nprint(x + y)"
        cell = NotebookGenerator.create_code_cell(code)

        self.assertEqual(cell["cell_type"], "code")
        self.assertIsNone(cell["execution_count"])
        self.assertEqual(cell["metadata"], {})
        self.assertEqual(cell["outputs"], [])
        self.assertIsInstance(cell["source"], list)
        self.assertIn("x = 1", cell["source"])

    def test_create_code_cell_with_description(self):
        """Test code cell creation with description."""
        code = "import pandas"
        description = "Import libraries"
        cell = NotebookGenerator.create_code_cell(code, description)

        self.assertEqual(cell["cell_type"], "code")
        # Description is accepted but not stored in our implementation

    def test_plot_comparison_notebook_structure(self):
        """Test notebook structure generation."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={
                "Name": {"$like": "Profile_*"},
            },
            measurement_quantity_names=["Speed", "Torque"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            available_quantities=["Speed", "Torque", "Temperature"],
            plot_type="scatter",
            title="Test Notebook",
        )

        self.assertIn("cells", notebook)
        self.assertIn("metadata", notebook)
        self.assertIn("nbformat", notebook)
        self.assertEqual(notebook["nbformat"], 4)
        self.assertEqual(notebook["nbformat_minor"], 4)

    def test_notebook_has_required_cells(self):
        """Test that notebook contains all required cell sections."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={"Name": {"$like": "Profile_*"}},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
        )

        cells = notebook["cells"]
        cell_types = [c["cell_type"] for c in cells]

        # Should have markdown and code cells
        self.assertIn("markdown", cell_types)
        self.assertIn("code", cell_types)

        # Find text content
        all_text = "\n".join("\n".join(c["source"]) for c in cells if isinstance(c["source"], list))

        # Should mention key sections
        self.assertIn("Define measurement", all_text)
        self.assertIn("Retrieve", all_text)
        self.assertIn("Prepare", all_text)
        self.assertIn("Plot", all_text)

    def test_notebook_includes_ods_credentials(self):
        """Test that notebook includes ODS connection info."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="https://my-ods.example.com/api",
            ods_username="testuser",
            ods_password="testpass",
        )

        all_text = "\n".join("\n".join(c["source"]) for c in notebook["cells"] if isinstance(c["source"], list))

        self.assertIn("https://my-ods.example.com/api", all_text)
        self.assertIn("testuser", all_text)

    def test_notebook_includes_measurement_quantities(self):
        """Test that notebook includes measurement quantities."""
        quantities = ["Motor_speed", "Torque", "Ambient"]
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=quantities,
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
        )

        all_text = "\n".join("\n".join(c["source"]) for c in notebook["cells"] if isinstance(c["source"], list))

        for qty in quantities:
            self.assertIn(qty, all_text)

    def test_notebook_scatter_plot_type(self):
        """Test notebook generation with scatter plot type."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed", "Torque"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            plot_type="scatter",
        )

        all_text = "\n".join("\n".join(c["source"]) for c in notebook["cells"] if isinstance(c["source"], list))

        self.assertIn("scatter", all_text)
        self.assertIn("colormap", all_text)

    def test_notebook_line_plot_type(self):
        """Test notebook generation with line plot type."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed", "Torque"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            plot_type="line",
        )

        all_text = "\n".join("\n".join(c["source"]) for c in notebook["cells"] if isinstance(c["source"], list))

        self.assertIn("plot", all_text)
        self.assertIn("legend", all_text)

    def test_notebook_title_in_cells(self):
        """Test that notebook title appears in first cell."""
        title = "My Custom Measurement Analysis"
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            title=title,
        )

        first_cell_text = "\n".join(notebook["cells"][0]["source"])
        self.assertIn(title, first_cell_text)

    def test_save_notebook_creates_file(self):
        """Test that save_notebook creates a valid .ipynb file."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={"Name": {"$eq": "Test"}},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_notebook.ipynb"

            NotebookGenerator.save_notebook(notebook, str(output_path))

            self.assertTrue(output_path.exists())

            # Verify it's valid JSON
            with open(output_path) as f:
                loaded = json.load(f)

            self.assertEqual(loaded["nbformat"], 4)
            self.assertIn("cells", loaded)

    def test_save_notebook_preserves_content(self):
        """Test that saved notebook preserves original content."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed", "Torque"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            title="Test Title",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.ipynb"
            NotebookGenerator.save_notebook(notebook, str(output_path))

            with open(output_path) as f:
                loaded = json.load(f)

            self.assertEqual(len(loaded["cells"]), len(notebook["cells"]))

    def test_format_dict_for_code(self):
        """Test dictionary formatting for code."""
        test_dict = {"Name": {"$like": "Profile_*"}, "Id": {"$gt": 100}}
        result = NotebookGenerator._format_dict_for_code(test_dict)

        # Result should be valid JSON
        parsed = json.loads(result)
        self.assertEqual(parsed, test_dict)

    def test_notebook_available_quantities_documentation(self):
        """Test that available quantities are included in documentation."""
        available = ["Speed", "Torque", "Ambient", "Coolant"]
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed", "Torque"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            available_quantities=available,
        )

        all_text = "\n".join("\n".join(c["source"]) for c in notebook["cells"] if isinstance(c["source"], list))

        for qty in available:
            self.assertIn(qty, all_text)

    def test_notebook_metadata_complete(self):
        """Test that notebook metadata is complete."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
        )

        metadata = notebook["metadata"]
        self.assertIn("kernelspec", metadata)
        self.assertIn("language_info", metadata)

        kernelspec = metadata["kernelspec"]
        self.assertEqual(kernelspec["language"], "python")
        self.assertEqual(kernelspec["display_name"], "Python 3")


class TestNotebookGeneratorTemplateRendering(unittest.TestCase):
    """Test Jinja2 template rendering in notebook generator."""

    def test_jinja_environment_setup(self):
        """Test that Jinja2 environment is properly configured."""
        env = NotebookGenerator._get_jinja_env()
        self.assertIsInstance(env, Environment)

    def test_jinja_templates_exist(self):
        """Test that all required templates exist."""
        env = NotebookGenerator._get_jinja_env()

        required_templates = [
            "notebook_retrieval.j2",
            "notebook_preparation.j2",
            "notebook_plot_scatter.j2",
            "notebook_plot_line.j2",
        ]

        for template_name in required_templates:
            with self.subTest(template=template_name):
                # Should not raise exception
                template = env.get_template(template_name)
                self.assertIsNotNone(template)

    def test_retrieval_template_renders_valid_python(self):
        """Test that retrieval template generates syntactically valid Python."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="testuser",
            ods_password="testpass",
        )

        # Find the retrieval code cell (second code cell after query definition)
        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        self.assertGreaterEqual(len(code_cells), 2)

        retrieval_code = "\n".join(code_cells[1]["source"])

        # Should be valid Python
        try:
            ast.parse(retrieval_code)
        except SyntaxError as e:
            self.fail(f"Retrieval template generated invalid Python: {e}")

    def test_preparation_template_renders_valid_python(self):
        """Test that preparation template generates syntactically valid Python."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="testuser",
            ods_password="testpass",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        self.assertGreaterEqual(len(code_cells), 3)

        preparation_code = "\n".join(code_cells[2]["source"])

        # Should be valid Python
        try:
            ast.parse(preparation_code)
        except SyntaxError as e:
            self.fail(f"Preparation template generated invalid Python: {e}")

    def test_plot_template_renders_valid_python_scatter(self):
        """Test that scatter plot template generates syntactically valid Python."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed", "Torque"],
            ods_url="http://localhost:8087/api",
            ods_username="testuser",
            ods_password="testpass",
            plot_type="scatter",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        self.assertGreaterEqual(len(code_cells), 4)

        plot_code = "\n".join(code_cells[3]["source"])

        # Should be valid Python
        try:
            ast.parse(plot_code)
        except SyntaxError as e:
            self.fail(f"Scatter plot template generated invalid Python: {e}")

    def test_plot_template_renders_valid_python_line(self):
        """Test that line plot template generates syntactically valid Python."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed", "Torque"],
            ods_url="http://localhost:8087/api",
            ods_username="testuser",
            ods_password="testpass",
            plot_type="line",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        self.assertGreaterEqual(len(code_cells), 4)

        plot_code = "\n".join(code_cells[3]["source"])

        # Should be valid Python
        try:
            ast.parse(plot_code)
        except SyntaxError as e:
            self.fail(f"Line plot template generated invalid Python: {e}")

    def test_retrieval_template_includes_ods_url(self):
        """Test that retrieval template properly renders ODS URL."""
        ods_url = "https://custom-ods.example.com:8443/api"
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url=ods_url,
            ods_username="user",
            ods_password="pass",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        retrieval_code = "\n".join(code_cells[1]["source"])

        self.assertIn(ods_url, retrieval_code)

    def test_retrieval_template_includes_credentials(self):
        """Test that retrieval template properly renders ODS credentials."""
        username = "testuser123"
        password = "testpass456"

        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username=username,
            ods_password=password,
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        retrieval_code = "\n".join(code_cells[1]["source"])

        self.assertIn(username, retrieval_code)
        self.assertIn(password, retrieval_code)

    def test_scatter_plot_template_uses_first_two_quantities(self):
        """Test that scatter plot template correctly uses first two quantities."""
        quantities = ["Speed", "Torque", "Temperature"]
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=quantities,
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            plot_type="scatter",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        plot_code = "\n".join(code_cells[3]["source"])

        # Should include first two quantities
        self.assertIn("Speed", plot_code)
        self.assertIn("Torque", plot_code)

    def test_line_plot_template_lists_all_quantities(self):
        """Test that line plot template includes all quantities in list."""
        quantities = ["Speed", "Torque", "Temperature"]
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=quantities,
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            plot_type="line",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        plot_code = "\n".join(code_cells[3]["source"])

        # All quantities should be in the list
        for qty in quantities:
            self.assertIn(qty, plot_code)

    def test_single_quantity_scatter_plot_fallback(self):
        """Test that scatter plot with single quantity falls back to default."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            plot_type="scatter",  # Requires at least 2 quantities
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        plot_code = "\n".join(code_cells[3]["source"])

        # Should be the fallback message
        self.assertIn("Plotting code would be generated here", plot_code)


class TestNotebookGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases in notebook generation."""

    def test_special_characters_in_ods_url(self):
        """Test handling of special characters in ODS URL."""
        ods_url = "https://user@host.com:8443/api?key=value&foo=bar"
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url=ods_url,
            ods_username="user",
            ods_password="pass",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        retrieval_code = "\n".join(code_cells[1]["source"])

        # Should handle special characters correctly
        self.assertIn(ods_url, retrieval_code)
        # Should still be valid Python
        try:
            ast.parse(retrieval_code)
        except SyntaxError as e:
            self.fail(f"URL with special characters caused syntax error: {e}")

    def test_special_characters_in_credentials(self):
        """Test handling of special characters in credentials."""
        password = "p@ssw0rd!#$%&*()"
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password=password,
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        retrieval_code = "\n".join(code_cells[1]["source"])

        # Should handle special characters correctly
        self.assertIn(password, retrieval_code)
        # Should still be valid Python
        try:
            ast.parse(retrieval_code)
        except SyntaxError as e:
            self.fail(f"Special characters in password caused syntax error: {e}")

    def test_many_measurement_quantities(self):
        """Test handling of many measurement quantities."""
        quantities = [f"Quantity_{i}" for i in range(50)]
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=quantities,
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            plot_type="line",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        plot_code = "\n".join(code_cells[3]["source"])

        # All quantities should be present
        for qty in quantities:
            self.assertIn(qty, plot_code)

        # Should still be valid Python
        try:
            ast.parse(plot_code)
        except SyntaxError as e:
            self.fail(f"Many quantities caused syntax error: {e}")

    def test_quantity_names_with_special_characters(self):
        """Test handling of measurement quantities with special characters."""
        quantities = ["Motor_Speed", "Torque-Value", "Ambient Temp"]
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=quantities,
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            plot_type="line",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        plot_code = "\n".join(code_cells[3]["source"])

        # All quantities should be properly quoted
        for qty in quantities:
            self.assertIn(f'"{qty}"', plot_code)

        # Should still be valid Python
        try:
            ast.parse(plot_code)
        except SyntaxError as e:
            self.fail(f"Special characters in quantities caused syntax error: {e}")

    def test_empty_available_quantities(self):
        """Test handling of empty available quantities list."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            available_quantities=[],
        )

        # Should not raise error and should generate valid notebook
        self.assertIn("cells", notebook)
        self.assertGreater(len(notebook["cells"]), 0)

    def test_unknown_plot_type(self):
        """Test handling of unknown plot type."""
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions={},
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
            plot_type="unknown_type",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        plot_code = "\n".join(code_cells[3]["source"])

        # Should fall back to default
        self.assertIn("Plotting code would be generated here", plot_code)

    def test_complex_query_conditions(self):
        """Test handling of complex measurement query conditions."""
        complex_conditions = {
            "Name": {"$like": "Profile_*"},
            "Id": {"$gt": 100, "$lt": 200},
            "$or": [
                {"Status": {"$eq": "OK"}},
                {"Status": {"$eq": "PENDING"}},
            ],
        }
        notebook = NotebookGenerator.plot_comparison_notebook(
            measurement_query_conditions=complex_conditions,
            measurement_quantity_names=["Speed"],
            ods_url="http://localhost:8087/api",
            ods_username="user",
            ods_password="pass",
        )

        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        query_code = "\n".join(code_cells[0]["source"])

        # Should include the complex conditions
        self.assertIn("Profile_*", query_code)
        self.assertIn("100", query_code)
        # Should be valid Python
        try:
            ast.parse(query_code)
        except SyntaxError as e:
            self.fail(f"Complex conditions caused syntax error: {e}")
