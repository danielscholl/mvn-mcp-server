# MCP Server Tool Spec - Prompts Implementation

> Add MCP Prompts capability to provide interactive conversation starters and guided workflows for Maven dependency management tasks, with integrated Resources for state management.

## Overview

MCP Prompts provide structured conversation starters that help AI assistants guide users through complex Maven dependency management workflows. This implementation focuses on three core prompts that work together: asset discovery, dependency triage, and update planning, creating a comprehensive workflow for managing Java project dependencies.

## Core Workflow Pattern

This specification implements a proven enterprise workflow for dependency management:

1. **Analysis-First Approach**: All planning begins with comprehensive dependency and security analysis
2. **Resource-Driven Integration**: Analysis outputs become plan inputs via stored resources
3. **Structured Plan Format**: Consistent planning structure with phases, tasks, and success criteria
4. **Traceability**: Each plan task links back to specific analysis findings (CVEs, dependencies)
5. **File Management**: Standardized naming and storage conventions for workflow artifacts

## Required Implementation Tasks

- [ ] Implement prompt registration system using FastMCP's `@mcp.prompt()` decorator
- [ ] Create 3 core prompts: list_mcp_assets, triage, and plan
- [ ] Implement MCP Resources for storing triage reports and plans
- [ ] Add prompt argument validation and processing
- [ ] Build dynamic content generation based on available tools
- [ ] Add comprehensive tests for all prompts and resources
- [ ] Update server.py to register prompts and resources
- [ ] Update README.md with prompt and resource documentation

## Prompt Details

### Core Implementation
- Implemented in `src/mvn_mcp_server/prompts/` directory structure
- Each prompt in its own file for maintainability
- Resources implemented in `src/mvn_mcp_server/resources/`
- **Prompt Registration Pattern**:
  ```python
  from fastmcp import FastMCP
  from mcp.types import Message
  
  @mcp.prompt()
  async def prompt_name(arg1: str, arg2: Optional[str] = None) -> List[Message]:
      """Prompt description for AI understanding."""
      return [
          Message(
              role="user", 
              content="Generated prompt content based on arguments"
          )
      ]
  ```

### Core Prompts to Implement

1. **list_mcp_assets** (no arguments)
   - Returns comprehensive overview of all server capabilities
   - Lists all available prompts with descriptions
   - Lists all tools with their parameters
   - Lists all resources with their URIs
   - Provides usage examples and quick start guide
   - Dynamic generation based on registered components

2. **triage** (service_name: str, workspace: Optional[str] = None)
   - Comprehensive dependency analysis and vulnerability assessment
   - Locates and analyzes POM files in the project
   - Identifies outdated dependencies using batch version checking
   - Scans for security vulnerabilities
   - Creates structured triage report
   - Stores report in Resources for later access
   - Follows enterprise-grade analysis workflow

3. **plan** (service_name: str, priorities: Optional[List[str]] = None)
   - Creates actionable update plan based on triage report
   - Retrieves triage data from Resources
   - Groups updates by risk and priority
   - Suggests update order and approach
   - Identifies potential breaking changes
   - Generates step-by-step implementation plan
   - Stores plan in Resources for execution tracking

### Resource Implementation

Resources provide persistent state between prompts:

1. **triage://reports/{service_name}/latest**
   - Stores the most recent triage report for a service
   - JSON format with vulnerability and dependency data
   - Accessible across prompt executions

2. **plans://updates/{service_name}/latest**
   - Stores the current update plan for a service
   - Tracks which updates have been applied
   - Links back to triage report

3. **assets://server/capabilities**
   - Dynamic list of all server capabilities
   - Used by list_mcp_assets prompt

## Implementation Structure

```
src/mvn_mcp_server/
├── prompts/
│   ├── __init__.py
│   ├── list_mcp_assets.py
│   ├── triage.py
│   └── plan.py
├── resources/
│   ├── __init__.py
│   ├── triage_reports.py
│   ├── update_plans.py
│   └── server_assets.py
├── tests/
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── test_list_mcp_assets.py
│   │   ├── test_triage.py
│   │   └── test_plan.py
│   └── resources/
│       ├── __init__.py
│       └── test_resources.py
```

## Detailed Implementations

### List MCP Assets Implementation

