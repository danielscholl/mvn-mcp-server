"""Tests for the Maven latest version retrieval tool.

This module tests the latest_version tool which has been refactored to use
the shared service layer.
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp.server.fastmcp.exceptions import ValidationError, ResourceError, ToolError

from maven_mcp_server.tools.check_version import latest_version
from maven_mcp_server.services.maven_api import MavenApiService
from maven_mcp_server.services.response import format_success_response


class TestLatestVersionRefactored:
    """Tests for the refactored latest_version function."""
    
    @patch.object(MavenApiService, 'get_latest_version')
    def test_successful_retrieval(self, mock_get_latest):
        """Test a successful latest version retrieval."""
        mock_get_latest.return_value = "5.3.11"
        
        result = latest_version(
            "org.springframework:spring-core"
        )
        
        expected_result = format_success_response("latest_version", {"latest_version": "5.3.11"})
        assert result == expected_result
        mock_get_latest.assert_called_once_with(
            "org.springframework", 
            "spring-core",
            "jar",
            None
        )
    
    @patch.object(MavenApiService, 'get_latest_version')
    def test_with_custom_packaging(self, mock_get_latest):
        """Test with a custom packaging type."""
        mock_get_latest.return_value = "5.3.11"
        
        result = latest_version(
            "org.springframework:spring-core",
            "war"
        )
        
        expected_result = format_success_response("latest_version", {"latest_version": "5.3.11"})
        assert result == expected_result
        mock_get_latest.assert_called_once_with(
            "org.springframework", 
            "spring-core",
            "war",
            None
        )
    
    @patch.object(MavenApiService, 'get_latest_version')
    def test_with_classifier(self, mock_get_latest):
        """Test with a classifier."""
        mock_get_latest.return_value = "5.3.11"
        
        result = latest_version(
            "org.springframework:spring-core",
            "jar",
            "sources"
        )
        
        expected_result = format_success_response("latest_version", {"latest_version": "5.3.11"})
        assert result == expected_result
        mock_get_latest.assert_called_once_with(
            "org.springframework", 
            "spring-core",
            "jar",
            "sources"
        )
    
    @patch.object(MavenApiService, 'get_latest_version')
    def test_with_bom_dependency(self, mock_get_latest):
        """Test with a BOM dependency."""
        mock_get_latest.return_value = "5.3.11"
        
        result = latest_version(
            "org.springframework:spring-bom"
        )
        
        expected_result = format_success_response("latest_version", {"latest_version": "5.3.11"})
        assert result == expected_result
        # Should use "pom" packaging automatically for BOMs
        mock_get_latest.assert_called_once_with(
            "org.springframework", 
            "spring-bom",
            "pom",  # BOM packaging should be automatically converted to POM
            None
        )
    
    def test_invalid_dependency_format(self):
        """Test with an invalid dependency format."""
        with pytest.raises(ValidationError):
            latest_version(
                "org.springframework.spring-core"  # Invalid format
            )
    
    @patch.object(MavenApiService, 'get_latest_version')
    def test_resource_error(self, mock_get_latest):
        """Test handling of ResourceError."""
        mock_get_latest.side_effect = ResourceError("API error")
        
        with pytest.raises(ResourceError):
            latest_version(
                "org.springframework:spring-core"
            )
    
    @patch.object(MavenApiService, 'get_latest_version')
    def test_unexpected_exception(self, mock_get_latest):
        """Test handling of unexpected exceptions."""
        mock_get_latest.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ToolError):
            latest_version(
                "org.springframework:spring-core"
            )