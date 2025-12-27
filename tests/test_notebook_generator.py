"""Tests for notebook generator."""

import json
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