```python
# src/mvn_mcp_server/prompts/list_mcp_assets.py
from typing import List
from mcp.types import Message

async def list_mcp_assets() -> List[Message]:
    """Return a comprehensive list of all MCP server capabilities."""
    
    content = """# 🚀 Maven MCP Server Assets

## 📝 Prompts
Interactive conversation starters and guided workflows:

• **list_mcp_assets** () - Comprehensive overview of all server capabilities
• **dependency_triage** (service_name, workspace) - Analyze dependencies and vulnerabilities
• **update_plan** (service_name, priorities) - Create actionable update plan from triage

## 🔧 Tools
Maven dependency management and analysis functions:

### Version Management
• **check_version_tool** (dependency, version, packaging, classifier) - Check version and get update info
• **check_version_batch_tool** (dependencies) - Process multiple version checks efficiently
• **list_available_versions_tool** (dependency, version, include_all_versions) - List versions by tracks

### Security Scanning
• **scan_java_project_tool** (workspace, scan_mode, severity_filter, max_results) - Scan for vulnerabilities
• **analyze_pom_file_tool** (pom_file_path, include_vulnerability_check) - Analyze single POM file

## 📂 Resources
Dynamic data and persistent state:

• **triage://reports/{service_name}/latest** - Latest triage report for a service
• **plans://updates/{service_name}/latest** - Current update plan for a service
• **assets://server/capabilities** - Dynamic server capabilities list

---

**🎯 Quick Start Workflow:**
1. Run `dependency_triage(service_name)` to analyze your service
2. Review the triage report stored in resources
3. Execute `update_plan(service_name)` to create an action plan
4. Use individual tools to implement specific updates

**💡 Pro Tips:**
• Triage reports are automatically stored and can be retrieved later
• Update plans track which changes have been applied
• Use scan_mode="pom_only" for large projects to avoid token limits
"""
    
    return [Message(role="user", content=content)]
```

### Dependency Triage Implementation

```python
# src/mvn_mcp_server/prompts/triage.py
from typing import List, Optional
from mcp.types import Message
import json
from datetime import datetime

async def dependency_triage(service_name: str, workspace: Optional[str] = None) -> List[Message]:
    """Analyze service dependencies and create comprehensive vulnerability triage report."""
    
    workspace_path = workspace or f"./{service_name}"
    timestamp = datetime.now().isoformat()
    
    content = f"""# Maven Dependency Triage Analysis 🔍

**Service:** {service_name}  
**Workspace:** {workspace_path}  
**Analysis Date:** {timestamp}

You are performing a comprehensive dependency triage analysis following enterprise workflow best practices. This analysis will become the foundation for the subsequent update planning phase.

## Triage Analysis Workflow

### Phase 1: Project Discovery
**Objective:** Map the Maven project structure and dependency landscape

**Tasks:**
1. **POM Hierarchy Analysis**
   - Search for all POM files: `{workspace_path}/**/pom.xml`
   - Map parent-child relationships and inheritance
   - Identify multi-module structure
   - Document dependency management strategy
   - Focus on main modules (exclude test/sample projects)

2. **Dependency Extraction**
   - Extract all `<dependency>` declarations from each POM
   - Identify managed dependencies from parent POMs
   - Note version variables and properties
   - Map dependencies to their declaring modules

### Phase 2: Version Analysis
**Objective:** Assess current state vs available updates

**Tasks:**
3. **Batch Version Checking**
   - Use `check_version_batch_tool` with ALL discovered dependencies
   - Categorize updates: MAJOR/MINOR/PATCH
   - Calculate age of current versions
   - Identify stale dependencies (>1 year old)

4. **Version Compatibility Assessment**
   - Use `list_available_versions_tool` for critical dependencies
   - Check release notes for breaking changes
   - Identify version compatibility constraints

### Phase 3: Security Assessment
**Objective:** Identify and prioritize security vulnerabilities

**Tasks:**
5. **Vulnerability Scanning**
   - Execute `scan_java_project_tool`:
     - workspace: `{workspace_path}`
     - scan_mode: "workspace" (or "pom_only" for token efficiency)
     - severity_filter: ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
     - max_results: 100
   - Cross-reference scan results with version analysis

6. **Risk Prioritization**
   - Correlate CVE data with dependency versions
   - Assess exploitability and impact
   - Map vulnerabilities to fix versions

### Phase 4: Triage Report Generation
**Objective:** Create comprehensive triage report for planning phase

**Required Report Structure:**
```markdown
# {service_name} Service — Dependency Triage Report 🔍

**Report ID:** {service_name}-triage-{timestamp[:10]}
**Analysis Date:** {timestamp}
**Workspace:** {workspace_path}

## Executive Summary
- **Total Dependencies:** [count]
- **Vulnerabilities Found:** [count] (Critical: X, High: Y, Medium: Z)
- **Outdated Dependencies:** [count]/[total] ([percentage]%)
- **Recommended Actions:** [count] (Immediate: X, This Sprint: Y, Next Sprint: Z)

## Critical Findings (Action Required)

### Security Vulnerabilities
| CVE ID | Severity | Dependency | Current | Fix Version | CVSS | Description |
|--------|----------|------------|---------|-------------|------|-------------|
| CVE-XXXX-YYYY | CRITICAL | log4j-core | 2.14.1 | 2.17.1+ | 9.0 | Remote code execution |

### Severely Outdated Dependencies
| Dependency | Current | Latest | Age | Update Type | Risk Level |
|------------|---------|--------|-----|-------------|------------|
| spring-core | 4.3.30 | 6.1.2 | 3.2 years | MAJOR | HIGH |

## Standard Findings (Planned Updates)

### Version Updates Available
| Dependency | Current | Latest Stable | Update Type | Module Location |
|------------|---------|---------------|-------------|-----------------|
| jackson-databind | 2.13.0 | 2.16.1 | MINOR | parent-pom.xml |

### Dependencies Analysis Summary
- **Up to Date:** [count] dependencies
- **Minor Updates:** [count] dependencies  
- **Major Updates:** [count] dependencies
- **Security Updates:** [count] dependencies

