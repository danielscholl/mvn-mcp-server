# ADR-006: Flexible Version Parsing Strategy

## Status
**Accepted** - 2025-01-24

## Context
Maven has no enforced version format standard. In practice, artifacts use various versioning schemes: semantic versioning (1.2.3), calendar versioning (2024.01.15), simple numeric (5), and versions with qualifiers (1.0-SNAPSHOT, 2.0-RC1). We needed a parsing strategy that handles real-world Maven artifacts.

## Decision
Implement a **flexible version parser** that supports multiple version formats with intelligent comparison logic.

## Rationale
1. **Real-World Compatibility**: Must handle actual artifacts in Maven Central
2. **No Enforcement**: Cannot force projects to use specific version format
3. **Comparison Requirements**: Need to compare versions for "latest" detection
4. **Qualifier Handling**: SNAPSHOT, RC, alpha, beta are common and meaningful
5. **User Expectations**: Should match Maven's own version ordering

## Version Formats Supported

### 1. Semantic Versioning
```
1.2.3
1.2.3-SNAPSHOT
1.2.3-RC1
1.2.3.Final
```

### 2. Calendar Versioning
```
2024.01.15
20240115
2024.1
```

### 3. Simple Numeric
```
5
5.1
```

### 4. Partial Versions
```
1.0
2
```

## Implementation Approach
```python
def parse_version(version_str: str) -> Version:
    """Parse version into comparable components."""
    # Split base version and qualifier
    base, qualifier = split_version_qualifier(version_str)
    
    # Try parsing strategies in order
    if is_calendar_version(base):
        return parse_calendar_version(base, qualifier)
    elif is_semver(base):
        return parse_semver(base, qualifier)
    else:
        return parse_numeric(base, qualifier)

def compare_versions(v1: Version, v2: Version) -> int:
    """Compare with special qualifier ordering."""
    # Compare base components
    base_cmp = compare_base_versions(v1, v2)
    if base_cmp != 0:
        return base_cmp
    
    # Compare qualifiers with ordering:
    # SNAPSHOT < alpha < beta < RC < (none) < Final
    return compare_qualifiers(v1.qualifier, v2.qualifier)
```

## Qualifier Ordering Rules
1. **Development**: SNAPSHOT, dev, preview
2. **Pre-release**: alpha < beta < milestone < RC
3. **Release**: (no qualifier) = Final = RELEASE
4. **Special**: GA (Generally Available) = Final

## Edge Cases Handled
- Mixed format comparison (semver vs calendar)
- Unusual separators (-, _, .)
- Case variations (SNAPSHOT vs snapshot)
- Numeric qualifiers (RC1 vs RC2)
- Missing components (1.0 vs 1.0.0)

## Alternatives Considered
1. **Strict Semver Only**
   - **Pros**: Simple, well-defined rules
   - **Cons**: Rejects many real artifacts
   - **Decision**: Rejected as too restrictive

2. **String Comparison**
   - **Pros**: Very simple
   - **Cons**: Incorrect ordering (e.g., "9" > "10")
   - **Decision**: Rejected as fundamentally broken

3. **Maven's Version Comparator**
   - **Pros**: Official implementation
   - **Cons**: Requires JVM, complex rules
   - **Decision**: Rejected but used as reference

## Consequences
**Positive:**
- Handles 99%+ of real Maven artifacts
- Intuitive version ordering
- Graceful handling of edge cases
- Compatible with existing ecosystems

**Negative:**
- Complex parsing logic
- Potential for edge case bugs
- Must maintain compatibility with Maven's ordering
- Performance overhead for parsing

## Success Criteria
- Correctly parse all version formats in test suite
- Version comparison matches Maven's ordering
- Handle malformed versions gracefully
- Performance remains acceptable (<10ms per parse)