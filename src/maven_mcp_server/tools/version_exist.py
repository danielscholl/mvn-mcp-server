"""Maven version existence checking tool.

This module implements a tool to check if a specific version of a Maven
dependency exists in the Maven Central repository.
"""

import logging
from typing import Dict, Any, Optional

from mcp.server.fastmcp.exceptions import ValidationError, ToolError, ResourceError

from maven_mcp_server.shared.data_types import ErrorCode, MavenVersionCheckRequest
from maven_mcp_server.shared.utils import (
    validate_maven_dependency,
    validate_version_string,
    determine_packaging
)
from maven_mcp_server.services.maven_api import MavenApiService
from maven_mcp_server.services.response import format_success_response, format_error_response

# Set up logging
logger = logging.getLogger("maven-mcp-server")

# Create a shared instance of MavenApiService
maven_api = MavenApiService()

def check_version(
    dependency: str,
    version: str,
    packaging: str = "jar",
    classifier: Optional[str] = None
) -> Dict[str, Any]:
    """Check if a specific version of a Maven dependency exists in Maven Central.
    
    Args:
        dependency: Maven dependency in groupId:artifactId format
        version: Version string to check
        packaging: Package type (jar, war, etc.), defaults to "jar"
        classifier: Optional classifier
        
    Returns:
        Dictionary with "exists" boolean indicating if the version exists
        
    Raises:
        ValidationError: If input parameters are invalid
        ResourceError: If there's an issue connecting to Maven Central
        ToolError: For other unexpected errors
    """
    tool_name = "check_version"
    
    try:
        # Validate inputs
        group_id, artifact_id = validate_maven_dependency(dependency)
        validated_version = validate_version_string(version)
        
        # Determine correct packaging (automatically use "pom" for BOM dependencies)
        actual_packaging = determine_packaging(packaging, artifact_id)
        
        # Log the input parameters
        logger.debug(
            f"Checking version existence: {group_id}:{artifact_id}:{validated_version} "
            f"(packaging: {actual_packaging}, classifier: {classifier})"
        )
        
        # Check if the specific version exists using MavenApiService
        exists = maven_api.check_artifact_exists(
            group_id, 
            artifact_id, 
            validated_version, 
            actual_packaging,
            classifier
        )
        
        # Return success response
        return format_success_response(tool_name, {"exists": exists})
        
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
        logger.error(f"Unexpected error checking Maven version: {str(e)}")
        raise ToolError(
            f"Unexpected error checking Maven version: {str(e)}",
            {"error_code": ErrorCode.INTERNAL_SERVER_ERROR}
        )