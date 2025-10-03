# ADR-009: External Tool Integration Pattern

## Status
**Accepted** - 2025-01-24

## Context
Security vulnerability scanning is a complex domain with rapidly evolving threat databases. Rather than implementing our own scanner, we needed to integrate with best-in-class security tools. This decision established a pattern for integrating external command-line tools.

## Decision
Integrate external tools via **subprocess execution with JSON output parsing**, using Trivy as the primary example.

## Rationale
1. **Leverage Expertise**: Security tools like Trivy have years of development
2. **Stay Current**: Vulnerability databases update daily
3. **Avoid Reinvention**: No need to implement CVE matching ourselves
4. **Maintainability**: Let tool maintainers handle updates
5. **User Choice**: Users can update tools independently

## Implementation Pattern

### 1. Tool Execution
```python
def scan_with_trivy(workspace: str, options: dict) -> dict:
    """Execute Trivy and parse results."""
    cmd = [
        "trivy", "fs",
        "--scanners", "vuln",
        "--format", "json",  # Always request JSON output
        "--quiet",           # Suppress progress output
        workspace
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            return handle_tool_error(result)
            
        return json.loads(result.stdout)
        
    except FileNotFoundError:
        return {
            "error": "Trivy not installed. Please install: https://trivy.dev"
        }
    except subprocess.TimeoutExpired:
        return {
            "error": "Scan timeout after 5 minutes"
        }
```

### 2. Graceful Degradation
```python
def check_tool_availability(tool_name: str) -> bool:
    """Check if external tool is available."""
    try:
        subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            timeout=5
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

# In tool implementation
if not check_tool_availability("trivy"):
    return format_error_response(
        "scan_java_project",
        "TOOL_NOT_AVAILABLE",
        "Trivy is not installed. Please see: https://trivy.dev/install"
    )
```

### 3. Output Parsing
```python
def parse_trivy_results(raw_results: dict) -> dict:
    """Transform Trivy output to MCP format."""
    vulnerabilities = []
    
    for result in raw_results.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            vulnerabilities.append({
                "id": vuln["VulnerabilityID"],
                "package": vuln["PkgName"],
                "severity": vuln["Severity"],
                "installed_version": vuln["InstalledVersion"],
                "fixed_version": vuln.get("FixedVersion", "none"),
                "description": vuln.get("Description", "")
            })
    
    return {
        "total_vulnerabilities": len(vulnerabilities),
        "vulnerabilities": vulnerabilities,
        "scan_date": datetime.now().isoformat()
    }
```

## Design Principles
1. **JSON Communication**: Always use JSON for structured data exchange
2. **Timeout Protection**: Prevent hanging on long operations
3. **Clear Error Messages**: Guide users to install/fix issues
4. **Version Compatibility**: Check tool version if format changes
5. **Optional Enhancement**: Tool absence doesn't break core functionality

## Security Considerations
- **Command Injection**: Never interpolate user input into commands
- **Path Validation**: Validate workspace paths before passing to tools
- **Output Limits**: Implement pagination for large results
- **Resource Limits**: Set timeouts and memory limits

## Alternatives Considered
1. **Library Integration**
   - **Pros**: Tighter integration, no subprocess overhead
   - **Cons**: Language limitations, version coupling
   - **Decision**: Rejected due to Trivy being Go-based

2. **REST API Integration**
   - **Pros**: Clean interface, no subprocess
   - **Cons**: Requires service running, network dependency
   - **Decision**: Rejected for simplicity

3. **Reimplementation**
   - **Pros**: Full control, no dependencies
   - **Cons**: Massive effort, inferior results
   - **Decision**: Rejected as impractical

## Consequences
**Positive:**
- Best-in-class tool capabilities
- Independent tool updates
- Clear separation of concerns
- Users can choose tool versions
- Supports future tool integrations

**Negative:**
- External dependency for features
- Subprocess overhead
- Potential format changes
- Platform-specific tool availability
- Additional installation step for users

## Future Applications
This pattern can be extended for:
- License scanning (scancode-toolkit)
- Dependency tree analysis (mvn dependency:tree)
- SBOM generation (syft)
- Code quality analysis (sonarqube)

## Success Criteria
- Clean tool output parsing
- Graceful handling when tool is missing
- Performance overhead <1 second for tool invocation
- Clear error messages guiding installation
- No security vulnerabilities from command execution