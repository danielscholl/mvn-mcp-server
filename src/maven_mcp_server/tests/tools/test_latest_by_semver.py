"""Tests for the Maven latest component version finder tool.

This module tests the find_version tool which has been refactored to use
the shared service layer.
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp.server.fastmcp.exceptions import ValidationError, ResourceError, ToolError

from maven_mcp_server.tools.latest_by_semver import find_version
from maven_mcp_server.services.maven_api import MavenApiService
from maven_mcp_server.services.version import VersionService
from maven_mcp_server.services.response import format_success_response


class TestFindVersionRefactored:
    """Tests for the refactored find_version function."""
    
    @patch.object(MavenApiService, 'get_all_versions')
    @patch.object(VersionService, 'filter_versions')
    @patch.object(VersionService, 'get_latest_version')
    def test_successful_major_version_find(self, mock_get_latest, mock_filter, mock_get_all):
        """Test a successful major version find."""
        # Setup mocks
        mock_get_all.return_value = ["5.0.0", "5.1.0", "5.2.0", "6.0.0", "6.0.1"]
        mock_filter.return_value = ["5.0.0", "5.1.0", "5.2.0", "6.0.0", "6.0.1"]
        mock_get_latest.return_value = "6.0.1"
        
        # Call the function
        result = find_version(
            "org.springframework:spring-core",
            "5.0.0",
            "major"
        )
        
        # Verify the result
        expected_result = format_success_response("find_version", {"latest_version": "6.0.1"})
        assert result == expected_result
        
        # Verify mock calls
        mock_get_all.assert_called_once_with("org.springframework", "spring-core")
        mock_filter.assert_called_once_with(
            ["5.0.0", "5.1.0", "5.2.0", "6.0.0", "6.0.1"],
            "major",
            "5.0.0"
        )
        mock_get_latest.assert_called_once_with(
            ["5.0.0", "5.1.0", "5.2.0", "6.0.0", "6.0.1"]
        )
    
    @patch.object(MavenApiService, 'get_all_versions')
    @patch.object(VersionService, 'filter_versions')
    @patch.object(VersionService, 'get_latest_version')
    def test_successful_minor_version_find(self, mock_get_latest, mock_filter, mock_get_all):
        """Test a successful minor version find."""
        # Setup mocks
        mock_get_all.return_value = ["5.0.0", "5.1.0", "5.2.0", "6.0.0", "6.0.1"]
        mock_filter.return_value = ["5.0.0", "5.1.0", "5.2.0"]
        mock_get_latest.return_value = "5.2.0"
        
        # Call the function
        result = find_version(
            "org.springframework:spring-core",
            "5.0.0",
            "minor"
        )
        
        # Verify the result
        expected_result = format_success_response("find_version", {"latest_version": "5.2.0"})
        assert result == expected_result
        
        # Verify mock calls
        mock_get_all.assert_called_once_with("org.springframework", "spring-core")
        mock_filter.assert_called_once_with(
            ["5.0.0", "5.1.0", "5.2.0", "6.0.0", "6.0.1"],
            "minor",
            "5.0.0"
        )
        mock_get_latest.assert_called_once_with(
            ["5.0.0", "5.1.0", "5.2.0"]
        )
    
    @patch.object(MavenApiService, 'get_all_versions')
    @patch.object(VersionService, 'filter_versions')
    @patch.object(VersionService, 'get_latest_version')
    def test_successful_patch_version_find(self, mock_get_latest, mock_filter, mock_get_all):
        """Test a successful patch version find."""
        # Setup mocks
        mock_get_all.return_value = ["5.0.0", "5.0.1", "5.0.2", "5.1.0"]
        mock_filter.return_value = ["5.0.0", "5.0.1", "5.0.2"]
        mock_get_latest.return_value = "5.0.2"
        
        # Call the function
        result = find_version(
            "org.springframework:spring-core",
            "5.0.0",
            "patch"
        )
        
        # Verify the result
        expected_result = format_success_response("find_version", {"latest_version": "5.0.2"})
        assert result == expected_result
        
        # Verify mock calls
        mock_get_all.assert_called_once_with("org.springframework", "spring-core")
        mock_filter.assert_called_once_with(
            ["5.0.0", "5.0.1", "5.0.2", "5.1.0"],
            "patch",
            "5.0.0"
        )
        mock_get_latest.assert_called_once_with(
            ["5.0.0", "5.0.1", "5.0.2"]
        )
    
    @patch.object(MavenApiService, 'get_all_versions')
    @patch.object(VersionService, 'filter_versions')
    @patch.object(VersionService, 'get_latest_version')
    def test_with_custom_packaging(self, mock_get_latest, mock_filter, mock_get_all):
        """Test with custom packaging."""
        # Setup mocks
        mock_get_all.return_value = ["5.0.0", "5.1.0"]
        mock_filter.return_value = ["5.0.0", "5.1.0"]
        mock_get_latest.return_value = "5.1.0"
        
        # Call the function
        result = find_version(
            "org.springframework:spring-core",
            "5.0.0",
            "major",
            "war"
        )
        
        # Verify the result
        expected_result = format_success_response("find_version", {"latest_version": "5.1.0"})
        assert result == expected_result
    
    @patch.object(MavenApiService, 'get_all_versions')
    @patch.object(VersionService, 'filter_versions')
    @patch.object(VersionService, 'get_latest_version')
    @patch.object(MavenApiService, 'check_artifact_exists')
    def test_with_classifier(self, mock_check, mock_get_latest, mock_filter, mock_get_all):
        """Test with classifier."""
        # Setup mocks
        mock_get_all.return_value = ["5.0.0", "5.1.0"]
        mock_filter.return_value = ["5.0.0", "5.1.0"]
        mock_get_latest.return_value = "5.1.0"
        mock_check.return_value = True
        
        # Call the function
        result = find_version(
            "org.springframework:spring-core",
            "5.0.0",
            "major",
            "jar",
            "sources"
        )
        
        # Verify the result
        expected_result = format_success_response("find_version", {"latest_version": "5.1.0"})
        assert result == expected_result
    
    @patch.object(MavenApiService, 'get_all_versions')
    @patch.object(VersionService, 'filter_versions')
    @patch.object(VersionService, 'get_latest_version')
    @patch.object(MavenApiService, 'check_artifact_exists')
    def test_with_classifier_fallback(self, mock_check, mock_get_latest, mock_filter, mock_get_all):
        """Test when classifier is not available in latest version."""
        # Setup mocks
        mock_get_all.return_value = ["5.0.0", "5.1.0"]
        mock_filter.return_value = ["5.0.0", "5.1.0"]
        mock_get_latest.return_value = "5.1.0"
        
        # First check fails, second check passes
        mock_check.side_effect = [False, True]
        
        # Call the function
        result = find_version(
            "org.springframework:spring-core",
            "5.0.0",
            "major",
            "jar",
            "sources"
        )
        
        # Verify the result
        expected_result = format_success_response("find_version", {"latest_version": "5.0.0"})
        assert result == expected_result
    
    def test_invalid_dependency_format(self):
        """Test with an invalid dependency format."""
        with pytest.raises(ValidationError):
            find_version(
                "org.springframework.spring-core",  # Invalid format
                "5.0.0",
                "major"
            )
    
    def test_invalid_target_component(self):
        """Test with an invalid target component."""
        with pytest.raises(ValidationError):
            find_version(
                "org.springframework:spring-core",
                "5.0.0",
                "invalid"  # Invalid component
            )
    
    @patch.object(MavenApiService, 'get_all_versions')
    def test_nonexistent_dependency(self, mock_get_all):
        """Test with a non-existent dependency."""
        with pytest.raises(ResourceError):
            find_version(
                "org.nonexistent:nonexistent-artifact",
                "1.0.0",
                "major"
            )
    
    @patch.object(MavenApiService, 'get_all_versions')
    @patch.object(VersionService, 'filter_versions')
    def test_no_matching_versions(self, mock_filter, mock_get_all):
        """Test when no versions match the filter criteria."""
        # Setup mocks
        mock_get_all.return_value = ["5.0.0", "5.1.0"]
        mock_filter.return_value = []
        
        # Call the function and check exception
        with pytest.raises(ResourceError):
            find_version(
                "org.springframework:spring-core",
                "9.9.9",  # No matching versions
                "patch"
            )