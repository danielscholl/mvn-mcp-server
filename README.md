# MCP Server

## Initial Execute Instruction Set

```bash
# Enter interactive mode with Claude
claude

# Once in interactive mode, send the following prompt:
READ specs/*
GITHUB: create a issue with the title: Implement: maven-mcp-server
GIT: checkout a branch and swith to it.
IMPLEMENT: maven-mcp-server
INITIAL TOOL: version-check

-- Where it makes sense provide task updates to the GITHUB issue. --

On Completion:
GIT: commit with a descriptive message.
GIT: push the branch to the remote repository.
GITHUB: create a PR.
```


