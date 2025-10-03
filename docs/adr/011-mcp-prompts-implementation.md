# ADR-011: MCP Prompts Implementation Strategy

## Status
Accepted

## Date
2025-01-25

## Context

The Maven MCP Server needed to provide structured workflows for complex dependency management tasks that go beyond simple tool calls. Users needed guided workflows that could:

1. Analyze entire projects for dependency vulnerabilities and updates
2. Create actionable remediation plans with full traceability
3. Maintain state between workflow steps
4. Provide enterprise-grade structure and documentation

MCP Prompts provide conversation starters that guide AI assistants through complex workflows, while MCP Resources enable persistent state management between prompt executions.

## Decision

Implement MCP Prompts with Resources for enterprise dependency management workflows using simplified, memorable prompt names.

### Core Prompt Design
- **list_mcp_assets**: Dynamic capability overview
- **triage**: Comprehensive dependency analysis (simplified from `dependency_triage`)
- **plan**: Actionable update planning (simplified from `update_plan`)

### Enterprise Workflow Pattern
1. **Analysis-First Approach**: All planning begins with comprehensive analysis
2. **Resource-Driven Integration**: Analysis outputs become plan inputs via stored resources
3. **Structured Plan Format**: Consistent planning with phases, tasks, and success criteria
4. **Full Traceability**: Each plan task links back to specific analysis findings
5. **File Management**: Standardized naming and storage conventions

### Resource Architecture
- **Triage Reports**: `triage://reports/{service_name}/latest`
- **Update Plans**: `plans://updates/{service_name}/latest`
- **Server Assets**: `assets://server/capabilities`

## Rationale

### Why Prompts Over Additional Tools
- **Guided Workflows**: Prompts provide structured guidance through complex multi-step processes
- **Natural Language**: AI assistants can follow detailed instructions naturally
- **Comprehensive Output**: Each prompt generates complete analysis/plans in enterprise format
- **Educational Value**: Prompts teach users enterprise dependency management practices

### Why Resources for State Management
- **Workflow Continuity**: Triage data persists for plan generation
- **Audit Trail**: Complete history of analysis and planning decisions
- **Reusability**: Reports and plans can be accessed multiple times
- **Integration**: Resources enable seamless prompt-to-prompt data flow

### Why Simplified Names (`triage` vs `dependency_triage`)
- **Memorability**: Shorter names are easier to remember and type
- **Natural Usage**: `triage("service")` feels more natural than `dependency_triage("service")`
- **Clarity**: Context makes purpose clear (Maven dependency server)
- **Consistency**: Follows command-line tool naming conventions

### Enterprise Workflow Implementation
```
triage("service") → stores analysis → plan("service") → actionable tasks
```

This pattern mirrors enterprise change management:
1. **Assessment**: Comprehensive analysis of current state
2. **Planning**: Structured approach to remediation
3. **Execution**: Step-by-step implementation with traceability
4. **Verification**: Security scanning and validation

## Implementation Details

### Prompt Structure
Each prompt follows consistent patterns:
- **Phase-based organization**: Clear workflow stages
- **Objective-driven tasks**: Each phase has specific goals
- **Tool integration**: Seamless use of existing MCP tools
- **Resource storage**: Automatic persistence of results

### Resource Data Models
- **Pydantic validation**: Type-safe data structures
- **Metadata tracking**: Comprehensive audit information
- **Progress monitoring**: Task completion and status tracking
- **History preservation**: Multiple versions maintained

### Error Handling
- **Graceful degradation**: Missing resources handled cleanly
- **Clear messaging**: Actionable error descriptions
- **Recovery guidance**: Specific steps to resolve issues

## Consequences

### Positive
- **Complete Workflows**: Users get end-to-end dependency management
- **Enterprise Ready**: Structured approach suitable for production environments
- **Knowledge Transfer**: Prompts teach best practices for dependency management
- **Audit Compliance**: Full traceability from vulnerability to remediation
- **Tool Integration**: Leverages all existing MCP capabilities
- **Simple Usage**: Memorable names reduce cognitive load

### Negative
- **Complexity**: More sophisticated than simple tool calls
- **Resource Management**: State persistence adds operational considerations
- **Learning Curve**: Users need to understand workflow patterns

### Neutral
- **File Organization**: Requires clear directory structure for prompts/resources
- **Testing Strategy**: Need comprehensive integration tests for workflows
- **Documentation**: Extensive examples needed for proper usage

## Implementation Evidence

### File Structure
```
src/mvn_mcp_server/
├── prompts/
│   ├── list_mcp_assets.py
│   ├── triage.py           # Simplified name
│   └── plan.py             # Simplified name
├── resources/
│   ├── triage_reports.py
│   ├── update_plans.py
│   └── server_assets.py
└── tests/
    ├── prompts/
    └── resources/
```

### Workflow Validation
- 59 tests passing for prompts and resources
- Complete triage → plan → implementation chain working
- Full traceability from CVEs to specific remediation tasks
- Resource persistence verified across prompt executions

### Usage Examples
```bash
# Simple, memorable workflow
triage("user-service")
plan("user-service", ["CRITICAL"])

# vs previous verbose names
dependency_triage("user-service") 
update_plan("user-service", ["CRITICAL"])
```

## Related ADRs
- ADR-005: Comprehensive Single-Call Pattern (leveraged in prompts)
- ADR-007: Service Layer Architecture (prompts use existing services)
- ADR-008: Mock-Based Testing Strategy (applied to prompt testing)

## Future Considerations

### Potential Enhancements
- **migration**: Guide major version migration strategies
- **compliance**: Verify license and policy compliance
- **performance**: Analyze dependency impact on performance
- **automation**: Automated dependency update workflows

### Resource Extensions
- **History tracking**: Compare reports over time
- **Team collaboration**: Share resources across team members
- **Export formats**: Generate reports in multiple formats
- **Integration APIs**: Connect with external systems

This ADR establishes MCP Prompts as the primary mechanism for complex dependency management workflows, providing enterprise-grade structure while maintaining simplicity through memorable naming conventions.