## Project Structure Analysis

### POM Hierarchy
```
parent-pom.xml (defines versions)
├── core-module/pom.xml
├── api-module/pom.xml
└── service-module/pom.xml
```

### Dependency Management Strategy
- Version management: [Centralized/Distributed]
- Property usage: [Property names for major deps]
- BOM usage: [Spring Boot BOM, etc.]

## Recommended Update Strategy

### Phase 1: Critical Security (Immediate)
**Priority:** CRITICAL - Deploy within 24-48 hours
**Risk:** LOW - Well-tested security patches

1. **CVE-XXXX-YYYY: log4j-core 2.14.1 → 2.17.1**
   - **Fix Location:** parent-pom.xml line 42
   - **Change:** `<log4j.version>2.17.1</log4j.version>`
   - **Impact:** Security vulnerability resolution
   - **Testing:** Smoke tests + security scan verification

### Phase 2: High Priority Updates (This Sprint)
**Priority:** HIGH - Complete within current sprint
**Risk:** MEDIUM - May require integration testing

[List specific updates with details]

### Phase 3: Maintenance Updates (Next Sprint)
**Priority:** MEDIUM - Complete in next maintenance window
**Risk:** LOW - Standard version bumps

[List remaining updates]

## Implementation Artifacts

### Files Requiring Updates
- `parent-pom.xml` (line references for each change)
- `core-module/pom.xml` (specific dependency overrides)
- [Additional POM files as needed]

### Version Control Strategy
**Recommended Branch:** `feature/security-updates-{service_name}`
**Commit Pattern:** `fix(deps): update [dependency] to [version] for [CVE/reason]`
**PR Template:** Include security scan results and test evidence

## Testing Requirements
- [ ] All unit tests pass
- [ ] Integration tests complete successfully
- [ ] Security scan shows resolved vulnerabilities
- [ ] No new vulnerabilities introduced
- [ ] Application startup verification
- [ ] Smoke tests for critical paths

## Success Criteria
- All CRITICAL and HIGH vulnerabilities resolved
- No build failures or test regressions
- Security scan passes with acceptable risk level
- Dependencies updated to secure, stable versions
- Documentation updated with changes

---
**Next Step:** Use `update_plan` prompt with this triage report to create implementation plan
```

### Phase 5: Resource Storage
**Objective:** Store triage results for subsequent planning

**Tasks:**
7. **Store Triage Report**
   - Save complete report to: `triage://reports/{service_name}/latest`
   - Include metadata: timestamp, workspace, dependency counts
   - Store raw scan data for plan generation

8. **Prepare for Planning Phase**
   - Validate all required data is captured
   - Confirm report structure matches planning requirements
   - Signal completion for next workflow step

## Critical Success Factors
- **Completeness:** Include ALL dependencies and vulnerabilities
- **Accuracy:** Verify version information and CVE details
- **Actionability:** Provide specific file locations and change instructions
- **Traceability:** Link each finding to specific dependencies and modules

**Begin comprehensive triage analysis now. The quality of this analysis directly impacts the effectiveness of the subsequent update planning phase.**"""
    
    return [Message(role="user", content=content)]
```

### Update Plan Implementation

```python
# src/mvn_mcp_server/prompts/plan.py
from typing import List, Optional
from mcp.types import Message

async def update_plan(service_name: str, priorities: Optional[List[str]] = None) -> List[Message]:
    """Create detailed remediation plan based on vulnerability triage report following enterprise workflow patterns."""
    
    priority_filter = priorities or ["CRITICAL", "HIGH"]
    
    content = f"""# Maven Remediation Plan Creation 📋

You are creating a detailed remediation plan for **{service_name}** based on the vulnerability triage report, following enterprise workflow best practices.

## Your Task

### 1. Retrieve and Analyze Triage Report
Access the triage report from: `triage://reports/{service_name}/latest`

Before drafting the final plan, work inside <triage_breakdown> tags to:
- Extract and list all vulnerabilities mentioned in the triage report
- Categorize vulnerabilities by severity (CRITICAL, HIGH, MEDIUM, LOW)  
- List all outdated dependencies and their current/target versions
- Note specific POM files that need updating
- Brainstorm Maven-specific considerations

### 2. Create Structured Remediation Plan

Generate a plan following this proven enterprise structure:

