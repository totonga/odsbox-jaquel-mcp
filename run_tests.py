#!/usr/bin/env python3
"""Test runner for ODS MCP Server.

Usage:
    python run_tests.py              # Run all unit tests (excluding integration)
    python run_tests.py -integration # Run integration tests only
    python run_tests.py -all         # Run all tests (unit + integration)
"""

import subprocess
import sys
from pathlib import Path


def run_tests(integration=False, all_tests=False):
    """Run the test suite.
    
    Args:
        integration: Run only integration tests
        all_tests: Run all tests including integration
    """
    try:
        # Check if pytest is available (just import to check)
        import pytest  # noqa: F401
    except ImportError:
        print("pytest not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]

    if all_tests:
        # Run all tests (no filtering)
        print("Running all tests (unit + integration)...")
    elif integration:
        # Run only integration tests
        cmd.extend(["-m", "integration"])
        print("Running integration tests...")
    else:
        # Run only unit tests (exclude integration)
        cmd.extend(["-m", "not integration"])
        print("Running unit tests (excluding integration)...")

    result = subprocess.run(cmd, cwd=Path(__file__).parent)

    return result.returncode


if __name__ == "__main__":
    integration = "-integration" in sys.argv
    all_tests = "-all" in sys.argv

    sys.exit(run_tests(integration=integration, all_tests=all_tests))

