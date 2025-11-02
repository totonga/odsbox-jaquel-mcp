"""Entry point for running the MCP server as a module."""

from .server import main as async_main
import asyncio


def main():
    """Synchronous entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
