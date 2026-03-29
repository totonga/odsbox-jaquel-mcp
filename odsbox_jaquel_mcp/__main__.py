"""Entry point for running the MCP server as a module."""

from .server import mcp


def main():
    """Synchronous entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
