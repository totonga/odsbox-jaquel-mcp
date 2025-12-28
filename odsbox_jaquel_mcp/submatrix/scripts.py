"""Script generators for submatrix data fetching."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from jinja2 import Environment, FileSystemLoader


def _get_jinja_env() -> Environment:
    """Get configured Jinja2 environment for templates."""
    template_dir = Path(__file__).parent.parent / "templates"
    return Environment(loader=FileSystemLoader(str(template_dir)), trim_blocks=True, lstrip_blocks=True)


def generate_basic_fetcher_script(submatrix_id: int, measurement_quantities: list[str], output_format: str) -> str:
    """Generate a basic Python script for fetching submatrix data."""
    env = _get_jinja_env()
    template = env.get_template("basic_fetcher.j2")

    return cast(
        str,
        template.render(
            submatrix_id=submatrix_id,
            measurement_quantities=measurement_quantities,
            output_format=output_format,
        ),
    )


def generate_advanced_fetcher_script(
    submatrix_id: int,
    measurement_quantities: list[str],
    output_format: str,
    include_visualization: bool,
    include_analysis: bool,
) -> str:
    """Generate an advanced Python script with error handling and logging."""
    env = _get_jinja_env()
    template = env.get_template("advanced_fetcher.j2")

    return cast(
        str,
        template.render(
            submatrix_id=submatrix_id,
            measurement_quantities=measurement_quantities,
            output_format=output_format,
            include_visualization=include_visualization,
            include_analysis=include_analysis,
        ),
    )


def generate_batch_fetcher_script(submatrix_id: int, measurement_quantities: list[str], output_format: str) -> str:
    """Generate a batch processing script for multiple submatrices."""
    env = _get_jinja_env()
    template = env.get_template("batch_fetcher.j2")

    return cast(
        str,
        template.render(
            submatrix_id=submatrix_id,
            measurement_quantities=measurement_quantities,
            output_format=output_format,
        ),
    )


def generate_analysis_fetcher_script(
    submatrix_id: int, measurement_quantities: list[str], output_format: str, include_visualization: bool
) -> str:
    """Generate a script focused on data analysis and visualization."""
    env = _get_jinja_env()
    template = env.get_template("analysis_fetcher.j2")

    return cast(
        str,
        template.render(
            submatrix_id=submatrix_id,
            measurement_quantities=measurement_quantities,
            output_format=output_format,
        ),
    )
