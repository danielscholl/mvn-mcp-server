# ADR-005: Comprehensive Single-Call Pattern

## Status
**Accepted** - 2025-01-24

## Context
MCP tools communicate with AI assistants through a request-response pattern. Each tool call requires a round trip through the MCP protocol. We needed to decide whether tools should be granular (single-purpose) or comprehensive (multi-purpose).

## Decision
Implement **comprehensive single-call tools** that return all relevant information in one response.

## Rationale
1. **Reduced Round Trips**: Fewer MCP protocol exchanges improve performance
2. **Better UX**: AI assistants get complete context without follow-up questions
3. **Efficient Caching**: One call can leverage multiple cached values
4. **Natural Language Friendly**: Matches how users ask questions ("tell me about version X")
5. **Token Efficiency**: Single comprehensive response vs multiple small ones

## Alternatives Considered
1. **Granular Tools (Unix Philosophy)**
   - **Pros**: Single responsibility, composable, smaller responses
   - **Cons**: Multiple round trips, more complex for AI to orchestrate
   - **Decision**: Rejected due to MCP protocol overhead

2. **Optional Parameters for Detail Level**
   - **Pros**: Flexible response size, backwards compatible
   - **Cons**: Complex parameter management, inconsistent responses
   - **Decision**: Partially adopted for some tools (include_all_versions)

## Implementation Example

### Comprehensive Pattern (Chosen)
```python
def check_version(dependency: str, version: str) -> dict:
    """Single call returns existence + latest versions + update availability."""
    return {
        "tool_name": "check_version",
        "status": "success",
        "result": {
            "exists": True,
            "current_version": "5.3.10",
            "latest_versions": {
                "major": "6.0.0",
                "minor": "5.3.39",
                "patch": "5.3.12"
            },
            "update_available": {
                "major": True,
                "minor": True,
                "patch": True
            }
        }
    }
```

### Granular Pattern (Rejected)
```python
# Would require 4 separate tool calls:
exists = check_exists("org.springframework:spring-core", "5.3.10")
latest_patch = get_latest_patch("org.springframework:spring-core", "5.3.10")
latest_minor = get_latest_minor("org.springframework:spring-core", "5.3.10")
latest_major = get_latest_major("org.springframework:spring-core", "5.3.10")
```

## Tool Design Principles
1. **Anticipate Follow-up Questions**: Include data the user will likely need next
2. **Structured Responses**: Consistent format across all tools
3. **Summary + Details**: High-level info first, then specifics
4. **Batch Operations**: Support multiple items in one call where sensible

## Consequences
**Positive:**
- Single tool call provides complete information
- Better performance through fewer round trips
- Improved AI assistant experience
- More efficient use of cached data
- Natural conversation flow

**Negative:**
- Larger response payloads
- Potential over-fetching of data
- More complex tool implementation
- Harder to test individual components

## Success Criteria
- 90%+ of use cases satisfied with single tool call
- Response times remain under 2 seconds
- AI assistants rarely need follow-up tool calls
- Response size remains reasonable for LLM context windows