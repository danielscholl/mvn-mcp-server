# MCP Server Tool Spec - Java Security Scan

> A Java-specific tool for scanning Maven projects for vulnerabilities and providing detailed information about detected security issues.

## Scope

This tool is **exclusively for Java/Maven projects**. 
The tool focuses solely on vulnerability **detection and reporting**.

## Required Implementation Tasks

- [x] ✅ Implement Java-specific project scanning using Trivy for vulnerability detection focusing on pom.xml files
- [x] ✅ Support Maven multi-module projects with parent-child relationships and nested directory structures
- [x] ✅ Enable scanning Maven profiles and conditional dependencies
- [x] ✅ Handle BOMs (Bill of Materials) and dependency management sections
- [x] ✅ Process version properties and version inheritance
- [x] ✅ Build comprehensive vulnerability report with severity levels and remediation recommendations
- [x] ✅ Implement proper error handling for scanning operations
- [x] ✅ Implement Trivy availability detection and provide clear error messages when unavailable
- [x] ✅ Make sure this functionality works end to end as an MCP tool in the server.py file

## Trivy Integration

This tool uses [Trivy](https://github.com/aquasecurity/trivy) for vulnerability scanning. Trivy is an external dependency that must be installed on the system where the MCP server runs.

### Trivy Configuration

1. **Availability Check**
   - On server initialization, check if Trivy is available by running `trivy --version`
   - If Trivy is not available, provide a clear error message instructing the user to install Trivy
   - No configuration parameters are needed - Trivy is expected to be available in the PATH

2. **Direct Scanning Approach**
   - Use Trivy to scan the entire project directory directly
   - Parse pom.xml files to understand the Maven structure
   - Use Trivy's filesystem scanning capabilities with the `--security-checks vuln` flag
   - Format results as JSON for easy parsing
   - Extract relevant vulnerability information from the scan results

### Tool Details
- Implemented in `src/mvn_mcp_server/tools/java_security_scan.py`
- **scan_java_project()**
  - Validate the Java project directory path (confirms presence of pom.xml)
  - Check Trivy availability
  - Execute Trivy scan on the project directory
  - Parse and format vulnerability scan results
  - Group vulnerabilities by severity
  - Provide detailed information including vulnerability IDs, descriptions, and suggested remediation versions
  - Return comprehensive vulnerability report
- Performance optimizations:
  - Use temporary files for efficient processing of Trivy results
  - Clean error handling for various failure scenarios

### Input Rules
- For scan_java_project_tool:
  - `workspace` is required and must be a valid Java project directory path with pom.xml
  - `include_profiles` is optional string array of profile IDs to activate during scan
  - `scan_all_modules` is optional boolean (default true) to scan all modules or just the specified project

### Testing Requirements
- Run tests with `uv run pytest`
- Tests should:
  - Mock Trivy commands and responses for predictable testing
  - Test error handling for when Trivy is not available
  - Verify correct parsing of Trivy results
- Test coverage requirements:
  - Successful scanning with vulnerabilities detected
  - Clear error when Trivy is not available
  - Error handling for invalid workspaces
  - Error handling for non-Maven projects
- Tests must verify correctness across normal and boundary cases

## Tool to Expose

```text
scan_java_project_tool(
    workspace: str,
    include_profiles: Optional[List[str]] = None,
    scan_all_modules: bool = True
) -> Dict[str, Any]
```

### Response Format
- Return format matches the defined success/error dictionary structure:
  ```python
  # Success response for scan_java_project
  {
    "tool_name": "scan_java_project",
    "status": "success",
    "result": {
      "scan_mode": str,  # "trivy" indicating which scanning mode was used
      "vulnerabilities_found": bool,
      "total_vulnerabilities": int,
      "modules_scanned": [str],  # List of modules scanned 
      "profiles_activated": [str],  # List of profiles activated during scan
      "severity_counts": {
        "critical": int,
        "high": int,
        "medium": int,
        "low": int,
        "unknown": int
      },
      "vulnerabilities": [
        {
          "module": str,  # Module name/path where vulnerability was found
          "group_id": str,
          "artifact_id": str,
          "installed_version": str,
          "vulnerability_id": str,
          "cve_id": str,  # CVE identifier (e.g., CVE-2021-44228)
          "severity": str,
          "description": str,
          "recommendation": str,  # Recommended version to upgrade to
          "in_profile": str,  # Optional, only if vulnerability is in a specific profile
          "direct_dependency": bool,  # Whether this is a direct dependency or transitive
          "is_in_bom": bool,  # Whether this dependency is in a Bill of Materials
          "version_source": str,  # "direct", "property", "parent", "bom", or "dependency_management"
          "source_location": str,  # File and location where the version is defined
          "links": [str],  # List of links to vulnerability information
          "fix_available": bool  # Whether a fixed version exists
        },
        # Additional vulnerabilities...
      ],
      "scan_limitations": null,  # Always null since we only use Trivy mode
      "recommendations": null  # Always null since we only use Trivy mode
    }
  }
  
  # Error response
  {
    "tool_name": str,  # "scan_java_project"
    "status": "error",
    "error": {
      "code": str,  # One of the ErrorCode enum values
      "message": str,  # Human-readable error message
      "details": {  # Optional detailed information about the error
        "file": str,  # Optional file where error occurred
        "command_output": str,  # Optional output from failed command
        "suggestion": str  # Optional suggestion for resolving the error
      }
    }
  }
  ```

### Error Codes

| Code | Meaning |
|------|---------|
| INVALID_INPUT_FORMAT | Malformed directory path or other parameter |
| MISSING_PARAMETER    | Required parameter missing |
| DIRECTORY_NOT_FOUND  | The specified directory does not exist |
| NOT_MAVEN_PROJECT    | The specified directory is not a Maven project (no pom.xml found) |
| MAVEN_ERROR          | Error executing Maven commands |
| TRIVY_ERROR          | Error executing the Trivy vulnerability scanner |
| INTERNAL_SERVER_ERROR| Unhandled exception inside the server |

## Relevant Files
- src/mvn_mcp_server/server.py
- src/mvn_mcp_server/shared/data_types.py
- src/mvn_mcp_server/tools/java_security_scan.py
- src/mvn_mcp_server/tests/tools/test_java_security_scan.py
- src/mvn_mcp_server/tests/resources/ (test POM files)

## 🚨 VALIDATION CHECKLIST 🚨

The implementation has been validated through:

1. [x] ✅ Comprehensive tests with mocked Trivy responses
2. [x] ✅ Tests to verify error handling when Trivy is not available
3. [x] ✅ Tests to ensure proper handling of invalid inputs
4. [x] ✅ All tests passing with `uv run pytest src/mvn_mcp_server/tests/tools/test_java_security_scan.py`
5. [x] ✅ Manual testing with real Java projects containing vulnerabilities
6. [x] ✅ Verification that the MCP tool properly registers and works end-to-end

📝 **Note:** This implementation requires Trivy to be installed on the system. If Trivy is not available, a clear error message will be returned instructing the user to install it.