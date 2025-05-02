"""Maven latest version retrieval tool.

This module implements a tool to get the latest version of a Maven
dependency from the Maven Central repository.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List

import requests
from mcp.server.fastmcp.exceptions import ValidationError, ToolError, ResourceError

from maven_mcp_server.shared.data_types import ErrorCode, MavenLatestVersionRequest
from maven_mcp_server.shared.utils import (
    validate_maven_dependency,
    determine_packaging,
    get_latest_version,
    format_error_response
)


def get_maven_latest_version(
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
    try:
        # Validate inputs
        group_id, artifact_id = validate_maven_dependency(dependency)
        
        # Determine correct packaging (automatically use "pom" for BOM dependencies)
        actual_packaging = determine_packaging(packaging, artifact_id)
        
        # Fetch all available versions
        versions = _fetch_all_versions_from_maven_central(
            group_id, 
            artifact_id
        )
        
        if not versions:
            # If no versions are found, generate a specific error
            raise ResourceError(
                f"No versions found for {dependency}",
                {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND.value}
            )
        
        # Get the latest version
        latest_version = get_latest_version(versions)
        
        # Return success response
        return {
            "latest_version": latest_version
        }
        
    except ValidationError as e:
        # Re-raise validation errors
        raise ValidationError(str(e))
    except requests.RequestException as e:
        # Handle network/API errors
        raise ResourceError(
            f"Error connecting to Maven Central: {str(e)}",
            {"error_code": ErrorCode.MAVEN_API_ERROR.value}
        )
    except Exception as e:
        # Handle unexpected errors
        raise ToolError(
            f"Unexpected error fetching Maven latest version: {str(e)}",
            {"error_code": ErrorCode.INTERNAL_SERVER_ERROR.value}
        )


def _fetch_all_versions_from_maven_central(
    group_id: str,
    artifact_id: str
) -> List[str]:
    """Fetch all available versions for an artifact from Maven Central.
    
    This function retrieves the maven-metadata.xml file from the Maven
    Central repository and extracts all available versions.
    
    Args:
        group_id: The Maven group ID
        artifact_id: The Maven artifact ID
        
    Returns:
        List of available version strings
        
    Raises:
        ResourceError: If there's an issue with the Maven Central API
    """
    # Convert group ID dots to slashes for repository path
    group_path = group_id.replace(".", "/")
    metadata_url = f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/maven-metadata.xml"
    
    try:
        response = requests.get(metadata_url, timeout=10)
        
        # If metadata doesn't exist, the dependency might not exist at all
        if response.status_code == 404:
            raise ResourceError(
                f"Dependency {group_id}:{artifact_id} not found in Maven Central",
                {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND.value}
            )
        
        # Check for successful response
        response.raise_for_status()
        
        # Parse the XML response
        xml_content = response.text
        
        try:
            root = ET.fromstring(xml_content)
            versions = []
            
            for version_element in root.findall(".//version"):
                if version_element.text:
                    versions.append(version_element.text)
            
            return versions
            
        except ET.ParseError:
            raise ResourceError(
                "Failed to parse Maven metadata XML",
                {"error_code": ErrorCode.MAVEN_API_ERROR.value}
            )
        
    except requests.RequestException as e:
        # Handle network errors or non-200 responses
        raise ResourceError(
            f"Error fetching Maven metadata: {str(e)}",
            {"error_code": ErrorCode.MAVEN_API_ERROR.value}
        )
    
    # Default fallback (should not reach here under normal circumstances)
    return []