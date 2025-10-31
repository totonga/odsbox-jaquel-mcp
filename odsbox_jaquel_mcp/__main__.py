"""Entry point for running the MCP server as a module."""

from .server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
