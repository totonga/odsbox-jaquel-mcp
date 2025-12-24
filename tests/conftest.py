"""Pytest configuration and fixtures for tests."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (select with '-m unit')"
    )


@pytest.fixture
def integration_credentials():
    """Fixture providing ODS server credentials for integration tests.
    
    Returns:
        dict: Dictionary with url, username, and password
    """
    return {
        "url": "https://docker.peak-solution.de:10032/api",
        "username": "Demo",
        "password": "mdm",
    }
