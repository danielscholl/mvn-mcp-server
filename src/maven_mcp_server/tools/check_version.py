"""Maven latest version retrieval tool.

This module implements a tool to get the latest version of a Maven
dependency from the Maven Central repository.
"""

import functools
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List

import requests
from mcp.server.fastmcp.exceptions import ValidationError, ToolError, ResourceError

from maven_mcp_server.shared.data_types import ErrorCode, MavenLatestVersionRequest
from maven_mcp_server.shared.utils import (
    validate_maven_dependency,
    determine_packaging,
    get_latest_version,
    compare_versions,
    format_error_response
)


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
        
        # Verify that the specific version with the requested packaging and classifier exists
        if classifier:
            # Check if the artifact with the specified classifier exists for the latest version
            artifact_exists = _check_specific_artifact_exists(
                group_id,
                artifact_id,
                latest_version,
                actual_packaging,
                classifier
            )
            if not artifact_exists:
                # Find the next latest version that has the specified classifier
                for version in sorted(versions, key=functools.cmp_to_key(compare_versions), reverse=True):
                    if version != latest_version:
                        if _check_specific_artifact_exists(
                            group_id, artifact_id, version, actual_packaging, classifier
                        ):
                            latest_version = version
                            break
        
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


def _check_specific_artifact_exists(
    group_id: str,
    artifact_id: str,
    version: str,
    packaging: str,
    classifier: str
) -> bool:
    """Check if a specific artifact with classifier exists in Maven Central.
    
    Args:
        group_id: The Maven group ID
        artifact_id: The Maven artifact ID
        version: The specific version to check
        packaging: The packaging type (jar, war, etc.)
        classifier: The classifier to check for
        
    Returns:
        Boolean indicating if the artifact with classifier exists
    """
    # Convert group ID dots to slashes for repository path
    group_path = group_id.replace(".", "/")
    
    # Build the URL for the direct repository check
    base_url = f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/{version}/"
    file_name = f"{artifact_id}-{version}-{classifier}.{packaging}"
    file_url = base_url + file_name
    
    # Check if the file exists using a HEAD request
    try:
        response = requests.head(file_url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False