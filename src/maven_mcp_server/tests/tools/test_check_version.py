"""Tests for the Maven latest version retrieval tool.

This module tests the get_maven_latest_version tool and related functions.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock

from mcp.server.fastmcp.exceptions import ValidationError, ResourceError, ToolError

from maven_mcp_server.tools.check_version import (
    get_maven_latest_version,
    _fetch_all_versions_from_maven_central
)
from maven_mcp_server.shared.utils import (
    parse_version_components,
    compare_versions,
    get_latest_version
)


class TestGetMavenLatestVersion:
    """Tests for the get_maven_latest_version function."""
    
    @patch("maven_mcp_server.tools.check_version._fetch_all_versions_from_maven_central")
    def test_successful_retrieval(self, mock_fetch):
        """Test a successful latest version retrieval."""
        mock_fetch.return_value = ["5.3.9", "5.3.10", "5.3.11"]
        
        result = get_maven_latest_version(
            "org.springframework:spring-core"
        )
        
        assert result == {"latest_version": "5.3.11"}
        mock_fetch.assert_called_once_with(
            "org.springframework", 
            "spring-core"
        )
    
    @patch("maven_mcp_server.tools.check_version._fetch_all_versions_from_maven_central")
    def test_with_snapshot_versions(self, mock_fetch):
        """Test with a mix of regular and snapshot versions."""
        mock_fetch.return_value = ["5.3.9", "5.3.10", "5.3.11", "5.3.12-SNAPSHOT"]
        
        result = get_maven_latest_version(
            "org.springframework:spring-core"
        )
        
        # Should return 5.3.11 as SNAPSHOT versions are filtered by default
        assert result == {"latest_version": "5.3.11"}
    
    def test_invalid_dependency_format(self):
        """Test with an invalid dependency format."""
        with pytest.raises(ValidationError):
            get_maven_latest_version(
                "org.springframework.spring-core"  # Invalid format
            )
    
    @patch("maven_mcp_server.tools.check_version._fetch_all_versions_from_maven_central")
    def test_with_custom_packaging(self, mock_fetch):
        """Test with a custom packaging type."""
        mock_fetch.return_value = ["5.3.9", "5.3.10", "5.3.11"]
        
        result = get_maven_latest_version(
            "org.springframework:spring-core",
            "war"
        )
        
        assert result == {"latest_version": "5.3.11"}
    
    @patch("maven_mcp_server.tools.check_version._fetch_all_versions_from_maven_central")
    @patch("maven_mcp_server.tools.check_version._check_specific_artifact_exists")
    def test_with_classifier(self, mock_check_artifact, mock_fetch):
        """Test with a classifier."""
        mock_fetch.return_value = ["5.3.9", "5.3.10", "5.3.11"]
        
        # Mock that the latest version has the classifier
        mock_check_artifact.return_value = True
        
        result = get_maven_latest_version(
            "org.springframework:spring-core",
            "jar",
            "sources"
        )
        
        assert result == {"latest_version": "5.3.11"}
        mock_check_artifact.assert_called_once_with(
            "org.springframework", 
            "spring-core", 
            "5.3.11", 
            "jar", 
            "sources"
        )
        
    @patch("maven_mcp_server.tools.check_version._fetch_all_versions_from_maven_central")
    @patch("maven_mcp_server.tools.check_version._check_specific_artifact_exists")
    def test_with_classifier_fallback(self, mock_check_artifact, mock_fetch):
        """Test fallback when latest version doesn't have the classifier."""
        mock_fetch.return_value = ["5.3.9", "5.3.10", "5.3.11"]
        
        # Mock that the latest version doesn't have the classifier but an older one does
        mock_check_artifact.side_effect = lambda g, a, v, p, c: v == "5.3.10"
        
        result = get_maven_latest_version(
            "org.springframework:spring-core",
            "jar",
            "sources"
        )
        
        # Should return the older version that has the classifier
        assert result == {"latest_version": "5.3.10"}
    
    @patch("maven_mcp_server.tools.check_version._fetch_all_versions_from_maven_central")
    def test_with_bom_dependency(self, mock_fetch):
        """Test with a BOM dependency."""
        mock_fetch.return_value = ["5.3.9", "5.3.10", "5.3.11"]
        
        result = get_maven_latest_version(
            "org.springframework:spring-bom"
        )
        
        assert result == {"latest_version": "5.3.11"}
        # Should use specific packaging based on artifact ID
        assert mock_fetch.call_args[0][1] == "spring-bom"
    
    @patch("maven_mcp_server.tools.check_version._fetch_all_versions_from_maven_central")
    def test_no_versions_found(self, mock_fetch):
        """Test when no versions are found."""
        mock_fetch.return_value = []
        
        # The exception can be either a ResourceError directly or wrapped in a ToolError
        try:
            get_maven_latest_version(
                "org.springframework:spring-core"
            )
            pytest.fail("Expected exception was not raised")
        except (ResourceError, ToolError) as e:
            # Verify that the exception message contains relevant text
            assert "version" in str(e).lower() or "dependency" in str(e).lower()
    
    @patch("maven_mcp_server.tools.check_version._fetch_all_versions_from_maven_central")
    def test_request_exception(self, mock_fetch):
        """Test handling of request exceptions."""
        mock_fetch.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(ResourceError):
            get_maven_latest_version(
                "org.springframework:spring-core"
            )
    
    @patch("maven_mcp_server.tools.check_version._fetch_all_versions_from_maven_central")
    def test_unexpected_exception(self, mock_fetch):
        """Test handling of unexpected exceptions."""
        mock_fetch.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ToolError):
            get_maven_latest_version(
                "org.springframework:spring-core"
            )


