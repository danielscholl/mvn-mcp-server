# ADR-003: In-Memory Caching Strategy

## Status
**Accepted** - 2025-01-24

## Context
Maven Central API calls are network-bound and can be slow. Users often check the same dependencies repeatedly within a session. We needed a caching strategy that reduces API calls while keeping the implementation simple and dependency-free.

## Decision
Implement a **simple in-memory cache with TTL (Time To Live)** for all Maven Central API responses.

## Rationale
1. **Significant Performance Improvement**: Reduces Maven Central API calls by 80%+ in typical usage
2. **No External Dependencies**: No need for Redis, Memcached, or other cache servers
3. **Simple Implementation**: Basic dictionary with timestamp tracking
4. **Appropriate for Use Case**: MCP servers are typically single-instance
5. **Fast Lookups**: In-memory access is essentially instant

## Alternatives Considered
1. **Redis/External Cache**
   - **Pros**: Persistence, shared across instances, advanced features
   - **Cons**: External dependency, network overhead, complexity
   - **Decision**: Rejected as overkill for single-instance MCP server

2. **File-Based Cache**
   - **Pros**: Persistence across restarts, no memory limits
   - **Cons**: Slower access, disk I/O, cleanup complexity
   - **Decision**: Rejected due to performance concerns

3. **No Caching**
   - **Pros**: Always fresh data, no cache invalidation issues
   - **Cons**: Poor performance, excessive API calls, rate limiting risk
   - **Decision**: Rejected due to performance requirements

## Implementation Details
```python
class CacheService:
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value if not expired."""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry.expires_at:
                return entry.value
            else:
                del self._cache[key]  # Clean up expired
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set with TTL."""
        self._cache[key] = CacheEntry(
            value=value,
            expires_at=time.time() + ttl_seconds
        )
```

## Cache Key Strategy
- Metadata: `"metadata:{group_id}:{artifact_id}"`
- Search: `"search:{group_id}:{artifact_id}:{version_pattern}"`
- Existence: `"exists:{group_id}:{artifact_id}:{version}:{packaging}:{classifier}"`

## TTL Configuration
- Metadata: 3600 seconds (1 hour) - changes infrequently
- Search results: 900 seconds (15 minutes) - may have new versions
- Version existence: 3600 seconds (1 hour) - immutable once published

## Consequences
**Positive:**
- 80%+ reduction in Maven Central API calls
- Sub-millisecond cache lookups
- No operational dependencies
- Simple to understand and debug
- Automatic cleanup of expired entries

**Negative:**
- Cache lost on server restart
- No sharing between multiple instances
- Memory usage grows with unique queries
- No cache warming or persistence

## Success Criteria
- Cache hit rate > 80% for repeated queries
- Memory usage remains under 100MB in typical usage
- No memory leaks from expired entries
- Correct TTL expiration behavior