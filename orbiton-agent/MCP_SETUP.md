# MCP Configuration Guide for Orbiton Agent

This guide explains how to configure and use Model Context Protocol (MCP) tools with your Orbiton Agent.

## What is MCP?

MCP (Model Context Protocol) enables AI agents to interact with external tools and services. With MCP, your agent can:
- Use web search APIs (like Tavily)
- Access crypto/blockchain tools from SpoonAI
- Connect to any MCP-compatible service

## Quick Start

### 1. Set Environment Variables

Create or update your `.env` file:

```bash
# Required for OpenAI/Anthropic
OPENAI_API_KEY=sk-your-key-here
BASE_URL=https://api.openai.com/v1

# Optional: For Tavily search
TAVILY_API_KEY=tvly-your-key-here
```

### 2. Enable MCP in Configuration

The MCP configuration is already set up in `config/defaults.json`:

```json
{
  "agent": {
    "type": "react-mcp",  // Use MCP-enabled agent
    ...
  },
  "mcp": {
    "enabled": true,
    "servers": [...]
  }
}
```

### 3. Run the Agent

```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent
uv run main.py
```

## Available MCP Servers

### 1. Tavily Search (NPX-based)

Web search powered by Tavily API:

```json
{
  "name": "tavily-search",
  "description": "Web search using Tavily API",
  "type": "npx",
  "config": {
    "command": "npx",
    "args": ["--yes", "tavily-mcp"],
    "env": {
      "TAVILY_API_KEY": "${TAVILY_API_KEY}"
    }
  }
}
```

**Usage:**
1. Get API key from https://tavily.com
2. Add to `.env`: `TAVILY_API_KEY=tvly-...`
3. Agent will automatically have search capability

### 2. SpoonAI Tools (Python-based)

Crypto and DeFi analysis tools:

```json
{
  "name": "spoon-tools",
  "description": "SpoonAI crypto tools via MCP",
  "type": "python",
  "config": {
    "command": "python",
    "args": ["-m", "spoon_ai.tools.mcp_tools_collection"],
    "url": "http://localhost:8765"
  }
}
```

**Usage:**
1. Start the MCP server in a separate terminal:
   ```bash
   cd /Users/meomeocoj/prediction-agent-spoon
   python -m spoon_ai.tools.mcp_tools_collection
   ```
2. Run your agent - it will connect to the server automatically

## Adding Custom MCP Servers

### Example: Custom HTTP/SSE Server

```json
{
  "name": "my-custom-tool",
  "description": "My custom MCP service",
  "type": "http",
  "config": {
    "url": "http://localhost:9000",
    "transport": "sse",
    "headers": {
      "Authorization": "Bearer ${MY_API_TOKEN}"
    }
  }
}
```

### Example: Custom Command-line Tool

```json
{
  "name": "my-cli-tool",
  "description": "MCP tool via CLI",
  "type": "stdio",
  "config": {
    "command": "python",
    "args": ["/path/to/my_mcp_server.py"],
    "env": {
      "MY_CONFIG": "value"
    }
  }
}
```

## Transport Types

Orbiton Agent supports multiple MCP transport mechanisms:

| Type | Use Case | Example |
|------|----------|---------|
| `npx` | Node.js packages | Tavily, other npm MCP tools |
| `uvx` | Python packages via uv | Python-based MCP servers |
| `python` | Python scripts | SpoonAI tools collection |
| `http/sse` | HTTP Server-Sent Events | Remote MCP services |
| `websocket` | WebSocket connections | Real-time MCP tools |
| `stdio` | Standard IO | Any CLI-based MCP tool |

## Configuration Options

### Per-Server Configuration

```json
{
  "name": "tool-name",
  "description": "Tool description",
  "config": {
    "command": "command-to-run",
    "args": ["arg1", "arg2"],
    "env": {
      "KEY": "value",
      "API_KEY": "${ENV_VAR}"  // Use ${VAR} to reference environment variables
    },
    "timeout": 30,              // Connection timeout in seconds
    "max_retries": 3,           // Number of retry attempts
    "health_check_interval": 300 // Health check interval in seconds
  }
}
```

## Testing MCP Configuration

### Test Individual Tools

```python
# test_mcp.py
import asyncio
from agents import AgentFactory
from config import ConfigManager

async def test_mcp():
    config = ConfigManager.load_config()

    # Create MCP-enabled agent
    agent = AgentFactory.create_agent("react-mcp", config)

    # Test a query
    response = await agent.run("Search for the latest news on NEO blockchain")
    print(response)

asyncio.run(test_mcp())
```

### Check Available Tools

Run with debug mode to see loaded tools:

```bash
uv run main.py --debug
```

Look for log messages like:
```
INFO: Created MCP tool: tavily-search
INFO: Created MCP tool: spoon-tools
INFO: Found 2 MCP tools
```

## Troubleshooting

### MCP Server Not Responding

1. **Check the server is running** (for HTTP/SSE servers):
   ```bash
   curl http://localhost:8765
   ```

2. **Check environment variables**:
   ```bash
   echo $TAVILY_API_KEY
   ```

3. **Enable debug logging**:
   ```bash
   uv run main.py --debug
   ```

### Tool Not Loading

- Verify the `command` path is correct
- Check `args` are properly formatted as JSON array
- Ensure environment variables are set
- Check logs for specific error messages

### Connection Timeouts

Increase timeout in server config:
```json
{
  "config": {
    "timeout": 60,
    "max_retries": 5
  }
}
```

## Examples

### Example 1: Web Search + Crypto Analysis

```bash
> Analyze the NEO token and search for recent news about it
```

The agent will:
1. Use `tavily-search` to find recent news
2. Use `spoon-tools` to get price data and metrics
3. Synthesize a comprehensive analysis

### Example 2: DeFi Operations

```bash
> Check the liquidity pools for NEO on Uniswap
```

The agent uses `spoon-tools` MCP server to access UniswapLiquidity tool.

## Architecture

```
orbiton-agent/
├── agents/
│   ├── __init__.py          # Exports AgentFactory, AgentSession
│   ├── factory.py           # Creates MCP-enabled agents
│   └── console_callback.py  # UI callbacks
├── config/
│   └── defaults.json        # MCP configuration
└── main.py                  # Entry point

spoon_ai/
├── agents/
│   ├── spoon_react_mcp.py   # MCP-enabled ReAct agent
│   └── mcp_client_mixin.py  # MCP client functionality
└── tools/
    ├── mcp_tool.py          # MCPTool class
    └── mcp_tools_collection.py  # MCP server for SpoonAI tools
```

## Further Reading

- [MCP Official Docs](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [SpoonAI MCP Tools README](../spoon_ai/tools/README_MCP_TOOLS.md)
