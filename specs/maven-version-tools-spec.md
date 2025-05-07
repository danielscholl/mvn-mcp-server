# Maven Version Tools Specification

## Overview

This specification outlines a consolidated approach to the Maven MCP Server tools, focusing on efficiency and comprehensive information. We propose implementing two powerful tools with simple names:

1. `check_version` - Checks a version and returns all version update information in a single call
2. `check_version_batch` - Processes multiple dependencies in a single batch request

These consolidated tools will optimize the workflow for analyzing POM files and generating dependency upgrade reports.

## Tool Details

### 1. check_version

**Tool Name:** `maven-mcp-server__check_version`

**Purpose:**  
Check if a version exists and simultaneously provide information about the latest available versions across all semantic versioning components.

**Parameters:**
- `dependency` (required): Maven dependency in format `groupId:artifactId`
- `version` (required): Version string to check and use as reference
- `packaging` (optional): Package type (jar, war, pom, etc.), defaults to "jar"
- `classifier` (optional): Classifier (e.g., "sources", "javadoc")

**Response Format:**
```json
{
  "tool_name": "check_version",
  "status": "success",
  "result": {
    "exists": true,
    "current_version": "5.3.10",
    "latest_versions": {
      "major": "7.0.0-M4",
      "minor": "5.4.6",
      "patch": "5.3.39"
    },
    "update_available": {
      "major": true,
      "minor": true,
      "patch": true
    }
  }
}
```

**Error Handling:**
- Standard error response format with appropriate error codes
- Common error codes: INVALID_INPUT_FORMAT, DEPENDENCY_NOT_FOUND, MAVEN_API_ERROR, INTERNAL_SERVER_ERROR

### 2. check_version_batch

**Tool Name:** `maven-mcp-server__check_version_batch`

**Purpose:**  
Process multiple dependency version checks in a single batch request, reducing the number of API calls.

**Parameters:**
- `dependencies` (required): Array of dependency objects, each containing:
  - `dependency` (required): Maven dependency in format `groupId:artifactId`
  - `version` (required): Version string to check and use as reference
  - `packaging` (optional): Package type, defaults to "jar"
  - `classifier` (optional): Classifier, if any

**Response Format:**
```json
{
  "tool_name": "check_version_batch",
  "status": "success",
  "result": {
    "summary": {
      "total": 3,
      "success": 3,
      "failed": 0,
      "updates_available": {
        "major": 2,
        "minor": 3,
        "patch": 1
      }
    },
    "dependencies": [
      {
        "dependency": "org.apache.commons:commons-lang3",
        "status": "success",
        "result": {
          "exists": true,
          "current_version": "3.12.0",
          "latest_versions": {
            "major": "3.14.0",
            "minor": "3.14.0",
            "patch": "3.12.0"
          },
          "update_available": {
            "major": true,
            "minor": true,
            "patch": false
          }
        }
      },
      {
        "dependency": "org.springframework.boot:spring-boot-dependencies",
        "status": "success",
        "result": {
          "exists": true,
          "current_version": "3.1.0",
          "latest_versions": {
            "major": "3.2.0",
            "minor": "3.1.5",
            "patch": "3.1.0"
          },
          "update_available": {
            "major": true,
            "minor": true,
            "patch": false
          }
        }
      },
      {
        "dependency": "org.json:json",
        "status": "success",
        "result": {
          "exists": true,
          "current_version": "20231013",
          "latest_versions": {
            "major": "20240303",
            "minor": "20240303", 
            "patch": "20231013"
          },
          "update_available": {
            "major": true,
            "minor": true,
            "patch": false
          }
        }
      }
    ]
  }
}
```

**Error Handling:**
- Individual dependency errors are tracked in the response
- Overall tool error only if the batch process itself fails
- Each dependency in the results has its own status field
- The summary includes counts of total, successful, and failed checks

## Implementation Notes

1. **Consolidation of Functionality:**
   - Replace the existing separate tools with these two comprehensive ones
   - Existing tools can be maintained for backward compatibility if needed
   - Optimize code to reduce redundancy between the two tools

2. **Reuse Existing Services:**
   - Leverage and extend the existing `MavenApiService` and `VersionService`
   - Add new methods to efficiently handle batch operations
   - Enhance version comparison logic to support all semantic version components

3. **Performance Optimization:**
   - Implement request caching to reduce redundant Maven API calls
   - Process batch dependencies in parallel where possible
   - Deduplicate requests for identical dependencies

4. **Code Organization:**
   - Add new tool files: `check_version.py` and `check_version_batch.py`
   - Add corresponding test files
   - Update server configuration to register the new tools

## Usage Examples

**Enhanced Check:**
```python
mcp__maven-mcp-server__check_version(
    dependency="org.springframework:spring-core",
    version="5.3.10"
)
```

**Batch Check:**
```python
mcp__maven-mcp-server__check_version_batch(
    dependencies=[
        {
            "dependency": "org.apache.commons:commons-lang3",
            "version": "3.12.0"
        },
        {
            "dependency": "org.springframework.boot:spring-boot-dependencies",
            "version": "3.1.0"
        }
    ]
)
```

## Benefits Over Current Implementation

1. **Efficiency:** Reduces the number of API calls needed to get comprehensive version information
2. **Simplicity:** Two tools instead of multiple specialized ones, with more comprehensive results from each
3. **Complete Information:** Each call provides existence check and all version updates in one response
4. **Upgrade Analysis:** Directly indicates if updates are available at each semantic version level
5. **Batch Processing:** Efficiently handles multiple dependencies in a single request

## Migration Path

Existing tools can continue to function alongside these new tools to maintain backward compatibility. Documentation should be updated to recommend the new tools for most use cases, especially for analyzing POM files and generating upgrade reports.

## 🚨 REQUIRED VALIDATION CHECKLIST 🚨

Every implementation MUST complete all validation steps in order:

1. [ ] ✅ Create and implement all required code
2. [ ] ✅ Write comprehensive tests covering the scenarios described above
3. [ ] ✅ Run test command: `uv run pytest src/maven_mcp_server/tests/tools/test_check_version.py src/maven_mcp_server/tests/tools/test_check_version_batch.py`
4. [ ] ✅ Ensure all tests pass successfully
5. [ ] ✅ Manually test with real-world Maven dependencies and versions

📝 **Note:** These validation steps are MANDATORY and must be completed in order. Each step depends on successful completion of previous steps.