```markdown
# {service_name} Service — Remediation Plan

## Overview
Brief description tying this plan to the triage report findings and total issues identified.

## References
- Triage Report: {service_name}_triage_YYYY-MM-DD.md  
- Maven Central documentation
- Relevant CVEs: [list specific CVEs from triage]

## Phases and Tasks

### Phase 1: Update Critical Dependencies
- [ ] **Update [dependency] from [current] to [target]**  
  _Ref: [CVE-ID] ([description]), Triage Table_  
  - Edit [specific-pom.xml file]
  - Property: `<[dependency].version>[target]</[dependency].version>`
  - Verify with: `check_version_tool("[groupId]:[artifactId]", "[target]")`

### Phase 2: Update High Priority Dependencies  
- [ ] **Update [dependency] from [current] to [target]**  
  _Ref: [CVE-ID] ([description]), Triage Table_  
  - [Specific implementation steps]

### Phase 3: Update Medium/Low Priority Dependencies
- [ ] [List remaining updates with same detailed format]

### Phase 4: Security Hardening & Verification
- [ ] Review transitive dependencies for affected libraries
- [ ] Run full security scan: `scan_java_project_tool("{service_name}", scan_mode="workspace")`
- [ ] Validate no new vulnerabilities introduced

### Phase 5: Build & Test Verification
- [ ] Build all updated modules: `mvn clean install`
- [ ] Run unit tests: `mvn test`
- [ ] Run integration tests: `mvn verify`
- [ ] Validate service functionality in staging environment

## Success Criteria
- All CRITICAL and HIGH vulnerabilities are remediated
- All listed dependencies updated to recommended versions
- No new critical/high vulnerabilities introduced
- All builds and tests pass successfully
- Service functionality verified in staging

## Dependency Updates Summary

| Dependency | Current | Target | Module | Priority |
|------------|---------|--------|--------|----------|
| [name] | [version] | [version] | [pom-location] | [CRITICAL/HIGH/MEDIUM] |

## Version Control Conventions
- **Branch naming:** `remediate/{service_name}-vuln-YYYY-MM`
- **Commit message format:**  
  `fix({service_name}): update [dependency] to [version] for [CVE-ID]`
- **Required PR checks:**  
  - Build passes (`mvn clean install`)
  - All tests pass (`mvn verify`)
  - Security scan passes (zero CRITICAL/HIGH)
  - Peer review completed

## Progress Checklist
- [ ] Phase 1: Critical updates complete
- [ ] Phase 2: High priority updates complete  
- [ ] Phase 3: Medium/low updates complete
- [ ] Phase 4: Security hardening complete
- [ ] Phase 5: Build & test verification complete
- [ ] Success criteria met
```

### 3. Implementation Guidelines
- **Traceability:** Every task must link back to specific triage findings (CVE IDs, dependency analysis)
- **Specificity:** Include exact POM file locations and Maven property names
- **Tool Integration:** Reference specific MCP tools for validation (`check_version_tool`, `scan_java_project_tool`)
- **Checkboxes:** Ensure all tasks start unchecked ([ ]) regardless of current progress
- **Priority Focus:** Emphasize {', '.join(priority_filter)} priority items

### 4. Critical Requirements
- Link each task back to specific triage item or CVE for traceability
- Use clear, concise language throughout the plan
- Include specific version updates for dependencies
- Add build verification phase
- Specify branch naming convention and commit message format
- List required PR checks

### 5. Final Steps
After creating the remediation plan:
- Store the plan at: `plans://updates/{service_name}/latest`
- Present only the final remediation plan in markdown format
- Ask if the plan should be saved with naming: `{service_name}_plan_YYYY-MM-DD.md`

**Priority Focus:** {', '.join(priority_filter)}

