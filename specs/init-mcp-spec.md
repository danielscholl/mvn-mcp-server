# MCP Server Spec - mvn-mcp-server

> A minimal MCP server implementation to serve as a learning example and sanity check.

## 📋 Implementation Checklist

The following tasks must be completed in order:

1. [ ] 📁 Create project structure
2. [ ] 📝 Create pyproject.toml
3. [ ] 🛠️ Implement basic MCP server structure
4. [ ] 🧩 Implement required tools
5. [ ] 📊 Create tests for all components
6. [ ] 🚨 Validate implementation (see validation checklist below)

## METADATA Prompt Argument Handling

This prompt may receive additional arguments during initialization. Here's how to interpret this information:

The MCP server will receive the following arguments on initialization:

- Contains `<mcpServerName>` tag with the server name
  - Example: `<mcpServerName>my-mcp-server</mcpServerName>`
  - IMPORTANT: When used in Python code, hyphenated names must be converted to underscores
    - Example: "my-mcp-server" becomes "scrum_team_mcp_server" in Python
  
- Contains `<toolSpec>` with `<toolsToExpose>` section listing tools
  - Each tool has exactly three tags:
    - `<n>`: The tool function name (e.g., "reverse_tool")
    - `<description>`: Short description of the tool (e.g., "String Reverse")
    - `<details>`: Detailed explanation of the tool's functionality
  
- Complete Example:
    ```xml
    <mcpServerName>my-mcp-server</mcpServerName>
    <toolSpec>
        <toolsToExpose>
            <tool>
                <n>my_tool_name</n>
                <description>my tool description</description>
                <details>my tool details</details>
            </tool>
        </toolsToExpose>
    </toolSpec>
    ```

## Implementation Details

