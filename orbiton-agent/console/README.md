# Console UI - Full-Screen TUI Layout

This directory contains the refactored console UI implementation using a **full-screen Terminal User Interface (TUI)** layout with `prompt_toolkit`.

## Architecture Overview

The new TUI layout follows the "Full-Screen Terminal Application" design pattern with two distinct, persistent regions:

### 1. **History Pane (Top)**
- Scrollable "chat log" that fills most of the screen
- Displays all conversation history (user messages, agent responses, tool executions, thinking)
- Automatically scrolls to bottom when new messages arrive
- Read-only viewport

### 2. **Input Bar (Bottom)**
- Fixed "command bar" permanently docked at the bottom
- Clearly defined with horizontal separator lines (top and bottom)
- Always ready for user input (cursor active)
- Shortcuts hint displayed below input

## Core Interaction Flow

```
┌─────────────────────────────────────────────────────┐
│ Orbiton Agent • claude-sonnet-4 • ~/directory      │  ← Header (1 line)
├─────────────────────────────────────────────────────┤
│                                                     │
│ > What is the state of prediction markets?         │  ← History Pane
│                                                     │  (scrollable,
│ • Prediction markets are seeing increased          │   fills all
│   adoption in 2024...                              │   available
│                                                     │   space)
│   ▸ fetch_market_data(market="polymarket")        │
│     ↳ Total volume: $1.2B | Active markets: 450   │
│                                                     │
│   💭 Thought for 0.8s                              │
│                                                     │
│ • The data shows strong growth trends...           │
│                                                     │
│ [Working...] (status line - optional)              │
├─────────────────────────────────────────────────────┤  ← Top separator
│ > your message here_                               │  ← Input Bar (1 line)
├─────────────────────────────────────────────────────┤  ← Bottom separator
│ esc interrupt • ctrl+l clear • ctrl+c exit         │  ← Shortcuts (1 line)
└─────────────────────────────────────────────────────┘
```

### User Interaction

1. **User Types**: Text appears in the Input Bar at the bottom
2. **User Hits Enter**:
   - Text is captured and moved to History Pane (formatted as `> message`)
   - Input Bar is instantly cleared
   - Cursor remains in the Input Bar, ready for next command
   - Agent processes the message and updates appear in History Pane
3. **Agent Responds**:
   - All output (thinking, tool calls, responses) streams into History Pane
   - Input Bar remains fixed and ready at the bottom
   - No scrolling of the input area

## Files

### `tui.py`
Core TUI implementation using `prompt_toolkit`:

- **TUIApp**: Main TUI application class
  - `_create_layout()`: Builds the full-screen layout (Header | History | Status | Input | Shortcuts)
  - `_create_key_bindings()`: Keyboard shortcuts (Enter, ESC, Ctrl+C, Ctrl+T, Ctrl+O, Ctrl+L)
  - `add_user_message()`, `add_agent_message()`: Add messages to history
  - `add_tool_action()`, `add_tool_result()`: Add tool executions
  - `add_thinking()`: Add thinking indicators
  - `set_status()`: Update status line
  - `run()`: Run the application (synchronous)
  - `run_async()`: Run the application (asynchronous)

### `app_tui.py`
Integration of TUI with the agent system:

- **ConsoleTUIApp**: Main console application using TUI
  - Integrates with `AgentFactory` and `AgentSession`
  - Handles slash commands (`/help`, `/clear`, `/config`, `/exit`)
  - Connects user input to agent execution
  - Uses `TUICallbackHandler` to update UI during agent execution

### `demo_tui.py`
Standalone demo that showcases the TUI without requiring full agent setup:

- Simulates agent responses and tool executions
- Demonstrates the full interaction flow
- Perfect for testing UI/UX changes independently

### Legacy Files (to be deprecated)
- `app.py`: Original sequential printing approach (Rich-based)
- `input_handler.py`: Basic input handling with `input()`
- `renderer.py`: Rich-based rendering (still used for some formatting)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Submit input message |
| `ESC` | Interrupt ongoing task |
| `Ctrl+C` | Exit application |
| `Ctrl+T` | Show todos (coming soon) |
| `Ctrl+O` | Expand/collapse details (coming soon) |
| `Ctrl+L` | Clear screen |

