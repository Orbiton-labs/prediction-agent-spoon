# Model Configuration Guide

There are **3 ways** to configure models in Orbiton Agent:

---

## Method 1: Environment Variables (.env file) - RECOMMENDED ✅

This is the **easiest and most common** method.

### Step 1: Create `.env` file

```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent
nano .env
```

### Step 2: Add your configuration

```bash
# ===== OpenAI Configuration =====
OPENAI_API_KEY=sk-your-actual-api-key-here
BASE_URL=https://your-custom-endpoint.com/v1  # Optional: for custom endpoints

# ===== Anthropic Configuration =====
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# ===== DeepSeek Configuration =====
DEEPSEEK_API_KEY=your-deepseek-key-here

# ===== Google Gemini Configuration =====
GEMINI_API_KEY=your-gemini-key-here
```

### Step 3: Run with default settings

```bash
# Will use config/defaults.json settings
uv run main.py

# Or override the model
uv run main.py --model gpt-4o
```

---

## Method 2: Command Line Arguments

Override configuration at runtime:

```bash
# Specify model
uv run main.py --model gpt-4-turbo

# Specify agent type
uv run main.py --agent react-mcp

# Combine multiple options
uv run main.py --model claude-sonnet-4 --debug
```

---

## Method 3: Configuration File (config/defaults.json)

Edit `orbiton-agent/config/defaults.json`:

```json
{
  "llm": {
    "default_provider": "openai",
    "default_model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 4096,
    "timeout": 120
  },
  "agent": {
    "type": "react",
    "memory_enabled": true,
    "max_iterations": 10,
    "tools": []
  }
}
```

**Note**: API keys should always be in `.env`, not in the config file!

---

## Supported Providers & Models

### OpenAI
```bash
OPENAI_API_KEY=sk-...

# Models:
# - gpt-4o
# - gpt-4-turbo
# - gpt-4
# - gpt-3.5-turbo
```

### Anthropic (Claude)
```bash
ANTHROPIC_API_KEY=sk-ant-...

# Models:
# - claude-sonnet-4
# - claude-opus-4
# - claude-3-5-sonnet-20241022
# - claude-3-opus-20240229
```

### DeepSeek
```bash
DEEPSEEK_API_KEY=...
BASE_URL=https://api.deepseek.com/v1

# Models:
# - deepseek-chat
# - deepseek-coder
```

### Google Gemini
```bash
GEMINI_API_KEY=...

# Models:
# - gemini-pro
# - gemini-1.5-pro
# - gemini-1.5-flash
```

---

## Custom OpenAI-Compatible Endpoints

For providers like Groq, Together.ai, OpenRouter, or local LLMs:

```bash
# Groq
OPENAI_API_KEY=gsk_...
BASE_URL=https://api.groq.com/openai/v1

# Together.ai
OPENAI_API_KEY=...
BASE_URL=https://api.together.xyz/v1

# OpenRouter
OPENAI_API_KEY=sk-or-...
BASE_URL=https://openrouter.ai/api/v1

# Local Ollama
OPENAI_API_KEY=dummy
BASE_URL=http://localhost:11434/v1

# Local vLLM
OPENAI_API_KEY=dummy
BASE_URL=http://localhost:8000/v1
```

Then run with OpenAI provider:
```bash
uv run main.py --model your-model-name
```

---

## Configuration Priority (Highest to Lowest)

1. **Command-line arguments** (`--model`, `--agent`)
2. **Environment variables** (`.env` file)
3. **Configuration file** (`config/defaults.json`)

### Example:

```bash
# .env file
OPENAI_API_KEY=sk-abc123
BASE_URL=https://api.openai.com/v1

# config/defaults.json
{
  "llm": {
    "default_model": "gpt-4o"
  }
}

# Command line (OVERRIDES everything)
uv run main.py --model gpt-4-turbo
# → Will use gpt-4-turbo (not gpt-4o)
```

---

## Advanced Configuration

### Temperature & Sampling

Edit `config/defaults.json`:

```json
{
  "llm": {
    "temperature": 0.7,      // Lower = more focused, Higher = more creative
    "max_tokens": 4096,      // Maximum response length
    "timeout": 120           // Request timeout in seconds
  }
}
```

