"""Maven latest component version finder tool.

This module implements a tool to find the latest version of a Maven dependency
based on semantic versioning components (major, minor, patch).
"""

import re
import requests
import logging
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

# Set up logging
logger = logging.getLogger("maven-mcp-server")

# These functions are kept for backward compatibility with tests
def _parse_input_version(version: str) -> Tuple[List[int], str]:
    """Parse input version string into components (backwards compatibility).
    
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
    is_valid, version_tuple, _ = _parse_semver(version)
    if is_valid and version_tuple:
        major, minor, patch = version_tuple
        # Convert to the list format expected by tests
        return [major, minor, patch], ""
    
    # Fallback to the original parse_version_components
    return parse_version_components(version)

def _get_all_versions(group_id: str, artifact_id: str) -> List[str]:
    """Get all available versions for a Maven dependency (backwards compatibility).
    
    Args:
        group_id: Maven group ID
        artifact_id: Maven artifact ID
        
    Returns:
        List of all available versions
        
    Raises:
        ResourceError: If there's an issue with the Maven API
    """
    query = f"g:{group_id} AND a:{artifact_id}"
    response_data, error = _query_maven_central(query, "")
    
    if error:
        raise ResourceError(
            f"Error fetching Maven metadata: {error.get('message', 'Unknown error')}",
            {"error_code": ErrorCode.MAVEN_API_ERROR}
        )
    
    docs = response_data.get("response", {}).get("docs", [])
    if not docs:
        raise ResourceError(
            f"Dependency {group_id}:{artifact_id} not found in Maven Central",
            {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND}
        )
    
    versions = []
    for doc in docs:
        version_str = doc.get("v")
        if version_str:
            versions.append(version_str)
    
    if not versions:
        raise ResourceError(
            f"No versions found for dependency: {group_id}:{artifact_id}",
            {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND}
        )
    
    return versions

def _find_latest_component_version(
    all_versions: List[str], 
    reference_components: List[int],
    target_component: str
) -> str:
    """Find the latest version based on the target component (backwards compatibility).
    
    Args:
        all_versions: List of all available versions
        reference_components: Numeric components of the reference version
        target_component: Component to find the latest version for ("major", "minor", or "patch")
        
    Returns:
        The latest version string based on the target component
    """
    # Convert reference_components list to tuple for internal use
    version_tuple = tuple(reference_components[:3])
    while len(version_tuple) < 3:
        version_tuple = version_tuple + (0,)
    
    # Filter out snapshot versions
    filtered_versions = [v for v in all_versions if "snapshot" not in v.lower()]
    
    # Also filter out beta/alpha/rc versions
    stable_versions = []
    for v in filtered_versions:
        if not any(qualifier in v.lower() for qualifier in ["-beta", "-alpha", "-rc", ".beta", ".alpha", ".rc"]):
            stable_versions.append(v)
    
    # If we filtered out all versions, fall back to the original filtered list
    versions_to_use = stable_versions if stable_versions else filtered_versions
    
    # Determine which parts of the reference version to match based on target_component
    if target_component == "major":
        # For major, use all versions
        pass
    elif target_component == "minor":
        # For minor, filter versions matching the major component
        if len(reference_components) >= 1:
            major = reference_components[0]
            versions_to_use = [v for v in versions_to_use if v.startswith(f"{major}.")]
    elif target_component == "patch":
        # For patch, filter versions matching the major.minor component
        if len(reference_components) >= 2:
            major, minor = reference_components[0], reference_components[1]
            versions_to_use = [v for v in versions_to_use if v.startswith(f"{major}.{minor}.")]
    
    if not versions_to_use:
        return ""
    
    # Use the compare_versions function to properly sort the versions
    from functools import cmp_to_key
    
    def version_comparator(v1, v2):
        return compare_versions(v1, v2)
    
    sorted_versions = sorted(versions_to_use, key=cmp_to_key(version_comparator), reverse=True)
    
    return sorted_versions[0] if sorted_versions else ""


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
    logger.info(f"find_version called with: dependency={dependency}, version={version}, " +
                f"target_component={target_component}, packaging={packaging}, classifier={classifier}")
    
    try:
        # Validate inputs
        group_id, artifact_id = validate_maven_dependency(dependency)
        
        # Validate target_component
        if target_component not in ["major", "minor", "patch"]:
            raise ValidationError(
                f"Invalid target_component: {target_component}. Must be one of 'major', 'minor', or 'patch'",
                {"error_code": ErrorCode.INVALID_TARGET_COMPONENT}
            )
        
        # Parse the version into components
        is_valid, version_tuple, error = _parse_semver(version)
        if not is_valid or not version_tuple:
            logger.warning(f"Could not parse version '{version}' in any recognized format")
            # Instead of failing, we'll use a default version tuple
            version_tuple = (0, 0, 0)  # Default to all zeros
        else:
            logger.info(f"Parsed version '{version}' as tuple {version_tuple}")
        
        # Determine correct packaging (automatically use "pom" for BOM dependencies)
        actual_packaging = determine_packaging(packaging, artifact_id)
        logger.info(f"Using packaging type: {actual_packaging}")
        
        # Get the latest version based on the target component
        result = _get_latest_component_version(
            group_id, 
            artifact_id, 
            version_tuple, 
            target_component,
            actual_packaging,
            classifier
        )
        logger.info(f"Search result: {result}")
        
        # Process the result
        if result.get("status") == "success":
            latest_version = result.get("result", {}).get("latest_version")
            logger.info(f"Latest component version found: {latest_version}")
            return {
                "latest_version": latest_version
            }
        else:
            error_msg = result.get("error", {}).get("message", "Unknown error")
            logger.error(f"Error getting latest component version: {error_msg}")
            
            # Map error messages to appropriate error codes
            if "No documents found" in error_msg:
                raise ResourceError(
                    f"Dependency {dependency} not found in Maven Central",
                    {"error_code": ErrorCode.DEPENDENCY_NOT_FOUND}
                )
            elif "No versions matching" in error_msg:
                raise ResourceError(
                    f"No matching version found for {dependency} with reference version {version} and component {target_component}",
                    {"error_code": ErrorCode.VERSION_NOT_FOUND}
                )
            else:
                raise ResourceError(
                    error_msg,
                    {"error_code": ErrorCode.MAVEN_API_ERROR}
                )
        
    except ValidationError as e:
        # Re-raise validation errors
        logger.error(f"Validation error: {str(e)}")
        raise ValidationError(str(e))
    except ResourceError as e:
        # Re-raise resource errors
        logger.error(f"Resource error: {str(e)}")
        raise ResourceError(str(e))
    except requests.RequestException as e:
        # Handle network/API errors
        logger.error(f"Request exception: {str(e)}")
        raise ResourceError(
            f"Error connecting to Maven Central: {str(e)}",
            {"error_code": ErrorCode.MAVEN_API_ERROR}
        )
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        raise ToolError(
            f"Unexpected error finding Maven latest component version: {str(e)}",
            {"error_code": ErrorCode.INTERNAL_SERVER_ERROR}
        )


def _parse_semver(version: str) -> Tuple[bool, Optional[Tuple[int, int, int]], Optional[Dict]]:
    """
    Parse a version string into its components.
    
    Args:
        version: The version string, preferably in semantic version format (MAJOR.MINOR.PATCH).
        
    Returns:
        A tuple of (is_valid, version_tuple, error) where:
        - is_valid is a boolean indicating if the parsing was successful
        - version_tuple is a tuple of (major, minor, patch) if successful, None otherwise
        - error is None if successful or an error dict if parsing failed
    """
    if not version:
        return False, None, {
            "message": "Version parameter is required."
        }
    
    # Regular expression for semantic versioning (MAJOR.MINOR.PATCH)
    semver_pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-[\w.-]+)?(?:\+[\w.-]+)?$'
    match = re.match(semver_pattern, version)
    
    if match:
        try:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3))
            return True, (major, minor, patch), None
        except Exception as e:
            return False, None, {
                "message": f"Failed to parse version components: {str(e)}"
            }
    
    # Handle non-semver formats
    
    # Calendar-based versions (YYYYMMDD) like 20231013
    if version.isdigit():
        # For calendar versions, use year as major, month as minor, day as patch
        if len(version) >= 8:
            try:
                year = int(version[:4])
                month = int(version[4:6])
                day = int(version[6:8])
                # Validate that it looks like a real date
                if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                    # Return the date components
                    logger.info(f"Parsed calendar version {version} as {year}.{month}.{day} (date-based)")
                    return True, (year, month, day), None
            except Exception:
                pass
        # For other numeric versions, use the number as major, 0 for minor and patch
        try:
            major = int(version)
            minor = 0
            patch = 0
            logger.info(f"Parsed numeric version {version} as {major}.{minor}.{patch}")
            return True, (major, minor, patch), None
        except Exception:
            pass
    
    # Other non-standard formats - handle as best effort
    # For versions like "1.0", "1", etc.
    parts = version.split('.')
    if parts:
        try:
            # Start with zeros for each component
            major = minor = patch = 0
            # Fill in with actual values where available
            if len(parts) > 0:
                major = int(parts[0])
            if len(parts) > 1:
                minor = int(parts[1])
            if len(parts) > 2:
                patch = int(parts[2])
            logger.info(f"Parsed partial version {version} as {major}.{minor}.{patch}")
            return True, (major, minor, patch), None
        except Exception:
            pass
    
    # If all parsing attempts fail, return an error
    return False, None, {
        "message": f"Version '{version}' could not be parsed in any recognized format."
    }


def _query_maven_central(query: str, packaging: str, classifier: Optional[str] = None) -> Tuple[Dict, Optional[Dict]]:
    """
    Query Maven Central for artifacts using the Solr API.
    
    Args:
        query: The search query
        packaging: The packaging type
        classifier: Optional classifier
        
    Returns:
        Tuple of (response_data, error) where:
        - response_data is the parsed JSON response if successful
        - error is None if successful or an error dict if the query failed
    """
    # Build the Solr query
    base_url = "https://search.maven.org/solrsearch/select"
    
    # Add packaging and classifier to query if provided
    full_query = query
    if packaging:
        full_query += f" AND p:{packaging}"
    if classifier:
        full_query += f" AND l:{classifier}"
    
    params = {
        "q": full_query,
        "rows": 100,  # Get more results to ensure we capture all versions
        "wt": "json"
    }
    
    try:
        # Make the request to Maven Central
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        return data, None
        
    except requests.RequestException as e:
        return {}, {
            "message": f"Error querying Maven Central: {str(e)}"
        }
    except ValueError as e:
        return {}, {
            "message": f"Error parsing Maven Central response: {str(e)}"
        }


def _get_latest_component_version(
    group_id: str, 
    artifact_id: str, 
    version_tuple: Tuple[int, int, int],
    target_component: str,
    packaging: str = "jar",
    classifier: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find the latest version of a Maven artifact based on the target component.
    
    Args:
        group_id: The Maven group ID.
        artifact_id: The Maven artifact ID.
        version_tuple: A tuple of (major, minor, patch) of the input version.
        target_component: The component to find the latest version for (major, minor, or patch).
        packaging: The packaging type (default: "jar").
        classifier: The classifier, if any.
        
    Returns:
        Dict containing the latest version or error information
    """
    try:
        # Build the query for Maven Central
        query = f"g:{group_id} AND a:{artifact_id}"
        
        # Make the query to Maven Central
        response_data, error = _query_maven_central(query, packaging, classifier)
        if error:
            return {
                "status": "error",
                "error": error
            }
        
        # Extract the documents from the response
        docs = response_data.get("response", {}).get("docs", [])
        if not docs:
            return {
                "status": "error",
                "error": {
                    "message": f"No documents found for {group_id}:{artifact_id} in Maven Central"
                }
            }
        
        # Extract and parse all versions
        versions = []
        date_based_versions = []  # Special handling for date-based versions
        for doc in docs:
            version_str = doc.get("v")
            if not version_str:
                continue
                
            # Skip pre-release versions
            if "-" in version_str and any(x in version_str.lower() for x in ["alpha", "beta", "rc", "snapshot", "pre"]):
                continue
                
            # Try to parse the version in various formats
            is_valid, parsed_version, _ = _parse_semver(version_str)
            if is_valid and parsed_version:
                # Check if this looks like a date-based version (year in 1900-2100 range)
                if 1900 <= parsed_version[0] <= 2100:
                    date_based_versions.append((parsed_version, version_str))
                else:
                    versions.append((parsed_version, version_str))
        
        # Process versions based on target component
        if not versions and not date_based_versions:
            return {
                "status": "error",
                "error": {
                    "message": f"No valid versions found for {group_id}:{artifact_id} in Maven Central"
                }
            }
        
        # Check if input version is a date-based version
        major, minor, patch = version_tuple
        is_input_date_based = False
        if 1900 <= major <= 2100:
            is_input_date_based = True
            logger.info(f"Detected input version {version_tuple} as date-based")
        
        # Handle date-based versions
        if is_input_date_based and date_based_versions:
            # Sort date versions by numeric value (descending)
            sorted_dates = sorted(date_based_versions, key=lambda x: x[0], reverse=True)
            return {
                "status": "success",
                "result": {
                    "latest_version": sorted_dates[0][1]
                }
            }
        
        # Normal semver processing
        filtered_versions = []
        if target_component == "major":
            # For major, return highest major version
            filtered_versions = versions
        elif target_component == "minor":
            # For minor, find versions with matching major
            filtered_versions = [v for v in versions if v[0][0] == major]
            # Fall back to all versions if no match
            if not filtered_versions:
                filtered_versions = versions
        elif target_component == "patch":
            # For patch, find versions with matching major.minor
            filtered_versions = [v for v in versions if v[0][0] == major and v[0][1] == minor]
            # Fall back to versions with matching major
            if not filtered_versions:
                filtered_versions = [v for v in versions if v[0][0] == major]
                # Fall back to all versions if still no match
                if not filtered_versions:
                    filtered_versions = versions
        
        if not filtered_versions:
            # If no matching versions, try date-based as fallback
            if date_based_versions:
                sorted_dates = sorted(date_based_versions, key=lambda x: x[0], reverse=True)
                return {
                    "status": "success",
                    "result": {
                        "latest_version": sorted_dates[0][1]
                    }
                }
            else:
                return {
                    "status": "error",
                    "error": {
                        "message": f"No versions matching the criteria found for {group_id}:{artifact_id}"
                    }
                }
        
        # Sort based on target component
        if target_component == "major":
            # Sort by major (descending)
            sorted_versions = sorted(filtered_versions, key=lambda x: x[0][0], reverse=True)
        elif target_component == "minor":
            # Sort by minor (descending) within same major
            sorted_versions = sorted(filtered_versions, key=lambda x: (x[0][1], x[0][2]), reverse=True)
        else:  # patch
            # Sort by patch (descending) within same major.minor
            sorted_versions = sorted(filtered_versions, key=lambda x: x[0][2], reverse=True)
        
        return {
            "status": "success",
            "result": {
                "latest_version": sorted_versions[0][1]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in _get_latest_component_version: {str(e)}")
        return {
            "status": "error",
            "error": {
                "message": f"Unexpected error: {str(e)}"
            }
        }


