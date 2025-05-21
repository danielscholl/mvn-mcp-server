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
uv pip install -e '.[dev]'

# Run tests to verify installation
uv run pytest
```

### MCP Configuration

To utilize this MCP server directly in other projects either use the buttons to install in VSCode, edit the `.mcp.json` file directory.

> Clients tend to have slighty different configurations

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22mvn-mcp-server%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22run%22%2C%22mvn-mcp-server%22%5D%2C%22env%22%3A%7B%7D%7D)   [![Install with Docker in VS Code](https://img.shields.io/badge/VS_Code-Docker-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22mvn-mcp-server%22%2C%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22--mount%22%2C%22type%3Dbind%2Csource%3D%3CYOUR_WORKSPACE_PATH%3E%2Ctarget%3D%2Fworkspace%22%2C%22danielscholl%2Fmvn-mcp-server%22%5D%2C%22env%22%3A%7B%7D%7D)

To use this MCP server in your projects, add the following to your `.mcp.json` file:

```json
{
  "mcpServers": {
    "mvn-mcp-server": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "mvn-mcp-server"
      ],
      "env": {}
    }
  }
}
```

## Available Tools

This MCP server provides three core tools for working with Maven dependencies:

### Check Maven Version Tool

A comprehensive tool that checks a Maven version and provides all related version update information in a single call.

**Tool Name:** `mvn-mcp-server__check_version_tool`

**Parameters:**
- `dependency`: Maven dependency in format `groupId:artifactId` (e.g., "org.springframework:spring-core")
- `version`: Version string to check (e.g., "5.3.10")
- `packaging`: (Optional) Package type (jar, war, pom, etc.), defaults to "jar"
- `classifier`: (Optional) Classifier (e.g., "sources", "javadoc")

**Usage Example:**

```python
# Through the Claude Code assistant:
mcp__mvn-mcp-server__check_version_tool(
    dependency="org.springframework:spring-core",
    version="5.3.10"
)

# With optional parameters:
mcp__mvn-mcp-server__check_version_tool(
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
    "exists": true,
    "current_version": "5.3.10",
    "latest_versions": {
      "major": "7.0.0-M4",
      "minor": "5.3.39",
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

> **Note:** The server still maintains the original `check_maven_version`, `get_maven_latest_version`, and `find_maven_version` tools for backward compatibility, but they now use the comprehensive `check_version_tool` internally.

### Check Maven Version Batch Tool

A batch processing tool that checks multiple Maven dependency versions in a single request.

**Tool Name:** `mvn-mcp-server__check_version_batch_tool`

**Parameters:**
- `dependencies`: A list of dependency objects, each containing:
  - `dependency`: Maven dependency in format `groupId:artifactId`
  - `version`: Version string to check
  - `packaging`: (Optional) Package type, defaults to "jar"
  - `classifier`: (Optional) Classifier

**Usage Example:**

```python
# Through the Claude Code assistant:
mcp__mvn-mcp-server__check_version_batch_tool(
    dependencies=[
        {
            "dependency": "org.springframework:spring-core",
            "version": "5.3.10"
        },
        {
            "dependency": "org.apache.logging.log4j:log4j-core",
            "version": "2.17.0",
            "packaging": "jar"
        },
        {
            "dependency": "com.fasterxml.jackson.core:jackson-databind",
            "version": "2.14.0",
            "packaging": "jar",
            "classifier": "sources"
        }
    ]
)
```

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
        "major": 1,
        "minor": 2,
        "patch": 3
      }
    },
    "dependencies": [
      {
        "dependency": "org.springframework:spring-core",
        "status": "success",
        "result": {
          "exists": true,
          "current_version": "5.3.10",
          "latest_versions": {
            "major": "7.0.0-M4",
            "minor": "5.3.39",
            "patch": "5.3.39"
          },
          "update_available": {
            "major": true,
            "minor": true,
            "patch": true
          }
        }
      },
      {
        "dependency": "org.apache.logging.log4j:log4j-core",
        "status": "success",
        "result": {
          "exists": true,
          "current_version": "2.17.0",
          "latest_versions": {
            "major": "2.22.1",
            "minor": "2.22.1",
            "patch": "2.17.2"
          },
          "update_available": {
            "major": true,
            "minor": true,
            "patch": true
          }
        }
      },
      {
        "dependency": "com.fasterxml.jackson.core:jackson-databind",
        "status": "success",
        "result": {
          "exists": true,
          "current_version": "2.14.0",
          "latest_versions": {
            "major": "2.17.0",
            "minor": "2.17.0",
            "patch": "2.14.3"
          },
          "update_available": {
            "major": true,
            "minor": true,
            "patch": true
          }
        }
      }
    ]
  }
}
```

### List Available Versions Tool

A tool that provides structured information about all available versions of a Maven dependency, grouped by minor version tracks.

**Tool Name:** `mvn-mcp-server__list_available_versions_tool`

**Parameters:**
- `dependency`: Maven dependency in format `groupId:artifactId` (e.g., "org.springframework:spring-core")
- `version`: Current version string to use as reference (e.g., "5.3.10")
- `packaging`: (Optional) Package type (jar, war, pom, etc.), defaults to "jar"
- `classifier`: (Optional) Classifier (e.g., "sources", "javadoc")
- `include_all_versions`: (Optional) Whether to include all versions in the response, defaults to false

**Usage Example:**

```python
# Through the Claude Code assistant:
# Basic usage - Get latest versions per track
mcp__mvn-mcp-server__list_available_versions_tool(
    dependency="org.springframework:spring-core",
    version="5.3.10"
)

