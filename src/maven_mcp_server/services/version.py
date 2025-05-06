"""Version service for Maven MCP Server.

This module provides a unified approach to version parsing, comparison,
and filtering based on semantic versioning principles.
"""

import re
import logging
import functools
from typing import List, Tuple, Dict, Any, Optional, Callable

# Set up logging
logger = logging.getLogger("maven-mcp-server")

class VersionService:
    """Service for handling Maven version parsing, comparison, and filtering.
    
    This service centralizes all version-related logic, providing a consistent
    approach to working with various version formats.
    """
    
    @staticmethod
    def parse_version(version_string: str) -> Tuple[List[int], str]:
        """Parse a version string into numeric components and qualifier.
        
        Supports multiple version formats:
        - Standard semver (MAJOR.MINOR.PATCH)
        - Calendar format (20231013)
        - Simple numeric (5)
        - Partial semver (1.0)
        
        Args:
            version_string: Version string to parse
            
        Returns:
            Tuple of (numeric_components, qualifier)
            where numeric_components is a list of integers
            and qualifier is the non-numeric suffix (if any)
        """
        if not version_string:
            return [], ""
            
        # Handle qualifier separately
        qualifier = ""
        base_version = version_string
        
        # Extract qualifier if present (e.g., "1.2.3-SNAPSHOT" -> "1.2.3", "SNAPSHOT")
        if "-" in version_string:
            base_version, qualifier = version_string.split("-", 1)
            qualifier = f"-{qualifier}"  # Preserve the hyphen for comparison
        elif "." in version_string and not version_string.replace(".", "").isdigit():
            # Handle format like "1.2.3.Final"
            parts = version_string.split(".")
            for i, part in enumerate(parts):
                if not part.isdigit():
                    base_version = ".".join(parts[:i])
                    qualifier = f".{'.'.join(parts[i:])}"
                    break
        
        # Standard semver pattern (MAJOR.MINOR.PATCH)
        semver_match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', base_version)
        if semver_match:
            major, minor, patch = map(int, semver_match.groups())
            return [major, minor, patch], qualifier
        
        # Partial semver pattern (MAJOR.MINOR)
        partial_match = re.match(r'^(\d+)\.(\d+)$', base_version)
        if partial_match:
            major, minor = map(int, partial_match.groups())
            return [major, minor, 0], qualifier
        
        # Simple numeric pattern (MAJOR)
        simple_match = re.match(r'^(\d+)$', base_version)
        if simple_match:
            major = int(simple_match.group(1))
            
            # Special case for calendar versions (YYYYMMDD)
            if len(base_version) == 8 and 1900 <= int(base_version[:4]) <= 2100:
                try:
                    year = int(base_version[:4])
                    month = int(base_version[4:6])
                    day = int(base_version[6:8])
                    # Validate that it looks like a real date
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        # Return the date components
                        logger.debug(f"Parsed calendar version {version_string} as {year}.{month}.{day}")
                        return [year, month, day], qualifier
                except (ValueError, IndexError):
                    pass
                    
            return [major, 0, 0], qualifier
        
        # Try to extract any numeric parts
        components = []
        for part in base_version.split('.'):
            if part.isdigit():
                components.append(int(part))
            else:
                break
                
        if not components:
            logger.warning(f"Could not parse any numeric components from version: {version_string}")
            return [0, 0, 0], version_string
        
        # Pad with zeros to ensure at least [major, minor, patch]
        while len(components) < 3:
            components.append(0)
            
        return components, qualifier
    
    @staticmethod
    def compare_versions(version1: str, version2: str) -> int:
        """Compare two version strings semantically.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2
            0 if version1 == version2
            1 if version1 > version2
        """
        # Handle None or empty input
        if not version1 and version2:
            return -1
        if version1 and not version2:
            return 1
        if not version1 and not version2:
            return 0
            
        # Parse version components
        v1_numeric, v1_qualifier = VersionService.parse_version(version1)
        v2_numeric, v2_qualifier = VersionService.parse_version(version2)
        
        # Compare numeric parts first
        for c1, c2 in zip(v1_numeric, v2_numeric):
            if c1 < c2:
                return -1
            if c1 > c2:
                return 1
        
        # If one version has more numeric components, it's usually newer
        if len(v1_numeric) < len(v2_numeric):
            return -1
        if len(v1_numeric) > len(v2_numeric):
            return 1
        
        # Finally, compare qualifiers
        # Special case for ".Final" which should be treated higher than no qualifier
        if v1_qualifier.lower() == ".final" and not v2_qualifier:
            return 1
        if v2_qualifier.lower() == ".final" and not v1_qualifier:
            return -1
            
        # No qualifier is considered higher than any qualifier (except .Final)
        if not v1_qualifier and v2_qualifier:
            return 1
        if v1_qualifier and not v2_qualifier:
            return -1
        
        # Handle special qualifiers with known rankings
        qualifier_ranks = {
            "final": 100,
            "release": 90,
            "ga": 80,
            "": 70,  # No qualifier is high but below explicit final/release
            "rc": 60,
            "cr": 50,
            "beta": 40,
            "alpha": 30,
            "snapshot": 10
        }
        
        # Extract main qualifier type
        v1_type = v1_qualifier.lower().replace("-", "").replace(".", "")
        v2_type = v2_qualifier.lower().replace("-", "").replace(".", "")
        
        # Try to match known qualifier types
        v1_rank = 0
        v2_rank = 0
        
        for q_type, rank in qualifier_ranks.items():
            if q_type in v1_type:
                v1_rank = max(v1_rank, rank)
            if q_type in v2_type:
                v2_rank = max(v2_rank, rank)
        
        if v1_rank != v2_rank:
            return 1 if v1_rank > v2_rank else -1
        
        # Default lexicographical comparison for qualifiers with same rank
        if v1_qualifier < v2_qualifier:
            return -1
        if v1_qualifier > v2_qualifier:
            return 1
        
        # Versions are equal
        return 0
    
    @staticmethod
    def filter_versions(
        versions: List[str], 
        target_component: str, 
        reference_version: str
    ) -> List[str]:
        """Filter versions based on target component (major, minor, patch).
        
        Args:
            versions: List of version strings to filter
            target_component: Component to filter by ("major", "minor", or "patch")
            reference_version: Reference version to compare against
            
        Returns:
            Filtered list of version strings
            
        Raises:
            ValueError: If target_component is invalid
        """
        if target_component not in ["major", "minor", "patch"]:
            raise ValueError(f"Invalid target_component: {target_component}. Must be one of 'major', 'minor', or 'patch'")
        
        # Parse reference version
        ref_components, _ = VersionService.parse_version(reference_version)
        
        # Ensure ref_components has at least 3 elements
        while len(ref_components) < 3:
            ref_components.append(0)
            
        ref_major, ref_minor, ref_patch = ref_components[:3]
        
        # Remove snapshot, alpha, beta, rc versions
        filtered_versions = []
        for version in versions:
            lower_version = version.lower()
            # Skip pre-release versions
            if any(qualifier in lower_version for qualifier in ["snapshot", "alpha", "beta", "rc", "-m", ".m"]):
                continue
            filtered_versions.append(version)
            
        # Filter based on target component
        component_filtered = []
        
        if target_component == "major":
            # For major, just use all stable versions
            component_filtered = filtered_versions
        elif target_component == "minor":
            # For minor, filter versions matching the major component
            component_filtered = [
                v for v in filtered_versions 
                if VersionService.parse_version(v)[0][0] == ref_major
            ]
        elif target_component == "patch":
            # For patch, filter versions matching the major.minor components
            component_filtered = [
                v for v in filtered_versions 
                if (
                    VersionService.parse_version(v)[0][0] == ref_major and 
                    VersionService.parse_version(v)[0][1] == ref_minor
                )
            ]
        
        # If no versions match the filter, fall back based on the target component
        if not component_filtered:
            if target_component == "patch":
                # Fall back to minor if patch filter returned no results
                logger.debug(f"No versions match patch filter, falling back to minor")
                return VersionService.filter_versions(versions, "minor", reference_version)
            elif target_component == "minor":
                # Fall back to all versions if minor filter returned no results
                logger.debug(f"No versions match minor filter, falling back to major")
                return VersionService.filter_versions(versions, "major", reference_version)
                
        return component_filtered
    
    @staticmethod
    def get_latest_version(versions: List[str], include_snapshots: bool = False) -> str:
        """Find the latest version from a list of versions.
        
        Args:
            versions: List of version strings
            include_snapshots: Whether to include SNAPSHOT versions
            
        Returns:
            The latest version string
            
        Raises:
            ValueError: If no valid versions are found
        """
        if not versions:
            raise ValueError("No versions provided")
            
        # Special handling for '.Final' versions which should be prioritized
        final_versions = [v for v in versions if ".Final" in v]
        if final_versions:
            return final_versions[0]
        
        # Filter out SNAPSHOT versions if needed
        filtered_versions = versions
        if not include_snapshots:
            filtered_versions = [v for v in versions if "snapshot" not in v.lower()]
            
            # If filtering removed all versions, fall back to original list
            if not filtered_versions and versions:
                filtered_versions = versions
        
        # Sort versions using semantic versioning comparison
        def version_comparator(v1, v2):
            return VersionService.compare_versions(v1, v2)
        
        sorted_versions = sorted(
            filtered_versions, 
            key=functools.cmp_to_key(version_comparator), 
            reverse=True
        )
        
        return sorted_versions[0] if sorted_versions else ""
    
    @staticmethod
    def is_date_based_version(version: str) -> bool:
        """Check if a version appears to be date-based (YYYYMMDD format).
        
        Args:
            version: Version string to check
            
        Returns:
            True if version appears to be date-based, False otherwise
        """
        if not version or not version.isdigit() or len(version) != 8:
            return False
            
        try:
            year = int(version[:4])
            month = int(version[4:6])
            day = int(version[6:8])
            # Check for valid date range
            return (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31)
        except (ValueError, IndexError):
            return False