# Maven MCP Server

A Model Context Protocol (MCP) server that provides tools for working with Maven dependencies, specifically for checking if specific versions of dependencies exist in the Maven Central repository, retrieving the latest versions, and finding the latest version based on semantic versioning components.

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

This MCP server provides three main tools for working with Maven dependencies:

### Check Maven Version

Verifies if a specific version of a Maven dependency exists in the Maven Central repository.

**Tool Name:** `maven-mcp-server__check_maven_version`

**Parameters:**
- `dependency`: Maven dependency in format `groupId:artifactId` (e.g., "org.springframework:spring-core")
- `version`: Version string to check (e.g., "5.3.10")
- `packaging`: (Optional) Package type (jar, war, pom, etc.), defaults to "jar"
- `classifier`: (Optional) Classifier (e.g., "sources", "javadoc")

**Usage Example:**

```python
# Through the Claude Code assistant:
mcp__maven-mcp-server__check_maven_version(
    dependency="org.springframework:spring-core",
    version="5.3.10"
)

# With optional parameters:
mcp__maven-mcp-server__check_maven_version(
    dependency="org.springframework:spring-core",
    version="5.3.10",
    packaging="jar",
    classifier="sources"
)
```

**Response Format:**
```json
{
  "tool_name": "check_version",
  "status": "success",
  "result": {
    "exists": true
  }
}
```

### Get Maven Latest Version

Retrieves the latest version of a Maven dependency from the Maven Central repository.

**Tool Name:** `maven-mcp-server__get_maven_latest_version`

**Parameters:**
- `dependency`: Maven dependency in format `groupId:artifactId` (e.g., "org.springframework:spring-core")
- `packaging`: (Optional) Package type (jar, war, pom, etc.), defaults to "jar"
- `classifier`: (Optional) Classifier (e.g., "sources", "javadoc")

**Usage Example:**

```python
# Through the Claude Code assistant:
mcp__maven-mcp-server__get_maven_latest_version(
    dependency="org.springframework:spring-core"
)

# With optional parameters:
mcp__maven-mcp-server__get_maven_latest_version(
    dependency="org.springframework:spring-core",
    packaging="jar",
    classifier="sources"
)
```

**Response Format:**
```json
{
  "tool_name": "latest_version",
  "status": "success",
  "result": {
    "latest_version": "7.0.0-M4"
  }
}
```

### Find Maven Version

Finds the latest version of a Maven dependency based on semantic versioning components (major, minor, patch).

**Tool Name:** `maven-mcp-server__find_maven_version`

**Parameters:**
- `dependency`: Maven dependency in format `groupId:artifactId` (e.g., "org.springframework:spring-core")
- `version`: Version string to use as reference (e.g., "5.3.10")
- `target_component`: Component to find the latest version for ("major", "minor", or "patch")
- `packaging`: (Optional) Package type (jar, war, pom, etc.), defaults to "jar"
- `classifier`: (Optional) Classifier (e.g., "sources", "javadoc")

**Usage Example:**

```python
# Through the Claude Code assistant:
# Find the latest patch version within 5.3.x
mcp__maven-mcp-server__find_maven_version(
    dependency="org.springframework:spring-core",
    version="5.3.0",
    target_component="patch"
)

# Find the latest minor version within major version 5 
mcp__maven-mcp-server__find_maven_version(
    dependency="org.springframework:spring-core",
    version="5.0.0",
    target_component="minor"
)

# With optional parameters:
mcp__maven-mcp-server__find_maven_version(
    dependency="org.springframework:spring-core",
    version="5.3.0",
    target_component="patch",
    packaging="jar",
    classifier="sources"
)
```

**Response Format:**
```json
{
  "tool_name": "find_version",
  "status": "success",
  "result": {
    "latest_version": "5.3.39"
  }
}
```

## Error Handling

All tools return standardized error responses when issues occur:

```json
{
  "tool_name": "[tool_name]",
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
- `VERSION_NOT_FOUND`: The specific version does not exist
- `MAVEN_API_ERROR`: Error connecting to Maven Central
- `INTERNAL_SERVER_ERROR`: Unexpected server error

## Development

### Testing

```bash
# Run all tests
uv run pytest

# Run specific tests
uv run pytest src/maven_mcp_server/tests/tools/test_version_exist.py
```

### Architecture

The server implements a layered architecture:
- **Service Layer**: Core functionality for Maven API interactions, caching, and version handling
- **Tool Layer**: MCP tool implementations that use the service layer
- **Shared Utilities**: Common utilities for validation and error handling

## License

[MIT License](LICENSE)