# MCP UI/UX Fixes

## Issues Fixed

1. ✅ **GMCPT debug messages appearing in UI**
2. ✅ **Tool call format not matching desired UX**
3. ✅ **Verbose logging from MCP subprocesses**

## Changes Made

### 1. Tool Display Format (`console/tui.py`)

**Before:**
```
  ▸ tool_name(input=...)      # 2 spaces indent, truncated args
    ↳ result                  # 4 spaces indent
```

**After:**
```
▸ tool_name(query="...", param="...")  # No indent, proper args
↳ result                                # No indent
```

**Changes:**
- Line 392: Removed extra indentation from tool action
- Line 409: Removed extra indentation from tool result
- Lines 378-388: Better argument formatting (shows full parameter names)
- Line 405: Increased result display from 200 to 300 chars

### 2. Argument Parsing (`console/app_tui.py:59-68`)

**Before:**
```python
args = {"input": input_str[:100]}  # Just truncated input
```

**After:**
```python
# Parse JSON arguments or format nicely
if input_str.strip().startswith("{"):
    args = json.loads(input_str)
else:
    args = {"query": input_str[:50] + "..."}
```

### 3. MCP Debug Message Filtering (`console/app_tui.py:72-86`)

Added filtering in `on_tool_end` to remove MCP debug output:
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

### 4. Subprocess Output Suppression (`console/app_tui.py:21-52`)

Created context manager to suppress stdout/stderr at file descriptor level:
```python
@contextmanager
def suppress_subprocess_output(debug=False):
    # Save original file descriptors
    original_stdout_fd = os.dup(1)
    original_stderr_fd = os.dup(2)

    # Redirect to devnull
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull_fd, 1)
    os.dup2(devnull_fd, 2)

    yield

    # Restore
    os.dup2(original_stdout_fd, 1)
    os.dup2(original_stderr_fd, 2)
```

Applied during agent execution (`console/app_tui.py:522-523`):
```python
with suppress_subprocess_output(debug=self.debug):
    response = self.agent_session.execute(message)
```

### 5. Logging Configuration (`main.py:92-122`)

- Changed level from `WARNING` to `ERROR`
- Simplified format to `"%(message)s"`
- Added suppressions for: `mcp`, `asyncio`, `fastmcp`
- Redirected logs to stderr

### 6. MCP Server Environment Variables (`agents/factory.py:70-76`)

Added environment variables to suppress MCP subprocess output:
```python
server_config["env"]["PYTHONWARNINGS"] = "ignore"
server_config["env"]["PYTHONUNBUFFERED"] = "0"
server_config["env"]["NODE_ENV"] = "production"
server_config["env"]["NPM_CONFIG_LOGLEVEL"] = "error"
```

### 7. Agent Initialization Suppression (`console/app_tui.py:195-252`)

Suppressed stdout/stderr during agent initialization to hide MCP tool init messages.

## Expected UI Output

### Tool Call Format

```
> User message here

▸ gemini-cli(query="Tell me about Kalshi...")
↳ Kalshi is a prediction market platform that allows users to...

• Agent response here
```

### No More Debug Messages

Before:
```
> [GMCPT] init gemini-mcp-tool
[GMCPT] gemini-mcp-tool listening on stdioand • ctrl+l clear • ctrl+c exit
[GMCPT] Raw: {...}
```

After:
```
(clean - no debug messages)
```

## Testing

Run the app:
```bash
cd /Users/meomeocoj/prediction-agent-spoon/orbiton-agent
uv run python main.py
```

Test with MCP tool:
```
> ask gemini about the kalshi market
```

Expected output:
- ✅ Clean tool call display: `▸ gemini-cli(query="...")`
- ✅ Clean result display: `↳ [response]`
- ✅ No `[GMCPT]` messages
- ✅ No debug logging visible

## Debug Mode

To see all messages (for debugging):
```bash
uv run python main.py --debug
```

In debug mode:
- Subprocess output is NOT suppressed
- All logging is visible
- MCP debug messages will appear (as intended)
