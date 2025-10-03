# CLAUDE.md

This file guides AI assistants working with the Maven MCP Server codebase.

## Project Context

Maven MCP Server provides Model Context Protocol access to Maven Central repository for dependency management. It features intelligent caching, comprehensive version parsing, and security scanning capabilities optimized for AI-assisted development workflows.

## Build/Test Commands
- Install dependencies: `uv sync`
- Install in dev mode: `uv pip install -e ".[dev]"`
- Run all tests: `uv run pytest`
- Run specific test: `uv run pytest src/mvn_mcp_server/tests/tools/test_check_version.py`
- Run specific test function: `uv run pytest src/mvn_mcp_server/tests/tools/test_check_version.py::TestCheckVersion::test_success`

## Testing Guidelines & Troubleshooting

### Async Test Requirements
- **IMPORTANT**: Async tests require `pytest-asyncio` plugin (included in dev dependencies)
- Verify async plugin is installed: `uv run pytest --version` should show `asyncio-X.X.X`
- If async tests fail with "async def functions are not natively supported", ensure dev dependencies are installed: `uv pip install -e ".[dev]"`

### CI Environment Simulation
```bash
# Test with exact CI environment setup
uv sync --frozen                    # Use locked dependencies
uv pip install -e ".[dev]"         # Install with all dev dependencies
uv run pytest --cov=src/mvn_mcp_server --cov-report=xml --cov-report=term-missing --cov-fail-under=70 -v
```

### Common CI Failures
1. **Async test failures**: Missing pytest-asyncio → Add to dev dependencies and update uv.lock
2. **Coverage below 70%**: Run coverage locally with exact CI command above
3. **Import errors**: Ensure all new dependencies are in pyproject.toml and uv.lock is updated

## Code Style
- Use Python type hints for function parameters and return values
- Follow PEP 8 conventions for naming and formatting
- Use docstrings with Args/Returns/Raises sections in Google style
- Group imports: stdlib, third-party, local
- Error handling: Use specific exceptions from fastmcp.exceptions
- Class naming: PascalCase
- Function/variable naming: snake_case
- Use Pydantic models for data validation
- Validate input parameters and handle exceptions with appropriate error codes
- Tests should use pytest fixtures and mocks for external services

## Commit Guidelines
- Use conventional commit message format (Release Please compatible):
  * Format: `<type>(<scope>): <description>`
  * Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
  * Example: `fix(cache): update TTL for metadata caching`
  * Breaking changes: Add `!` after type/scope and include `BREAKING CHANGE:` in body
  * Example: `feat(api)!: change response format` with body containing `BREAKING CHANGE: API now returns JSON instead of XML`
- Ensure commit messages are concise and descriptive
- Explain the purpose and impact of changes in the commit message
- Group related changes in a single commit
- Keep commits focused and atomic
- For version bumps, use `chore(release): v1.2.3` format

## PR Description Guidelines
Use the output of the git diff to create the description of the Merge Request. Follow this structure exactly:

1. **Title**  
   *A one-line summary of the change (max 60 characters).*

2. **Summary**  
   *Briefly explain what this PR does and why.*

3. **Changes**  
   *List each major change as a bullet:*  
   - Change A: what was done  
   - Change B: what was done  

4. **Technical Details**
   *Highlight any notable technical details relevant to the changes*

## CHANGELOG Guidelines
- Maintain a CHANGELOG.md file in the root directory
- Add entries under the following sections:
  * `Added` - New features
  * `Changed` - Changes in existing functionality
  * `Fixed` - Bug fixes
  * `Security` - Vulnerability fixes
- Example:
  ```markdown
  ## 2024-03-20
  ### Added
  - New feature X
  ### Fixed
  - Bug fix Y
  ```

## Essential Commands

```bash
# Quality checks (run before committing)
uv run mypy . && uv run flake8 src/ && uv run pytest

# Individual commands
uv run pytest                    # Run all tests
uv run pytest -xvs              # Run tests, stop on first failure
uv run mypy .                   # Type checking
uv run flake8 src/              # Linting
uv run black src/               # Format code

# Development workflow
uv sync                         # Sync dependencies
uv pip install -e ".[dev]"      # Install package with dev dependencies (includes pytest-asyncio)
```

## Key Architecture Patterns

1. **Synchronous Architecture**: No async/await - simplifies implementation (ADR-002)
2. **Service Layer Pattern**: Business logic in services, not tools (ADR-007)
3. **Comprehensive Single-Call**: Tools return all relevant data in one response (ADR-005)
4. **In-Memory Caching**: TTL-based cache with strategic key design (ADR-003)
5. **Direct HTTP Integration**: No JVM dependency, pure Python (ADR-004)

## Core Documentation

- @docs/adr/index.md - Architectural decisions index
- @docs/project-architect.md - System architecture
- @docs/project-prd.md - Product requirements
- @docs/project-brief.md - Project overview
- @AI_EVOLUTION.md - Project evolution story for AI understanding
- @README.md - Getting started guide

## Development Guidelines

1. **Tool Implementation**: Follow patterns in `src/mvn_mcp_server/tools/`
2. **Service Design**: Keep business logic in service layer
3. **Testing**: Write mock-based tests, achieve 70%+ coverage
4. **Version Parsing**: Support multiple formats (semver, calendar, numeric)
5. **Error Responses**: Use standardized format with error codes

## Common Tasks

### Adding a New Tool
1. Create tool file in `src/mvn_mcp_server/tools/`
2. Implement using service layer for business logic
3. Register in `server.py` with `@mcp.tool` decorator
4. Return comprehensive data in single response
5. Write tests with mocked services

### Modifying Services
1. Update service in `src/mvn_mcp_server/services/`
2. Consider cache implications
3. Update tests to cover new scenarios
4. Maintain backwards compatibility

### Working with Version Parsing
- Version formats: semantic (1.2.3), calendar (2024.01.15), numeric (5)
- Qualifiers: SNAPSHOT < alpha < beta < RC < release
- Comparison must handle mixed formats correctly

## Testing Guidelines

- Mock external services at service boundaries
- Use `unittest.mock.patch.object` for service methods
- Test success and error scenarios
- Use fixtures for test data
- Run `uv run pytest` for all tests

## Important Context

- Direct HTTP integration with Maven Central (no Maven libraries)
- Caching is crucial - respect TTL settings
- Version parsing must handle real-world Maven artifacts
- External tools (Trivy) integrated via subprocess
- All responses optimized for AI consumption

## Maven-Specific Knowledge

### API Endpoints
- Metadata: `https://repo1.maven.org/maven2/{group}/{artifact}/maven-metadata.xml`
- Search: `https://search.maven.org/solrsearch/select`
- Artifacts: Direct URLs with HEAD requests for existence

### Caching Strategy
- Metadata: 1 hour TTL
- Search results: 15 minutes TTL
- Cache keys include all relevant parameters

### Security Scanning
- Trivy integration for vulnerability detection
- Graceful degradation if Trivy not installed
- JSON output parsing for structured results