class TestFetchAllVersionsFromMavenCentral:
    """Tests for the _fetch_all_versions_from_maven_central function."""
    
    @patch("requests.get")
    def test_successful_fetch(self, mock_get):
        """Test successfully fetching all versions."""
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
        
        versions = _fetch_all_versions_from_maven_central(
            "org.springframework", 
            "spring-core"
        )
        
        assert versions == ["5.3.9", "5.3.10", "5.3.11"]
        mock_get.assert_called_once()
    
    @patch("requests.get")
    def test_dependency_not_found(self, mock_get):
        """Test when the dependency is not found (404 response)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(ResourceError) as excinfo:
            _fetch_all_versions_from_maven_central(
                "org.nonexistent", 
                "nonexistent-artifact"
            )
        
        assert "not found in Maven Central" in str(excinfo.value)
    
    @patch("requests.get")
    def test_invalid_xml(self, mock_get):
        """Test handling of invalid XML responses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <invalid>xml
        """
        mock_get.return_value = mock_response
        
        with pytest.raises(ResourceError) as excinfo:
            _fetch_all_versions_from_maven_central(
                "org.springframework", 
                "spring-core"
            )
        
        assert "Failed to parse Maven metadata XML" in str(excinfo.value)
    
    @patch("requests.get")
    def test_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        mock_get.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(ResourceError) as excinfo:
            _fetch_all_versions_from_maven_central(
                "org.springframework", 
                "spring-core"
            )
        
        assert "Error fetching Maven metadata" in str(excinfo.value)


class TestVersionComparison:
    """Tests for version comparison utilities."""
    
    def test_parse_version_components(self):
        """Test parsing version components."""
        # Simple version
        assert parse_version_components("1.2.3") == ([1, 2, 3], "")
        
        # Version with qualifier
        assert parse_version_components("1.2.3-SNAPSHOT") == ([1, 2, 3], "-SNAPSHOT")
        
        # Version with dot qualifier
        assert parse_version_components("1.2.3.Final") == ([1, 2, 3], ".Final")
        
        # Invalid version
        assert parse_version_components("invalid") == ([], "invalid")
    
    def test_compare_versions(self):
        """Test comparing different versions."""
        # Equal versions
        assert compare_versions("1.2.3", "1.2.3") == 0
        
        # Different numeric versions
        assert compare_versions("1.2.3", "1.2.4") < 0
        assert compare_versions("1.2.4", "1.2.3") > 0
        
        # Different number of components
        assert compare_versions("1.2", "1.2.0") < 0
        assert compare_versions("1.2.0", "1.2") > 0
        
        # Qualifiers
        assert compare_versions("1.2.3-SNAPSHOT", "1.2.3") < 0
        assert compare_versions("1.2.3", "1.2.3-SNAPSHOT") > 0
        assert compare_versions("1.2.3-SNAPSHOT", "1.2.3-beta") != 0
    
    def test_get_latest_version(self):
        """Test getting the latest version from a list."""
        # Simple versions
        assert get_latest_version(["1.0.0", "1.1.0", "1.2.0"]) == "1.2.0"
        
        # Complex scenario with qualifiers
        versions = ["1.0.0", "1.1.0", "1.2.0", "1.2.0-SNAPSHOT", "1.3.0-SNAPSHOT"]
        assert get_latest_version(versions) == "1.2.0"  # Should filter snapshots
        
        # Only snapshot versions available
        versions = ["1.0.0-SNAPSHOT", "1.1.0-SNAPSHOT", "1.2.0-SNAPSHOT"]
        assert get_latest_version(versions) == "1.2.0-SNAPSHOT"
        
        # Empty list
        with pytest.raises(ValueError):
            get_latest_version([])
        
        # Non-standard versions with known qualifier ranks
        versions = ["1.0.0.Final", "1.0.0.RC1", "1.0.0.Beta2"]
        # Now this should work with our improved qualifier ranking
        assert get_latest_version(versions) == "1.0.0.Final"