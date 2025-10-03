# GitHub Copilot Instructions for Maven MCP Server

This is a Python-based Model Context Protocol (MCP) server that provides AI assistants with access to Maven Central repository capabilities. The project follows an AI-driven development workflow with strict architectural patterns.

## Project Overview

Maven MCP Server enables AI assistants to interact with Maven Central for dependency management tasks. It provides tools for version checking, security scanning, and dependency analysis with intelligent caching and comprehensive responses.

## Code Standards

### Required Before Each Commit
Run these commands to ensure code quality:
```bash
uv run mypy .           # Type checking (must pass)
uv run flake8 src/      # Linting (must pass)
uv run black src/ tests/ # Format code
uv run pytest           # All tests must pass (70% coverage minimum)
```

### Development Flow
- Setup: `uv sync && uv pip install -e .[dev]`
- Test: `uv run pytest`
- Type check: `uv run mypy .`
- Format: `uv run black src/ tests/`
- Full check: `uv run mypy . && uv run flake8 src/ && uv run pytest`

## Repository Structure
- `src/mvn_mcp_server/`: Main package
  - `services/`: Core services (Maven API, caching, version parsing)
  - `shared/`: Common utilities and data types
  - `tools/`: MCP tool implementations
  - `server.py`: FastMCP server configuration
- `tests/`: Test suite mirroring src structure
- `docs/adr/`: Architectural Decision Records (MUST read before major changes)
- `specs/`: Tool specifications

## Key Architectural Patterns

1. **Synchronous Architecture**: No async/await - keeps implementation simple (ADR-002)
2. **Service Layer Pattern**: Separate services for Maven API, caching, and version logic (ADR-007)
3. **Comprehensive Single-Call**: Tools return all relevant data in one response (ADR-005)
4. **In-Memory Caching**: TTL-based cache reduces Maven Central API calls (ADR-003)
5. **Mock-Based Testing**: All external calls mocked for fast, reliable tests (ADR-008)

## Guidelines for Changes

### When Adding New Tools
1. Follow the existing pattern in `src/mvn_mcp_server/tools/`
2. Use service layer for business logic (don't put logic in tools)
3. Add comprehensive docstrings with Args/Returns sections
4. Return all relevant information in a single response
5. Write mock-based tests with >70% coverage

### When Modifying Services
1. Check if changes affect caching strategy
2. Ensure version parsing handles edge cases
3. Maintain backwards compatibility
4. Update tests to cover new scenarios

### Commit Message Format
Use Conventional Commits for Release Please automation:
- `feat:` New feature (minor version)
- `fix:` Bug fix (patch version)
- `chore:` Maintenance (no version change)
- `docs:` Documentation only
- `test:` Test improvements

### Issue Creation and Labels
When creating GitHub issues, apply appropriate labels from these categories:
1. **Type** (required): bug, enhancement, documentation, refactor, cleanup, testing, security, performance
2. **Priority**: high-priority, medium-priority, low-priority
3. **Component**: configuration, dependencies, github_actions, code-quality, ADR
4. **Status**: needs-triage, blocked, breaking-change, help wanted, good first issue
5. **AI Agent**: copilot (for issues suitable for Copilot implementation)

Example: `gh issue create -l "bug,high-priority,copilot"`

## Important Context

- This project uses direct HTTP integration with Maven Central (ADR-004)
- Version parsing supports multiple formats (semver, calendar, numeric) (ADR-006)
- External tools (like Trivy) integrated via subprocess (ADR-009)
- All tools follow the comprehensive single-call pattern
- Caching is crucial for performance - respect TTL settings

## Testing Requirements

- Minimum 70% test coverage required
- Tests should mock external services (Maven API calls)
- Use `unittest.mock` for mocking service methods
- Mock at service boundaries only
- Run `uv run pytest` to execute all tests

## Common Tasks Suitable for Copilot

- Adding new version comparison features
- Improving error messages for better AI understanding
- Extending version parsing for new formats
- Adding new batch processing capabilities
- Improving test coverage for edge cases
- Optimizing caching strategies

## Maven-Specific Considerations

### Version Handling
- Support semantic versioning (1.2.3)
- Handle calendar versions (2024.01.15)
- Parse qualifiers (SNAPSHOT, RC, alpha, beta)
- Compare versions correctly (1.9 < 1.10)

### API Integration
- Use metadata XML for version lists
- Fall back to Solr search API when needed
- Cache responses to minimize API calls
- Handle both old and new Maven repository layouts

### Security Scanning
- Trivy integration for vulnerability detection
- Support multi-module Maven projects
- Parse POM files for dependency extraction
- Provide actionable security recommendations