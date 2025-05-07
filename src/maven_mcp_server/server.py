"""Maven MCP Server using FastMCP framework.

This module creates and configures the FastMCP server instance for the Maven MCP tools.
"""

import os
import logging
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Import the consolidated tools
from maven_mcp_server.tools.check_version import check_version, latest_version
from maven_mcp_server.tools.check_version_batch import check_version_batch
from maven_mcp_server.tools.list_available_versions import list_available_versions

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

# Register MCP tools with detailed descriptions
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
    # Use the consolidated check_version but extract only the exists property
    result = check_version(dependency, version, packaging, classifier)
    
    # Convert the response to match the original format
    if result["status"] == "success":
        # Just return the exists field to maintain the same response format
        exists_result = {
            "tool_name": "check_version",
            "status": "success",
            "result": {
                "exists": result["result"]["exists"]
            }
        }
        return exists_result
    
    # If there was an error, pass through the error response
    return result

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
    
    # Use the consolidated check_version tool to get all version data
    result = check_version(dependency, version, packaging, classifier)
    
    # Extract the specific component version from the result
    if result["status"] == "success":
        component_version = result["result"]["latest_versions"].get(target_component)
        
        # Format the response to match the original format
        if component_version:
            find_result = {
                "tool_name": "find_version",
                "status": "success",
                "result": {
                    "latest_version": component_version
                }
            }
            logger.info(f"Result: {component_version}")
            return find_result
    
    # If there was an error, pass through the error response
    logger.error(f"Error finding version for component: {target_component}")
    return result

# Register new consolidated tools
@mcp.tool(
    description="Check a Maven version and get all version update information in a single call"
)
def check_version_tool(dependency: str, version: str, packaging: str = "jar", classifier: str = None):
    """Check a Maven dependency version and provide comprehensive version information.
    
    This consolidated tool checks if a version exists and simultaneously provides 
    information about the latest available versions across all semantic versioning components.
    
    Args:
        dependency: Maven dependency in groupId:artifactId format
        version: Version string to check and use as reference
        packaging: Package type (jar, war, etc.), defaults to "jar"
        classifier: Optional classifier
        
    Returns:
        Comprehensive version information including:
        - If the version exists
        - The latest versions available (major, minor, patch)
        - Which updates are available
    """
    logger.info(f"MCP call to consolidated check_version with: {dependency}, {version}")
    result = check_version(dependency, version, packaging, classifier)
    logger.info(f"Result summary: {dependency} v{version} exists={result.get('result', {}).get('exists', False)}")
    return result

@mcp.tool(
    description="Process multiple Maven dependency version checks in a single batch request"
)
def check_version_batch_tool(dependencies: List[Dict[str, Any]]):
    """Process multiple Maven dependency version checks in a single batch request.
    
    This tool efficiently handles processing multiple dependencies in a single call,
    reducing the number of API calls and providing a summary of updates available.
    
    Args:
        dependencies: List of dependency objects, each containing:
            - dependency: Maven dependency in groupId:artifactId format
            - version: Version string to check and use as reference
            - packaging: (Optional) Package type, defaults to "jar"
            - classifier: (Optional) Classifier
            
    Returns:
        Comprehensive batch results including:
        - Summary statistics (total, success, failed, updates available)
        - Detailed information for each dependency
    """
    logger.info(f"MCP call to batch check_version with {len(dependencies)} dependencies")
    result = check_version_batch(dependencies)
    summary = result.get("result", {}).get("summary", {})
    logger.info(f"Batch result summary: {summary.get('success', 0)}/{summary.get('total', 0)} successful, "
                f"updates available: major={summary.get('updates_available', {}).get('major', 0)}, "
                f"minor={summary.get('updates_available', {}).get('minor', 0)}, "
                f"patch={summary.get('updates_available', {}).get('patch', 0)}")
    return result

@mcp.tool(
    description="List all available versions of a Maven artifact grouped by minor version tracks"
)
def list_available_versions_tool(
    dependency: str, 
    version: str, 
    packaging: str = "jar", 
    classifier: str = None,
    include_all_versions: bool = False
):
    """List all available versions of a Maven dependency grouped by minor tracks.
    
    This tool provides a comprehensive view of all available versions for a Maven dependency,
    organized by major.minor version tracks. It helps developers make informed decisions
    about version upgrades by showing the complete version landscape.
    
    Args:
        dependency: Maven dependency in groupId:artifactId format
        version: Current version string to use as reference
        packaging: Package type (jar, war, etc.), defaults to "jar"
        classifier: Optional classifier
        include_all_versions: Whether to include all versions in the response (default: False)
            When False, only includes versions for the current track
            When True, includes full version lists for all tracks
            
    Returns:
        Structured version information including:
        - Current version and whether it exists
        - Latest overall version
        - All minor version tracks with their latest versions
        - Full version lists for selected tracks based on include_all_versions
    """
    logger.info(f"MCP call to list_available_versions with: {dependency}, {version}, include_all={include_all_versions}")
    result = list_available_versions(
        dependency, 
        version, 
        packaging, 
        classifier, 
        include_all_versions
    )
    
    # Log info about the result
    minor_tracks = result.get("result", {}).get("minor_tracks", {})
    track_count = len(minor_tracks)
    current_track = next((track for track, info in minor_tracks.items() 
                          if info.get("is_current_track", False)), "none")
    
    logger.info(f"Found {track_count} minor version tracks for {dependency}, "
                f"current track: {current_track}")
    
    return result