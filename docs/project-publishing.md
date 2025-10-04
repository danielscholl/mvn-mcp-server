# Publishing Guide

This guide explains how to publish the Maven MCP Server through PyPI and MCP Registry.

## Understanding the Distribution Strategy

Maven MCP Server is a **Python-based** MCP server that provides Maven Central repository integration. We publish through two channels:

1. **PyPI** (Python Package Index) - Primary distribution
2. **MCP Registry** - Secondary for MCP ecosystem discovery

## PyPI Publishing (Automated)

### Prerequisites

**Enable GitHub Actions Permissions:**
1. Go to: `https://github.com/danielscholl/mvn-mcp-server/settings/actions`
2. Under "Workflow permissions":
   - ✅ Check "Allow GitHub Actions to create and approve pull requests"
   - Click Save

### How It Works

Publishing is **fully automated** via Release Please and GitHub Actions:

1. **Make changes** using Conventional Commits:
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug"
   git commit -m "feat!: breaking change"  # Bumps major version
   ```

2. **Push to main** - Release Please automatically:
   - Detects releasable commits
   - Creates a release PR with:
     - Updated CHANGELOG.md
     - Bumped version in all tracked files
     - Release notes

3. **Merge release PR** - GitHub Actions automatically:
   - Creates GitHub release
   - Builds Python package
   - Publishes to PyPI

**No manual version bumps or publish commands needed!**

### Version Files Automatically Updated

Release Please updates these 5 files:

1. `pyproject.toml` - Python package version
2. `.release-please-manifest.json` - Release tracking
3. `CHANGELOG.md` - Auto-generated changelog
4. `server.json` - MCP Registry manifest version
5. `src/mvn_mcp_server/__init__.py` - Package `__version__`

### Conventional Commit Prefixes

| Prefix | Version Bump | Example |
|--------|-------------|---------|
| `feat:` | Minor (0.x.0) | `feat: add batch processing` |
| `fix:` | Patch (0.0.x) | `fix: resolve parsing error` |
| `feat!:` or `fix!:` | Major (x.0.0) | `feat!: change API format` |
| `docs:`, `chore:`, `test:` | No bump | Documentation/maintenance |

### Verifying Publication

After merging a release PR:

```bash
# Wait a few minutes, then check PyPI
pip index versions mvn-mcp-server

# Test installation
pip install mvn-mcp-server
```

## MCP Registry Publishing (Manual)

### Prerequisites

Install MCP publisher CLI:

```bash
# macOS
brew install mcp-publisher

# Or download from:
# https://modelcontextprotocol.info/tools/registry/publishing/
```

### Publishing Steps

1. **Ensure server.json is up to date**
   - Version should match latest PyPI release
   - Release Please automatically updates this

2. **Authenticate**
   ```bash
   mcp-publisher auth
   ```
   Follow prompts (GitHub login)

3. **Validate**
   ```bash
   mcp-publisher validate
   ```
   Should show "✓ server.json is valid"

4. **Publish**
   ```bash
   mcp-publisher publish
   ```

5. **Verify**
   ```bash
   curl "https://registry.modelcontextprotocol.io/v0/servers?search=mvn-mcp-server"
   ```

## Release Workflow

### Complete Release Process

```
1. Development: Make changes with conventional commits
2. Push to main
3. Release Please: Creates release PR automatically
4. Review: Check CHANGELOG and version bump
5. Merge: GitHub Actions publishes to PyPI automatically
6. MCP Registry: Run `mcp-publisher publish` (manual, one-time)
```

### First Release Setup

**One-time actions:**
1. ✅ Enable GitHub Actions PR permissions (see Prerequisites)
2. ✅ Configure PyPI Trusted Publishing (optional but recommended)
3. ✅ Install `mcp-publisher` CLI

**After that:**
- PyPI publishing is automatic
- MCP Registry needs manual publish after each release

## Troubleshooting

### Release Please Not Creating PR

**Issue**: No release PR appears after pushing commits

**Solutions**:
- Ensure commits use conventional commit format (`feat:`, `fix:`, etc.)
- Check GitHub Actions permissions are enabled
- Verify commits are actually releasable (not just `docs:` or `chore:`)
- Look at GitHub Actions logs for errors

### PyPI Publishing Fails

**Issue**: Release workflow fails during publish step

**Solutions**:
- Verify package name `mvn-mcp-server` is available on PyPI
- Check GitHub Actions has proper permissions
- Review release workflow logs for specific errors
- Ensure PyPI Trusted Publishing is configured (if using)

### MCP Publisher Command Not Found

**Issue**: `mcp-publisher: command not found`

**Solutions**:
- Install via brew: `brew install mcp-publisher`
- Download binary from official docs
- Add to PATH if installed but not found

### Version Mismatch

**Issue**: server.json version doesn't match PyPI

**Solution**: This should not happen if `extra-files` is configured in `release-please-config.json`. Verify:
```json
{
  "packages": {
    ".": {
      "extra-files": [
        "server.json",
        "src/mvn_mcp_server/__init__.py"
      ]
    }
  }
}
```

## Configuration Files

### release-please-config.json
Defines changelog sections and version update behavior

### .release-please-manifest.json
Tracks current version (0.2.0 → 1.0.0 → 1.0.1, etc.)

### server.json
MCP Registry manifest - automatically updated by Release Please

### .github/workflows/release.yml
GitHub Actions workflow for automated publishing

## Post-Release Tasks

After a successful release:

1. **Update MCP Registry** (if not done already):
   ```bash
   mcp-publisher publish
   ```

2. **Verify installations work**:
   ```bash
   # Test PyPI
   pip install mvn-mcp-server==<version>

   # Test uvx
   uvx mvn-mcp-server --version
   ```

3. **Announce** (optional):
   - Share on relevant communities
   - Update project website/documentation
   - Post release notes

## Best Practices

1. **Use Conventional Commits** - Enables automatic changelog and versioning
2. **Test Before Merging** - Ensure CI passes on all PRs
3. **Review Release PRs** - Verify CHANGELOG accuracy before merging
4. **Keep server.json Synced** - Let Release Please handle it automatically
5. **Manual MCP Publish** - Run after each PyPI release

## References

- [Release Please Documentation](https://github.com/googleapis/release-please)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [MCP Registry Publishing](https://modelcontextprotocol.info/tools/registry/publishing/)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
