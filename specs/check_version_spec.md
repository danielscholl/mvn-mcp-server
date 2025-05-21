# MCP Server Tool Spec - Check Version

> Check a Maven version and retrieve comprehensive version update information in a single call.

## Required Implementation Tasks

- [ ] ✅ Implement direct version existence checking against Maven Central
- [ ] ✅ Provide latest version information for major, minor, and patch updates
- [ ] ✅ Build robust error handling for all possible failure scenarios
- [ ] ✅ Make sure this functionality works end to end as an MCP tool in the server.py file

### Tool Details
- Implemented in `src/mvn_mcp_server/tools/check_version.py`
- **check_version()**
  - Validate the dependency format (must be groupId:artifactId)
  - Validate the version string format
  - Query Maven Central API to check if the specific version exists
  - Get all available versions for the dependency
  - Find latest versions for each semantic component (major, minor, patch)
  - Determine if updates are available
  - Return comprehensive version information
- Optimize API calls with caching to reduce redundant requests
- Automatically detect POM dependencies (artifacts with -bom or -dependencies suffix)
- Special handling for version formats (standard semver, calendar format, simple numeric)

### Input Rules
- `dependency` **MUST** match `groupId:artifactId` (no embedded version)
- `version` is required and must be a valid version string
- `packaging` is optional, defaults to "jar" (automatically uses "pom" for dependencies with -bom or -dependencies suffix)
- `classifier` is optional, can be null or a valid classifier string

### Testing Requirements
- Run tests with `uv run pytest`
- Implement mocks for Maven API calls for reliable testing
- Add test coverage for:
  - Existing versions
  - Non-existing versions
  - Different packaging types
  - Dependencies with classifiers
  - Input validation errors
  - API response errors
  - Latest component version calculation
- Tests must verify correctness across normal and boundary cases

## Tool to Expose

```text
check_version_tool(
    dependency: str,
    version: str,
    packaging: str = "jar",
    classifier: str | None = None
) -> Dict[str, Any]
```

### Response Format
- Return format matches the defined success/error dictionary structure:
  ```python
  # Success response
  {
    "tool_name": "check_version",
    "status": "success",
    "result": {
      "exists": bool,
      "current_version": str,
      "latest_versions": {
        "major": str,
        "minor": str,
        "patch": str
      },
      "update_available": {
        "major": bool,
        "minor": bool,
        "patch": bool
      }
    }
  }
  
  # Error response
  {
    "tool_name": "check_version",
    "status": "error",
    "error": {
      "code": str,  # One of the ErrorCode enum values
      "message": str  # Human-readable error message
    }
  }
  ```

### Error Codes

| Code | Meaning |
|------|---------|
| INVALID_INPUT_FORMAT | Malformed dependency or version string |
| MISSING_PARAMETER    | Required parameter missing |
| DEPENDENCY_NOT_FOUND | No versions found for the dependency |
| VERSION_NOT_FOUND    | Version couldn't be found |
| MAVEN_API_ERROR      | Upstream Maven Central error (non‑200, network failure) |
| INTERNAL_SERVER_ERROR| Unhandled exception inside the server |

## Relevant Files
- src/mvn_mcp_server/server.py
- src/mvn_mcp_server/shared/utils.py
- src/mvn_mcp_server/shared/data_types.py
- src/mvn_mcp_server/tools/check_version.py
- src/mvn_mcp_server/tests/tools/test_check_version.py
- src/mvn_mcp_server/services/maven_api.py
- src/mvn_mcp_server/services/version.py
- src/mvn_mcp_server/services/cache.py


## 🚨 REQUIRED VALIDATION CHECKLIST 🚨

Every implementation MUST complete all validation steps in order:

1. [ ] ✅ Create and implement all required code
2. [ ] ✅ Write comprehensive tests covering the scenarios described above
3. [ ] ✅ Run test command: `uv run pytest src/mvn_mcp_server/tests/tools/test_check_version.py`
4. [ ] ✅ Ensure all tests pass successfully
5. [ ] ✅ Manually test with real-world Maven dependencies and versions

📝 **Note:** These validation steps are MANDATORY and must be completed in order. Each step depends on successful completion of previous steps.