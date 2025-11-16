# Testing Orbiton Agent with Custom OpenAI Endpoint

## Quick Setup Guide

### Step 1: Create .env File

Create a `.env` file in `/Users/meomeocoj/prediction-agent-spoon/orbiton-agent/` or use the parent project's `.env` file.

```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent

# Option 1: Create new .env for orbiton-agent
cp .env.example .env

# Option 2: Use parent project's .env (recommended)
# The app will automatically find it in the parent directory
```

### Step 2: Configure Your .env File

Edit the `.env` file with your OpenAI API key and custom base URL:

```bash
# Required: Your OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Required: Your custom base URL (if using custom endpoint)
BASE_URL=https://your-custom-endpoint.com/v1
```

**Examples of custom base URLs:**
- Groq: `https://api.groq.com/openai/v1`
- Together.ai: `https://api.together.xyz/v1`
- Local Ollama: `http://localhost:11434/v1`
- Local vLLM: `http://localhost:8000/v1`
- OpenRouter: `https://openrouter.ai/api/v1`

### Step 3: (Optional) Override Configuration

You can override the default model and provider:

```bash
# In .env file:
ORBITON_LLM_MODEL=gpt-4o
ORBITON_LLM_PROVIDER=openai

# Or use command line:
uv run main.py --model gpt-4o
```

### Step 4: Run the CLI

```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent

# Start the agent
uv run main.py

# Or with specific options:
uv run main.py --model gpt-4o --debug
```

---

## Testing Checklist

### Basic Functionality
- [ ] CLI starts without errors
- [ ] Welcome message displays agent status
- [ ] Help command works: `/help`
- [ ] Config shows correct settings: `/config`

### Agent Interaction
- [ ] Simple question: "What is 2+2?"
- [ ] Thinking mode displays
- [ ] Agent response appears

### Tool Usage (if tools available)
- [ ] Ask a question that requires tool use
- [ ] Tool execution displays with tree structure (▸ action → ↳ result)
- [ ] Tool result shows correctly

### UI Features
- [ ] User messages display with `>`
- [ ] Agent messages display with `•`
- [ ] Markdown formatting works
- [ ] Syntax highlighting for code blocks
- [ ] Status spinner appears during processing

### Commands
- [ ] `/help` - Shows help
- [ ] `/config` - Shows configuration
- [ ] `/clear` - Clears screen
- [ ] `/test` - Shows UI test
- [ ] `/exit` - Exits gracefully

### Error Handling
- [ ] Invalid API key shows error
- [ ] Wrong base URL shows error
- [ ] Network issues handled gracefully
- [ ] Ctrl+C exits cleanly

---

## Troubleshooting

### Issue: "Agent failed to initialize"

**Possible causes:**
1. Missing or invalid API key
2. Wrong base URL
3. Network connectivity issues

**Solutions:**
```bash
# Check your .env file exists
ls -la .env

# Verify API key is set
echo $OPENAI_API_KEY

# Test with debug mode
uv run main.py --debug
```

### Issue: "Provider not found" or "Module import error"

**Solution:**
Make sure you're in the orbiton-agent directory and spoon_ai is in the parent:
```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent
pwd  # Should show: .../prediction-agent-spoon/orbiton-agent
```

### Issue: Connection errors or timeouts

**Possible causes:**
1. Base URL is incorrect
2. Endpoint is not reachable
3. Firewall/proxy issues

**Solutions:**
```bash
# Test connectivity to your endpoint
curl https://your-custom-endpoint.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Increase timeout in config/defaults.json:
{
  "llm": {
    "timeout": 180  // Increase to 3 minutes
  }
}
```

### Issue: Model not found

**Solution:**
Check which models are available on your endpoint and update the config:
```bash
# In config/defaults.json or via command line:
uv run main.py --model your-model-name
```

---

## Example Session

```
$ uv run main.py

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Orbiton Agent • gpt-4o                      ┃
┃ ~/prediction-agent-spoon/orbiton-agent      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─ ✨ Welcome ─────────────────────────────────┐
│ Welcome to Orbiton Agent - A Glass Box CLI │
│ Interface                                   │
│                                             │
│ ✓ Agent ready: react                       │
│                                             │
│ Try asking:                                 │
│   • "What is 2+2?"                          │
│   • "Write a Python function..."           │
└─────────────────────────────────────────────┘

> What is the capital of France?

💭 Thinking... (0.8s)

• The capital of France is **Paris**. It's the country's
  largest city and has been the capital since the 12th
  century.

> /exit

Goodbye! 👋
```

---

## Common Commands During Testing

```bash
# View current config
/config

# Test UI components
/test

# Clear screen and start fresh
/clear

# See all available commands
/help

# Exit
/exit
```

---

## Next Steps After Testing

Once testing is successful, you can:

1. **Continue MVP Development**: Complete Phase 4 & 5
   - Keyboard shortcuts (ctrl+o to expand)
   - Session persistence
   - Advanced commands

2. **Customize Configuration**: Edit `config/defaults.json`
   - Adjust temperature, max_tokens
   - Change UI preferences
   - Configure tools

3. **Add Tools**: Integrate custom tools for your agent
   - See parent project `spoon_ai/tools/` for examples

4. **Report Issues**: If you find bugs or have suggestions
   - Note the error message
   - Check logs if in debug mode
   - Provide steps to reproduce
