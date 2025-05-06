# Maven MCP Server Tool Optimization Specification

## Overview

This specification outlines proposed improvements to the Maven MCP Server tools to optimize performance, reduce code duplication, and enhance maintainability. The current implementation includes three separate tools (`check_version`, `latest_version`, and `find_version`) with significant overlap in functionality and duplicated code.

## Current Implementation Analysis

### Issues Identified

1. **Code Duplication**:
   - Similar Maven Central API calls are implemented multiple times across tools
   - Version parsing and comparison logic is duplicated
   - Error handling patterns are repeated

2. **Inconsistent Fallback Mechanisms**:
   - `latest_by_semver.py` has complex fallback logic not present in other tools
   - Redundant HTTP requests when fallbacks are used

3. **API Efficiency**:
   - Multiple API calls are made when a single call could provide the necessary data
   - Inefficient parsing and re-parsing of version data

4. **Maintenance Challenges**:
   - Similar functions with slight variations make bug fixes difficult to apply consistently
   - Complex version parsing logic spread across multiple modules

## Proposed Solution

### 1. Core Service Layer

Create a shared service layer that provides core functionality used by all tools:

```
src/maven_mcp_server/
  └── services/
      ├── __init__.py
      ├── maven_api.py     # Maven Central API interactions
      └── version.py       # Version parsing and comparison logic
```

Key components:

#### Maven API Service (`maven_api.py`)

```python
class MavenApiService:
    def fetch_artifact_metadata(group_id, artifact_id):
        """Fetch and cache Maven metadata for an artifact"""
    
    def check_artifact_exists(group_id, artifact_id, version, packaging, classifier=None):
        """Check if specific artifact exists using HEAD request"""
    
    def get_all_versions(group_id, artifact_id):
        """Get all available versions using metadata.xml, with caching"""
    
    def search_artifacts(query, packaging=None, classifier=None):
        """Search Maven Central using Solr API"""
```

#### Version Service (`version.py`)

```python
class VersionService:
    def parse_version(version_string):
        """Unified version parsing that handles all formats"""
    
    def compare_versions(version1, version2):
        """Compare two version strings"""
    
    def filter_versions(versions, target_component, reference_version):
        """Filter versions based on target component (major, minor, patch)"""
    
    def get_latest_version(versions, include_snapshots=False):
        """Find latest version in a list"""
```

### 2. Unified Tool Implementation

Refactor tools to use the shared services:

```python
def check_version(dependency, version, packaging="jar", classifier=None):
    """Check if version exists, using the unified API service"""
    # Validate inputs
    group_id, artifact_id = utils.validate_maven_dependency(dependency)
    validated_version = utils.validate_version_string(version)
    
    # Get Maven API service
    maven_service = MavenApiService()
    
    # Direct check (most efficient path)
    exists = maven_service.check_artifact_exists(
        group_id, artifact_id, validated_version, packaging, classifier)
    
    return {"exists": exists}
```

### 3. Caching Layer

Implement a caching layer to reduce redundant API calls:

```python
class MavenCache:
    """Simple in-memory cache for Maven API responses with TTL"""
    
    def get(self, key):
        """Retrieve cached value if not expired"""
    
    def set(self, key, value, ttl=300):  # Default 5 minutes TTL
        """Store value with expiration time"""
    
    def invalidate(self, key_pattern=None):
        """Invalidate cache entries"""
```

### 4. Response Standardization

Standardize response formats across all tools:

```python
def format_success_response(tool_name, data):
    """Format a standardized success response"""
    return {
        "tool_name": tool_name,
        "status": "success",
        "result": data
    }

def format_error_response(tool_name, error_code, message, details=None):
    """Format a standardized error response"""
    response = {
        "tool_name": tool_name,
        "status": "error",
        "error": {
            "code": error_code,
            "message": message
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response
```

## Optimization Strategies

### 1. Maven Central API Access

1. **Single Source of Truth**:
   - Centralize all Maven Central API interactions in the `MavenApiService` class
   - Implement consistent retry and timeout logic

2. **Smart Fallback Mechanism**:
   - Create a prioritized fallback chain:
     1. Direct artifact URL check (fastest, for `check_version`)
     2. Metadata XML check (for version listings)
     3. Solr API search (for complex queries)

3. **Request Batching**:
   - Where possible, batch related requests to reduce HTTP overhead
   - Use async/await patterns for parallel requests when appropriate

### 2. Version Management

1. **Unified Version Parser**:
   - Create a single robust version parser that handles all cases
   - Support semantic versioning, calendar versioning, and custom formats

2. **Intelligent Version Filtering**:
   - Optimize the filtering of versions based on target component
   - Implement an efficient version comparator function

### 3. Error Handling

1. **Consistent Error Codes**:
   - Use the same error codes and messaging across all tools
   - Provide detailed context in error responses

2. **Graceful Degradation**:
   - Implement progressive fallback strategies when preferred methods fail
   - Log detailed diagnostics for troubleshooting

## Implementation Plan

### Phase 1: Core Services

1. Implement `MavenApiService` with caching
2. Implement unified `VersionService`
3. Add comprehensive tests for these services

### Phase 2: Tool Refactoring

1. Refactor `check_version` to use the new services
2. Refactor `latest_version` to use the new services
3. Refactor `find_version` to use the new services
4. Update all tests to verify consistency

### Phase 3: Performance Optimization

1. Add benchmarking to measure performance improvements
2. Optimize caching strategy based on usage patterns
3. Implement any additional optimizations identified

## API Changes

No changes to the external API contracts are required. All improvements will be internal to maintain backward compatibility.

## Testing Strategy

1. **Unit Tests**:
   - Comprehensive tests for each service function
   - Mocked Maven Central API responses for deterministic testing

2. **Integration Tests**:
   - End-to-end tests using real Maven Central dependencies
   - Performance comparison tests (before/after)

3. **Compatibility Tests**:
   - Verify all existing tool behaviors are preserved
   - Test with edge cases from real-world dependencies

## Expected Benefits

1. **Performance**:
   - Reduced API calls through caching and optimized request patterns
   - Faster tool execution, especially for repeated queries

2. **Maintenance**:
   - Easier bug fixes with centralized code
   - Simplified addition of new features

3. **Code Quality**:
   - Reduced duplication (estimated 30-40% code reduction)
   - Better separation of concerns

4. **Reliability**:
   - More consistent error handling
   - Better retry and fallback mechanisms

## Future Considerations

1. **Advanced Version Intelligence**:
   - Support for more complex version constraints (ranges, etc.)
   - Integration with vulnerability databases for security advisories


## 🚨 REQUIRED VALIDATION CHECKLIST 🚨

Every implementation MUST complete all validation steps in order:

1. [ ] ✅ Create and implement all required code
2. [ ] ✅ Write comprehensive tests covering the scenarios described above
3. [ ] ✅ Run test command: `uv run pytest src/maven_mcp_server/tests/tools/test_version_exist.py`
4. [ ] ✅ Ensure all tests pass successfully
5. [ ] ✅ Manually test with real-world Maven dependencies and versions

📝 **Note:** These validation steps are MANDATORY and must be completed in order. Each step depends on successful completion of previous steps.