### Agent Settings

```json
{
  "agent": {
    "type": "react",         // or "react-mcp"
    "memory_enabled": true,  // Enable conversation memory
    "max_iterations": 10,    // Max reasoning steps
    "tools": []              // Available tools (auto-detected)
  }
}
```

### UI Preferences

```json
{
  "ui": {
    "theme": "default",
    "show_thinking": true,           // Show agent thinking process
    "auto_expand_threshold": 5,      // Auto-expand if less than N lines
    "syntax_highlighting": true,     // Highlight code blocks
    "show_timestamps": false,        // Show message timestamps
    "show_token_usage": true         // Show token usage stats
  }
}
```

---

## Environment Variable Overrides

You can also override config via environment variables:

```bash
# Model settings
export ORBITON_LLM_MODEL=gpt-4o
export ORBITON_LLM_PROVIDER=openai

# UI settings
export ORBITON_UI_SHOW_THINKING=true
export ORBITON_UI_THEME=default

# Then run
uv run main.py
```

---

## Testing Your Configuration

### 1. Check what configuration is loaded:

```bash
uv run main.py
# Then in the CLI:
> /config
```

This will show:
- Current provider
- Current model
- Temperature
- Max tokens
- All settings

### 2. Test with debug mode:

```bash
uv run main.py --debug
```

This shows:
- Configuration loading process
- API key detection (masked)
- Base URL being used
- Any errors during initialization

### 3. Quick test question:

```bash
uv run main.py
> What model are you?
```

The agent will tell you which model it's using.

---

## Common Configuration Examples

### 1. OpenAI with custom endpoint (Groq)

```bash
# .env
OPENAI_API_KEY=gsk_your_groq_key
BASE_URL=https://api.groq.com/openai/v1
```

```bash
# Run with groq's fast model
uv run main.py --model llama-3.1-70b-versatile
```

### 2. Anthropic Claude

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-key
```

```bash
# Use Claude
uv run main.py --model claude-sonnet-4
```

### 3. Local Ollama

```bash
# .env
OPENAI_API_KEY=dummy
BASE_URL=http://localhost:11434/v1
```

```bash
# Use local model
uv run main.py --model llama3.2
```

### 4. Multiple providers (fallback)

The system automatically falls back to alternative providers if one fails:

```bash
# .env - Configure multiple providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=...
```

If OpenAI fails, it will try Anthropic, then DeepSeek.

---

## Troubleshooting

### Issue: "API key not found"

**Solution:**
```bash
# Check your .env file exists
ls -la .env

# Check the API key is set
cat .env | grep API_KEY

# Make sure no spaces around the =
# ✅ CORRECT:   OPENAI_API_KEY=sk-abc123
# ❌ WRONG:     OPENAI_API_KEY = sk-abc123
```

### Issue: "Connection timeout"

**Solution:**
```json
// Increase timeout in config/defaults.json
{
  "llm": {
    "timeout": 180  // 3 minutes
  }
}
```

### Issue: "Model not found"

**Solution:**
```bash
# Check model name is correct
uv run main.py --model gpt-4o  # Not gpt4o or gpt-4-o

# For custom endpoints, check their documentation for model names
```

### Issue: Base URL not working

**Solution:**
```bash
# Ensure URL includes /v1 suffix
BASE_URL=https://api.groq.com/openai/v1  # ✅
# Not: https://api.groq.com                # ❌

# Test the endpoint manually:
curl $BASE_URL/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## Quick Reference Card

```bash
# === SETUP ===
cd orbiton-agent
nano .env  # Add API keys

# === RUN ===
uv run main.py                      # Default config
uv run main.py --model gpt-4o      # Specific model
uv run main.py --debug             # Debug mode

# === IN-APP ===
> /config                           # View config
> /help                             # Show help
> What model are you?               # Test

# === COMMON .env ===
OPENAI_API_KEY=sk-...
BASE_URL=https://api.openai.com/v1
```

---

## Need More Help?

- Check `README.md` for general usage
- Check `TESTING.md` for testing guide
- Run with `--debug` flag for detailed logs
- Use `/config` command to see current settings
