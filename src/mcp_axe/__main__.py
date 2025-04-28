#!/usr/bin/env python3
import asyncio
from .server import server

def main():
    """Entry point for both `python -m mcp_axe` and the console‐script."""
    # this will run the MCP server over stdio
asyncio.run(server.run_stdio_async())
if __name__ == "__main__":
    main()