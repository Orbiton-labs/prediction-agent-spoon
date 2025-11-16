# Orbiton Agent

> A "Glass Box" CLI interface for AI agents - See how they think and work in real-time

Orbiton Agent is a transparent command-line interface that shows you the agent's thinking process, tool usage, and decision-making as it works. Inspired by Claude Code's "working out loud" philosophy.

## Features

- 🎨 **Beautiful CLI Interface** - Rich UI with syntax highlighting, tree displays, and styled messages
- 🤖 **Real-time Agent Display** - Watch the agent think, plan, and execute tools
- 🔧 **Tool Transparency** - See exactly what tools are called and their results
- 💭 **Thinking Mode** - Stream the agent's reasoning process in real-time
- ⚙️ **Flexible Configuration** - JSON config + environment variables
- 🔌 **Custom Endpoints** - Works with OpenAI, custom endpoints, and local LLMs

## Quick Start

### 1. Setup Environment

```bash
# Navigate to orbiton-agent directory
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent

# Create .env file from example
cp .env.example .env

# Edit .env with your API key and base URL
nano .env
```

Required in `.env`:
```bash
# Your OpenAI API key
OPENAI_API_KEY=sk-your-actual-key-here

# Your custom base URL (if using custom endpoint)
BASE_URL=https://your-endpoint.com/v1
```

### 2. Run the CLI

```bash
# Start with default settings
uv run main.py

# Or specify model
uv run main.py --model gpt-4o

# Debug mode for troubleshooting
uv run main.py --debug
```

### 3. Start Chatting!

```
> Hello, what can you help me with?

💭 Thinking... (0.5s)

• Hello! I'm an AI assistant that can help you with:
  - Answering questions
  - Writing code
  - Analyzing data
  - And much more!

  What would you like help with today?
```

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands and shortcuts |
| `/config` | Display current configuration |
| `/clear` | Clear the screen |
| `/test` | Demo UI components |
| `/exit`, `/quit` | Exit the application |

## Configuration

### Environment Variables

Override defaults with environment variables:

```bash
# Model and provider
ORBITON_LLM_MODEL=gpt-4o
ORBITON_LLM_PROVIDER=openai

# UI preferences
ORBITON_UI_SHOW_THINKING=true
ORBITON_UI_THEME=default

# Session settings
ORBITON_SESSION_SAVE_HISTORY=true
```

### Configuration File

Edit `config/defaults.json`:

```json
{
  "llm": {
    "default_provider": "openai",
    "default_model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "ui": {
    "show_thinking": true,
    "syntax_highlighting": true
  }
}
```

## Custom Endpoints

Orbiton Agent works with any OpenAI-compatible endpoint:

### Groq
```bash
BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=your-groq-api-key
```

### Local Ollama
```bash
BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=dummy  # Ollama doesn't need real key
```

### OpenRouter
```bash
BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=your-openrouter-key
```

## Examples

### Simple Conversation
```
> What's the weather like in Tokyo?

💭 Thinking... (0.8s)

▸ search_web(query="Tokyo weather today", max_results=3)
  ↳ Found 3 results (ctrl+o to expand) +15 lines

• Based on current data, Tokyo is experiencing:
  - Temperature: 18°C (64°F)
  - Conditions: Partly cloudy
  - Humidity: 65%
```

### Code Generation
```
> Write a Python function to calculate fibonacci

💭 Thinking... (1.2s)

• Here's a Python function to calculate Fibonacci numbers:

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

Would you like me to add memoization for better performance?
```

## Architecture

```
orbiton-agent/
├── main.py              # CLI entry point
├── config/              # Configuration management
├── console/             # UI components (Rich-based)
├── agents/              # Agent integration
└── specs/               # Documentation & design
```

## Development Status

**Current Version**: 0.1.0 (MVP - 60% complete)

### ✅ Completed
- Phase 1: Project setup & infrastructure
- Phase 2: Console UI components
- Phase 3: Agent integration & callbacks

### 🚧 In Progress
- Phase 4: Interactive features (keyboard shortcuts)
- Phase 5: State management (session persistence)

See [TESTING.md](./TESTING.md) for detailed testing guide.

## Troubleshooting

### Agent fails to initialize
- Check your API key in `.env`
- Verify `BASE_URL` is correct
- Run with `--debug` flag for details

### Import errors
- Ensure you're in the `orbiton-agent` directory
- Parent `spoon_ai` must be accessible

### Connection timeouts
- Check your endpoint is reachable
- Increase timeout in `config/defaults.json`

See [TESTING.md](./TESTING.md) for more troubleshooting tips.

## Credits

- Built on [spoon_ai](https://github.com/XSpoonAi/prediction-agent-spoon) framework
- UI inspired by [Claude Code](https://code.anthropic.com)
- Powered by [Rich](https://rich.readthedocs.io/) library

## License

[Your License Here]
