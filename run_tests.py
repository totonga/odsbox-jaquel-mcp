#!/usr/bin/env python3
"""Test runner for ODS MCP Server."""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run the test suite."""
    try:
        # Check if pytest is available (just import to check)
        import pytest  # noqa: F401
    except ImportError:
        print("pytest not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])

    # Run tests
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"], cwd=Path(__file__).parent)

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
