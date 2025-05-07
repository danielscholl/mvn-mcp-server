# Maven List Available Versions Tool Specification

## Overview

This specification defines a new MCP tool for the Maven MCP Server that provides structured information about all available versions of a Maven dependency. The tool allows users to discover available versions within specific major/minor tracks to facilitate informed version upgrade decisions.

## Tool Name

`maven-mcp-server__list_available_versions`

## Purpose

When maintaining applications with Maven dependencies, developers often need to make incremental version upgrades. While the existing `check_version_tool` provides the absolute latest versions across major/minor/patch components, it doesn't provide visibility into the intermediate versions available within each minor track.

This tool solves this problem by:
1. Providing a comprehensive list of all available versions
2. Identifying the latest version within each minor track
3. Presenting the data in a structured format that facilitates version upgrade planning

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `dependency` | string | Yes | - | Maven dependency in format `groupId:artifactId` (e.g., "org.springframework:spring-core") |
| `version` | string | Yes | - | Current version string to use as reference (e.g., "5.3.10") |
| `packaging` | string | No | "jar" | Package type (jar, war, pom, etc.) |
| `classifier` | string | No | null | Optional classifier (e.g., "sources", "javadoc") |
| `include_all_versions` | boolean | No | false | When true, includes all versions in the response. When false, includes only the latest version per minor. |

## Response Format

```json
{
  "tool_name": "list_available_versions",
  "status": "success",
  "result": {
    "current_version": "5.3.10",
    "current_exists": true,
    "latest_version": "6.2.6",
    "minor_tracks": {
      "5.0": {
        "latest": "5.0.20",
        "is_current_track": false
      },
      "5.1": {
        "latest": "5.1.21",
        "is_current_track": false
      },
      "5.2": {
        "latest": "5.2.25",
        "is_current_track": false
      },
      "5.3": {
        "latest": "5.3.39",
        "is_current_track": true,
        "versions": ["5.3.0", "5.3.1", ... , "5.3.39"]
      },
      "6.0": {
        "latest": "6.0.17",
        "is_current_track": false
      },
      "6.1": {
        "latest": "6.1.8",
        "is_current_track": false
      },
      "6.2": {
        "latest": "6.2.6",
        "is_current_track": false
      }
    }
  }
}
```

When `include_all_versions` is true, each minor track will include a complete `versions` array listing all versions within that track.

## Error Response

Standard error responses will follow the MCP server convention:

```json
{
  "tool_name": "list_available_versions",
  "status": "error",
  "error": {
    "code": "[ERROR_CODE]",
    "message": "[Error description]"
  }
}
```

Common error codes include:
- `INVALID_INPUT_FORMAT`: Input parameters are malformed
- `DEPENDENCY_NOT_FOUND`: The requested Maven dependency does not exist
- `VERSION_INVALID`: The provided version is not a valid semantic version
- `MAVEN_API_ERROR`: Error connecting to Maven Central
- `INTERNAL_SERVER_ERROR`: Unexpected server error

## Implementation Details

### Service Layer Integration

The tool will utilize the existing service layer components:
- `MavenApiService` to retrieve available versions from Maven Central
- `VersionService` for semantic version parsing, comparison, and filtering
- `Cache` to optimize frequent requests for the same dependencies

### Version Processing

The implementation will:
1. Retrieve all available versions for the given artifact
2. Group versions by major.minor tracks
3. For each track, determine the latest version
4. Highlight the track containing the current version
5. Optionally include the full list of versions per track based on the `include_all_versions` parameter

### Performance Considerations

- Results will be cached to minimize repeated API calls to Maven Central
- Version parsing and grouping will be optimized for large version sets
- The `include_all_versions` parameter allows clients to control response size

## Usage Examples

### Example 1: Basic Usage

```python
mcp__maven-mcp-server__list_available_versions(
    dependency="org.springframework:spring-core",
    version="5.3.10"
)
```

### Example 2: With All Versions

```python
mcp__maven-mcp-server__list_available_versions(
    dependency="org.springframework:spring-core",
    version="5.3.10",
    include_all_versions=True
)
```

### Example 3: With Specific Packaging and Classifier

```python
mcp__maven-mcp-server__list_available_versions(
    dependency="org.springframework:spring-core",
    version="5.3.10",
    packaging="jar",
    classifier="sources",
    include_all_versions=True
)
```

## Use Cases

1. **Controlled Upgrades**: Developers can identify the latest version within their current minor track for minimal-risk upgrades
2. **Minor Version Upgrade Planning**: Teams can see all available minor versions and choose the appropriate upgrade target
3. **Dependency Stability Analysis**: The complete version history helps evaluate the release frequency and stability of dependencies
4. **Release Train Alignment**: Organizations can identify which minor versions align with their internal release cadences

## Testing Strategy

The implementation will include comprehensive test coverage:
1. Unit tests for version grouping and track identification logic
2. Integration tests with mock Maven API responses
3. End-to-end tests against real Maven Central dependencies
4. Edge case testing for unusual versioning patterns and very large version sets


## 🚨 REQUIRED VALIDATION CHECKLIST 🚨

Every implementation MUST complete all validation steps in order:

1. [ ] ✅ Create and implement all required code
2. [ ] ✅ Write comprehensive tests covering the scenarios described above
3. [ ] ✅ Run test command: `uv run pytest src/maven_mcp_server/tests/tools/test_check_version.py src/maven_mcp_server/tests/tools/test_check_version_batch.py`
4. [ ] ✅ Ensure all tests pass successfully
5. [ ] ✅ Manually test with real-world Maven dependencies and versions

📝 **Note:** These validation steps are MANDATORY and must be completed in order. Each step depends on successful completion of previous steps.