# Include all versions in each track
mcp__mvn-mcp-server__list_available_versions_tool(
    dependency="org.springframework:spring-core",
    version="5.3.10",
    include_all_versions=True
)

# With optional parameters
mcp__mvn-mcp-server__list_available_versions_tool(
    dependency="org.springframework:spring-core",
    version="5.3.10",
    packaging="jar",
    classifier="sources",
    include_all_versions=True
)
```

**Response Format:**
```json
{
  "tool_name": "list_available_versions",
  "status": "success",
  "result": {
    "current_version": "5.3.10",
    "current_exists": true,
    "latest_version": "6.2.6",
    "minor_tracks": {
      "6.2": {
        "latest": "6.2.6",
        "is_current_track": false
      },
      "6.1": {
        "latest": "6.1.8",
        "is_current_track": false
      },
      "6.0": {
        "latest": "6.0.17",
        "is_current_track": false
      },
      "5.3": {
        "latest": "5.3.39",
        "is_current_track": true,
        "versions": ["5.3.0", "5.3.1", "5.3.2", "5.3.3", "5.3.4", "5.3.5", 
                    "5.3.6", "5.3.7", "5.3.8", "5.3.9", "5.3.10", "5.3.11",
                    "5.3.12", "5.3.13", "5.3.14", "5.3.15", "5.3.16", "5.3.17",
                    "5.3.18", "5.3.19", "5.3.20", "5.3.21", "5.3.22", "5.3.23",
                    "5.3.24", "5.3.25", "5.3.26", "5.3.27", "5.3.28", "5.3.29",
                    "5.3.30", "5.3.31", "5.3.32", "5.3.33", "5.3.34", "5.3.35",
                    "5.3.36", "5.3.37", "5.3.38", "5.3.39"]
      },
      "5.2": {
        "latest": "5.2.25",
        "is_current_track": false
      },
      "5.1": {
        "latest": "5.1.21",
        "is_current_track": false
      },
      "5.0": {
        "latest": "5.0.20",
        "is_current_track": false
      }
    }
  }
}
```

When `include_all_versions` is false (default), only the current track will include the full `versions` array. When true, all minor tracks will include their complete version lists.

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
uv run pytest src/mvn_mcp_server/tests/tools/test_check_version.py
```

### Architecture

The server implements a layered architecture:
- **Service Layer**: Core functionality for Maven API interactions, caching, and version handling
- **Tool Layer**: MCP tool implementations that use the service layer
- **Shared Utilities**: Common utilities for validation and error handling

## License

[MIT License](LICENSE)