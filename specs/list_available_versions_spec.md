# MCP Server Tool Spec - List Available Versions

> List all available versions of a Maven artifact grouped by minor version tracks.

## Required Implementation Tasks

- [ ] ✅ Implement retrieval of all available versions from Maven Central
- [ ] ✅ Build structured view of versions organized by minor version tracks
- [ ] ✅ Filter out unstable or pre-release versions for production use
- [ ] ✅ Add support for selectively including all versions in the response
- [ ] ✅ Make sure this functionality works end to end as an MCP tool in the server.py file

### Tool Details
- Implemented in `src/mvn_mcp_server/tools/list_available_versions.py`
- **list_available_versions()**
  - Validate the dependency format (must be groupId:artifactId)
  - Validate the version string format
  - Check if the specified version exists
  - Retrieve all available versions from Maven Central
  - Filter out snapshot and pre-release versions
  - Group versions by major.minor tracks
  - Highlight the current version's track
  - Optionally include full version lists for all tracks
  - Return structured version information
- Optimize API calls with caching to reduce redundant requests
- Special handling for version formats (standard semver, calendar format, simple numeric)

### Input Rules
- `dependency` **MUST** match `groupId:artifactId` (no embedded version)
- `version` is required and must be a valid version string
- `packaging` is optional, defaults to "jar" (automatically uses "pom" for dependencies with -bom or -dependencies suffix)
- `classifier` is optional, can be null or a valid classifier string
- `include_all_versions` is optional boolean, defaults to false

### Testing Requirements
- Run tests with `uv run pytest`
- Implement mocks for Maven API calls for reliable testing
- Add test coverage for:
  - Successful version listing with all versions included
  - Successful version listing without all versions
  - Empty versions list handling
  - Input validation errors
  - Maven API errors
  - Dependency not found errors
  - Unexpected error handling
- Tests must verify correctness across normal and boundary cases

## Tool to Expose

```text
list_available_versions_tool(
    dependency: str,
    version: str,
    packaging: str = "jar",
    classifier: str | None = None,
    include_all_versions: bool = False
) -> Dict[str, Any]
```

### Response Format
- Return format matches the defined success/error dictionary structure:
  ```python
  # Success response
  {
    "tool_name": "list_available_versions",
    "status": "success",
    "result": {
      "current_version": str,
      "current_exists": bool,
      "latest_version": str,
      "minor_tracks": {
        "1.0": {
          "latest": "1.0.2",
          "is_current_track": bool,
          "versions": ["1.0.2", "1.0.1", "1.0.0"]  # Only included if is_current_track=True or include_all_versions=True
        },
        "1.1": {
          "latest": "1.1.1",
          "is_current_track": bool
        },
        "2.0": {
          "latest": "2.0.2",
          "is_current_track": bool
        }
      }
    }
  }
  
  # Error response
  {
    "tool_name": "list_available_versions",
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
- src/mvn_mcp_server/tools/list_available_versions.py
- src/mvn_mcp_server/tests/tools/test_list_available_versions.py
- src/mvn_mcp_server/services/maven_api.py
- src/mvn_mcp_server/services/version.py
- src/mvn_mcp_server/services/cache.py


## 🚨 REQUIRED VALIDATION CHECKLIST 🚨

Every implementation MUST complete all validation steps in order:

1. [ ] ✅ Create and implement all required code
2. [ ] ✅ Write comprehensive tests covering the scenarios described above
3. [ ] ✅ Run test command: `uv run pytest src/mvn_mcp_server/tests/tools/test_list_available_versions.py`
4. [ ] ✅ Ensure all tests pass successfully
5. [ ] ✅ Manually test with real-world Maven dependencies and versions

📝 **Note:** These validation steps are MANDATORY and must be completed in order. Each step depends on successful completion of previous steps.