Begin creating the remediation plan now, ensuring it follows the proven enterprise structure with full traceability to triage findings."""
    
    return [Message(role="user", content=content)]
```

## Resource Implementation Examples

Resources provide structured state management with strong data integrity for enterprise workflow support:

```python
# src/mvn_mcp_server/resources/triage_reports.py
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from pydantic import BaseModel, Field

class TriageMetadata(BaseModel):
    """Metadata for triage reports following enterprise workflow pattern."""
    report_id: str = Field(..., description="Unique report identifier")
    service_name: str = Field(..., description="Service being analyzed")
    workspace: str = Field(..., description="Workspace path analyzed")
    timestamp: str = Field(..., description="ISO timestamp of analysis")
    version: str = Field(default="1.0", description="Report format version")
    total_dependencies: int = Field(..., description="Total dependencies analyzed")
    vulnerabilities_found: int = Field(..., description="Total vulnerabilities found")
    critical_count: int = Field(default=0, description="Critical vulnerabilities")
    high_count: int = Field(default=0, description="High vulnerabilities")
    medium_count: int = Field(default=0, description="Medium vulnerabilities")
    low_count: int = Field(default=0, description="Low vulnerabilities")

class VulnerabilityFinding(BaseModel):
    """Individual vulnerability finding from triage."""
    cve_id: str = Field(..., description="CVE identifier")
    severity: str = Field(..., description="Vulnerability severity")
    dependency: str = Field(..., description="Affected dependency")
    current_version: str = Field(..., description="Current vulnerable version")
    fix_version: str = Field(..., description="Minimum version that fixes vulnerability")
    cvss_score: Optional[float] = Field(None, description="CVSS score if available")
    description: str = Field(..., description="Vulnerability description")

class DependencyUpdate(BaseModel):
    """Dependency update information from triage."""
    dependency: str = Field(..., description="Maven coordinates")
    current_version: str = Field(..., description="Current version")
    latest_version: str = Field(..., description="Latest available version")
    update_type: str = Field(..., description="MAJOR/MINOR/PATCH")
    module_location: str = Field(..., description="POM file containing dependency")
    age_months: Optional[int] = Field(None, description="Age of current version in months")

class TriageReport(BaseModel):
    """Complete triage report structure following enterprise workflow pattern."""
    metadata: TriageMetadata
    vulnerabilities: List[VulnerabilityFinding] = Field(default_factory=list)
    dependency_updates: List[DependencyUpdate] = Field(default_factory=list)
    pom_hierarchy: Dict[str, Any] = Field(default_factory=dict)
    recommendations: Dict[str, List[str]] = Field(default_factory=dict)
    raw_scan_data: Optional[Dict[str, Any]] = Field(None, description="Original scan output")

class TriageReportResource:
    """Manages triage report storage and retrieval following enterprise workflow patterns."""
    
    def __init__(self):
        self._reports: Dict[str, TriageReport] = {}
        self._history: Dict[str, List[TriageReport]] = {}
    
    async def get_report(self, service_name: str) -> Optional[TriageReport]:
        """Retrieve the latest triage report for a service."""
        return self._reports.get(service_name)
    
    async def save_report(self, service_name: str, report_data: Dict[str, Any]) -> TriageReport:
        """Save a triage report with validation and metadata."""
        # Generate report ID following enterprise pattern
        timestamp = datetime.now().isoformat()
        report_id = f"{service_name}-triage-{timestamp[:10]}"
        
        # Create metadata
        metadata = TriageMetadata(
            report_id=report_id,
            service_name=service_name,
            workspace=report_data.get("workspace", f"./{service_name}"),
            timestamp=timestamp,
            total_dependencies=len(report_data.get("dependency_updates", [])),
            vulnerabilities_found=len(report_data.get("vulnerabilities", [])),
            critical_count=len([v for v in report_data.get("vulnerabilities", []) if v.get("severity") == "CRITICAL"]),
            high_count=len([v for v in report_data.get("vulnerabilities", []) if v.get("severity") == "HIGH"]),
            medium_count=len([v for v in report_data.get("vulnerabilities", []) if v.get("severity") == "MEDIUM"]),
            low_count=len([v for v in report_data.get("vulnerabilities", []) if v.get("severity") == "LOW"])
        )
        
        # Create structured report
        report = TriageReport(
            metadata=metadata,
            vulnerabilities=[VulnerabilityFinding(**v) for v in report_data.get("vulnerabilities", [])],
            dependency_updates=[DependencyUpdate(**d) for d in report_data.get("dependency_updates", [])],
            pom_hierarchy=report_data.get("pom_hierarchy", {}),
            recommendations=report_data.get("recommendations", {}),
            raw_scan_data=report_data.get("raw_scan_data")
        )
        
        # Store latest report
        self._reports[service_name] = report
        
        # Store in history
        if service_name not in self._history:
            self._history[service_name] = []
        self._history[service_name].append(report)
        
        return report
    
    async def get_report_summary(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get summary information for plan generation."""
        report = await self.get_report(service_name)
        if not report:
            return None
            
        return {
            "report_id": report.metadata.report_id,
            "timestamp": report.metadata.timestamp,
            "total_dependencies": report.metadata.total_dependencies,
            "vulnerability_counts": {
                "critical": report.metadata.critical_count,
                "high": report.metadata.high_count,
                "medium": report.metadata.medium_count,
                "low": report.metadata.low_count
            },
            "critical_vulnerabilities": [
                v for v in report.vulnerabilities if v.severity == "CRITICAL"
            ],
            "high_priority_updates": [
                d for d in report.dependency_updates if d.update_type == "MAJOR" or d.age_months and d.age_months > 12
            ]
        }

