"""Maven latest version retrieval tool.

This module implements a tool to get the latest version of a Maven
dependency from the Maven Central repository.
"""

import logging
from typing import Dict, Any, Optional

from mcp.server.fastmcp.exceptions import ValidationError, ToolError, ResourceError

from maven_mcp_server.shared.data_types import ErrorCode, MavenLatestVersionRequest
from maven_mcp_server.shared.utils import (
    validate_maven_dependency,
    determine_packaging
)
from maven_mcp_server.services.maven_api import MavenApiService
from maven_mcp_server.services.response import format_success_response, format_error_response

# Set up logging
logger = logging.getLogger("maven-mcp-server")

# Create a shared instance of MavenApiService
maven_api = MavenApiService()

def latest_version(
    dependency: str,
    packaging: str = "jar",
    classifier: Optional[str] = None
) -> Dict[str, Any]:
    """Get the latest version of a Maven dependency from Maven Central.
    
    Args:
        dependency: Maven dependency in groupId:artifactId format
        packaging: Package type (jar, war, etc.), defaults to "jar"
        classifier: Optional classifier
        
    Returns:
        Dictionary with "latest_version" string indicating the latest available version
        
    Raises:
        ValidationError: If input parameters are invalid
        ResourceError: If there's an issue connecting to Maven Central
        ToolError: For other unexpected errors
    """
    tool_name = "latest_version"
    
    try:
        # Validate inputs
        group_id, artifact_id = validate_maven_dependency(dependency)
        
        # Determine correct packaging (automatically use "pom" for BOM dependencies)
        actual_packaging = determine_packaging(packaging, artifact_id)
        
        # Log the input parameters
        logger.debug(
            f"Getting latest version for: {group_id}:{artifact_id} "
            f"(packaging: {actual_packaging}, classifier: {classifier})"
        )
        
        # Get the latest version using MavenApiService
        latest = maven_api.get_latest_version(
            group_id, 
            artifact_id, 
            actual_packaging,
            classifier
        )
        
        # Return success response
        return format_success_response(tool_name, {"latest_version": latest})
        
    except ValidationError as e:
        # Re-raise validation errors
        logger.error(f"Validation error: {str(e)}")
        raise ValidationError(str(e))
    except ResourceError as e:
        # Handle resource errors
        logger.error(f"Resource error: {str(e)}")
        raise e
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error fetching Maven latest version: {str(e)}")
        raise ToolError(
            f"Unexpected error fetching Maven latest version: {str(e)}",
            {"error_code": ErrorCode.INTERNAL_SERVER_ERROR}
        )