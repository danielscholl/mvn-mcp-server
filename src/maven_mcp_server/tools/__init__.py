"""Maven MCP Server tools package.

This package contains tools for interacting with Maven Central.
"""

# Import consolidated tools for easier access
from maven_mcp_server.tools.check_version import check_version, latest_version
from maven_mcp_server.tools.check_version_batch import check_version_batch
from maven_mcp_server.tools.list_available_versions import list_available_versions

__all__ = ['check_version', 'latest_version', 'check_version_batch', 'list_available_versions']