# Update Plan Resource Implementation
```python
# src/mvn_mcp_server/resources/update_plans.py
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class TaskStatus(str, Enum):
    """Task completion status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class UpdatePriority(str, Enum):
    """Update priority levels following enterprise workflow pattern."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class UpdateTask(BaseModel):
    """Individual update task within a plan."""
    task_id: str = Field(..., description="Unique task identifier")
    dependency: str = Field(..., description="Maven coordinates")
    current_version: str = Field(..., description="Current version")
    target_version: str = Field(..., description="Target version")
    update_type: str = Field(..., description="MAJOR/MINOR/PATCH")
    priority: UpdatePriority = Field(..., description="Task priority")
    complexity: str = Field(..., description="LOW/MEDIUM/HIGH")
    file_location: str = Field(..., description="POM file to modify")
    line_number: Optional[int] = Field(None, description="Line number for change")
    change_description: str = Field(..., description="Description of required change")
    traceability_link: str = Field(..., description="Link to triage finding")
    cve_ids: List[str] = Field(default_factory=list, description="Related CVE IDs")
    testing_requirements: List[str] = Field(default_factory=list, description="Required tests")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status")
    estimated_effort_hours: float = Field(default=1.0, description="Estimated effort")

class PlanPhase(BaseModel):
    """Plan phase containing related tasks."""
    phase_id: str = Field(..., description="Phase identifier")
    phase_name: str = Field(..., description="Human-readable phase name")
    priority: UpdatePriority = Field(..., description="Phase priority")
    description: str = Field(..., description="Phase description")
    prerequisites: List[str] = Field(default_factory=list, description="Required prerequisites")
    tasks: List[UpdateTask] = Field(default_factory=list, description="Tasks in this phase")
    success_criteria: List[str] = Field(default_factory=list, description="Phase success criteria")
    estimated_effort_hours: float = Field(default=0.0, description="Total phase effort")

class PlanMetadata(BaseModel):
    """Plan metadata following enterprise workflow pattern."""
    plan_id: str = Field(..., description="Unique plan identifier")
    service_name: str = Field(..., description="Service being updated")
    triage_report_id: str = Field(..., description="Source triage report ID")
    created_timestamp: str = Field(..., description="Plan creation timestamp")
    priority_filter: List[str] = Field(..., description="Priorities included in plan")
    total_updates: int = Field(..., description="Total number of updates")
    total_estimated_hours: float = Field(..., description="Total estimated effort")

class UpdatePlan(BaseModel):
    """Complete update plan structure following enterprise workflow pattern."""
    metadata: PlanMetadata
    phases: List[PlanPhase] = Field(default_factory=list)
    version_control_strategy: Dict[str, str] = Field(default_factory=dict)
    testing_strategy: Dict[str, Any] = Field(default_factory=dict)
    deployment_strategy: Dict[str, Any] = Field(default_factory=dict)
    progress_summary: Dict[str, int] = Field(default_factory=dict)

class UpdatePlanResource:
    """Manages update plan storage and progress tracking following enterprise patterns."""
    
    def __init__(self):
        self._plans: Dict[str, UpdatePlan] = {}
        self._history: Dict[str, List[UpdatePlan]] = {}
    
    async def get_plan(self, service_name: str) -> Optional[UpdatePlan]:
        """Retrieve the latest update plan for a service."""
        return self._plans.get(service_name)
    
    async def save_plan(self, service_name: str, plan_data: Dict[str, Any], 
                       triage_report_id: str) -> UpdatePlan:
        """Save an update plan with full structure validation."""
        timestamp = datetime.now().isoformat()
        plan_id = f"{service_name}-plan-{timestamp[:10]}"
        
        # Create metadata
        metadata = PlanMetadata(
            plan_id=plan_id,
            service_name=service_name,
            triage_report_id=triage_report_id,
            created_timestamp=timestamp,
            priority_filter=plan_data.get("priority_filter", ["CRITICAL", "HIGH"]),
            total_updates=len(plan_data.get("all_tasks", [])),
            total_estimated_hours=sum(task.get("estimated_effort_hours", 1.0) for task in plan_data.get("all_tasks", []))
        )
        
        # Create phases with tasks
        phases = []
        for phase_data in plan_data.get("phases", []):
            tasks = [UpdateTask(**task) for task in phase_data.get("tasks", [])]
            phase = PlanPhase(
                **{k: v for k, v in phase_data.items() if k != "tasks"},
                tasks=tasks,
                estimated_effort_hours=sum(task.estimated_effort_hours for task in tasks)
            )
            phases.append(phase)
        
        # Create complete plan
        plan = UpdatePlan(
            metadata=metadata,
            phases=phases,
            version_control_strategy=plan_data.get("version_control_strategy", {}),
            testing_strategy=plan_data.get("testing_strategy", {}),
            deployment_strategy=plan_data.get("deployment_strategy", {}),
            progress_summary=self._calculate_progress_summary(phases)
        )
        
        # Store plan
        self._plans[service_name] = plan
        
        # Store in history
        if service_name not in self._history:
            self._history[service_name] = []
        self._history[service_name].append(plan)
        
        return plan
    
    async def update_task_status(self, service_name: str, task_id: str, 
                                status: TaskStatus) -> bool:
        """Update the status of a specific task."""
        plan = await self.get_plan(service_name)
        if not plan:
            return False
        
        # Find and update task
        for phase in plan.phases:
            for task in phase.tasks:
                if task.task_id == task_id:
                    task.status = status
                    # Recalculate progress summary
                    plan.progress_summary = self._calculate_progress_summary(plan.phases)
                    return True
        
        return False
    
    def _calculate_progress_summary(self, phases: List[PlanPhase]) -> Dict[str, int]:
        """Calculate progress summary across all phases."""
        all_tasks = [task for phase in phases for task in phase.tasks]
        
        return {
            "total_tasks": len(all_tasks),
            "pending": len([t for t in all_tasks if t.status == TaskStatus.PENDING]),
            "in_progress": len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]),
            "completed": len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in all_tasks if t.status == TaskStatus.FAILED]),
            "completion_percentage": int((len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]) / len(all_tasks)) * 100) if all_tasks else 0
        }
    
    async def get_plan_summary(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get plan summary for status reporting."""
        plan = await self.get_plan(service_name)
        if not plan:
            return None
        
        return {
            "plan_id": plan.metadata.plan_id,
            "service_name": plan.metadata.service_name,
            "created_timestamp": plan.metadata.created_timestamp,
            "triage_report_id": plan.metadata.triage_report_id,
            "total_updates": plan.metadata.total_updates,
            "progress": plan.progress_summary,
            "phases": [
                {
                    "phase_id": phase.phase_id,
                    "phase_name": phase.phase_name,
                    "priority": phase.priority,
                    "task_count": len(phase.tasks),
                    "estimated_hours": phase.estimated_effort_hours
                }
                for phase in plan.phases
            ]
        }
```

