"""Tests for the Maven version existence checking tool.

This module tests the check_version tool and related functions.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock

from mcp.server.fastmcp.exceptions import ValidationError, ResourceError, ToolError

from maven_mcp_server.tools.version_exist import (
    check_version,
    _check_version_exists_in_maven_central,
    _check_version_in_metadata
)


class TestCheckVersion:
    """Tests for the check_version function."""
    
    @patch("maven_mcp_server.tools.version_exist._check_version_exists_in_maven_central")
    def test_successful_check_true(self, mock_check):
        """Test a successful version check that returns True."""
        mock_check.return_value = True
        
        result = check_version(
            "org.springframework:spring-core",
            "5.3.10"
        )
        
        assert result == {"exists": True}
        mock_check.assert_called_once_with(
            "org.springframework", 
            "spring-core", 
            "5.3.10", 
            "jar", 
            None
        )
    
    @patch("maven_mcp_server.tools.version_exist._check_version_exists_in_maven_central")
    def test_successful_check_false(self, mock_check):
        """Test a successful version check that returns False."""
        mock_check.return_value = False
        
        result = check_version(
            "org.springframework:spring-core",
            "999.999.999"  # Non-existent version
        )
        
        assert result == {"exists": False}
    
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
    
    @patch("maven_mcp_server.tools.version_exist._check_version_exists_in_maven_central")
    def test_with_custom_packaging(self, mock_check):
        """Test with a custom packaging type."""
        mock_check.return_value = True
        
        result = check_version(
            "org.springframework:spring-core",
            "5.3.10",
            "war"
        )
        
        assert result == {"exists": True}
        mock_check.assert_called_once_with(
            "org.springframework", 
            "spring-core", 
            "5.3.10", 
            "war", 
            None
        )
    
    @patch("maven_mcp_server.tools.version_exist._check_version_exists_in_maven_central")
    def test_with_classifier(self, mock_check):
        """Test with a classifier."""
        mock_check.return_value = True
        
        result = check_version(
            "org.springframework:spring-core",
            "5.3.10",
            "jar",
            "sources"
        )
        
        assert result == {"exists": True}
        mock_check.assert_called_once_with(
            "org.springframework", 
            "spring-core", 
            "5.3.10", 
            "jar", 
            "sources"
        )
    
    @patch("maven_mcp_server.tools.version_exist._check_version_exists_in_maven_central")
    def test_with_bom_dependency(self, mock_check):
        """Test with a BOM dependency."""
        mock_check.return_value = True
        
        result = check_version(
            "org.springframework:spring-bom",
            "5.3.10"
        )
        
        assert result == {"exists": True}
        # Should use "pom" packaging automatically
        mock_check.assert_called_once_with(
            "org.springframework", 
            "spring-bom", 
            "5.3.10", 
            "pom", 
            None
        )
    
    @patch("maven_mcp_server.tools.version_exist._check_version_exists_in_maven_central")
    def test_request_exception(self, mock_check):
        """Test handling of request exceptions."""
        mock_check.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(ResourceError):
            check_version(
                "org.springframework:spring-core",
                "5.3.10"
            )
    
    @patch("maven_mcp_server.tools.version_exist._check_version_exists_in_maven_central")
    def test_unexpected_exception(self, mock_check):
        """Test handling of unexpected exceptions."""
        mock_check.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ToolError):
            check_version(
                "org.springframework:spring-core",
                "5.3.10"
            )


class TestCheckVersionExistsInMavenCentral:
    """Tests for the _check_version_exists_in_maven_central function."""
    
    @patch("requests.head")
    def test_direct_file_exists(self, mock_head):
        """Test when the file directly exists in Maven Central."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response
        
        result = _check_version_exists_in_maven_central(
            "org.springframework", 
            "spring-core", 
            "5.3.10", 
            "jar"
        )
        
        assert result is True
        mock_head.assert_called_once()
    
    @patch("requests.head")
    @patch("maven_mcp_server.tools.version_exist._check_version_in_metadata")
    def test_fallback_to_metadata(self, mock_check_metadata, mock_head):
        """Test fallback to metadata check when direct file check fails."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_head.return_value = mock_response
        
        mock_check_metadata.return_value = True
        
        result = _check_version_exists_in_maven_central(
            "org.springframework", 
            "spring-core", 
            "5.3.10", 
            "jar"
        )
        
        assert result is True
        mock_head.assert_called_once()
        mock_check_metadata.assert_called_once_with(
            "org.springframework", 
            "spring-core", 
            "5.3.10"
        )
    
    @patch("requests.head")
    def test_request_exception(self, mock_head):
        """Test handling of request exceptions."""
        mock_head.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(ResourceError):
            _check_version_exists_in_maven_central(
                "org.springframework", 
                "spring-core", 
                "5.3.10", 
                "jar"
            )


class TestCheckVersionInMetadata:
    """Tests for the _check_version_in_metadata function."""
    
    @patch("requests.get")
    def test_version_in_metadata(self, mock_get):
        """Test when the version is found in the metadata."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <metadata>
            <groupId>org.springframework</groupId>
            <artifactId>spring-core</artifactId>
            <versioning>
                <versions>
                    <version>5.3.9</version>
                    <version>5.3.10</version>
                    <version>5.3.11</version>
                </versions>
            </versioning>
        </metadata>
        """
        mock_get.return_value = mock_response
        
        result = _check_version_in_metadata(
            "org.springframework", 
            "spring-core", 
            "5.3.10"
        )
        
        assert result is True
    
    @patch("requests.get")
    def test_version_not_in_metadata(self, mock_get):
        """Test when the version is not found in the metadata."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <metadata>
            <groupId>org.springframework</groupId>
            <artifactId>spring-core</artifactId>
            <versioning>
                <versions>
                    <version>5.3.9</version>
                    <version>5.3.11</version>
                </versions>
            </versioning>
        </metadata>
        """
        mock_get.return_value = mock_response
        
        result = _check_version_in_metadata(
            "org.springframework", 
            "spring-core", 
            "5.3.10"
        )
        
        assert result is False
    
    @patch("requests.get")
    def test_dependency_not_found(self, mock_get):
        """Test when the dependency is not found (404 response)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(ResourceError):
            _check_version_in_metadata(
                "org.nonexistent", 
                "nonexistent-artifact", 
                "1.0.0"
            )
    
    @patch("requests.get")
    def test_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        mock_get.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(ResourceError):
            _check_version_in_metadata(
                "org.springframework", 
                "spring-core", 
                "5.3.10"
            )