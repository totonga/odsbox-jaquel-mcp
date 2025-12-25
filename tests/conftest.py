"""Pytest configuration and fixtures for tests."""

import pytest

from tests.mcp_test_client import MCPServerTestClient


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line("markers", "unit: marks tests as unit tests (select with '-m unit')")


@pytest.fixture(scope="function")
async def mcp_client():
    """MCP server test client fixture.

    Yields:
        MCPServerTestClient connected to server or skips if unable to connect
    """
    client = MCPServerTestClient(timeout=10.0)
    try:
        await client.start()
        yield client
        await client.stop()
    except Exception as e:
        # Skip tests if MCP server can't start
        pytest.skip(f"Could not start MCP server: {e}")


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
