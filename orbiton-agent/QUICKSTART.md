# Quick Start Guide

## How to Run Orbiton Agent

### Method 1: Using the Helper Script (Recommended)

```bash
cd orbiton-agent
./run.sh
```

This will launch the full-screen TUI with your configured agent.

### Method 2: Direct Python Execution

```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent
PYTHONPATH=/Users/meomeocoj/prediction-agent-spoon/orbiton-agent:$PYTHONPATH uv run python main.py
```

### Method 3: Demo Mode (No Configuration Needed)

To try the UI without setting up an agent:

```bash
cd orbiton-agent
PYTHONPATH=/Users/meomeocoj/prediction-agent-spoon/orbiton-agent:$PYTHONPATH uv run python console/demo_tui.py
```

## Command-Line Options

```bash
# Show help
./run.sh --help

# Use specific model
./run.sh --model claude-sonnet-4

# Use specific agent type
./run.sh --agent react-mcp

# Enable debug mode
./run.sh --debug

# Use legacy UI (old sequential interface)
./run.sh --legacy
```

## What to Expect

When you run the app, you'll see a full-screen TUI:

```
┌─────────────────────────────────────────┐
│ Orbiton Agent • your-model             │  ← Header (shows model & directory)
│ ~/your/directory                       │
├─────────────────────────────────────────┤
│                                         │
│ ✓ Agent ready: react                   │  ← History Pane
│                                         │  (scrollable chat log)
│ Welcome to Orbiton!                    │
│ Type your question and press Enter...  │
│                                         │
├─────────────────────────────────────────┤
│ ┌───────────────────────────────────┐ │  ← Input Bar (fixed at bottom)
│ │ > type your message here_         │ │
│ └───────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ esc interrupt • ctrl+l clear • ctrl+c │  ← Keyboard shortcuts
└─────────────────────────────────────────┘
```

## Using the TUI

1. **Type your message** in the input bar (bottom)
2. **Press Enter** → message moves to history, input clears
3. **See agent work** → thinking, tool calls, results appear in history
4. **Use keyboard shortcuts**:
   - `Enter` - Submit message
   - `Ctrl+L` - Clear screen
   - `Ctrl+C` - Exit
   - `ESC` - Interrupt current task

## Troubleshooting

### "OSError: [Errno 22] Invalid argument"

This means you're trying to run the TUI through a pipe or redirect. The TUI requires an interactive terminal.

**Solution**: Run directly in your terminal (not through pipes, background processes, or SSH without proper terminal allocation).

### "ModuleNotFoundError: No module named 'console'"

The Python path isn't set correctly.

**Solution**: Use the `./run.sh` script or set PYTHONPATH manually:
```bash
export PYTHONPATH=/Users/meomeocoj/prediction-agent-spoon/orbiton-agent:$PYTHONPATH
```

### "Agent failed to initialize"

Your configuration or API keys might be missing.

**Solution**:
1. Check your `.env` file in the orbiton-agent directory
2. Make sure you have valid API keys for your LLM provider
3. Run with `--debug` to see detailed error messages:
   ```bash
   ./run.sh --debug
   ```

### TUI doesn't render properly

Your terminal might not support the required features.

**Solution**:
- Use a modern terminal (iTerm2, Terminal.app on macOS, Windows Terminal, etc.)
- Ensure your terminal supports 256 colors and UTF-8
- Try resizing your terminal window
- If all else fails, use legacy mode: `./run.sh --legacy`

## Configuration

The app reads configuration from:
1. `config/default.toml` - Default settings
2. `.env` - Environment variables (API keys, etc.)
3. Command-line arguments (override everything)

See `config/default.toml` for all available options.

## Next Steps

Once you have the TUI running:
- Try asking questions about prediction markets
- Watch the agent think and use tools
- Press `Ctrl+L` to clear and start fresh
- Check the `console/README.md` for advanced features

## Demo Mode

If you just want to see the UI without setting up an agent:

```bash
cd orbiton-agent
PYTHONPATH=$PWD:$PYTHONPATH uv run python console/demo_tui.py
```

This will show simulated agent responses so you can test the interface.
