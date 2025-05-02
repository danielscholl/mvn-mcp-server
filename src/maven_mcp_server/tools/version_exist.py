"""Maven version existence checking tool.

This module implements a tool to check if a specific version of a Maven
dependency exists in the Maven Central repository.
"""

import requests
from typing import Dict, Any, Optional

from mcp.server.fastmcp.exceptions import ValidationError, ToolError, ResourceError

from maven_mcp_server.shared.data_types import ErrorCode, MavenVersionCheckRequest
from maven_mcp_server.shared.utils import (
    validate_maven_dependency,
    validate_version_string,
    determine_packaging,
    format_error_response
)


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
    try:
        # Validate inputs
        group_id, artifact_id = validate_maven_dependency(dependency)
        validated_version = validate_version_string(version)
        
        # Determine correct packaging (automatically use "pom" for BOM dependencies)
        actual_packaging = determine_packaging(packaging, artifact_id)
        
        # Check if the specific version exists
        exists = _check_version_exists_in_maven_central(
            group_id, 
            artifact_id, 
            validated_version, 
            actual_packaging,
            classifier
        )
        
        # Return success response
        return {
            "exists": exists
        }
        
    except ValidationError as e:
        # Re-raise validation errors
        raise ValidationError(str(e))
    except requests.RequestException as e:
        # Handle network/API errors
        raise ResourceError(
            f"Error connecting to Maven Central: {str(e)}",
            {"error_code": ErrorCode.MAVEN_API_ERROR}
        )
    except Exception as e:
        # Handle unexpected errors
        raise ToolError(
            f"Unexpected error checking Maven version: {str(e)}",
            {"error_code": ErrorCode.INTERNAL_SERVER_ERROR}
        )


def _check_version_exists_in_maven_central(
    group_id: str,
    artifact_id: str,
    version: str,
    packaging: str,
    classifier: Optional[str] = None
) -> bool:
    """Check if a specific version exists in Maven Central.
    
    This function uses the Maven Central Repository API to check
    if a specific artifact version exists.
    
    Args:
        group_id: The Maven group ID
        artifact_id: The Maven artifact ID
        version: The version to check
        packaging: The packaging type (jar, war, pom, etc.)
        classifier: Optional classifier
        
    Returns:
        Boolean indicating if the version exists
        
    Raises:
        ResourceError: If there's an issue with the Maven Central API
    """
    # Convert group ID dots to slashes for repository path
    group_path = group_id.replace(".", "/")
    
    # Build the URL for the direct repository check
    # First try the direct file existence method
    base_url = f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/{version}/"
    file_name = f"{artifact_id}-{version}"
    
    if classifier:
        file_name += f"-{classifier}"
    
    file_name += f".{packaging}"
    file_url = base_url + file_name
    
    # Check if the file exists using a HEAD request
    try:
        response = requests.head(file_url, timeout=10)
        
        # If we get a 200 OK, the file exists
        if response.status_code == 200:
            return True
            
        # If the direct file check failed, try the Maven metadata approach
        if response.status_code == 404:
            # Try to fetch metadata to check if version is listed
            return _check_version_in_metadata(group_id, artifact_id, version)
            
        # For other status codes, raise an error
        response.raise_for_status()
        
    except requests.RequestException as e:
        # Handle network errors or non-200 responses
        raise ResourceError(
            f"Error connecting to Maven Central: {str(e)}",
            {"error_code": ErrorCode.MAVEN_API_ERROR}
        )
        
    # Default fallback (should not reach here under normal circumstances)
    return False


def _check_version_in_metadata(group_id: str, artifact_id: str, version: str) -> bool:
    """Check if a version is listed in the Maven metadata.
    
    This is a fallback approach that checks the maven-metadata.xml file
    to see if a version is listed.
    
    Args:
        group_id: The Maven group ID
        artifact_id: The Maven artifact ID
        version: The version to check
        
    Returns:
        Boolean indicating if the version is listed in metadata
    """
    group_path = group_id.replace(".", "/")
    metadata_url = f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/maven-metadata.xml"
    
    try:
        response = requests.get(metadata_url, timeout=10)
        
        # If metadata doesn't exist, the dependency might not exist at all
        if response.status_code == 404:
            raise ResourceError(
                f"Dependency {group_id}:{artifact_id} not found in Maven Central",
                {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND}
            )
        
        # Check for successful response
        response.raise_for_status()
        
        # Parse the XML response
        xml_content = response.text
        
        # Use an XML parser to check for the version in metadata
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(xml_content)
            for version_element in root.findall(".//version"):
                if version_element.text == version:
                    return True
            return False
        except ET.ParseError:
            raise ResourceError(
                "Failed to parse Maven metadata XML",
                {"error_code": ErrorCode.MAVEN_API_ERROR}
            )
        
    except requests.RequestException as e:
        # Handle network errors or non-200 responses
        raise ResourceError(
            f"Error fetching Maven metadata: {str(e)}",
            {"error_code": ErrorCode.MAVEN_API_ERROR}
        )
        
    # Default fallback
    return False