# MCP Server Tool Spec - Check Version Batch

> Process multiple Maven dependency version checks in a single batch request.

## Required Implementation Tasks

- [ ] ✅ Implement batch processing of dependency version checks
- [ ] ✅ Optimize processing with parallel execution and deduplication
- [ ] ✅ Build comprehensive summary statistics for batch results
- [ ] ✅ Implement proper error handling with individual dependency error tracking
- [ ] ✅ Make sure this functionality works end to end as an MCP tool in the server.py file

### Tool Details
- Implemented in `src/mvn_mcp_server/tools/check_version_batch.py`
- **check_version_batch()**
  - Validate the input dependency list
  - Deduplicate dependencies to avoid redundant checks
  - Process unique dependencies in parallel using ThreadPoolExecutor
  - Calculate summary statistics including update counts
  - Return consolidated results with detailed information for each dependency
- Performance optimizations:
  - Parallel processing with concurrent.futures
  - Deduplication of identical dependency requests
  - Shared caching through MavenCache service
  - Reuse of individual check_version tool for consistent behavior

### Input Rules
- `dependencies` **MUST** be a non-empty list of dependency objects
- Each dependency object must contain:
  - `dependency`: Maven dependency in groupId:artifactId format (required)
  - `version`: Version string to check (required)
  - `packaging`: Package type, defaults to "jar" (optional)
  - `classifier`: Classifier string (optional)

### Testing Requirements
- Run tests with `uv run pytest`
- Implement mocks for parallel processing behavior
- Add test coverage for:
  - Successful batch processing
  - Deduplication of dependencies
  - Dependency key generation
  - Summary statistics calculation
  - Input validation errors
  - Error handling during processing
  - Mixed success/error results
- Tests must verify correctness across normal and boundary cases

## Tool to Expose

```text
check_version_batch_tool(
    dependencies: List[Dict[str, Any]]
) -> Dict[str, Any]
```

### Response Format
- Return format matches the defined success/error dictionary structure:
  ```python
  # Success response
  {
    "tool_name": "check_version_batch",
    "status": "success",
    "result": {
      "summary": {
        "total": int,
        "success": int,
        "failed": int,
        "updates_available": {
          "major": int,
          "minor": int,
          "patch": int
        }
      },
      "dependencies": [
        {
          "dependency": str,
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
        },
        {
          "dependency": str,
          "status": "error",
          "error": {
            "code": str,
            "message": str
          }
        }
      ]
    }
  }
  
  # Error response (for global errors)
  {
    "tool_name": "check_version_batch",
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
| INVALID_INPUT_FORMAT | Malformed dependency list or dependency object |
| MISSING_PARAMETER    | Required parameter missing |
| MAVEN_API_ERROR      | Upstream Maven Central error (non‑200, network failure) |
| INTERNAL_SERVER_ERROR| Unhandled exception inside the server |

## Relevant Files
- src/mvn_mcp_server/server.py
- src/mvn_mcp_server/shared/utils.py
- src/mvn_mcp_server/shared/data_types.py
- src/mvn_mcp_server/tools/check_version_batch.py
- src/mvn_mcp_server/tools/check_version.py
- src/mvn_mcp_server/tests/tools/test_check_version_batch.py
- src/mvn_mcp_server/services/maven_api.py
- src/mvn_mcp_server/services/version.py
- src/mvn_mcp_server/services/cache.py


## 🚨 REQUIRED VALIDATION CHECKLIST 🚨

Every implementation MUST complete all validation steps in order:

1. [ ] ✅ Create and implement all required code
2. [ ] ✅ Write comprehensive tests covering the scenarios described above
3. [ ] ✅ Run test command: `uv run pytest src/mvn_mcp_server/tests/tools/test_check_version_batch.py`
4. [ ] ✅ Ensure all tests pass successfully
5. [ ] ✅ Manually test with real-world Maven dependencies and versions

📝 **Note:** These validation steps are MANDATORY and must be completed in order. Each step depends on successful completion of previous steps.