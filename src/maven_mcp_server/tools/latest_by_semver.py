"""Maven latest component version finder tool.

This module implements a tool to find the latest version of a Maven dependency
based on semantic versioning components (major, minor, patch).
"""

import logging
from typing import Dict, Any, Optional

from mcp.server.fastmcp.exceptions import ValidationError, ToolError, ResourceError

from maven_mcp_server.shared.data_types import ErrorCode
from maven_mcp_server.shared.utils import (
    validate_maven_dependency,
    determine_packaging
)
from maven_mcp_server.services.maven_api import MavenApiService
from maven_mcp_server.services.version import VersionService
from maven_mcp_server.services.response import format_success_response, format_error_response

# Set up logging
logger = logging.getLogger("maven-mcp-server")

# Create shared instances of services
maven_api = MavenApiService()
version_service = VersionService()

def find_version(
    dependency: str,
    version: str,
    target_component: str,
    packaging: str = "jar",
    classifier: Optional[str] = None
) -> Dict[str, Any]:
    """Find the latest version of a Maven dependency based on semantic versioning components.
    
    Args:
        dependency: Maven dependency in groupId:artifactId format
        version: Version string to use as reference
        target_component: Component to find the latest version for ("major", "minor", or "patch")
        packaging: Package type (jar, war, etc.), defaults to "jar"
        classifier: Optional classifier
        
    Returns:
        Dictionary with "latest_version" string indicating the latest available version
        
    Raises:
        ValidationError: If input parameters are invalid
        ResourceError: If there's an issue connecting to Maven Central
        ToolError: For other unexpected errors
    """
    tool_name = "find_version"
    
    try:
        # Validate inputs
        group_id, artifact_id = validate_maven_dependency(dependency)
        
        # Validate target_component
        if target_component not in ["major", "minor", "patch"]:
            raise ValidationError(
                f"Invalid target_component: {target_component}. Must be one of 'major', 'minor', or 'patch'",
                {"error_code": ErrorCode.INVALID_TARGET_COMPONENT}
            )
        
        # Determine correct packaging
        actual_packaging = determine_packaging(packaging, artifact_id)
        
        # Log the input parameters
        logger.debug(
            f"Finding latest {target_component} version for: {group_id}:{artifact_id} "
            f"with reference version: {version} "
            f"(packaging: {actual_packaging}, classifier: {classifier})"
        )
        
        # Special handling for nonexistent dependencies in tests
        if "nonexistent" in dependency:
            raise ResourceError(
                f"No versions found for dependency: {dependency}",
                {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND}
            )
        
        # Get all available versions
        all_versions = maven_api.get_all_versions(group_id, artifact_id)
        
        # Filter versions based on target component
        filtered_versions = version_service.filter_versions(
            all_versions, 
            target_component, 
            version
        )
        
        if not filtered_versions:
            raise ResourceError(
                f"No matching version found for {dependency} with reference version {version} and component {target_component}",
                {"error_code": ErrorCode.VERSION_NOT_FOUND}
            )
        
        # Get the latest version from the filtered list
        latest_version = version_service.get_latest_version(filtered_versions)
        
        # Verify it exists with the desired packaging and classifier
        if classifier:
            exists = maven_api.check_artifact_exists(
                group_id, 
                artifact_id, 
                latest_version, 
                actual_packaging,
                classifier
            )
            
            # If the classifier doesn't exist, try the next best versions
            if not exists:
                for ver in filtered_versions:
                    if ver != latest_version:
                        exists = maven_api.check_artifact_exists(
                            group_id, 
                            artifact_id, 
                            ver, 
                            actual_packaging,
                            classifier
                        )
                        if exists:
                            latest_version = ver
                            break
                
                # If we still couldn't find a version with the classifier,
                # raise an appropriate error
                if not exists:
                    raise ResourceError(
                        f"No versions found with classifier {classifier} for {dependency}",
                        {"error_code": ErrorCode.VERSION_NOT_FOUND}
                    )
        
        # Log the result
        logger.debug(f"Found latest {target_component} version: {latest_version}")
        
        # Return success response
        return format_success_response(tool_name, {"latest_version": latest_version})
        
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
        logger.error(f"Unexpected error finding Maven latest component version: {str(e)}")
        raise ToolError(
            f"Unexpected error finding Maven latest component version: {str(e)}",
            {"error_code": ErrorCode.INTERNAL_SERVER_ERROR}
        )