# Maven MCP Server

A Model-Client-Programmer (MCP) server that provides tools for working with Maven dependencies, specifically for checking if specific versions of dependencies exist in the Maven Central repository, retrieving the latest versions, and finding the latest version based on semantic versioning components.

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

### Check Version

Verifies if a specific version of a Maven dependency exists in the Maven Central repository.

```
check_version(
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
check_version: "org.springframework:spring-core" "5.3.10"

# Check with specific packaging
check_version: "org.springframework:spring-web" "5.3.10" "jar"

# Check with classifier
check_version: "org.springframework:spring-core" "5.3.10" "jar" "sources"
```

**Response Format:**
- Success response:
  ```json
  {
    "tool_name": "check_version",
    "status": "success",
    "result": {
      "exists": true
    }
  }
  ```

- Error response:
  ```json
  {
    "tool_name": "check_version",
    "status": "error",
    "error": {
      "code": "INVALID_INPUT_FORMAT",
      "message": "Dependency must be in groupId:artifactId format"
    }
  }
  ```

### Latest Version

Retrieves the latest version of a Maven dependency from the Maven Central repository.

```
latest_version(
    dependency: str,
    packaging: str = "jar",
    classifier: str | None = None
) -> str
```

**Parameters:**
- `dependency`: Maven dependency in format `groupId:artifactId` (e.g., "org.springframework:spring-core")
- `packaging`: Package type (jar, war, pom, etc.), defaults to "jar"
- `classifier`: Optional classifier (e.g., "sources", "javadoc")

**Returns:**
- A dictionary with a `latest_version` string indicating the latest available version

**Usage Examples:**

```
# Get latest version of Spring Core
latest_version: "org.springframework:spring-core"

# Get latest version with specific packaging
latest_version: "org.springframework:spring-web" "jar"

# Get latest version with classifier
latest_version: "org.springframework:spring-core" "jar" "sources"
```

**Response Format:**
- Success response:
  ```json
  {
    "tool_name": "latest_version",
    "status": "success",
    "result": {
      "latest_version": "6.0.13"
    }
  }
  ```

- Error response:
  ```json
  {
    "tool_name": "latest_version",
    "status": "error",
    "error": {
      "code": "INVALID_INPUT_FORMAT",
      "message": "Dependency must be in groupId:artifactId format"
    }
  }
  ```

### Find Latest Component Version

Finds the latest version of a Maven dependency based on semantic versioning components (major, minor, patch).

```
find_version(
    dependency: str,
    version: str,
    target_component: str,
    packaging: str = "jar",
    classifier: str | None = None
) -> Dict[str, str]
```

**Parameters:**
- `dependency`: Maven dependency in format `groupId:artifactId` (e.g., "org.springframework:spring-core")
- `version`: Version string to use as reference (e.g., "5.3.10")
- `target_component`: Component to find the latest version for ("major", "minor", or "patch")
- `packaging`: Package type (jar, war, pom, etc.), defaults to "jar"
- `classifier`: Optional classifier (e.g., "sources", "javadoc")

**Returns:**
- A dictionary with a `latest_version` string indicating the latest available version for the specified component

**Usage Examples:**

```
# Find the latest major version based on reference version 5.3.10
find_version: "org.springframework:spring-core" "5.3.10" "major"

# Find the latest minor version within major version 5 
find_version: "org.springframework:spring-core" "5.0.0" "minor"

# Find the latest patch version within 5.3.x
find_version: "org.springframework:spring-core" "5.3.0" "patch"

# Find with specific packaging
find_version: "org.springframework:spring-web" "5.3.10" "major" "war"

# Find with classifier
find_version: "org.springframework:spring-core" "5.3.10" "major" "jar" "sources"
```

**Response Format:**
- Success response:
  ```json
  {
    "tool_name": "find_version",
    "status": "success",
    "result": {
      "latest_version": "6.0.13"
    }
  }
  ```

- Error response:
  ```json
  {
    "tool_name": "find_version",
    "status": "error",
    "error": {
      "code": "INVALID_TARGET_COMPONENT",
      "message": "Target component must be one of 'major', 'minor', or 'patch'"
    }
  }
  ```

## Error Codes

| Code | Meaning |
|------|---------|
| INVALID_INPUT_FORMAT | Malformed dependency or version string |
| INVALID_TARGET_COMPONENT | Invalid target_component value |
| MISSING_PARAMETER    | Required parameter missing |
| DEPENDENCY_NOT_FOUND | No versions found for the dependency |
| VERSION_NOT_FOUND    | Version not found though dependency exists |
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