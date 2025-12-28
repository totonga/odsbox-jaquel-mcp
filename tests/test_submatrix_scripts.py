"""Tests for submatrix script generation using Jinja2 templates."""

import ast
from pathlib import Path

from odsbox_jaquel_mcp.submatrix.scripts import (
    generate_advanced_fetcher_script,
    generate_analysis_fetcher_script,
    generate_basic_fetcher_script,
    generate_batch_fetcher_script,
)


class TestBasicFetcherScript:
    """Test basic fetcher script generation."""

    def test_generate_basic_fetcher_csv(self):
        """Test basic script generation with CSV output."""
        script = generate_basic_fetcher_script(
            submatrix_id=123,
            measurement_quantities=["Temperature", "Pressure"],
            output_format="csv",
        )

        # Verify script is not empty
        assert script
        assert len(script) > 0

        # Verify variables are substituted
        assert "123" in script
        assert "Temperature" in script
        assert "Pressure" in script
        assert 'df.to_csv("submatrix_123_data.csv"' in script

        # Verify it's valid Python syntax
        ast.parse(script)

    def test_generate_basic_fetcher_json(self):
        """Test basic script generation with JSON output."""
        script = generate_basic_fetcher_script(
            submatrix_id=456,
            measurement_quantities=["Speed"],
            output_format="json",
        )

        assert "456" in script
        assert "Speed" in script
        assert 'df.to_json("submatrix_456_data.json"' in script
        ast.parse(script)

    def test_generate_basic_fetcher_parquet(self):
        """Test basic script generation with Parquet output."""
        script = generate_basic_fetcher_script(
            submatrix_id=789,
            measurement_quantities=["Current", "Voltage"],
            output_format="parquet",
        )

        assert "789" in script
        assert "Current" in script
        assert "Voltage" in script
        assert 'df.to_parquet("submatrix_789_data.parquet"' in script
        ast.parse(script)

    def test_generate_basic_fetcher_excel(self):
        """Test basic script generation with Excel output."""
        script = generate_basic_fetcher_script(
            submatrix_id=321,
            measurement_quantities=["Power"],
            output_format="excel",
        )

        assert "321" in script
        assert "Power" in script
        assert 'df.to_excel("submatrix_321_data.xlsx"' in script
        ast.parse(script)

    def test_generate_basic_fetcher_unknown_format(self):
        """Test basic script with unknown format falls back to print."""
        script = generate_basic_fetcher_script(
            submatrix_id=555,
            measurement_quantities=["Flow"],
            output_format="unknown_format",
        )

        assert "555" in script
        assert "Flow" in script
        assert 'print("Data loaded into DataFrame' in script
        ast.parse(script)

    def test_generate_basic_fetcher_multiple_quantities(self):
        """Test with multiple measurement quantities."""
        quantities = ["Temp1", "Temp2", "Temp3", "Humidity", "Pressure"]
        script = generate_basic_fetcher_script(
            submatrix_id=999,
            measurement_quantities=quantities,
            output_format="csv",
        )

        # All quantities should be present
        for qty in quantities:
            assert qty in script

        ast.parse(script)


class TestAdvancedFetcherScript:
    """Test advanced fetcher script generation."""

    def test_generate_advanced_basic_config(self):
        """Test advanced script with no visualization or analysis."""
        script = generate_advanced_fetcher_script(
            submatrix_id=100,
            measurement_quantities=["Signal"],
            output_format="csv",
            include_visualization=False,
            include_analysis=False,
        )

        assert "100" in script
        assert "Signal" in script
        assert "class SubmatrixDataFetcher" in script
        assert "def connect(" in script
        assert "def fetch_submatrix_data(" in script
        ast.parse(script)

    def test_generate_advanced_with_analysis(self):
        """Test advanced script with analysis enabled."""
        script = generate_advanced_fetcher_script(
            submatrix_id=200,
            measurement_quantities=["Data"],
            output_format="json",
            include_visualization=False,
            include_analysis=True,
        )

        assert "200" in script
        assert "Data" in script
        assert "Performing basic data analysis" in script
        assert "missing_data" in script
        ast.parse(script)

    def test_generate_advanced_with_visualization(self):
        """Test advanced script with visualization enabled."""
        script = generate_advanced_fetcher_script(
            submatrix_id=300,
            measurement_quantities=["Value"],
            output_format="parquet",
            include_visualization=True,
            include_analysis=False,
        )

        assert "300" in script
        assert "Value" in script
        assert "Create visualizations" in script
        assert "matplotlib" in script
        assert "seaborn" in script
        ast.parse(script)

    def test_generate_advanced_with_both_options(self):
        """Test advanced script with both analysis and visualization."""
        script = generate_advanced_fetcher_script(
            submatrix_id=400,
            measurement_quantities=["Metric1", "Metric2"],
            output_format="excel",
            include_visualization=True,
            include_analysis=True,
        )

        assert "400" in script
        assert "Metric1" in script
        assert "Metric2" in script
        assert "Performing basic data analysis" in script
        assert "Create visualizations" in script
        ast.parse(script)


class TestBatchFetcherScript:
    """Test batch fetcher script generation."""

    def test_generate_batch_fetcher(self):
        """Test batch script generation."""
        script = generate_batch_fetcher_script(
            submatrix_id=500,
            measurement_quantities=["BatchData"],
            output_format="csv",
        )

        assert "500" in script
        assert "BatchData" in script
        assert "class BatchSubmatrixFetcher" in script
        assert "def connect(" in script
        assert "def fetch_single_submatrix(" in script
        assert "concurrent" in script or "ThreadPool" in script
        ast.parse(script)

    def test_generate_batch_multiple_quantities(self):
        """Test batch script with multiple quantities."""
        quantities = ["Q1", "Q2", "Q3"]
        script = generate_batch_fetcher_script(
            submatrix_id=501,
            measurement_quantities=quantities,
            output_format="json",
        )

        for qty in quantities:
            assert qty in script

        ast.parse(script)


