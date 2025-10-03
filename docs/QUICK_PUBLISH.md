# Quick Publishing Checklist

## Immediate Actions to Enable Publishing

### ✅ Step 1: Fix GitHub Actions Permissions (REQUIRED for PyPI)

**What**: Enable GitHub Actions to create Pull Requests

**Why**: Your Release Please workflow is currently failing because it can't create release PRs

**How**:
1. Go to: https://github.com/danielscholl/mvn-mcp-server/settings/actions
2. Scroll to "Workflow permissions"
3. ✅ Check: **"Allow GitHub Actions to create and approve pull requests"**
4. Click **Save**

**Result**: Next time you push commits to main, Release Please will create a release PR

---

### 📦 Step 2: Verify PyPI Publishing Works

**After enabling permissions above:**

1. **Make a test commit** (already done - you have fixes ready!)
   ```bash
   git commit -m "fix(ci): test release workflow"
   ```

2. **Push to main**
   ```bash
   git push origin main
   ```

3. **Wait for Release Please**
   - A new PR should appear titled "chore(main): release 0.2.1" (or similar)
   - This PR will contain updated CHANGELOG and version bump

4. **Merge the Release PR**
   - Review the auto-generated CHANGELOG
   - Merge the PR
   - GitHub Actions will automatically publish to PyPI

**Verify Success**:
```bash
# After a few minutes, check if published
pip index versions mvn-mcp-server
```

---

### 🌐 Step 3: Publish to MCP Registry (Optional but Recommended)

**Prerequisites**:
```bash
# Install MCP publisher
brew install mcp-publisher
# If brew doesn't work, download from:
# https://modelcontextprotocol.info/tools/registry/publishing/
```

**Publishing Steps**:

1. **Update version in server.json**
   - Match the version that was just published to PyPI
   - Edit `server.json` line 3: `"version": "0.2.1"`

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

---

## Testing Installation

After publishing, test both methods:

### Test PyPI Installation
```bash
# Create test directory
mkdir /tmp/test-mvn-mcp && cd /tmp/test-mvn-mcp

# Test with uvx
uvx mvn-mcp-server --version

# Test with pip
pip install mvn-mcp-server
python -c "import mvn_mcp_server; print(mvn_mcp_server.__version__)"
```

### Test MCP Configuration
```bash
# Create test config
cat > test-mcp.json << 'EOF'
{
  "mcpServers": {
    "mvn-mcp-server": {
      "command": "uvx",
      "args": ["mvn-mcp-server"]
    }
  }
}
EOF

# Test with MCP client (if you have one configured)
```

---

## What You Get

### After PyPI Publishing ✅
- Users can install with `pip install mvn-mcp-server`
- Users can run with `uvx mvn-mcp-server`
- Package appears at https://pypi.org/project/mvn-mcp-server/
- Automated releases via GitHub

### After MCP Registry Publishing ✅
- Server discoverable in MCP ecosystem
- Listed at MCP registry
- Easier for non-Python MCP users
- Official MCP server listing

---

## Current Status Checklist

- [ ] Enable GitHub Actions PR permissions (Step 1)
- [ ] Verify first PyPI release works (Step 2)
- [ ] Install MCP publisher CLI (Step 3)
- [ ] Publish to MCP Registry (Step 3)
- [ ] Test both installation methods
- [ ] Update README with installation instructions

---

## Common Issues

### "Release Please not creating PR"
- Ensure permissions are enabled (Step 1)
- Check that commits use conventional commit format
- Look at GitHub Actions logs for errors

### "PyPI publish fails"
- Check if PyPI package name is available
- Verify GitHub Actions has proper permissions
- Check release workflow logs

### "MCP publisher command not found"
- Install via brew: `brew install mcp-publisher`
- Or download binary from official docs
- Add to PATH if needed

---

## Next Steps After Publishing

1. **Update README.md** - Add installation badges and instructions
2. **Create GitHub Release Notes** - Highlight key features
3. **Announce** - Share on relevant communities
4. **Monitor** - Watch for issues from early users

---

## Quick Reference

| Task | Command |
|------|---------|
| Check PyPI version | `pip index versions mvn-mcp-server` |
| Install from PyPI | `pip install mvn-mcp-server` |
| Run with uvx | `uvx mvn-mcp-server` |
| Validate server.json | `mcp-publisher validate` |
| Publish to MCP | `mcp-publisher publish` |
| Check MCP registry | `curl "https://registry.modelcontextprotocol.io/v0/servers?search=mvn-mcp-server"` |

---

For detailed information, see [PUBLISHING.md](./PUBLISHING.md)
