"""Tests for Java security scanning tool.

This module tests the Java security scanning tool for Maven projects.
"""

import json
import pytest
from unittest.mock import patch, MagicMock, mock_open

from mvn_mcp_server.tools.java_security_scan import (
    scan_java_project,
    check_trivy_availability
)


class TestJavaSecurityScan:
    """Tests for the scan_java_project function."""

    @pytest.fixture
    def mock_workspace(self, tmp_path):
        """Create a temporary workspace with a POM file."""
        # Create a temporary directory
        workspace = tmp_path / "test-java-project"
        workspace.mkdir()

        # Create a dummy POM file
        pom_content = """<project>
            <groupId>com.example</groupId>
            <artifactId>test-project</artifactId>
            <version>1.0.0</version>
        </project>"""

        pom_path = workspace / "pom.xml"
        with open(pom_path, 'w') as f:
            f.write(pom_content)

        return workspace

    @patch('mvn_mcp_server.tools.java_security_scan.check_trivy_availability')
    @patch('os.unlink')  # Add patch for os.unlink
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    def test_trivy_scan(self, mock_open_file, mock_run, mock_temp_file, mock_unlink, mock_check_trivy, mock_workspace):
        """Test Trivy scanning."""
        # Set up mocks
        mock_check_trivy.return_value = True

        # Mock the temp file
        temp_file_name = "/tmp/trivy_results.json"
        mock_temp_file.return_value.__enter__.return_value.name = temp_file_name

        # Mock subprocess execution
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        # Mock Trivy JSON response
        trivy_json_response = {
            "Results": [
                {
                    "Target": "pom.xml",
                    "Class": "lang-pkgs",
                    "Type": "pom",
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2021-44228",
                            "PkgID": "org.apache.logging.log4j:log4j-core:2.14.1",
                            "PkgName": "org.apache.logging.log4j:log4j-core",
                            "InstalledVersion": "2.14.1",
                            "FixedVersion": "2.17.1",
                            "Severity": "CRITICAL",
                            "Description": "Log4Shell vulnerability",
                            "References": [
                                {"URL": "https://nvd.nist.gov/vuln/detail/CVE-2021-44228"}
                            ]
                        }
                    ]
                }
            ]
        }

        # Configure the mock_open to work correctly with the explicit filename
        mock_open_file.return_value.__enter__.return_value.read.return_value = json.dumps(trivy_json_response)

        # Execute the function
        result = scan_java_project(str(mock_workspace))

        # Check the result
        assert result["status"] == "success"
        assert result["result"]["scan_mode"] == "trivy"
        assert result["result"]["vulnerabilities_found"] is True
        assert result["result"]["total_vulnerabilities"] == 1
        assert len(result["result"]["modules_scanned"]) == 1
        assert result["result"]["severity_counts"]["critical"] == 1
        assert "scan_limitations" not in result["result"] or result["result"]["scan_limitations"] is None

        # Verify mock calls
        mock_check_trivy.assert_called_once()
        mock_run.assert_called_once()
        mock_open_file.assert_called_with(temp_file_name, 'r')

        # Verify Trivy command arguments
        args, kwargs = mock_run.call_args
        trivy_cmd = args[0]
        assert "trivy" in trivy_cmd
        assert "fs" in trivy_cmd
        assert "--security-checks" in trivy_cmd
        assert "vuln" in trivy_cmd
        assert "--format" in trivy_cmd
        assert "json" in trivy_cmd

    @patch('mvn_mcp_server.tools.java_security_scan.check_trivy_availability')
    def test_trivy_not_available(self, mock_check_trivy, mock_workspace):
        """Test handling when Trivy is not available."""
        # Set up mock
        mock_check_trivy.return_value = False

        # Execute the function and check for ResourceError in the response
        result = scan_java_project(str(mock_workspace))

        assert result["status"] == "error"
        assert result["error"]["code"] == "TRIVY_ERROR"
        assert "Trivy is not available" in result["error"]["message"]

    def test_invalid_workspace(self):
        """Test with an invalid workspace path."""
        result = scan_java_project("/path/that/does/not/exist")

        assert result["status"] == "error"
        assert result["error"]["code"] == "INVALID_INPUT_FORMAT"

    def test_not_maven_project(self, tmp_path):
        """Test with a directory that is not a Maven project."""
        workspace = tmp_path / "not-maven"
        workspace.mkdir()

        result = scan_java_project(str(workspace))

        assert result["status"] == "error"
        assert result["error"]["code"] == "INVALID_INPUT_FORMAT"
        assert "pom.xml" in result["error"]["message"]


class TestHelperFunctions:
    """Tests for helper functions in the java_security_scan module."""

    @patch('subprocess.run')
    def test_trivy_availability_check(self, mock_run):
        """Test checking Trivy availability."""
        # Trivy available
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        assert check_trivy_availability() is True

        # Trivy not available
        mock_process.returncode = 1
        assert check_trivy_availability() is False

        # Trivy not found
        mock_run.side_effect = FileNotFoundError()
        assert check_trivy_availability() is False
