# OSDU Maven MCP Server

[![CI](https://github.com/danielscholl/mvn-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/danielscholl/mvn-mcp-server/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/danielscholl/mvn-mcp-server)](https://github.com/danielscholl/mvn-mcp-server/releases)
[![Python](https://img.shields.io/badge/python-3.12%20|%203.13-blue)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green)](https://modelcontextprotocol.io)


A Model Context Protocol (MCP) server that enables AI assistants to interact with Maven Central repository, providing comprehensive tools for dependency version checking, security scanning, and dependency analysis.

## Documentation

- [Project Brief](docs/project-brief.md) - Executive summary and design philosophy
- [Project Requirements](docs/project-prd.md) - Comprehensive product requirements
- [Architecture Overview](docs/project-architect.md) - Technical architecture details
- [Architecture Design Decisions](docs/adr/index.md) - ADR catalog with decision rationale
- [AI Evolution Log](AI_EVOLUTION.md) - Project evolution story for AI understanding

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

Add the Maven MCP Server to your MCP client configuration (`.mcp.json`):

```json
{
  "mcpServers": {
    "mvn-mcp-server": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/danielscholl/mvn-mcp-server@main",
        "mvn-mcp-server"
      ],
      "env": {}
    }
  }
}
```

**VS Code Quick Install:**

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22mvn-mcp-server%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22git%2Bhttps%3A%2F%2Fgithub.com%2Fazure%2Fosdu-mvn-mcp%40main%22%2C%22mvn-mcp-server%22%5D%2C%22env%22%3A%7B%7D%7D)

## Usage

The MCP server provides several tools for working with Maven dependencies and Java projects. Below are examples of how to use each tool:

### Check Single Version

```
mvn:check_version_tool
Parameters:
- dependency: "group:artifact" (e.g., "org.apache.logging.log4j:log4j-core")
- version: "2.17.1"
- packaging: "jar" (optional, defaults to "jar")
- classifier: null (optional)
```

Checks if a specific version exists and provides update information.

### Batch Version Check

```
mvn:check_version_batch_tool
Parameters:
- dependencies: [
    {"dependency": "org.springframework:spring-core", "version": "5.3.0"},
    {"dependency": "com.fasterxml.jackson.core:jackson-databind", "version": "2.13.0"}
  ]
```

Process multiple dependency checks in a single request.

### List Available Versions

```
mvn:list_available_versions_tool
Parameters:
- dependency: "org.apache.commons:commons-lang3"
- version: "3.12.0" (current version for context)
- include_all_versions: false (optional)
```

Lists all available versions grouped by minor version tracks.

### Scan Java Project

```
mvn:scan_java_project_tool
Parameters:
- workspace: "/path/to/java/project"
- pom_file: "pom.xml" (optional, relative to workspace)
- scan_mode: "workspace" (optional)
- severity_filter: ["CRITICAL", "HIGH"] (optional)
```

Scans Maven projects for security vulnerabilities using Trivy.

### Analyze POM File

```
mvn:analyze_pom_file_tool
Parameters:
- pom_file_path: "/path/to/pom.xml"
- include_vulnerability_check: true (optional)
```

Analyzes a single POM file for dependencies and vulnerabilities.

## Available Tools

### Version Management
- **check_version_tool**: Check a Maven version and get all version update information
- **check_version_batch_tool**: Process multiple Maven dependency version checks in a single batch
- **list_available_versions_tool**: List all available versions grouped by minor version tracks

### Security Scanning  
- **scan_java_project_tool**: Scan Java Maven projects for vulnerabilities using Trivy
- **analyze_pom_file_tool**: Analyze a single Maven POM file for dependencies and vulnerabilities

## Available Prompts

Interactive conversation starters and guided workflows for complex dependency management tasks:

### Enterprise Workflow Prompts
- **list_mcp_assets**: Comprehensive overview of all server capabilities
  - Arguments: None
  - Usage: Dynamic listing of prompts, tools, and resources with examples
- **triage**: Analyze dependencies and create vulnerability triage report
  - Arguments: `service_name` (required), `workspace` (optional)
  - Usage: Comprehensive analysis following enterprise workflow: Discovery → Analysis → Security → Report
- **plan**: Create actionable update plan from triage results
  - Arguments: `service_name` (required), `priorities` (optional list)
  - Usage: Creates structured remediation plan with phases, tasks, and full traceability

### Using Prompts

Prompts provide guided workflows for complex dependency management tasks:

```bash
# Start a dependency triage
Use prompt: triage with service_name="my-service", workspace="./my-service"

# Create an update plan focusing on critical issues
Use prompt: plan with service_name="my-service", priorities=["CRITICAL", "HIGH"]

# View all server capabilities
Use prompt: list_mcp_assets
```

## Available Resources

Resources provide persistent state between prompt executions:

- **triage://reports/{service_name}/latest** - Latest triage report for a service
- **plans://updates/{service_name}/latest** - Current update plan for a service  
- **assets://server/capabilities** - Dynamic list of server capabilities

### Workflow Example

1. **Analyze Dependencies**
   ```
   Use prompt: triage("my-service")
   Result: Comprehensive analysis stored in triage://reports/my-service/latest
   ```

2. **Review Triage Report**
   ```
   Access resource: triage://reports/my-service/latest
   Contains: Vulnerabilities, outdated dependencies, POM analysis, recommendations
   ```

3. **Create Update Plan**
   ```
   Use prompt: plan("my-service", ["CRITICAL"])
   Result: Actionable plan stored in plans://updates/my-service/latest
   ```

4. **Implement Updates**
   ```
   Use individual tools to execute specific updates following the plan:
   - check_version_tool for validation
   - scan_java_project_tool for verification
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
uv run pytest src/mvn_mcp_server/tests/tools/test_check_version.py
```

### Architecture

The server implements a layered architecture:
- **Service Layer**: Core functionality for Maven API interactions, caching, and version handling
- **Tool Layer**: MCP tool implementations that use the service layer
- **Shared Utilities**: Common utilities for validation and error handling

## Contributing

This project welcomes contributions and suggestions.

For more information, see [CONTRIBUTING.md](CONTRIBUTING.md).


## Support

For support and help, see [SUPPORT.md](SUPPORT.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Development Notes

This project was developed using AI-assisted development workflows with Claude Code and GitHub Copilot. For insights into the AI-driven development process, see [AI_EVOLUTION.md](AI_EVOLUTION.md).