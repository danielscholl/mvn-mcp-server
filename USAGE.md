# Maven MCP Server - Usage Guide

Complete guide for using the Maven MCP Server tools, prompts, and resources.

## Table of Contents

- [Tools](#tools)
  - [Check Single Version](#check-single-version)
  - [Batch Version Check](#batch-version-check)
  - [List Available Versions](#list-available-versions)
  - [Scan Java Project](#scan-java-project)
  - [Analyze POM File](#analyze-pom-file)
- [Prompts](#prompts)
  - [List MCP Assets](#list-mcp-assets)
  - [Dependency Triage](#dependency-triage)
  - [Update Plan](#update-plan)
- [Resources](#resources)
- [Workflows](#workflows)

---

## Tools

### Check Single Version

Check if a specific Maven version exists and get update information.

**Tool**: `check_version_tool`

**Parameters**:
```json
{
  "dependency": "org.apache.logging.log4j:log4j-core",
  "version": "2.17.1",
  "packaging": "jar",       // optional, defaults to "jar"
  "classifier": null        // optional
}
```

**Example**:
```
Check version org.springframework:spring-core 5.3.0
```

**Response includes**:
- Version existence confirmation
- Latest major/minor/patch versions
- Update availability
- Version comparison

---

### Batch Version Check

Process multiple dependency version checks in a single request.

**Tool**: `check_version_batch_tool`

**Parameters**:
```json
{
  "dependencies": [
    {
      "dependency": "org.springframework:spring-core",
      "version": "5.3.0"
    },
    {
      "dependency": "com.fasterxml.jackson.core:jackson-databind",
      "version": "2.13.0"
    }
  ]
}
```

**Example**:
```
Check these dependencies:
- org.springframework:spring-core 5.3.0
- junit:junit 4.13.2
```

**Response includes**:
- Summary statistics (total, success, failed, updates available)
- Individual results for each dependency
- Batch processing efficiency

---

### List Available Versions

List all available versions of a Maven artifact grouped by minor version tracks.

**Tool**: `list_available_versions_tool`

**Parameters**:
```json
{
  "dependency": "org.apache.commons:commons-lang3",
  "version": "3.12.0",              // current version for context
  "include_all_versions": false     // optional, defaults to false
}
```

**Example**:
```
List all versions of org.apache.commons:commons-lang3
```

**Response includes**:
- Versions grouped by minor tracks (e.g., 3.12.x, 3.13.x)
- Latest version in each track
- Stable vs pre-release versions

---

### Scan Java Project

Scan Java Maven projects for security vulnerabilities using Trivy.

**Tool**: `scan_java_project_tool`

**Parameters**:
```json
{
  "workspace": "/path/to/java/project",
  "pom_file": "pom.xml",                    // optional, relative to workspace
  "scan_mode": "workspace",                 // optional
  "severity_filter": ["CRITICAL", "HIGH"]   // optional
}
```

**Example**:
```
Scan this Java project for vulnerabilities
```

**Response includes**:
- Vulnerability count by severity
- CVE details with descriptions
- Affected dependencies
- Fix recommendations

**Requirements**:
- Trivy must be installed (`brew install trivy` on macOS)
- Project must contain a `pom.xml` file

---

### Analyze POM File

Analyze a single Maven POM file for dependencies and vulnerabilities.

**Tool**: `analyze_pom_file_tool`

**Parameters**:
```json
{
  "pom_file_path": "/path/to/pom.xml",
  "include_vulnerability_check": true       // optional, defaults to true
}
```

**Example**:
```
Analyze this pom.xml file
```

**Response includes**:
- Dependency list with versions
- Vulnerability assessment
- Update recommendations
- Dependency tree structure

---

## Prompts

### List MCP Assets

Comprehensive overview of all server capabilities with examples.

**Prompt**: `list_mcp_assets_prompt`

**Arguments**: None

**Example**:
```
Show me what this MCP server can do
```

**Returns**:
- Complete list of tools with descriptions
- Available prompts with usage
- Resource URIs and formats
- Workflow examples
- Pro tips for effective usage

---

### Dependency Triage

Analyze dependencies and create comprehensive vulnerability triage report.

**Prompt**: `triage`

**Arguments**:
```json
{
  "service_name": "my-service",           // required
  "workspace": "./path/to/service"        // optional, defaults to ./{service_name}
}
```

**Example**:
```
Run a dependency triage for my-service
```

**Workflow**:
1. **Discovery**: Scans workspace for POM files
2. **Analysis**: Checks all dependencies for updates
3. **Security**: Runs vulnerability scan with Trivy
4. **Report**: Generates structured triage report
5. **Storage**: Saves to `triage://reports/{service_name}/latest`

**Output includes**:
- Vulnerability summary by severity
- Outdated dependencies
- Security findings with CVE details
- Remediation recommendations
- POM structure analysis

---

### Update Plan

Create actionable remediation plan from triage results with full traceability.

**Prompt**: `plan`

**Arguments**:
```json
{
  "service_name": "my-service",               // required
  "priorities": ["CRITICAL", "HIGH"]          // optional, defaults to all
}
```

**Example**:
```
Create an update plan for my-service focusing on critical issues
```

**Workflow**:
1. **Retrieve**: Loads triage report from resources
2. **Analyze**: Filters by priority levels
3. **Structure**: Organizes into implementation phases
4. **Plan**: Creates tasks with CVE traceability
5. **Storage**: Saves to `plans://updates/{service_name}/latest`

**Output includes**:
- Phase-based implementation plan
- Tasks with file locations and line numbers
- CVE traceability for each change
- Tool integration commands
- Quality assurance checklist

---

## Resources

Resources provide persistent state between prompt executions.

### Triage Reports

**URI**: `triage://reports/{service_name}/latest`

**Contains**:
- Metadata (report ID, timestamp, service name)
- Vulnerability findings by severity
- Outdated dependencies
- POM analysis results
- Recommendations

**Access**:
```
Read the triage report for my-service
```

### Update Plans

**URI**: `plans://updates/{service_name}/latest`

**Contains**:
- Plan metadata and progress
- Implementation phases
- Tasks with status tracking
- CVE traceability
- Success criteria

**Access**:
```
Show me the update plan for my-service
```

### Server Assets

**URI**: `assets://server/capabilities`

**Contains**:
- Server metadata
- Available tools
- Available prompts
- Available resources
- Quick start guide

**Access**:
```
Show server capabilities
```

---

## Workflows

### Complete Dependency Management Workflow

**Step 1: Analyze Dependencies**
```
Use prompt: triage("my-service", "./path/to/my-service")
```
Result: Comprehensive analysis stored in resources

**Step 2: Review Triage Report**
```
Read resource: triage://reports/my-service/latest
```
Contains: Vulnerabilities, outdated dependencies, recommendations

**Step 3: Create Update Plan**
```
Use prompt: plan("my-service", ["CRITICAL", "HIGH"])
```
Result: Actionable plan with tasks and traceability

**Step 4: Implement Updates**

Follow the plan using individual tools:
```
# Validate updates
Use tool: check_version_tool("org.springframework:spring-core", "6.0.0")

# Verify security
Use tool: scan_java_project_tool(workspace="/path/to/project")
```

---

## Error Handling

All tools return standardized error responses:

```json
{
  "tool_name": "check_version",
  "status": "error",
  "error": {
    "code": "DEPENDENCY_NOT_FOUND",
    "message": "Dependency 'com.example:unknown' not found in Maven Central"
  }
}
```

### Common Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| `INVALID_INPUT_FORMAT` | Input parameters malformed | Check dependency format (groupId:artifactId) |
| `DEPENDENCY_NOT_FOUND` | Maven dependency doesn't exist | Verify dependency coordinates |
| `VERSION_NOT_FOUND` | Specific version doesn't exist | Check version number |
| `MAVEN_API_ERROR` | Error connecting to Maven Central | Retry, check network |
| `INTERNAL_SERVER_ERROR` | Unexpected server error | Report issue |

---

## Best Practices

### Version Checking

✅ **DO**: Use batch checking for multiple dependencies
```
check_version_batch_tool([...])  // More efficient
```

❌ **DON'T**: Call check_version_tool repeatedly
```
// Inefficient
check_version_tool(dep1)
check_version_tool(dep2)
check_version_tool(dep3)
```

### Security Scanning

✅ **DO**: Filter by severity to focus on critical issues
```json
{
  "severity_filter": ["CRITICAL", "HIGH"]
}
```

✅ **DO**: Use workspace scanning for multi-module projects
```json
{
  "scan_mode": "workspace"
}
```

### Workflow Integration

✅ **DO**: Use prompts for complex workflows
```
1. triage() → Complete analysis
2. plan() → Actionable tasks
3. Individual tools → Implementation
```

✅ **DO**: Leverage resources for state persistence
```
Triage → Save report → Plan reads report → Traceability maintained
```

---

## Tips & Tricks

### Quick Dependency Check

For a single dependency with full context:
```
check_version_tool("org.springframework:spring-core", "5.3.0")
```
Returns everything in one call - no need for multiple queries.

### Enterprise Workflow

For complete dependency management:
1. `triage()` - Full analysis with security
2. Review resource - Understand findings
3. `plan()` - Create implementation roadmap
4. Execute - Use tools to implement changes

### Version Discovery

To explore all available versions:
```
list_available_versions_tool("org.apache.commons:commons-lang3", "3.12.0", true)
```
Set `include_all_versions: true` to see complete history.

### Fast Security Check

For quick vulnerability assessment:
```
analyze_pom_file_tool("/path/to/pom.xml", true)
```
No full workspace scan needed.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/danielscholl/mvn-mcp-server/issues)
- **Documentation**: [Project Docs](https://github.com/danielscholl/mvn-mcp-server/tree/main/docs)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)
