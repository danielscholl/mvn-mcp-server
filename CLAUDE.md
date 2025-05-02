# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Install dependencies: `uv sync`
- Install in dev mode: `uv pip install -e .`
- Run all tests: `uv run pytest`
- Run specific test: `uv run pytest src/maven_mcp_server/tests/tools/test_version_exist.py`
- Run specific test function: `uv run pytest src/maven_mcp_server/tests/tools/test_version_exist.py::TestCheckMavenVersionExists::test_successful_check_true`

## Code Style
- Use Python type hints for function parameters and return values
- Follow PEP 8 conventions for naming and formatting
- Use docstrings with Args/Returns/Raises sections in Google style
- Group imports: stdlib, third-party, local
- Error handling: Use specific exceptions from mcp.server.fastmcp.exceptions
- Class naming: PascalCase
- Function/variable naming: snake_case
- Use Pydantic models for data validation
- Validate input parameters and handle exceptions with appropriate error codes
- Tests should use pytest fixtures and mocks for external services

## Commit Guidelines
- Use conventional commit message format (Release Please compatible):
  * Format: `<type>(<scope>): <description>`
  * Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
  * Example: `fix(dependencies): update log4j to patch security vulnerability`
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