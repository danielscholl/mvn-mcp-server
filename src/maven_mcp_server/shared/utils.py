"""Utility functions for Maven MCP Server.

This module contains helper functions for API calls, response formatting, and error handling.
"""

import re
from typing import Dict, Any, Optional

import requests
from mcp.server.fastmcp.exceptions import ValidationError, ToolError, ResourceError

from maven_mcp_server.shared.data_types import ErrorCode


def format_error_response(error_code: ErrorCode, error_message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Format a standardized error response.
    
    Args:
        error_code: The error code enum value
        error_message: Human-readable error message
        details: Optional additional details about the error
        
    Returns:
        Formatted error response dictionary
    """
    response = {
        "error": {
            "code": error_code,
            "message": error_message
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def validate_maven_dependency(dependency: str) -> tuple[str, str]:
    """Validate Maven dependency string and extract groupId and artifactId.
    
    Args:
        dependency: Maven dependency in groupId:artifactId format
        
    Returns:
        Tuple of (groupId, artifactId)
        
    Raises:
        ValidationError: If dependency format is invalid
    """
    if not dependency or not isinstance(dependency, str):
        raise ValidationError("Dependency must be a non-empty string")
    
    parts = dependency.split(":")
    if len(parts) != 2:
        raise ValidationError("Dependency must be in groupId:artifactId format")
    
    group_id, artifact_id = parts
    if not group_id or not artifact_id:
        raise ValidationError("Both groupId and artifactId must be non-empty")
    
    return group_id, artifact_id


def validate_version_string(version: str) -> str:
    """Validate Maven version string.
    
    Args:
        version: Version string to validate
        
    Returns:
        Validated version string
        
    Raises:
        ValidationError: If version format is invalid
    """
    if not version or not isinstance(version, str):
        raise ValidationError("Version must be a non-empty string")
    
    # Basic version validation pattern
    # Allows standard versions like 1.2.3, 1.2.3-SNAPSHOT, 1.2.3.Final, etc.
    version_pattern = r'^[\d]+(\.[\d]+)*([-.][\w]+)*$'
    if not re.match(version_pattern, version):
        raise ValidationError(f"Invalid version format: {version}")
    
    return version


def determine_packaging(packaging: str, artifact_id: str) -> str:
    """Determine correct packaging based on artifact ID or specified packaging.
    
    Args:
        packaging: User-specified packaging (jar, war, etc.)
        artifact_id: The artifact ID from the dependency
        
    Returns:
        The determined packaging type
    """
    # If artifact ends with -bom or -dependencies, it's likely a POM
    if artifact_id.endswith(("-bom", "-dependencies")):
        return "pom"
    
    # Otherwise use the provided packaging or default to jar
    return packaging.lower() if packaging else "jar"