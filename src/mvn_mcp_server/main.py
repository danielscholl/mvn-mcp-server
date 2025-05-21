"""mvn MCP Server main entry point.

This module serves as the primary entry point for the mvn MCP Server.
"""

import sys
from mvn_mcp_server.server import mcp


def main():
    """Start the mvn MCP Server."""
    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        print("mvn MCP Server version 0.1.0")
        return 0

    # Run the FastMCP server
    mcp.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
