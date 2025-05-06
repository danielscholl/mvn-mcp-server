"""Maven MCP Server using FastMCP framework.

This module creates and configures the FastMCP server instance for the Maven MCP tools.
"""

import os
import logging
from mcp.server.fastmcp import FastMCP

from maven_mcp_server.tools.version_exist import check_version
from maven_mcp_server.tools.check_version import latest_version
from maven_mcp_server.tools.latest_by_semver import find_version

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("maven-mcp-server")

# Create FastMCP server instance with descriptions
mcp = FastMCP(
    "Maven MCP Server", 
    description="A server providing tools for Maven dependency version management"
)

# Register tools with detailed descriptions
@mcp.tool(
    description="Check if a specific version of a Maven artifact exists in Maven Central"
)
def check_maven_version(dependency: str, version: str, packaging: str = "jar", classifier: str = None):
    """Check if a specific version of a Maven dependency exists in Maven Central.
    
    Args:
        dependency: Maven dependency in groupId:artifactId format
        version: Version string to check
        packaging: Package type (jar, war, etc.), defaults to "jar"
        classifier: Optional classifier
    """
    return check_version(dependency, version, packaging, classifier)

@mcp.tool(
    description="Get the latest version of a Maven artifact from Maven Central"
)
def get_maven_latest_version(dependency: str, packaging: str = "jar", classifier: str = None):
    """Get the latest version of a Maven dependency from Maven Central.
    
    Args:
        dependency: Maven dependency in groupId:artifactId format
        packaging: Package type (jar, war, etc.), defaults to "jar"
        classifier: Optional classifier
    """
    return latest_version(dependency, packaging, classifier)

@mcp.tool(
    description="Find the latest version of a Maven artifact based on semantic versioning components"
)
def find_maven_version(dependency: str, version: str, target_component: str, packaging: str = "jar", classifier: str = None):
    """Find the latest version of a Maven dependency based on semantic versioning components.
    
    Args:
        dependency: Maven dependency in groupId:artifactId format
        version: Version string to use as reference
        target_component: Component to find the latest version for ("major", "minor", or "patch")
        packaging: Package type (jar, war, etc.), defaults to "jar"
        classifier: Optional classifier
    """
    logger.info(f"MCP call to find_maven_version with: {dependency}, {version}, {target_component}")
    result = find_version(dependency, version, target_component, packaging, classifier)
    logger.info(f"Result: {result}")
    return result