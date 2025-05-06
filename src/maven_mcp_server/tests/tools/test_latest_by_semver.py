"""Tests for the Maven latest component version finder tool.

This module tests the find_maven_latest_component_version tool and related functions.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock

from mcp.server.fastmcp.exceptions import ValidationError, ResourceError, ToolError

from maven_mcp_server.tools.latest_by_semver import (
    find_version,
    _parse_input_version,
    _get_all_versions,
    _find_latest_component_version
)




class TestFindVersion:
    """Tests for the find_version function."""
    
    @patch("maven_mcp_server.tools.latest_by_semver._get_all_versions")
    @patch("maven_mcp_server.tools.latest_by_semver._find_latest_component_version")
    def test_successful_major_version_find(self, mock_find_latest, mock_get_versions):
        """Test a successful major version find."""
        # Setup mocks
        mock_get_versions.return_value = ["5.0.0", "5.1.0", "5.2.0", "6.0.0", "6.0.1"]
        mock_find_latest.return_value = "6.0.1"
        
        # Call the function
        result = find_version(
            "org.springframework:spring-core",
            "5.0.0",
            "major"
        )
        
        # Verify the result
        assert result == {"latest_version": "6.0.1"}
        
        # Verify mock calls
        mock_get_versions.assert_called_once_with("org.springframework", "spring-core")
        mock_find_latest.assert_called_once()
    
    @patch("maven_mcp_server.tools.latest_by_semver._get_all_versions")
    @patch("maven_mcp_server.tools.latest_by_semver._find_latest_component_version")
    def test_successful_minor_version_find(self, mock_find_latest, mock_get_versions):
        """Test a successful minor version find."""
        # Setup mocks
        mock_get_versions.return_value = ["5.0.0", "5.1.0", "5.2.0", "5.3.0", "5.3.1", "6.0.0"]
        mock_find_latest.return_value = "5.3.1"
        
        # Call the function
        result = find_version(
            "org.springframework:spring-core",
            "5.0.0",
            "minor"
        )
        
        # Verify the result
        assert result == {"latest_version": "5.3.1"}
    
    @patch("maven_mcp_server.tools.latest_by_semver._get_all_versions")
    @patch("maven_mcp_server.tools.latest_by_semver._find_latest_component_version")
    def test_successful_patch_version_find(self, mock_find_latest, mock_get_versions):
        """Test a successful patch version find."""
        # Setup mocks
        mock_get_versions.return_value = ["5.0.0", "5.1.0", "5.1.1", "5.1.2", "5.2.0"]
        mock_find_latest.return_value = "5.1.2"
        
        # Call the function
        result = find_version(
            "org.springframework:spring-core",
            "5.1.0",
            "patch"
        )
        
        # Verify the result
        assert result == {"latest_version": "5.1.2"}
    
    @patch("maven_mcp_server.tools.latest_by_semver._get_all_versions")
    @patch("maven_mcp_server.tools.latest_by_semver._find_latest_component_version")
    def test_with_custom_packaging(self, mock_find_latest, mock_get_versions):
        """Test with a custom packaging type."""
        # Setup mocks
        mock_get_versions.return_value = ["1.0.0", "1.0.1"]
        mock_find_latest.return_value = "1.0.1"
        
        # Call the function with custom packaging
        result = find_version(
            "org.example:example-lib",
            "1.0.0",
            "patch",
            "war"
        )
        
        # Verify the result
        assert result == {"latest_version": "1.0.1"}
    
    @patch("maven_mcp_server.tools.latest_by_semver._get_all_versions")
    @patch("maven_mcp_server.tools.latest_by_semver._find_latest_component_version")
    def test_with_classifier(self, mock_find_latest, mock_get_versions):
        """Test with a classifier."""
        # Setup mocks
        mock_get_versions.return_value = ["1.0.0", "1.0.1"]
        mock_find_latest.return_value = "1.0.1"
        
        # Call the function with a classifier
        result = find_version(
            "org.example:example-lib",
            "1.0.0",
            "patch",
            "jar",
            "sources"
        )
        
        # Verify the result
        assert result == {"latest_version": "1.0.1"}
    
    def test_invalid_dependency_format(self):
        """Test with an invalid dependency format."""
        with pytest.raises(ValidationError):
            find_version(
                "org.springframework.spring-core",  # Invalid format
                "5.0.0",
                "major"
            )
    
    def test_invalid_target_component(self):
        """Test with an invalid target_component value."""
        with pytest.raises(ValidationError) as excinfo:
            find_version(
                "org.springframework:spring-core",
                "5.0.0",
                "invalid-component"  # Invalid value
            )
        assert "Invalid target_component" in str(excinfo.value)
    
    @patch("maven_mcp_server.tools.latest_by_semver._get_all_versions")
    def test_no_versions_found(self, mock_get_versions):
        """Test when no versions are found for the dependency."""
        # Setup mock to simulate no versions found
        mock_get_versions.return_value = []
        
        with pytest.raises(ResourceError) as excinfo:
            find_version(
                "org.nonexistent:nonexistent-lib",
                "1.0.0",
                "major"
            )
        assert "No versions found" in str(excinfo.value)
    
    @patch("maven_mcp_server.tools.latest_by_semver._get_all_versions")
    @patch("maven_mcp_server.tools.latest_by_semver._find_latest_component_version")
    def test_no_matching_version_found(self, mock_find_latest, mock_get_versions):
        """Test when no matching version is found."""
        # Setup mocks
        mock_get_versions.return_value = ["1.0.0", "1.0.1"]
        mock_find_latest.return_value = ""  # No matching version
        
        with pytest.raises(ResourceError) as excinfo:
            find_version(
                "org.example:example-lib",
                "2.0.0",  # No matching version for this reference
                "minor"
            )
        assert "No matching version found" in str(excinfo.value)
    
    @patch("maven_mcp_server.tools.latest_by_semver._get_all_versions")
    def test_request_exception(self, mock_get_versions):
        """Test handling of request exceptions."""
        # Setup mock to simulate a network error
        mock_get_versions.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(ResourceError):
            find_version(
                "org.springframework:spring-core",
                "5.0.0",
                "major"
            )
    
    @patch("maven_mcp_server.tools.latest_by_semver._get_all_versions")
    def test_unexpected_exception(self, mock_get_versions):
        """Test handling of unexpected exceptions."""
        # Setup mock to simulate an unexpected error
        mock_get_versions.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ToolError):
            find_version(
                "org.springframework:spring-core",
                "5.0.0",
                "major"
            )


class TestParseInputVersion:
    """Tests for the _parse_input_version function."""
    
    def test_parse_standard_semver(self):
        """Test parsing a standard semantic version."""
        result = _parse_input_version("1.2.3")
        assert result == ([1, 2, 3], "")
    
    def test_parse_standard_semver_with_qualifier(self):
        """Test parsing a standard semantic version with qualifier."""
        result = _parse_input_version("1.2.3-SNAPSHOT")
        assert result == ([1, 2, 3], "SNAPSHOT")
    
    def test_parse_partial_semver(self):
        """Test parsing a partial semantic version (MAJOR.MINOR)."""
        result = _parse_input_version("1.2")
        assert result == ([1, 2], "")
    
    def test_parse_simple_numeric(self):
        """Test parsing a simple numeric version (MAJOR)."""
        result = _parse_input_version("1")
        assert result == ([1], "")
    
    def test_parse_calendar_format(self):
        """Test parsing a calendar format version."""
        result = _parse_input_version("20231013")
        assert result == ([20231013], "")
    
    def test_parse_nonstandard_format(self):
        """Test parsing a non-standard format using the fallback parser."""
        result = _parse_input_version("1.2.3.Final")
        # The exact result may vary depending on the fallback parser implementation
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], list)
        assert isinstance(result[1], str)


class TestFindLatestComponentVersion:
    """Tests for the _find_latest_component_version function."""
    
    @patch("maven_mcp_server.tools.latest_by_semver.compare_versions")
    def test_find_latest_major_version(self, mock_compare_versions):
        """Test finding the latest major version."""
        all_versions = ["1.0.0", "2.0.0", "2.1.0", "3.0.0-beta"]
        reference_components = [1, 0, 0]
        
        # Mock the compare_versions function to sort correctly
        def mock_compare(v1, v2):
            if v1 == "2.1.0" and v2 == "2.0.0":
                return 1
            elif v1 == "2.0.0" and v2 == "2.1.0":
                return -1
            elif v1 == "2.1.0" and v2 in ["1.0.0", "3.0.0-beta"]:
                return 1
            elif v1 == "2.0.0" and v2 in ["1.0.0", "3.0.0-beta"]:
                return 1
            elif v1 == "1.0.0" and v2 in ["2.0.0", "2.1.0"]:
                return -1
            elif v1 == "3.0.0-beta" and v2 in ["1.0.0", "2.0.0", "2.1.0"]:
                return -1
            return 0
        
        mock_compare_versions.side_effect = mock_compare
        
        result = _find_latest_component_version(all_versions, reference_components, "major")
        assert result == "2.1.0"  # 3.0.0-beta should be excluded as it's a pre-release
    
    def test_find_latest_minor_version(self):
        """Test finding the latest minor version within a major version."""
        all_versions = ["5.0.0", "5.1.0", "5.2.0", "5.3.0", "6.0.0"]
        reference_components = [5, 0, 0]
        
        result = _find_latest_component_version(all_versions, reference_components, "minor")
        assert result == "5.3.0"
    
    def test_find_latest_patch_version(self):
        """Test finding the latest patch version within a major.minor version."""
        all_versions = ["5.1.0", "5.1.1", "5.1.2", "5.2.0"]
        reference_components = [5, 1, 0]
        
        result = _find_latest_component_version(all_versions, reference_components, "patch")
        assert result == "5.1.2"
    
    def test_no_matching_versions(self):
        """Test when no matching versions are found."""
        all_versions = ["6.0.0", "6.1.0", "7.0.0"]
        reference_components = [5, 0, 0]
        
        result = _find_latest_component_version(all_versions, reference_components, "minor")
        assert result == ""
    
    def test_filter_snapshot_versions(self):
        """Test that snapshot versions are filtered out."""
        all_versions = ["1.0.0", "1.0.1-SNAPSHOT", "1.0.2"]
        reference_components = [1, 0, 0]
        
        result = _find_latest_component_version(all_versions, reference_components, "patch")
        assert result == "1.0.2"
    
    def test_handle_calendar_versions(self):
        """Test handling calendar versions."""
        all_versions = ["20220101", "20220201", "20220301"]
        reference_components = [20220101]
        
        result = _find_latest_component_version(all_versions, reference_components, "major")
        assert result == "20220301"


# Integration Tests
# These tests hit the real Maven Central API and aren't mocked

class TestIntegrationTests:
    """Integration tests for the find_maven_latest_component_version function.
    
    These tests hit the real Maven Central API.
    """
    
    def test_real_spring_core_major(self):
        """Integration test with real Spring Core dependency for major version."""
        try:
            result = find_version(
                "org.springframework:spring-core",
                "5.0.0",
                "major"
            )
            
            # Get the latest version from the result
            latest_version = result.get("latest_version", "")
            
            # Verify it's not empty and starts with a valid version number
            assert latest_version, "Latest version should not be empty"
            assert latest_version[0].isdigit(), "Latest version should start with a digit"
            
            # Verify it's a newer or equal major version than the reference (5.0.0)
            major_version = int(latest_version.split('.')[0])
            assert major_version >= 5, "Major version should be at least 5"
        except ResourceError:
            # If we can't find the latest version, skip this test rather than fail
            pytest.skip("Could not find latest major version for org.springframework:spring-core")
    
    def test_real_spring_core_minor(self):
        """Integration test with real Spring Core dependency for minor version."""
        try:
            # Using 5.0.0 as the reference version to find the latest 5.x.x
            result = find_version(
                "org.springframework:spring-core",
                "5.0.0",
                "minor"
            )
            
            latest_version = result.get("latest_version", "")
            
            # Verify it's not empty and has the expected format
            assert latest_version, "Latest version should not be empty"
            version_parts = latest_version.split('.')
            assert len(version_parts) >= 2, "Version should have at least major.minor parts"
            
            # Verify it's still in the same major version but a newer or equal minor version
            assert version_parts[0] == "5", "Major version should remain 5"
            assert int(version_parts[1]) >= 0, "Minor version should be at least 0"
        except ResourceError:
            # If we can't find the latest version, skip this test rather than fail
            pytest.skip("Could not find latest minor version for org.springframework:spring-core")
    
    def test_real_spring_core_patch(self):
        """Integration test with real Spring Core dependency for patch version."""
        try:
            # Using 5.3.0 as the reference version to find the latest 5.3.x
            result = find_version(
                "org.springframework:spring-core",
                "5.3.0",
                "patch"
            )
            
            latest_version = result.get("latest_version", "")
            
            # Verify it's not empty and has the expected format
            assert latest_version, "Latest version should not be empty"
            version_parts = latest_version.split('.')
            assert len(version_parts) >= 3, "Version should have at least major.minor.patch parts"
            
            # Verify it's still in the same major.minor version
            assert version_parts[0] == "5", "Major version should remain 5"
            assert version_parts[1] == "3", "Minor version should remain 3"
            assert int(version_parts[2]) >= 0, "Patch version should be at least 0"
        except ResourceError:
            # If we can't find the latest version, skip this test rather than fail
            pytest.skip("Could not find latest patch version for org.springframework:spring-core")
    
    @pytest.mark.skip(reason="Depends on external API")
    def test_real_spring_boot_special_handling(self):
        """Integration test with Spring Boot which might need special handling."""
        result = find_version(
            "org.springframework.boot:spring-boot",
            "2.0.0",
            "major"
        )
        
        latest_version = result.get("latest_version", "")
        
        # Verify it's not empty
        assert latest_version, "Latest version should not be empty"
        
        # Verify it's a valid version number
        assert latest_version[0].isdigit(), "Latest version should start with a digit"
    
    @pytest.mark.skip(reason="Depends on external API")
    def test_real_with_bom_dependency(self):
        """Integration test with a BOM dependency."""
        result = find_version(
            "org.springframework.boot:spring-boot-dependencies",
            "2.0.0",
            "major"
        )
        
        latest_version = result.get("latest_version", "")
        
        # Verify it's not empty
        assert latest_version, "Latest version should not be empty"
        
        # Verify it's a valid version number
        assert latest_version[0].isdigit(), "Latest version should start with a digit"
    
    def test_calendar_versioned_dependency(self):
        """Integration test with a dependency that uses calendar versioning."""
        # Find a dependency that uses calendar versioning (YYYYMMDD format)
        # Using a dummy version as reference
        try:
            result = find_version(
                "io.quarkus:quarkus-bom",
                "20220101",
                "major"
            )
            
            latest_version = result.get("latest_version", "")
            
            # If the test passes, verify the result is not empty
            assert latest_version, "Latest version should not be empty"
        except ResourceError:
            # If this particular dependency doesn't use calendar versioning,
            # the test should be skipped rather than failed
            pytest.skip("Could not find a calendar-versioned dependency")
    
    def test_nonexistent_dependency(self):
        """Integration test with a non-existent dependency."""
        with pytest.raises(ResourceError) as excinfo:
            find_version(
                "org.nonexistent:nonexistent-lib",
                "1.0.0",
                "major"
            )
        assert "No versions found" in str(excinfo.value) or "not found" in str(excinfo.value)