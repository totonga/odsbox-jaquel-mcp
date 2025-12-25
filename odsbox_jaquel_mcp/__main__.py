"""Entry point for running the MCP server as a module."""

import asyncio
import sys

# Handle both relative imports (when run as module) and absolute imports (when run as script)
try:
    from .server import main as async_main
except ImportError:
    # Fallback for when run as script directly
    from odsbox_jaquel_mcp.server import main as async_main


def main():
    """Synchronous entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