class TestAnalysisFetcherScript:
    """Test analysis-focused fetcher script generation."""

    def test_generate_analysis_fetcher(self):
        """Test analysis script generation."""
        script = generate_analysis_fetcher_script(
            submatrix_id=600,
            measurement_quantities=["AnalysisData"],
            output_format="csv",
            include_visualization=False,
        )

        assert "600" in script
        assert "AnalysisData" in script
        assert "perform_statistical_analysis" in script
        assert "STATISTICAL ANALYSIS" in script
        assert "Shape:" in script
        ast.parse(script)

    def test_generate_analysis_with_visualization(self):
        """Test analysis script with visualization flag (parameter ignored)."""
        # Note: include_visualization param is accepted but not used in analysis script
        script = generate_analysis_fetcher_script(
            submatrix_id=601,
            measurement_quantities=["Data"],
            output_format="parquet",
            include_visualization=True,
        )

        assert "601" in script
        assert "Data" in script
        assert "perform_statistical_analysis" in script
        ast.parse(script)

    def test_generate_analysis_all_output_formats(self):
        """Test analysis script with all output formats."""
        for output_format in ["csv", "json", "parquet", "excel"]:
            script = generate_analysis_fetcher_script(
                submatrix_id=602,
                measurement_quantities=["Value"],
                output_format=output_format,
                include_visualization=False,
            )

            assert "602" in script
            assert "Value" in script
            # Verify format handling
            if output_format == "csv":
                assert "to_csv" in script
            elif output_format == "json":
                assert "to_json" in script
            elif output_format == "parquet":
                assert "to_parquet" in script
            elif output_format == "excel":
                assert "to_excel" in script

            ast.parse(script)


class TestTemplateLoading:
    """Test that templates exist and are loaded correctly."""

    def test_template_files_exist(self):
        """Verify all template files exist."""
        template_dir = Path(__file__).parent.parent / "odsbox_jaquel_mcp" / "templates"

        templates = [
            "basic_fetcher.j2",
            "advanced_fetcher.j2",
            "batch_fetcher.j2",
            "analysis_fetcher.j2",
        ]

        for template in templates:
            template_path = template_dir / template
            assert template_path.exists(), f"Template {template} not found at {template_path}"

    def test_template_files_are_readable(self):
        """Verify all template files can be read."""
        template_dir = Path(__file__).parent.parent / "odsbox_jaquel_mcp" / "templates"

        templates = [
            "basic_fetcher.j2",
            "advanced_fetcher.j2",
            "batch_fetcher.j2",
            "analysis_fetcher.j2",
        ]

        for template in templates:
            template_path = template_dir / template
            content = template_path.read_text(encoding="utf-8")
            assert len(content) > 0, f"Template {template} is empty"
            # Check for Jinja2 variables
            assert "{{" in content or "{%" in content, f"Template {template} has no Jinja2 syntax"


class TestScriptIntegration:
    """Integration tests for script generation."""

    def test_all_scripts_contain_shebang(self):
        """Verify all generated scripts have Python shebang."""
        test_cases = [
            generate_basic_fetcher_script(123, ["Test"], "csv"),
            generate_advanced_fetcher_script(456, ["Test"], "csv", False, False),
            generate_batch_fetcher_script(789, ["Test"], "csv"),
            generate_analysis_fetcher_script(321, ["Test"], "csv", False),
        ]

        for script in test_cases:
            assert script.startswith("#!/usr/bin/env python3"), "Script missing shebang"

    def test_all_scripts_are_parseable(self):
        """Verify all generated scripts have valid Python syntax."""
        test_cases = [
            generate_basic_fetcher_script(111, ["Quantity"], "csv"),
            generate_advanced_fetcher_script(222, ["Quantity"], "json", True, True),
            generate_batch_fetcher_script(333, ["Quantity"], "parquet"),
            generate_analysis_fetcher_script(444, ["Quantity"], "excel", True),
        ]

        for script in test_cases:
            # This will raise SyntaxError if parsing fails
            ast.parse(script)

    def test_scripts_have_main_function(self):
        """Verify all scripts have a main() function."""
        test_cases = [
            generate_basic_fetcher_script(555, ["Test"], "csv"),
            generate_advanced_fetcher_script(666, ["Test"], "json", False, False),
            generate_batch_fetcher_script(777, ["Test"], "parquet"),
            generate_analysis_fetcher_script(888, ["Test"], "excel", False),
        ]

        for script in test_cases:
            assert "def main():" in script, "Script missing main() function"
            assert 'if __name__ == "__main__":' in script, "Script missing main guard"

    def test_scripts_have_docstrings(self):
        """Verify all generated scripts have module docstrings."""
        test_cases = [
            generate_basic_fetcher_script(1111, ["Test"], "csv"),
            generate_advanced_fetcher_script(2222, ["Test"], "json", False, False),
            generate_batch_fetcher_script(3333, ["Test"], "parquet"),
            generate_analysis_fetcher_script(4444, ["Test"], "excel", False),
        ]

        for script in test_cases:
            assert '"""' in script or "'''" in script, "Script missing docstring"
