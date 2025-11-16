# UI Freeze Fix

## Problem
After adding subprocess output suppression, the UI was freezing and not showing tool usage.

## Root Causes

1. **stdout/stderr suppression during execution** - The `suppress_subprocess_output()` context manager was redirecting file descriptors 1 and 2 to `/dev/null` during agent execution, which prevented the TUI from rendering (prompt_toolkit needs stdout)

2. **Callback handler not connected** - The agent was being created with `callback_handler=None`, so tool usage was never displayed in the TUI

3. **Missing inheritance** - `TUICallbackHandler` didn't inherit from `BaseCallbackHandler`, so it wasn't recognized by spoon_ai

## Fixes Applied

### 1. Removed stdout suppression during execution (`console/app_tui.py:521-523`)

**Before:**
```python
with suppress_subprocess_output(debug=self.debug):
    response = self.agent_session.execute(message)
```

**After:**
```python
# Execute agent with callbacks enabled
# The callbacks will show tool usage and responses
response = self.agent_session.execute(message)
```

### 2. Connected callback handler (`console/app_tui.py:274-279`)

**Before:**
```python
agent = AgentFactory.create_agent(
    agent_type=self.current_agent_type,
    config=agent_config,
    callback_handler=None,  # Will be handled separately
)
```

**After:**
```python
agent = AgentFactory.create_agent(
    agent_type=self.current_agent_type,
    config=agent_config,
    callback_handler=self.callback_handler,  # Pass TUI callback
)
```

### 3. Added proper inheritance (`console/app_tui.py:56,66`)

**Before:**
```python
class TUICallbackHandler:
    def __init__(self, tui: TUIApp):
        self.tui = tui
        ...
```

**After:**
```python
from spoon_ai.callbacks.base import BaseCallbackHandler

class TUICallbackHandler(BaseCallbackHandler):
    def __init__(self, tui: TUIApp):
        super().__init__()
        self.tui = tui
        ...
```

## What Works Now

✅ **UI doesn't freeze** - TUI can render normally during execution
✅ **Tool usage is shown** - Callbacks display tool calls
✅ **Tool responses are shown** - Results are displayed in TUI
✅ **MCP debug messages filtered** - `on_tool_end` filters out `[GMCPT]` lines
✅ **Init messages suppressed** - Agent initialization still suppresses stdout

## Expected UI Flow

```
> ask gemini about how weather today in Hanoi ?

Processing...

▸ gemini-cli(query="Tell me about the weather in Hanoi today")
↳ The weather in Hanoi today is partly cloudy with a temperature of...

• Agent response here
```

## How Callbacks Work

1. User sends message
2. Agent executes
3. **on_tool_start** → Shows `▸ tool_name(params)`
4. **on_tool_end** → Shows `↳ result` (after filtering GMCPT messages)
5. **on_agent_finish** → Shows final agent response

## MCP Message Filtering

The `on_tool_end` callback filters out debug messages:
```python
filtered_lines = [
    line for line in lines
    if not (
        line.strip().startswith('[GMCPT]') or
        line.strip().startswith('[MCP]') or
        'listening on stdio' in line or
        'ctrl+l clear' in line
    )
]
```

## Testing

```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent
uv run python main.py
```

Try:
```
> ask gemini about how weather today in Hanoi ?
```

Should see:
- ✅ UI responsive (no freeze)
- ✅ Tool call displayed
- ✅ Tool response displayed
- ✅ No GMCPT debug messages
- ✅ Final agent response
