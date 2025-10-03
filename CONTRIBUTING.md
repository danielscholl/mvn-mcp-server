# Contributing to Maven MCP Server

Thank you for your interest in contributing to the Maven MCP Server!

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/danielscholl/mvn-mcp-server.git
   cd mvn-mcp-server
   ```

2. Install dependencies:
   ```bash
   uv sync
   uv pip install -e '.[dev]'
   ```

3. Run tests:
   ```bash
   uv run pytest
   ```

### Code Quality

Before submitting a pull request, ensure all quality checks pass:

```bash
uv run black src/
uv run flake8 src/
uv run mypy .
uv run pytest --cov=src/mvn_mcp_server --cov-fail-under=70
```

### Commit Guidelines

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated release management. Format your commit messages as:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(tools): add batch version checking support

Implements batch processing for multiple dependency version checks
to improve performance when analyzing large projects.
```

### Testing

#### Run All Tests

```bash
uv run pytest
```

#### Run Specific Tests

```bash
# Run tests for a specific module
uv run pytest src/mvn_mcp_server/tests/tools/test_check_version.py

# Run a specific test function
uv run pytest src/mvn_mcp_server/tests/tools/test_check_version.py::TestEnhancedVersionCheck::test_successful_check

# Run with verbose output
uv run pytest -xvs
```

#### Coverage

```bash
# Run with coverage report
uv run pytest --cov=src/mvn_mcp_server --cov-report=term-missing --cov-fail-under=70

# Generate HTML coverage report
uv run pytest --cov=src/mvn_mcp_server --cov-report=html
open htmlcov/index.html
```

### Architecture

The server implements a layered architecture:

#### Service Layer (`src/mvn_mcp_server/services/`)
- **maven_api.py**: Maven Central API integration
- **version.py**: Version parsing and comparison
- **cache.py**: In-memory caching with TTL
- **response.py**: Response formatting utilities

#### Tool Layer (`src/mvn_mcp_server/tools/`)
- MCP tool implementations
- Uses service layer for business logic
- Provides standardized responses

#### Prompt Layer (`src/mvn_mcp_server/prompts/`)
- Enterprise workflow implementations
- Orchestrates multiple tools
- Provides guided multi-step processes

#### Resource Layer (`src/mvn_mcp_server/resources/`)
- Persistent state management
- URI-based access patterns
- Pydantic-validated data structures

#### Shared Components (`src/mvn_mcp_server/shared/`)
- Data types and Pydantic models
- Validation utilities
- Common error handling

See [docs/project-architect.md](docs/project-architect.md) for detailed architecture documentation.

### Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following code style guidelines
3. **Add tests** for new functionality
4. **Ensure tests pass** and coverage meets requirements
5. **Update documentation** if needed
6. **Use conventional commits** for commit messages
7. **Submit pull request** with clear description

### Code Review

All submissions require review. We use GitHub pull requests for this purpose. Reviewers will check:

- Code quality and style
- Test coverage
- Documentation completeness
- Commit message format
- Breaking changes properly documented

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

