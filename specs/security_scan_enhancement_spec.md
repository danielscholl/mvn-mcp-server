# MCP Server Tool Spec - Java Security Scan Enhancements

> Enhance the Java security scan tool to support selective scanning modes, result filtering, and pagination to prevent token limit overflows.

## Issue Background

The current implementation of the Java security scanning tool faces a critical issue with token limit overflows when scanning large Java projects. When scanning the sample/partition directory, the tool generates 78,474 tokens, exceeding the 25,000 token limit.

Investigation revealed:
- Scanning the entire directory finds 243 vulnerabilities
- Scanning just the parent pom.xml finds 0 vulnerabilities
- Scanning partition-core/pom.xml finds 5 vulnerabilities
- File-specific scanning can significantly reduce token usage

## Required Implementation Tasks

- [ ] ✅ Add scan_mode parameter with "workspace" and "pom_only" options
- [ ] ✅ Add pom_file parameter for targeting a specific POM file in pom_only mode
- [ ] ✅ Add severity_filter parameter to limit results to specified severity levels
- [ ] ✅ Add max_results parameter to limit the number of vulnerabilities returned
- [ ] ✅ Add offset parameter for result pagination
- [ ] ✅ Update the server.py tool definition to expose new parameters
- [ ] ✅ Update documentation in README.md
- [ ] ✅ Ensure full test coverage for new parameters

## Enhanced Tool Details

- Implemented in `src/mvn_mcp_server/tools/java_security_scan.py`
- **scan_java_project()**
  - New parameter `scan_mode`: Controls scan scope ("workspace" or "pom_only")
  - New parameter `pom_file`: Optional path to specific POM file to scan (defaults to workspace/pom.xml)
  - New parameter `severity_filter`: Optional list of severity levels to include
  - New parameter `max_results`: Maximum number of vulnerability results to return
  - New parameter `offset`: Starting offset for paginated results
  - Add filtering logic for severity levels
  - Add slicing logic for pagination using offset and max_results
  - Maintain backward compatibility with existing parameters
  - Update Trivy command generation to target specific file in pom_only mode

### Input Rules
- For scan_java_project_tool:
  - `workspace` is required and must be a valid Java project directory path with pom.xml
  - `include_profiles` is optional string array of profile IDs to activate during scan
  - `scan_all_modules` is optional boolean (default true) to scan all modules or just the specified project
  - `scan_mode` is optional string, must be one of ["workspace", "pom_only"], defaults to "workspace"
  - `pom_file` is optional string, path to a specific pom.xml file. Used only in pom_only mode
  - `severity_filter` is optional string array with values from ["critical", "high", "medium", "low"]
  - `max_results` is optional integer, defaults to 100
  - `offset` is optional integer, defaults to 0

### Testing Requirements
- Run tests with `uv run pytest`
- Tests should be updated to include:
  - Testing both workspace and pom_only scan modes
  - Testing severity filtering functionality
  - Testing pagination with offset and max_results parameters
  - Edge case testing for all new parameters
- Manual verification with the problematic sample/partition directory

## Tool to Expose

```text
scan_java_project_tool(
    workspace: str,
    include_profiles: Optional[List[str]] = None,
    scan_all_modules: bool = True,
    scan_mode: str = "workspace",
    pom_file: Optional[str] = None,
    severity_filter: Optional[List[str]] = None,
    max_results: int = 100,
    offset: int = 0
) -> Dict[str, Any]
```

### Response Format
- The response format remains the same but adds pagination information:
  ```python
  # Success response for scan_java_project
  {
    "tool_name": "scan_java_project",
    "status": "success",
    "result": {
      "scan_mode": str,  # "trivy" or "trivy-pom-only" indicating which scanning mode was used
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
      "pagination": {
        "offset": int,  # Starting offset (0-based)
        "max_results": int,  # Maximum results per page
        "total_results": int,  # Total vulnerabilities found
        "has_more": bool  # Whether more results are available
      },
      "vulnerabilities": [
        # Same vulnerability format as before
      ],
      "scan_limitations": null,  # Always null since we only use Trivy mode
      "recommendations": null  # Always null since we only use Trivy mode
    }
  }
  ```

### Additional Error Codes

| Code | Meaning |
|------|---------|
| INVALID_SCAN_MODE | Invalid scan_mode parameter value |
| POM_FILE_NOT_FOUND | Specified pom_file does not exist |
| INVALID_SEVERITY_FILTER | Invalid severity level in severity_filter |

## Implementation Details

### Scan Mode Logic
```python
# Simplified pseudocode
if scan_mode == "pom_only":
    # Use the specified pom_file or default to workspace/pom.xml
    target_file = pom_file if pom_file else os.path.join(workspace, "pom.xml")
    if not os.path.exists(target_file):
        raise ValidationError(f"POM file does not exist: {target_file}")
    
    # Run Trivy on the specific POM file
    trivy_cmd = [
        "trivy", "fs",
        "--security-checks", "vuln",
        "--format", "json",
        "--output", output_file,
        target_file
    ]
else:  # Default "workspace" mode
    # Run Trivy on the entire workspace (current behavior)
    trivy_cmd = [
        "trivy", "fs",
        "--security-checks", "vuln",
        "--format", "json",
        "--output", output_file,
        str(workspace_path)
    ]
```

### Filtering and Pagination Logic
```python
# Simplified pseudocode
# Apply severity filtering if provided
if severity_filter:
    filtered_results = [v for v in scan_results if v.get("severity", "").lower() in severity_filter]
else:
    filtered_results = scan_results

# Calculate pagination information
total_results = len(filtered_results)
paginated_results = filtered_results[offset:offset + max_results]
has_more = offset + max_results < total_results

# Add pagination info to the response
pagination_info = {
    "offset": offset,
    "max_results": max_results,
    "total_results": total_results,
    "has_more": has_more
}
```

## Relevant Files
- src/mvn_mcp_server/server.py
- src/mvn_mcp_server/shared/data_types.py
- src/mvn_mcp_server/tools/java_security_scan.py
- src/mvn_mcp_server/tests/tools/test_java_security_scan.py
- README.md

## 🚨 VALIDATION CHECKLIST 🚨

Once implemented, the solution should be validated through:

1. [ ] ✅ Unit tests for new parameters and functionality
2. [ ] ✅ Run test command: `uv run pytest src/mvn_mcp_server/tests/tools/test_java_security_scan.py`
3. [ ] ✅ Ensure all tests pass successfully
4. [ ] ✅ Manual testing with the problematic sample/partition directory using different modes:
   - workspace mode with limited results
   - pom_only mode with specific pom.xml file
   - various severity filter combinations
   - pagination with different offsets and max_results
5. [ ] ✅ Verification that the enhanced MCP tool properly registers and works end-to-end

📝 **Note:** These enhancements will maintain backward compatibility while providing the flexibility to scan large projects without token limit issues.