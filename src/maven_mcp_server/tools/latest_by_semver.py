"""Maven latest component version finder tool.

This module implements a tool to find the latest version of a Maven dependency
based on semantic versioning components (major, minor, patch).
"""

import re
import requests
from typing import Dict, Any, Optional, List, Tuple

from mcp.server.fastmcp.exceptions import ValidationError, ToolError, ResourceError

from maven_mcp_server.shared.data_types import ErrorCode
from maven_mcp_server.shared.utils import (
    validate_maven_dependency,
    determine_packaging,
    format_error_response,
    parse_version_components,
    compare_versions
)


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
    try:
        # Validate inputs
        group_id, artifact_id = validate_maven_dependency(dependency)
        
        # Validate target_component
        if target_component not in ["major", "minor", "patch"]:
            raise ValidationError(
                f"Invalid target_component: {target_component}. Must be one of 'major', 'minor', or 'patch'",
                {"error_code": ErrorCode.INVALID_TARGET_COMPONENT}
            )
        
        # Parse and validate the input version
        version_components = _parse_input_version(version)
        if not version_components:
            raise ValidationError(
                f"Cannot parse version: {version}",
                {"error_code": ErrorCode.INVALID_INPUT_FORMAT}
            )
        
        # Determine correct packaging (automatically use "pom" for BOM dependencies)
        actual_packaging = determine_packaging(packaging, artifact_id)
        
        # Get all available versions for the dependency
        all_versions = _get_all_versions(group_id, artifact_id)
        
        if not all_versions:
            raise ResourceError(
                f"No versions found for dependency: {group_id}:{artifact_id}",
                {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND}
            )
        
        # Find the latest version based on the target component
        latest_version = _find_latest_component_version(
            all_versions, 
            version_components, 
            target_component
        )
        
        if not latest_version:
            raise ResourceError(
                f"No matching version found for {dependency} with reference version {version} and component {target_component}",
                {"error_code": ErrorCode.VERSION_NOT_FOUND}
            )
        
        # Return success response
        return {
            "latest_version": latest_version
        }
        
    except ValidationError as e:
        # Re-raise validation errors
        raise ValidationError(str(e))
    except ResourceError as e:
        # Re-raise resource errors
        raise ResourceError(str(e))
    except requests.RequestException as e:
        # Handle network/API errors
        raise ResourceError(
            f"Error connecting to Maven Central: {str(e)}",
            {"error_code": ErrorCode.MAVEN_API_ERROR}
        )
    except Exception as e:
        # Handle unexpected errors
        raise ToolError(
            f"Unexpected error finding Maven latest component version: {str(e)}",
            {"error_code": ErrorCode.INTERNAL_SERVER_ERROR}
        )


def _parse_input_version(version: str) -> Tuple[List[int], str]:
    """Parse input version string into components.
    
    Supports multiple version formats:
    - Standard semver (MAJOR.MINOR.PATCH)
    - Calendar format (20231013)
    - Simple numeric (5)
    - Partial semver (1.0)
    
    Args:
        version: Input version string
        
    Returns:
        Tuple of (numeric_components, qualifier)
    """
    # Handle standard semver format (MAJOR.MINOR.PATCH)
    semver_match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:[-.](.+))?$', version)
    if semver_match:
        major, minor, patch, qualifier = semver_match.groups()
        return [int(major), int(minor), int(patch)], qualifier or ""
    
    # Handle partial semver format (MAJOR.MINOR)
    partial_semver_match = re.match(r'^(\d+)\.(\d+)(?:[-.](.+))?$', version)
    if partial_semver_match:
        major, minor, qualifier = partial_semver_match.groups()
        return [int(major), int(minor)], qualifier or ""
    
    # Handle simple numeric format (MAJOR)
    simple_numeric_match = re.match(r'^(\d+)(?:[-.](.+))?$', version)
    if simple_numeric_match:
        major, qualifier = simple_numeric_match.groups()
        return [int(major)], qualifier or ""
    
    # Handle calendar format (YYYYMMDD or similar)
    calendar_match = re.match(r'^(20\d{2}\d{2,4})(?:[-.](.+))?$', version)
    if calendar_match:
        calendar_version, qualifier = calendar_match.groups()
        return [int(calendar_version)], qualifier or ""
    
    # If no format matched, use the existing parser as fallback
    return parse_version_components(version)


