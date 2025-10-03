# ADR-007: Service Layer Architecture

## Status
**Accepted** - 2025-01-24

## Context
As the MCP server grew to support multiple tools with shared functionality, we needed a clear architectural pattern to avoid code duplication and maintain separation of concerns. The choice was between a flat structure with shared utilities or a proper service layer.

## Decision
Implement a **service layer architecture** with dedicated services for different responsibilities.

## Rationale
1. **Single Responsibility**: Each service handles one aspect of the system
2. **Reusability**: Services can be used by multiple tools
3. **Testability**: Services can be tested in isolation with mocks
4. **Clear Boundaries**: Well-defined interfaces between layers
5. **Maintainability**: Changes to Maven API don't affect tool logic

## Architecture Layers

### 1. Tool Layer (`tools/`)
- MCP protocol handling
- Parameter validation via FastMCP
- Response formatting
- Orchestrates service calls

### 2. Service Layer (`services/`)
- Business logic implementation
- External API integration
- Data transformation
- No MCP protocol knowledge

### 3. Shared Layer (`shared/`)
- Data models (Pydantic)
- Common utilities
- Constants and enums
- Cross-cutting concerns

## Service Responsibilities

### MavenApiService
```python
class MavenApiService:
    """Handles all Maven Central API interactions."""
    - check_version_exists()
    - get_metadata()
    - search_versions()
```

### CacheService
```python
class CacheService:
    """Manages in-memory caching with TTL."""
    - get()
    - set()
    - invalidate_pattern()
```

### VersionService
```python
class VersionService:
    """Version parsing and comparison logic."""
    - parse_version()
    - compare_versions()
    - find_latest_versions()
    - filter_versions_by_type()
```

### ResponseService
```python
"""Standardized response formatting."""
- format_success_response()
- format_error_response()
```

## Implementation Pattern
```python
# Tool layer - orchestrates services
def check_version(dependency: str, version: str) -> dict:
    try:
        # Initialize services
        cache = CacheService()
        maven_api = MavenApiService(cache)
        version_svc = VersionService()
        
        # Orchestrate service calls
        exists = maven_api.check_version_exists(...)
        versions = maven_api.search_versions(...)
        latest = version_svc.find_latest_versions(...)
        
        # Format response
        return format_success_response("check_version", {
            "exists": exists,
            "latest_versions": latest
        })
    except Exception as e:
        return format_error_response(...)

# Service layer - business logic
class MavenApiService:
    def check_version_exists(self, group_id, artifact_id, version):
        # Pure business logic
        cache_key = f"exists:{group_id}:{artifact_id}:{version}"
        
        if cached := self.cache.get(cache_key):
            return cached
            
        exists = self._check_maven_central(...)
        self.cache.set(cache_key, exists)
        return exists
```

## Alternatives Considered
1. **Monolithic Tools**
   - **Pros**: Simple, all logic in one place
   - **Cons**: Code duplication, hard to test, large files
   - **Decision**: Rejected due to maintainability concerns

2. **Shared Utilities Only**
   - **Pros**: Some code reuse, simple structure
   - **Cons**: Logic scattered, unclear responsibilities
   - **Decision**: Rejected as insufficient structure

3. **Repository Pattern**
   - **Pros**: More abstraction, database-like interface
   - **Cons**: Overengineered for our use case
   - **Decision**: Rejected as unnecessary complexity

## Consequences
**Positive:**
- Clear separation of concerns
- Easy to unit test services
- Reusable components across tools
- Consistent patterns throughout codebase
- Easy to add new tools

**Negative:**
- More files and directories
- Indirection between layers
- Need to maintain service interfaces
- Potential for over-abstraction

## Success Criteria
- Each service has a single, clear responsibility
- Services are reused by multiple tools
- Unit tests achieve >90% coverage on services
- New developers understand the architecture quickly