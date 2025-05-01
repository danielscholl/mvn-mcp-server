# Just Prompt - MCP Server (Experimental)

A lightweight MCP server providing unified access to popular LLM providers including OpenAI, Anthropic, Google Gemini, Groq, DeepSeek, and Ollama.

## Setup

### Installation

```bash
# Clone and install
git clone https://github.com/danielscholl/just-prompt-mcp.git
cd just-prompt
uv sync

# Install
uv pip install -e .

# Run tests to verify installation
uv run pytest
```

### Environment Configuration

Create and edit your `.env` file with your API keys:

```bash
# Create environment file from template
cp .env.sample .env
```

Required API keys in your `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OLLAMA_HOST=http://localhost:11434
```

## MCP Server Configuration

To utilize this MCP server directly in other projects either use the buttons to install in VSCode, edit the `.mcp.json` file directory.

> Clients tend to have slighty different configurations

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22just-prompt%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22git%2Bhttps%3A%2F%2Fgithub.com%2Fdanielscholl%2Fjust-prompt-mcp%40main%22%2C%22just-prompt%22%2C%22--default-models%22%2C%22high%2Copenai%3Ao4-mini%3Ahigh%2Canthropic%3Aclaude-3-7-sonnet-20250219%3A4k%2Cgemini%3Agemini-2.5-pro-preview-03-25%2Cgemini%3Agemini-2.5-flash-preview-04-17%22%5D%2C%22env%22%3A%7B%22OPENAI_API_KEY%22%3A%22%24%7Binput%3Aopenai_key%7D%22%2C%22ANTHROPIC_API_KEY%22%3A%22%24%7Binput%3Aanthropic_key%7D%22%2C%22GEMINI_API_KEY%22%3A%22%24%7Binput%3Agemini_key%7D%22%2C%22GROQ_API_KEY%22%3A%22%24%7Binput%3Agroq_key%7D%22%2C%22DEEPSEEK_API_KEY%22%3A%22%24%7Binput%3Adeepseek_key%7D%22%2C%22OLLAMA_HOST%22%3A%22http%3A%2F%2Flocalhost%3A11434%22%7D%2C%22inputs%22%3A%5B%7B%22id%22%3A%22openai_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22OpenAI%20API%20Key%22%2C%22password%22%3Atrue%7D%2C%7B%22id%22%3A%22anthropic_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Anthropic%20API%20Key%22%2C%22password%22%3Atrue%7D%2C%7B%22id%22%3A%22gemini_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Google%20Gemini%20API%20Key%22%2C%22password%22%3Atrue%7D%2C%7B%22id%22%3A%22groq_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Groq%20API%20Key%22%2C%22password%22%3Atrue%7D%2C%7B%22id%22%3A%22deepseek_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22DeepSeek%20API%20Key%22%2C%22password%22%3Atrue%7D%5D%7D)   [![Install with Docker in VS Code](https://img.shields.io/badge/VS_Code-Docker-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22just-prompt%22%2C%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22--mount%22%2C%22type%3Dbind%2Csource%3D%3CYOUR_WORKSPACE_PATH%3E%2Ctarget%3D%2Fworkspace%22%2C%22danielscholl%2Fjust-prompt-mcp%22%5D%2C%22env%22%3A%7B%22OPENAI_API_KEY%22%3A%22%24%7Binput%3Aopenai_key%7D%22%2C%22ANTHROPIC_API_KEY%22%3A%22%24%7Binput%3Aanthropic_key%7D%22%2C%22GEMINI_API_KEY%22%3A%22%24%7Binput%3Agemini_key%7D%22%2C%22GROQ_API_KEY%22%3A%22%24%7Binput%3Agroq_key%7D%22%2C%22DEEPSEEK_API_KEY%22%3A%22%24%7Binput%3Adeepseek_key%7D%22%2C%22OLLAMA_HOST%22%3A%22http%3A%2F%2Flocalhost%3A11434%22%7D%2C%22inputs%22%3A%5B%7B%22id%22%3A%22openai_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22OpenAI%20API%20Key%22%2C%22password%22%3Atrue%7D%2C%7B%22id%22%3A%22anthropic_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Anthropic%20API%20Key%22%2C%22password%22%3Atrue%7D%2C%7B%22id%22%3A%22gemini_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Google%20Gemini%20API%20Key%22%2C%22password%22%3Atrue%7D%2C%7B%22id%22%3A%22groq_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22Groq%20API%20Key%22%2C%22password%22%3Atrue%7D%2C%7B%22id%22%3A%22deepseek_key%22%2C%22type%22%3A%22promptString%22%2C%22description%22%3A%22DeepSeek%20API%20Key%22%2C%22password%22%3Atrue%7D%5D%7D) 

### Configure for Claude.app

```json
{
  "mcpServers": {
    "just-prompt": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/danielscholl/just-prompt-mcp@main",
        "just-prompt",
        "--default-models",
        "high,openai:o4-mini:high,anthropic:claude-3-7-sonnet-20250219:4k,gemini:gemini-2.5-pro-preview-03-25,gemini:gemini-2.5-flash-preview-04-17"
      ],
      "env": {
        "OPENAI_API_KEY": "<YOUR_OPENAI_KEY>",
        "ANTHROPIC_API_KEY": "<YOUR_ANTHROPIC_KEY>",
        "GEMINI_API_KEY": "<YOUR_GEMINI_KEY>",
        "GROQ_API_KEY": "<YOUR_GROQ_KEY>",
        "DEEPSEEK_API_KEY": "<YOUR_DEEPSEEK_KEY>",
        "OLLAMA_HOST": "http://localhost:11434"
      }
    }
  }
}
```

### Configure for Claude.code

Setting up Just Prompt with Claude Code easily by importing it.

```bash
claude mcp add-from-claude-desktop
```

> Note: "--directory" would be the path to the source code if not in the same directory.

```bash
# Copy this JSON configuration
{
    "command": "uvx",
    "args": ["--from", "git+https://github.com/danielscholl/just-prompt-mcp@main", "just-prompt", "--default-models", "high,openai:o4-mini:high,anthropic:claude-3-7-sonnet-20250219:4k,gemini:gemini-2.5-pro-preview-03-25,gemini:gemini-2.5-flash-preview-04-17"]
}

# Then run this command in Claude Code
claude mcp add just-prompt "$(pbpaste)"
```

To remove the configuration later:
```bash
claude mcp remove just-prompt
```

## Available LLM Providers

| Provider | Short Prefix | Full Prefix | Example Usage |
|----------|--------------|-------------|--------------|
| OpenAI   | `o`          | `openai`    | `o:gpt-4o-mini` |
| Anthropic | `a`         | `anthropic` | `a:claude-3-5-haiku` |
| Google Gemini | `g`     | `gemini`    | `g:gemini-2.5-pro-exp-03-25` |
| Groq     | `q`          | `groq`      | `q:llama-3.1-70b-versatile` |
| DeepSeek | `d`          | `deepseek`  | `d:deepseek-coder` |
| Ollama   | `l`          | `ollama`    | `l:llama3.1` |

## MCP Tools

### Send Prompts to Models

**Usage examples:**
```bash
# Basic prompt with default model
prompt: "ping"

# Claude with 4k thinking tokens
prompt: "Analyze quantum computing applications" ["a:claude-3-7-sonnet-20250219:4k"]

# OpenAI with high reasoning effort
prompt: "Solve this complex math problem" ["openai:o3-mini:high"]

# Gemini with 8k thinking budget
prompt: "Evaluate climate change solutions" ["gemini:gemini-2.5-flash-preview-04-17:8k"]
```

Send text prompts to one or more LLM models and receive responses.

```bash
# Basic prompt with default model
prompt: "Your prompt text here"

# Specify model(s)
prompt: "Your prompt text here" "openai:gpt-4o"

# Examples with thinking capability
prompt: "Develop a strategy for learning how to create MCP Servers for AI" "anthropic:claude-3-7-sonnet-20250219:4k"

prompt: "Write a function to calculate the factorial of a number" "openai:o4-mini:high"
```

### List Available Options

Check which providers and models are available for use.

```bash
# List all providers
list-providers

# List models for a specific provider
list-models: "openai"
```

### Work with Files

Process prompts from files and save responses to files for batch processing.

```bash
# Send prompt from file
prompt-from-file: [o:o4-mini] "prompts/function.txt"

# Save responses to files
prompt-from-file-to-file: [o:o4-mini] "prompts/uv_script.txt" "prompts/responses"
```

### CEO and Board Decision Making

Send a prompt to multiple models as a "board of directors", then have a "CEO" model make a final decision based on all responses.

```bash
# Use default models as board members and default CEO model
ceo_and_board_prompt: "./prompts/ceo_decision_iac.txt" "./prompts/responses"

# Specify board members and CEO model
ceo_and_board_prompt: "./prompts/ceo_decision_ai_assistant.txt" "prompts/responses" ["anthropic:claude-3-7-sonnet-20250219", "openai:gpt-4o", "gemini:gemini-2.5-pro-preview-03-25"] "openai:o3"
```

### Business Analyst Project Briefing

Send a prompt to one or more models to generate detailed business analyst briefs.

```bash
business_analyst_prompt: "./prompts/product_concept.txt" "./prompts/responses" ["a:claude-3-7-sonnet-20250219"]
```

This tool:
1. Sends your prompt to each specified model
2. Each model creates its own business analyst brief
3. If multiple models are specified, a consolidated final brief is created by combining insights from all individual briefs
4. All individual briefs and (if multiple models are used) the consolidated brief are saved as markdown files

## Thinking and Reasoning Capabilities

Each provider offers special capabilities to enhance reasoning on complex questions:

| Provider | Model | Capability | Format | Range | Example |
|----------|-------|------------|--------|-------|---------|
| Anthropic | claude-3-7-sonnet-20250219 | Thinking tokens | `:Nk` or `:N` | 1024-16000 | `anthropic:claude-3-7-sonnet-20250219:4k` |
| OpenAI | o4-mini, o3 | Reasoning effort | `:level` | low, medium, high | `openai:o3-mini:high` |
| Google | gemini-2.5-flash-preview-04-17 | Thinking budget | `:Nk` or `:N` | 0-24576 | `gemini:gemini-2.5-flash-preview-04-17:8k` |
