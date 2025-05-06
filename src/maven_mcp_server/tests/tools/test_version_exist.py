"""Tests for the Maven version existence checking tool.

This module tests the check_version tool which has been refactored to use 
the shared service layer.
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp.server.fastmcp.exceptions import ValidationError, ResourceError, ToolError

from maven_mcp_server.tools.version_exist import check_version
from maven_mcp_server.services.maven_api import MavenApiService
from maven_mcp_server.services.response import format_success_response


class TestCheckVersionRefactored:
    """Tests for the refactored check_version function."""
    
    @patch.object(MavenApiService, 'check_artifact_exists')
    def test_successful_check_true(self, mock_check):
        """Test a successful version check that returns True."""
        mock_check.return_value = True
        
        result = check_version(
            "org.springframework:spring-core",
            "5.3.10"
        )
        
        expected_result = format_success_response("check_version", {"exists": True})
        assert result == expected_result
        mock_check.assert_called_once_with(
            "org.springframework", 
            "spring-core", 
            "5.3.10", 
            "jar", 
            None
        )
    
    @patch.object(MavenApiService, 'check_artifact_exists')
    def test_successful_check_false(self, mock_check):
        """Test a successful version check that returns False."""
        mock_check.return_value = False
        
        result = check_version(
            "org.springframework:spring-core",
            "999.999.999"  # Non-existent version
        )
        
        expected_result = format_success_response("check_version", {"exists": False})
        assert result == expected_result
    
    def test_invalid_dependency_format(self):
        """Test with an invalid dependency format."""
        with pytest.raises(ValidationError):
            check_version(
                "org.springframework.spring-core",  # Invalid format
                "5.3.10"
            )
    
    def test_invalid_version_format(self):
        """Test with an invalid version format."""
        with pytest.raises(ValidationError):
            check_version(
                "org.springframework:spring-core",
                "invalid-version"  # Invalid format
            )
    
    @patch.object(MavenApiService, 'check_artifact_exists')
    def test_with_custom_packaging(self, mock_check):
        """Test with a custom packaging type."""
        mock_check.return_value = True
        
        result = check_version(
            "org.springframework:spring-core",
            "5.3.10",
            "war"
        )
        
        expected_result = format_success_response("check_version", {"exists": True})
        assert result == expected_result
        mock_check.assert_called_once_with(
            "org.springframework", 
            "spring-core", 
            "5.3.10", 
            "war", 
            None
        )
    
    @patch.object(MavenApiService, 'check_artifact_exists')
    def test_with_classifier(self, mock_check):
        """Test with a classifier."""
        mock_check.return_value = True
        
        result = check_version(
            "org.springframework:spring-core",
            "5.3.10",
            "jar",
            "sources"
        )
        
        expected_result = format_success_response("check_version", {"exists": True})
        assert result == expected_result
        mock_check.assert_called_once_with(
            "org.springframework", 
            "spring-core", 
            "5.3.10", 
            "jar", 
            "sources"
        )
    
    @patch.object(MavenApiService, 'check_artifact_exists')
    def test_with_bom_dependency(self, mock_check):
        """Test with a BOM dependency."""
        mock_check.return_value = True
        
        result = check_version(
            "org.springframework:spring-bom",
            "5.3.10"
        )
        
        expected_result = format_success_response("check_version", {"exists": True})
        assert result == expected_result
        # Should use "pom" packaging automatically
        mock_check.assert_called_once_with(
            "org.springframework", 
            "spring-bom", 
            "5.3.10", 
            "pom", 
            None
        )
    
    @patch.object(MavenApiService, 'check_artifact_exists')
    def test_resource_error(self, mock_check):
        """Test handling of ResourceError."""
        mock_check.side_effect = ResourceError("API error")
        
        with pytest.raises(ResourceError):
            check_version(
                "org.springframework:spring-core",
                "5.3.10"
            )
    
    @patch.object(MavenApiService, 'check_artifact_exists')
    def test_unexpected_exception(self, mock_check):
        """Test handling of unexpected exceptions."""
        mock_check.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ToolError):
            check_version(
                "org.springframework:spring-core",
                "5.3.10"
            )