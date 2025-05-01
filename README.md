# Maven MCP Server

A Model-Client-Programmer (MCP) server that provides tools for working with Maven dependencies, specifically for checking if specific versions of dependencies exist in the Maven Central repository.

## Setup

### Installation

```bash
# Clone the repository
git clone https://github.com/danielscholl/mvn-mcp-server.git
cd mvn-mcp-server

# Install dependencies
uv sync

# Install the package in development mode
uv pip install -e .

# Run tests to verify installation
uv run pytest
```

### MCP Configuration

To use this MCP server in your projects, add the following to your `.mcp.json` file:

```json
{
  "mcpServers": {
    "maven-mcp-server": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "maven-mcp-server"
      ],
      "env": {}
    }
  }
}
```

## Available Tools

### Check Maven Version Exists

Verifies if a specific version of a Maven dependency exists in the Maven Central repository.

```
check_maven_version_exists(
    dependency: str,
    version: str,
    packaging: str = "jar",
    classifier: str | None = None
) -> bool
```

**Parameters:**
- `dependency`: Maven dependency in format `groupId:artifactId` (e.g., "org.springframework:spring-core")
- `version`: Version string to check (e.g., "5.3.10")
- `packaging`: Package type (jar, war, pom, etc.), defaults to "jar"
- `classifier`: Optional classifier (e.g., "sources", "javadoc")

**Returns:**
- A dictionary with an `exists` boolean indicating if the version exists

**Usage Examples:**

```
# Check if Spring Core 5.3.10 exists
check_maven_version_exists: "org.springframework:spring-core" "5.3.10"

# Check with specific packaging
check_maven_version_exists: "org.springframework:spring-web" "5.3.10" "jar"

# Check with classifier
check_maven_version_exists: "org.springframework:spring-core" "5.3.10" "jar" "sources"
```

**Response Format:**
- Success response:
  ```json
  {
    "tool_name": "check_maven_version_exists",
    "status": "success",
    "result": {
      "exists": true
    }
  }
  ```

- Error response:
  ```json
  {
    "tool_name": "check_maven_version_exists",
    "status": "error",
    "error": {
      "code": "INVALID_INPUT_FORMAT",
      "message": "Dependency must be in groupId:artifactId format"
    }
  }
  ```

## Error Codes

| Code | Meaning |
|------|---------|
| INVALID_INPUT_FORMAT | Malformed dependency or version string |
| MISSING_PARAMETER    | Required parameter missing |
| DEPENDENCY_NOT_FOUND | No versions found for the dependency |
| MAVEN_API_ERROR      | Upstream Maven Central error (non‑200, network failure) |
| INTERNAL_SERVER_ERROR| Unhandled exception inside the server |

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest src/maven_mcp_server/tests/tools/test_version_exist.py
```

### Version Checking Logic

The tool uses two approaches to check version existence:

1. **Direct File Check**: First attempts to directly access the artifact file in the Maven repository
2. **Metadata Check**: If the direct check fails, falls back to examining the maven-metadata.xml file

This dual approach provides robust version checking that works with different repository structures.