## Usage

### Running the Demo

```bash
cd orbiton-agent
uv run python -m console.demo_tui
```

This will launch the full-screen TUI demo with simulated responses. You can:
- Type messages and press Enter to see simulated agent responses
- Use keyboard shortcuts to interact
- Test the UI/UX without needing API keys or agent configuration

### Running with Real Agent

```bash
cd orbiton-agent
uv run python main.py --tui
```

(Note: This requires updating `main.py` to support the `--tui` flag)

### Programmatic Usage

```python
from console.tui import TUIApp

def on_user_input(text: str):
    """Handle user input."""
    tui.add_agent_message(f"You said: {text}")

tui = TUIApp(
    agent_name="Orbiton Agent",
    model="claude-sonnet-4",
    on_input=on_user_input,
)

tui.add_info_message("Welcome!")
tui.run()
```

## Design Philosophy

The TUI follows the "glass box" design philosophy:

1. **Transparency**: Show what the agent is thinking and doing
2. **Progressive Disclosure**: Collapse long outputs by default, expand on demand
3. **Contextual Hints**: Show keyboard shortcuts and interaction hints
4. **Hierarchical Information**: Use tree structures for tool execution chains
5. **Live Updates**: Stream agent activity in real-time

## Color Scheme

The TUI uses a dark theme optimized for terminal readability:

- **Header**: White on dark background (`#1a1a2e`)
- **History**: Light text on dark background (`#0f0f23`)
- **User messages**: Cyan (`#00d4ff`)
- **Agent messages**: Green (`#00ff88`)
- **Tool actions**: Green (`#00ff88`)
- **Tool results**: Cyan (`#00d4ff`)
- **Thinking**: Gray italic (`#888888`)
- **Errors**: Red (`#ff4444`)
- **Warnings**: Orange (`#ffaa00`)
- **Input**: White text on dark background

## Key Improvements Over Original

1. ✅ **Fixed Input Bar**: Always at the bottom, never scrolls away
2. ✅ **Persistent Layout**: No more sequential printing - proper TUI structure
3. ✅ **No Duplication**: Messages appear only once in history, input bar clears after Enter
4. ✅ **Keyboard Shortcuts**: Full keyboard control (ESC, Ctrl+C, Ctrl+L, etc.)
5. ✅ **Scrollable History**: Navigate through long conversations easily
6. ✅ **Live Status Updates**: Status line shows current activity
7. ✅ **Clean Separation**: History (read-only) and Input (write-only) are clearly separated

## Future Enhancements

- [ ] Implement progressive disclosure (Ctrl+O to expand/collapse)
- [ ] Add todo list viewer (Ctrl+T)
- [ ] Mouse support for clicking on expandable sections
- [ ] Syntax highlighting for code blocks in history
- [ ] Search/filter in history
- [ ] Save conversation to file
- [ ] Multi-line input support
- [ ] Auto-completion for commands

## Dependencies

- `prompt_toolkit>=3.0.51`: Full-screen TUI framework
- `rich>=13.0.0`: Text formatting and styling (used for some rendering)

## Testing

To test the TUI layout:

```bash
# Run the demo
cd orbiton-agent
uv run python console/demo_tui.py

# In the TUI:
# 1. Type a message and press Enter
# 2. Try keyboard shortcuts (Ctrl+L to clear, Ctrl+C to exit)
# 3. Scroll through history if needed
```

## Troubleshooting

**Issue**: TUI doesn't render properly
- **Solution**: Ensure your terminal supports 256 colors and UTF-8 encoding

**Issue**: Input doesn't work
- **Solution**: The Input Bar should always be focused. Press Tab if focus is lost.

**Issue**: Can't scroll history
- **Solution**: Use arrow keys or Page Up/Down to scroll the History Pane

**Issue**: Keyboard shortcuts don't work
- **Solution**: Make sure you're in the input field and not in another terminal mode

## Contributing

When adding new features to the TUI:

1. Add methods to `TUIApp` class in `tui.py`
2. Update keyboard bindings in `_create_key_bindings()`
3. Test with `demo_tui.py` first
4. Update this README with new features
5. Consider backward compatibility with legacy `app.py`
