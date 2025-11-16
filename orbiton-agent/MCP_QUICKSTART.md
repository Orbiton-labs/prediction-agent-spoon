# MCP Quick Start Guide

## ✅ Configuration Complete!

Your Orbiton Agent is now configured with MCP (Model Context Protocol) support. Here's what was set up:

### What Changed

1. **Agent Type**: Changed from `react` to `react-mcp` in `config/defaults.json`
2. **MCP Enabled**: MCP is now enabled with 2 configured servers
3. **Factory Updated**: `agents/factory.py` now creates MCP tools from configuration
4. **Auto-loading**: MCP tools are automatically loaded when you start the agent

### Configured MCP Servers

#### 1. Tavily Search (Web Search)
- **Type**: NPX-based (Node.js)
- **Command**: `npx --yes tavily-mcp`
- **Requires**: `TAVILY_API_KEY` environment variable
- **Get API Key**: https://tavily.com

#### 2. SpoonAI Tools (Crypto/DeFi)
- **Type**: Python-based
- **Server**: HTTP/SSE on `http://localhost:8765`
- **Requires**: MCP server running in background
- **Tools**: Price prediction, token analysis, liquidity monitoring, etc.

## 🚀 Usage

### Option 1: Basic Usage (No MCP Servers)

Just run the agent:
```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent
uv run main.py
```

The agent will work but MCP tools won't be available (they'll be skipped).

### Option 2: With Tavily Search

1. Get API key from https://tavily.com
2. Add to `.env`:
   ```bash
   TAVILY_API_KEY=tvly-your-key-here
   ```
3. Run agent:
   ```bash
   uv run main.py
   ```

Now you can ask the agent to search the web!

### Option 3: With SpoonAI Tools

1. Start the MCP server (in a separate terminal):
   ```bash
   cd /Users/meomeocoj/prediction-agent-spoon
   python -m spoon_ai.tools.mcp_tools_collection
   ```

2. Run the agent (in another terminal):
   ```bash
   cd orbiton-agent
   uv run main.py
   ```

Now you have access to all SpoonAI crypto tools!

### Option 4: Full Setup (Both)

Terminal 1 - MCP Server:
```bash
cd /Users/meomeocoj/prediction-agent-spoon
python -m spoon_ai.tools.mcp_tools_collection
```

Terminal 2 - Agent:
```bash
export TAVILY_API_KEY=tvly-your-key-here
cd orbiton-agent
uv run main.py
```

## 🧪 Test Your Configuration

Run the configuration test:
```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent
python test_mcp_simple.py
```

This will show:
- ✓ What's configured correctly
- ✗ What's missing (like API keys)
- Next steps to complete setup

## 📝 Example Queries

Once MCP is set up, try these:

### With Tavily Search:
```
> Search for the latest news about Bitcoin
> What are the top trending cryptocurrencies today?
```

### With SpoonAI Tools:
```
> Get the current price of NEO token
> Analyze the liquidity pools for USDC
> Check for sudden price increases in the market
```

### Combined:
```
> Search for news about NEO, then analyze its current price and liquidity
```

## 🔧 Troubleshooting

### MCP Tools Not Loading

Check logs when starting the agent:
```bash
uv run main.py --debug
```

Look for:
- `Created MCP tool: tavily-search` ✓
- `Created MCP tool: spoon-tools` ✓
- Errors or warnings ✗

### Tavily Not Working

1. Check API key is set:
   ```bash
   echo $TAVILY_API_KEY
   ```

2. Or add to `.env` file:
   ```bash
   echo "TAVILY_API_KEY=tvly-your-key" >> .env
   ```

### SpoonAI Tools Not Working

1. Make sure MCP server is running:
   ```bash
   # In separate terminal
   python -m spoon_ai.tools.mcp_tools_collection
   ```

2. Check server is responding:
   ```bash
   curl http://localhost:8765
   ```

### Connection Timeouts

Increase timeout in `config/defaults.json`:
```json
{
  "mcp": {
    "servers": [
      {
        "config": {
          "timeout": 60,
          "max_retries": 5
        }
      }
    ]
  }
}
```

## 📚 More Information

- **Full Setup Guide**: See `MCP_SETUP.md`
- **SpoonAI MCP Tools**: See `../spoon_ai/tools/README_MCP_TOOLS.md`
- **Test Script**: `test_mcp_simple.py`

## 🎯 Summary

✓ **Configuration**: MCP is configured in `config/defaults.json`
✓ **Agent Type**: `react-mcp` (MCP-enabled)
✓ **Factory**: Updated to create MCP tools
✓ **Servers**: 2 MCP servers configured (Tavily + SpoonAI)
✓ **Ready**: Just add API keys and start using!

Enjoy your MCP-powered Orbiton Agent! 🚀
