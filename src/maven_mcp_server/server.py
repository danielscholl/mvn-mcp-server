"""Maven MCP Server using FastMCP framework.

This module creates and configures the FastMCP server instance for the Maven MCP tools.
"""

from mcp.server.fastmcp import FastMCP

from maven_mcp_server.tools.version_exist import check_version
from maven_mcp_server.tools.check_version import latest_version
from maven_mcp_server.tools.latest_by_semver import find_version

# Create FastMCP server instance
mcp = FastMCP("Maven MCP Server")

# Register tools
mcp.tool()(check_version)
mcp.tool()(latest_version)
mcp.tool()(find_version)