- Run tests with `uv run pytest`
- Test coverage for prompts:
  - Prompt registration and discovery
  - Argument validation for each prompt
  - Content generation with proper formatting
  - Dynamic tool/resource listing in list_mcp_assets
  - Error handling for invalid arguments
- Test coverage for resources:
  - Resource registration and URI patterns
  - Data persistence between calls
  - Concurrent access handling
  - Data format validation
- Mock external tool calls in prompt tests
- Verify integration between prompts and resources

## Integration with Server

Update `server.py` to register prompts and resources:

```python
# Import prompt functions
from mvn_mcp_server.prompts.list_mcp_assets import list_mcp_assets
from mvn_mcp_server.prompts.triage import dependency_triage
from mvn_mcp_server.prompts.plan import update_plan

# Import resource handlers
from mvn_mcp_server.resources.triage_reports import TriageReportResource
from mvn_mcp_server.resources.update_plans import UpdatePlanResource

# Initialize resources
triage_resource = TriageReportResource()
plan_resource = UpdatePlanResource()

# Register prompts
@mcp.prompt()
async def list_mcp_assets_prompt() -> List[Message]:
    """Return a comprehensive list of all MCP server capabilities."""
    return await list_mcp_assets()

@mcp.prompt()
async def triage(service_name: str, workspace: Optional[str] = None) -> List[Message]:
    """Analyze service dependencies and create vulnerability triage report."""
    return await dependency_triage(service_name, workspace)

@mcp.prompt()
async def plan(service_name: str, priorities: Optional[List[str]] = None) -> List[Message]:
    """Create actionable update plan based on triage report."""
    return await update_plan(service_name, priorities)

# Register resources
@mcp.resource("triage://reports/{service_name}/latest")
async def get_triage_report(service_name: str) -> Dict[str, Any]:
    """Get the latest triage report for a service."""
    report = await triage_resource.get_report(service_name)
    if not report:
        return {"error": f"No triage report found for {service_name}"}
    return report

@mcp.resource("plans://updates/{service_name}/latest")
async def get_update_plan(service_name: str) -> Dict[str, Any]:
    """Get the current update plan for a service."""
    plan = await plan_resource.get_plan(service_name)
    if not plan:
        return {"error": f"No update plan found for {service_name}"}
    return plan
```

## Documentation Updates

Update README.md to include Prompts and Resources:

```markdown
## Available Prompts

### Interactive Workflows
- **list_mcp_assets**: Comprehensive overview of server capabilities
- **triage**: Analyze dependencies and create vulnerability report
  - Arguments: `service_name` (required), `workspace` (optional)
- **plan**: Create actionable update plan from triage results
  - Arguments: `service_name` (required), `priorities` (optional list)

### Using Prompts

Prompts provide guided workflows for complex dependency management tasks:

```bash
# Start a dependency triage
Use prompt: triage with service_name="my-service", workspace="./my-service"

# Create an update plan focusing on critical issues
Use prompt: plan with service_name="my-service", priorities=["CRITICAL", "HIGH"]

# View all server capabilities
Use prompt: list_mcp_assets
```

## Available Resources

Resources provide persistent state between prompt executions:

- **triage://reports/{service_name}/latest** - Latest triage report for a service
- **plans://updates/{service_name}/latest** - Current update plan for a service
- **assets://server/capabilities** - Dynamic list of server capabilities

### Workflow Example

1. Run dependency triage: `triage("my-service")`
2. View report: Access `triage://reports/my-service/latest`
3. Create plan: `plan("my-service", ["CRITICAL"])`
4. View plan: Access `plans://updates/my-service/latest`
```

## Error Handling

Prompts and resources handle errors gracefully:
- Invalid arguments return helpful error messages
- Missing dependencies are clearly reported
- Resource not found returns descriptive error
- Network failures suggest offline alternatives
- Clear guidance on resolution steps

## Future Enhancements

### Prompt Enhancements
- **migration_assistant**: Guide version migration strategies
- **dependency_graph**: Visualize dependency relationships
- **compliance_check**: Verify license and policy compliance
- **performance_analyzer**: Analyze dependency impact on performance

### Resource Enhancements
- **History tracking**: Store multiple versions of reports/plans
- **Diff generation**: Compare reports over time
- **Team collaboration**: Share reports across team members
- **Export formats**: Generate reports in multiple formats

## 🚨 REQUIRED VALIDATION CHECKLIST 🚨

Every implementation MUST complete all validation steps following the proven enterprise workflow pattern:

### Phase 1: Foundation Setup
1. [ ] Create directory structure: `src/mvn_mcp_server/prompts/` and `src/mvn_mcp_server/resources/`
2. [ ] Implement Pydantic models for structured data (TriageReport, UpdatePlan, etc.)
3. [ ] Create resource storage classes with history tracking
4. [ ] Implement all 3 prompt files following enterprise workflow structure

### Phase 2: Core Workflow Implementation
5. [ ] **Dependency Triage Prompt**: Implement comprehensive analysis workflow
   - [ ] Phase-based triage execution (Discovery → Analysis → Security → Report)
   - [ ] Structured report generation with metadata and traceability
   - [ ] Resource storage integration with `triage://reports/{service_name}/latest`
