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

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

