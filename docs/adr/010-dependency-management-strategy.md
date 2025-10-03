# ADR-010: Dependency Management Strategy

## Status
**Accepted** - 2025-01-24

## Context
During initial setup and testing, we discovered that the project's dependencies needed refinement. The original imports referenced `mcp.server.fastmcp` which doesn't exist in the current FastMCP package structure. Additionally, we needed to clarify our HTTP client strategy.

## Decision
1. Use **FastMCP** (>=2.0.0) as the primary MCP framework dependency
2. Use **httpx** (>=0.27.0) as the primary HTTP client for Maven Central API calls
3. Maintain **requests** (>=2.32.3) for compatibility with existing code
4. Use direct imports from `fastmcp` package (not nested paths)

## Rationale

### FastMCP vs MCP
- FastMCP is the actively maintained framework that provides the features we need
- The `mcp` package alone doesn't provide the server framework capabilities
- FastMCP 2.0+ has stable APIs and better exception handling

### Import Pattern
- The correct import is `from fastmcp import FastMCP`, not `from mcp.server.fastmcp`
- Exceptions are imported as `from fastmcp.exceptions import ValidationError, ResourceError, ToolError`
- This aligns with the actual package structure of FastMCP

### HTTP Client Strategy
- **httpx**: Modern, supports both sync and async, better connection pooling
- **requests**: Kept for compatibility, widely used and stable
- Both libraries coexist without conflicts

## Consequences

**Positive:**
- Clear dependency specifications prevent version conflicts
- Correct import patterns prevent ModuleNotFoundError issues
- Modern HTTP client (httpx) provides better performance
- Maintaining requests ensures backward compatibility

**Negative:**
- Two HTTP libraries increase dependency footprint
- Must ensure team uses correct import patterns
- Version pinning may require periodic updates

## Implementation Notes

### Correct Import Patterns
```python
# Framework imports
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError, ResourceError, ToolError

# HTTP client imports
import httpx  # Primary for new code
import requests  # For compatibility
```

### pyproject.toml Dependencies
```toml
dependencies = [
    "fastmcp>=2.0.0",
    "pydantic>=2.11.4",
    "requests>=2.32.3",
    "httpx>=0.27.0",
]
```

## Migration Guide
When updating existing code:
1. Replace `from mcp.server.fastmcp` with `from fastmcp`
2. Ensure FastMCP version is >=2.0.0
3. Add httpx to dependencies if using MavenApiService

## References
- FastMCP Documentation: https://github.com/fastmcp/fastmcp
- Issue #1: Initial dependency configuration issues