- Read ai_docs/** for Examples demonstrating Best Practices
- Update specs/init-mcp-spec.md with tool information if received.
- READ AGAIN the updated specs/init-mcp-spec.md after the update.

### Development Environment
- Python ≥ 3.12 with uv as the package manager
- Document all functions and classes with clear docstrings
- Focus on simplicity and clarity for demonstration purposes
- Document README.  
    - Use ai_docs/sample_readme.md to understand what a well formed README should look like.
    - Ensure there are usage examples.

### MCP Server Framework
- Use the standard `mcp` package (≥1.6.0) for MCP protocol compatibility
- Implement server using the high-level FastMCP approach via `mcp.server.fastmcp`
- The server will handle stdin/stdout communication with the client
- FastMCP automatically handles conversion of tool results to MCP protocol format
- Tool responses are returned as Python objects that FastMCP converts to proper `content` array format


#### Library Versions
- mcp ≥ 1.7.0
- pydantic ≥ 2.11.4
- requests ≥ 2.32.3


### Tool Response Flow
1. Tool function returns a native Python type (like a string or dictionary)
2. FastMCP automatically converts this to MCP format using TextContent objects
3. Error handling is simplified by using Python's native exception mechanism
   - Raised exceptions are automatically converted to appropriate error responses
   - FastMCP provides helper functions for standardized error responses

### Server Implementation Details

With FastMCP, the server implementation is simplified using decorators:

*Example*
```python
from mcp.server.fastmcp import FastMCP

# Create a FastMCP server instance
mcp = FastMCP("Template MCP Server")

# Register tools using decorators
@mcp.tool()
def sample_tool(name: str = "John") -> str:
    """Hello world sample tool."""
    return f"Hello, {name}!"

# Main entry point
if __name__ == "__main__":
    mcp.run()
```

The server supports:
1. Tool registration via decorators
2. Automatic handling of tool calls with proper argument passing
3. Automatic conversion of tool results to MCP protocol format
4. Built-in error handling with standardized error responses

### Testing Requirements
- Run tests with `uv run pytest`
- Tests should verify both success and error paths
- Keep tests simple but comprehensive

## Codebase Structure

> NOTE: $ARGUMENTS is a placeholder that should be replaced with the name of your MCP server (e.g., "my_mcp_server").
> All instances of $ARGUMENTS in this spec should be replaced with your chosen server name.
> When using hyphenated names like "my-mcp-server", they should be converted to valid Python package names by replacing hyphens with underscores (e.g., "my_mcp_server").


- pyproject.toml
- README.md
- src/
    - $mcpServerName/                   # Main package directory with your server name
        - __init__.py
        - main.py             # Entry point for the application
        - server.py           # FastMCP instance creation and tool registration
        - tools/
            - __init__.py
            - sample_tool.py  # File name should match the tool function name
            - ...
        - shared/
            - __init__.py
            - utils.py        # Helper functions for formatting, error handling, etc.
            - data_types.py   # Pydantic models for request/response validation
        - tests/
            - __init__.py
            - tools/
                - __init__.py
                - test_sample_tool.py  # Tests should match their implementation file names
                - ...
            - shared/
                - __init__.py
                - test_utils.py

## Project Configuration

- CREATE pyproject.toml
- Requires Python >=3.12
- Ensure Sections 
    - [project], [build-system], [tool.setuptools], [tool.pytest] ...
- Add [project.scripts] section to make package executable:
  ```toml
  [project.scripts]
  $mcpServerName= "$mcpServerName.main:main"  # This makes your server executable with the name matching your package
  ```

### Data Types Implementation

The `data_types.py` file should contain pydantic Data types and models for validating tool inputs.
These models can be used directly in your tool functions or for validation.

*Example*
```python
from pydantic import BaseModel, Field, field_validator

class GreetingRequest(BaseModel):
    """Request model for the sample_tool."""
    name: str = Field(default="John", description="The name to greet")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Name cannot be empty")
        return v

# You can then use this model in your tool implementation:
# from $mcpServerName.shared.data_types import GreetingRequest
# def sample_tool(request: GreetingRequest) -> str:
#     return f"Hello, {request.name}!"
```

### Utilities Implementation

The `utils.py` file should contain helper functions used across the server:

*Example*
```python
def format_error_response(error_code: str, error_message: str, details: dict = None) -> dict:
    """Format a standard error response."""
    response = {
        "error": {
            "code": error_code,
            "message": error_message
        }
    }
    if details:
        response["error"]["details"] = details
    return response
```

### Error Handling

Use the built-in exception classes from the MCP package:

```python
# For validation errors in tool inputs
from mcp.server.fastmcp.exceptions import ValidationError

# Usage example
if not name or not isinstance(name, str):
    raise ValidationError("Empty or invalid name parameter")
```

Available exception classes:
- `mcp.server.fastmcp.exceptions.ValidationError` - For input validation errors
- `mcp.server.fastmcp.exceptions.ToolError` - For errors during tool execution
- `mcp.server.fastmcp.exceptions.ResourceError` - For resource-related errors
- `mcp.server.fastmcp.exceptions.FastMCPError` - Base error class

### Error Codes

When to use each error code:

| Code | Meaning | When to Use |
|------|---------|-------------|
| INVALID_INPUT_FORMAT | Input validation failed | When user input doesn't meet expected format or constraints |
| INTERNAL_SERVER_ERROR | Unhandled server exception | For unexpected errors during tool execution |


## Tools to Expose

- CREATE def sample_tool(name: str = "John") -> str:
- Tool Description: Hello World Sample
- Import and registration pattern:
  ```python
  # In tools/sample_tool.py (filename should match function name)
  def sample_tool(name: str = "John") -> str:
      """Hello world sample tool."""
      return f"Hello, {name}!"
      
  # In server.py
  from $mcpServerName.tools.sample_tool import sample_tool
  mcp.tool()(sample_tool)
  ```

### Required .mcp.json Configuration

*Example*
```json
{
  "mcpServers": {
    "$mcpServerName": {  // Replace with your actual server name
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "$mcpServerName"  // Replace with your actual server name
      ],
      "env": {}
    }
  }
}
```

### Test Implementation Pattern

Example test for a tool function:

```python
# In tests/tools/test_sample_tool.py
import pytest
from mcp.server.fastmcp.exceptions import ValidationError
from $mcpServerName.tools.sample_tool import sample_tool

def test_sample_tool_default():
    """Test sample_tool with default parameter."""
    result = sample_tool()
    assert result == "Hello, John!"

def test_sample_tool_empty_name():
    """Test sample_tool with empty name."""
    with pytest.raises(ValidationError):
        sample_tool(name="")
```

## 🚨 REQUIRED VALIDATION CHECKLIST 🚨

Every implementation MUST complete all validation steps below in order:

1. [ ] ✅ `uv sync` - Install dependencies and create virtual environment
2. [ ] ✅ `uv pip install -e .` - Install the package in development mode
3. [ ] ✅ `uv run pytest` - Run all tests and ensure they pass
4. [ ] ✅ `uv run $mcpServerName --version` - Verify the server runs successfully

⚠️ **WARNING**: Skipping any validation step is not acceptable. Your implementation is not complete until all validation steps pass successfully.

📋 **Documentation**: Each validation step should be documented with the command output to confirm success.