def _get_all_versions(group_id: str, artifact_id: str) -> List[str]:
    """Get all available versions for a Maven dependency.
    
    Args:
        group_id: Maven group ID
        artifact_id: Maven artifact ID
        
    Returns:
        List of all available versions
        
    Raises:
        ResourceError: If there's an issue with the Maven API
    """
    group_path = group_id.replace(".", "/")
    metadata_url = f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/maven-metadata.xml"
    
    try:
        response = requests.get(metadata_url, timeout=10)
        
        # Check if the dependency exists
        if response.status_code == 404:
            raise ResourceError(
                f"Dependency {group_id}:{artifact_id} not found in Maven Central",
                {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND}
            )
        
        # Check for successful response
        response.raise_for_status()
        
        # Parse the XML response
        xml_content = response.text
        
        # Use an XML parser to extract versions from metadata
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(xml_content)
            versions = []
            
            for version_element in root.findall(".//version"):
                if version_element.text:
                    versions.append(version_element.text)
            
            if not versions:
                raise ResourceError(
                    f"No versions found for dependency: {group_id}:{artifact_id}",
                    {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND}
                )
            
            return versions
            
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


def _find_latest_component_version(
    all_versions: List[str], 
    reference_components: List[int],
    target_component: str
) -> str:
    """Find the latest version based on the target component.
    
    Args:
        all_versions: List of all available versions
        reference_components: Numeric components of the reference version
        target_component: Component to find the latest version for ("major", "minor", or "patch")
        
    Returns:
        The latest version string based on the target component
    """
    # Filter out snapshot versions
    filtered_versions = [v for v in all_versions if "snapshot" not in v.lower()]
    
    # Also filter out beta/alpha/rc versions
    stable_versions = []
    for v in filtered_versions:
        if not any(qualifier in v.lower() for qualifier in ["-beta", "-alpha", "-rc", ".beta", ".alpha", ".rc"]):
            stable_versions.append(v)
    
    # If we filtered out all versions, fall back to the original filtered list
    versions_to_use = stable_versions if stable_versions else filtered_versions
    
    # Parse components for all versions
    parsed_versions = []
    for version in versions_to_use:
        components, qualifier = _parse_input_version(version)
        parsed_versions.append((version, components, qualifier))
    
    # Determine which parts of the reference version to match based on target_component
    if target_component == "major":
        # For major, we want the highest major version across all versions
        matching_versions = parsed_versions
    elif target_component == "minor":
        # For minor, we want the highest minor version within the given major version
        if len(reference_components) < 1:
            return ""
        
        matching_versions = [
            (v, c, q) for v, c, q in parsed_versions 
            if len(c) >= 1 and c[0] == reference_components[0]
        ]
    elif target_component == "patch":
        # For patch, we want the highest patch version within the given major.minor version
        if len(reference_components) < 2:
            return ""
        
        matching_versions = [
            (v, c, q) for v, c, q in parsed_versions 
            if len(c) >= 2 and c[0] == reference_components[0] and c[1] == reference_components[1]
        ]
    else:
        return ""
    
    if not matching_versions:
        return ""
    
    # Use the compare_versions function from utils to properly sort the versions
    from maven_mcp_server.shared.utils import compare_versions
    from functools import cmp_to_key
    
    def version_comparator(v1, v2):
        return compare_versions(v1, v2)
    
    original_versions = [v[0] for v in matching_versions]
    sorted_versions = sorted(original_versions, key=cmp_to_key(version_comparator), reverse=True)
    
    return sorted_versions[0] if sorted_versions else ""


