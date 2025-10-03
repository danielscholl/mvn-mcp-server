# ADR Catalog 

Optimized ADR Index for Agent Context

## Index

| id  | title                               | status | details |
| --- | ----------------------------------- | ------ | ------- |
| 001 | MCP Framework Selection             | acc    | [ADR-001](001-mcp-framework-selection.md) |
| 002 | Synchronous Architecture Choice     | acc    | [ADR-002](002-synchronous-architecture-choice.md) |
| 003 | In-Memory Caching Strategy          | acc    | [ADR-003](003-in-memory-caching-strategy.md) |
| 004 | Direct Maven Central HTTP Integration | acc    | [ADR-004](004-direct-maven-central-integration.md) |
| 005 | Comprehensive Single-Call Pattern   | acc    | [ADR-005](005-comprehensive-single-call-pattern.md) |
| 006 | Flexible Version Parsing Strategy   | acc    | [ADR-006](006-flexible-version-parsing-strategy.md) |
| 007 | Service Layer Architecture          | acc    | [ADR-007](007-service-layer-architecture.md) |
| 008 | Mock-Based Testing Strategy         | acc    | [ADR-008](008-mock-based-testing-strategy.md) |
| 009 | External Tool Integration Pattern   | acc    | [ADR-009](009-external-tool-integration-pattern.md) |
| 010 | Dependency Management Strategy      | acc    | [ADR-010](010-dependency-management-strategy.md) |
| 011 | MCP Prompts Implementation Strategy | acc    | [ADR-011](011-mcp-prompts-implementation.md) |

## ADR Records

--------------------------------------------
```yaml
id: 001
title: MCP Framework Selection
status: accepted
date: 2025-05-25
decision: Use FastMCP framework to implement the MCP server.
why: |
• \~70 % less boilerplate than raw MCP
• Built‑in type safety & JSON‑RPC handling
• Familiar CLI‑style pattern
• Active community & docs
tradeoffs:
positive: \[fast-dev, fewer protocol bugs, auto validation]
negative: \[framework lock‑in, less low‑level control]
```

--------------------------------------------
```yaml
id: 002
title: Synchronous Architecture Choice
status: accepted
date: 2025-01-24
decision: Use synchronous (non-async) implementation throughout the codebase.
why: |
• Maven operations are inherently I/O bound but sequential
• Simpler debugging and error handling
• No concurrent state management needed
• FastMCP framework is sync-based
tradeoffs:
positive: \[simpler code, easier debugging, no async complexity]
negative: \[limited concurrent requests, potential blocking on slow APIs]
```

--------------------------------------------
```yaml
id: 003
title: In-Memory Caching Strategy
status: accepted
date: 2025-01-24
decision: Implement simple in-memory cache with TTL for Maven API responses.
why: |
• Reduces Maven Central API calls by 80%+
• No external dependencies (Redis, etc.)
• Simple TTL-based expiration
• Fast lookups for repeated queries
tradeoffs:
positive: \[fast, simple, no dependencies, effective]
negative: \[lost on restart, no sharing between instances, memory usage]
```

--------------------------------------------
```yaml
id: 004
title: Direct Maven Central HTTP Integration
status: accepted
date: 2025-01-24
decision: Use direct HTTP calls to Maven Central instead of Maven libraries.
why: |
• No JVM or Maven installation required
• Full control over caching and retries
• Lightweight - just HTTP requests
• Dual API approach (XML metadata + JSON search)
tradeoffs:
positive: \[lightweight, flexible, no dependencies, full control]
negative: \[reimplementing Maven logic, API changes impact us]
```

--------------------------------------------
```yaml
id: 005
title: Comprehensive Single-Call Pattern
status: accepted
date: 2025-01-24
decision: Each tool returns complete information in a single call.
why: |
• Reduces MCP protocol round-trips
• Better UX for AI assistants
• Efficient use of cached data
• Predictable response structure
implementation: |
• check_version returns: existence + all latest versions + update info
• Single API call provides complete context
tradeoffs:
positive: \[efficient, complete info, better UX]
negative: \[larger responses, potential over-fetching]
```

--------------------------------------------
```yaml
id: 006
title: Flexible Version Parsing Strategy
status: accepted
date: 2025-01-24
decision: Support multiple version formats with custom parser.
why: |
• Maven has no enforced version standard
• Handle semver, calendar, numeric formats
• Support qualifiers (SNAPSHOT, RC, etc.)
• Real-world compatibility required
implementation: |
• Parse into comparable components
• Handle partial versions gracefully
• Qualifier ordering (SNAPSHOT < alpha < beta < RC < release)
tradeoffs:
positive: \[handles real artifacts, flexible, robust]
negative: \[complex parsing logic, edge cases]
```

--------------------------------------------
```yaml
id: 007
title: Service Layer Architecture
status: accepted
date: 2025-01-24
decision: Separate services for Maven API, caching, version handling.
why: |
• Single responsibility principle
• Easy to test in isolation
• Clear boundaries between concerns
• Reusable across multiple tools
tradeoffs:
positive: \[maintainable, testable, clear structure]
negative: \[more files, indirection layers]
```

--------------------------------------------
```yaml
id: 008
title: Mock-Based Testing Strategy
status: accepted
date: 2025-01-24
decision: Use mocks for all external service calls in tests.
why: |
• Tests run without network access
• Deterministic test results
• Fast test execution (<5 seconds)
• Test edge cases easily
implementation: |
• Mock MavenApiService for tools
• Mock HTTP calls for services
• Use fixtures for test data
tradeoffs:
positive: \[fast, reliable, offline testing]
negative: \[mock maintenance, integration gaps]
```

--------------------------------------------
```yaml
id: 009
title: External Tool Integration Pattern
status: accepted
date: 2025-01-24
decision: Integrate security scanning via subprocess calls to external tools.
why: |
• Leverage best-in-class tools (Trivy)
• No need to reimplement scanning
• Graceful degradation if not installed
• Keep server lightweight
implementation: |
• JSON output parsing from tools
• Timeout handling for long scans
• Clear error when tool missing
tradeoffs:
positive: \[leverage existing tools, maintainable, up-to-date scanning]
negative: \[external dependency, subprocess overhead]
```

--------------------------------------------
```yaml
id: 010
title: Dependency Management Strategy
status: accepted
date: 2025-01-24
decision: Use FastMCP>=2.0.0 with correct import patterns and httpx for HTTP.
why: |
• FastMCP 2.0+ has stable APIs
• Correct imports prevent ModuleNotFoundError
• httpx provides better connection pooling
• Maintain requests for compatibility
implementation: |
• Import from fastmcp not mcp.server.fastmcp
• Use fastmcp.exceptions for error types
• httpx for new HTTP code
• Keep requests for backward compatibility
tradeoffs:
positive: \[clear deps, modern HTTP client, no import errors]
negative: \[two HTTP libraries, version pinning needed]
```

--------------------------------------------
```yaml
id: 011
title: MCP Prompts Implementation Strategy
status: accepted
date: 2025-01-25
decision: Implement MCP Prompts with Resources for enterprise dependency management workflows using simplified, memorable prompt names.
why: |
• Enable guided workflows for complex dependency management
• Provide enterprise-grade structure and documentation
• Maintain state between workflow steps with Resources
• Simplify usage with memorable names (triage vs dependency_triage)
tradeoffs:
positive: \[complete workflows, enterprise ready, knowledge transfer, audit compliance, simple usage]
negative: \[complexity, resource management, learning curve]
```