6. [ ] **Update Plan Prompt**: Implement plan creation from triage data
   - [ ] Triage report retrieval and validation
   - [ ] Phase-based task organization (Critical → High → Medium)
   - [ ] Full traceability from plan tasks back to triage findings
   - [ ] Resource storage with `plans://updates/{service_name}/latest`
7. [ ] **List MCP Assets Prompt**: Dynamic capability listing
   - [ ] Integration with existing tools and prompts
   - [ ] Resource URI documentation
   - [ ] Quick start workflow guidance

### Phase 3: Resource Integration
8. [ ] Implement TriageReportResource with Pydantic validation
   - [ ] Structured data storage (VulnerabilityFinding, DependencyUpdate)
   - [ ] Report metadata and ID generation
   - [ ] Summary extraction for plan generation
9. [ ] Implement UpdatePlanResource with progress tracking
   - [ ] Task-based structure with status tracking
   - [ ] Phase organization and completion metrics
   - [ ] Traceability links to source triage reports

### Phase 4: Testing & Validation
10. [ ] Write comprehensive test coverage for prompts:
    - [ ] Prompt content generation and structure validation
    - [ ] Argument processing and error handling
    - [ ] Dynamic content based on available tools/resources
11. [ ] Write comprehensive test coverage for resources:
    - [ ] Data storage and retrieval operations
    - [ ] Pydantic model validation
    - [ ] Progress tracking and status updates
12. [ ] Run test commands and ensure 100% pass rate:
    - [ ] `uv run pytest src/mvn_mcp_server/tests/prompts/`
    - [ ] `uv run pytest src/mvn_mcp_server/tests/resources/`

### Phase 5: Integration & Registration
13. [ ] Update server.py with prompt and resource registrations:
    - [ ] FastMCP prompt registration with proper decorators
    - [ ] Resource URI pattern registration
    - [ ] Error handling for missing resources
14. [ ] Update README.md with complete workflow documentation:
    - [ ] Triage → Plan workflow example
    - [ ] Resource URI patterns and usage
    - [ ] Integration with existing tools

### Phase 6: Workflow Validation
15. [ ] **End-to-End Workflow Testing**: Validate complete enterprise workflow pattern
    - [ ] Execute: `dependency_triage("test-service")`
    - [ ] Verify: Triage report stored at `triage://reports/test-service/latest`
    - [ ] Execute: `update_plan("test-service", ["CRITICAL", "HIGH"])`
    - [ ] Verify: Plan stored at `plans://updates/test-service/latest`
    - [ ] Verify: Plan references triage report ID for traceability
16. [ ] **Resource Interaction Testing**:
    - [ ] Test resource retrieval for valid service names
    - [ ] Test error handling for non-existent resources
    - [ ] Verify progress tracking and status updates
17. [ ] **Integration Testing**:
    - [ ] Verify prompts correctly invoke Maven MCP tools
    - [ ] Test batch processing of dependencies
    - [ ] Validate security scan integration
    - [ ] Confirm structured output formatting

### Phase 7: Quality Assurance
18. [ ] **Traceability Validation**: Every plan task must link to triage finding
19. [ ] **Data Integrity**: All resources maintain consistent structure
20. [ ] **Error Resilience**: Graceful handling of missing data and failed operations
21. [ ] **Performance Testing**: Workflow completes in reasonable time (<5 minutes for typical service)

### Success Criteria Validation
- [ ] **Workflow Completeness**: Triage → Plan → Implementation guidance chain working
- [ ] **Data Traceability**: Clear linkage from CVEs through triage to plan tasks
- [ ] **Actionable Output**: Plans contain specific file locations, commands, and criteria
- [ ] **Resource Persistence**: Data survives between prompt executions
- [ ] **Tool Integration**: Seamless use of existing Maven MCP tools

### Critical Pattern Compliance
- [ ] **Enterprise Pattern**: Phase-based organization with clear objectives and tasks
- [ ] **Resource Integration**: Triage data drives plan generation via stored resources
- [ ] **Structured Planning**: Consistent plan format with phases, tasks, and success criteria
- [ ] **Full Traceability**: Each plan element traces back to specific triage findings
- [ ] **File Management**: Standardized naming and storage conventions

📝 **Implementation Notes:**
- This specification implements a proven enterprise workflow pattern for dependency management
- The triage → plan workflow creates a complete audit trail from vulnerability discovery to implementation tasks
- Resources provide persistent state management enabling complex multi-step workflows
- Full integration with existing Maven MCP tools leverages all available capabilities
- The structured approach ensures consistency and reliability in enterprise dependency management

🎯 **Success Validation**: The implementation is complete when a user can execute `dependency_triage("service")`, review the stored triage report, then execute `update_plan("service")` to receive a comprehensive, actionable plan that directly references the triage findings with full traceability for implementation teams.