# Debug Logging for Orbiton Agent

This document explains how to enable debug logging to see what's being sent to the OpenAI SDK and troubleshoot issues.

## Quick Start

Run the TUI app with debug logging enabled:

```bash
cd orbiton-agent
uv run python run_debug.py
```

## What Gets Logged

When debug mode is enabled, you'll see:

1. **Agent Input/Output**
   - User input to the agent
   - Agent responses
   - Response length and timing

2. **OpenAI SDK Requests**
   - HTTP requests to the OpenAI API
   - Request headers and body
   - API endpoint URLs

3. **OpenAI SDK Responses**
   - HTTP responses from the API
   - Response status codes
   - Response body (including token usage)

4. **LLM Provider Activity**
   - Provider initialization
   - Model selection
   - Token counting and memory management

5. **HTTP Layer (httpx)**
   - Low-level HTTP request/response details
   - Connection pooling
   - Retry attempts

## Log Output Locations

Debug logs are written to **two places**:

1. **Console** - Real-time output while running
2. **Log File** - `logs/orbiton_debug.log`

### Viewing Logs

**Real-time (tail the log file):**
```bash
tail -f logs/orbiton_debug.log
```

**Search for specific patterns:**
```bash
# Find all API requests
grep "openai" logs/orbiton_debug.log

# Find all agent inputs
grep "AGENT INPUT" logs/orbiton_debug.log

# Find errors
grep "ERROR" logs/orbiton_debug.log
```

## Log Format

Logs follow this format:
```
YYYY-MM-DD HH:MM:SS,mmm - logger_name - LEVEL - message
```

Example:
```
2025-01-16 10:30:45,123 - agents.factory - INFO - ================================================================================
2025-01-16 10:30:45,124 - agents.factory - INFO - AGENT INPUT:
2025-01-16 10:30:45,125 - agents.factory - INFO -   User Input: Hello!
2025-01-16 10:30:45,126 - agents.factory - INFO - ================================================================================
2025-01-16 10:30:47,456 - openai - DEBUG - Request POST https://api.openai.com/v1/chat/completions
2025-01-16 10:30:47,457 - openai - DEBUG - Headers: {...}
2025-01-16 10:30:47,458 - openai - DEBUG - Body: {"model":"gpt-4o","messages":[...]}
2025-01-16 10:30:48,789 - openai - DEBUG - Response: 200 OK
2025-01-16 10:30:48,790 - agents.factory - INFO - ================================================================================
2025-01-16 10:30:48,791 - agents.factory - INFO - AGENT OUTPUT:
2025-01-16 10:30:48,792 - agents.factory - INFO -   Response: Hello! How can I help you today?
2025-01-16 10:30:48,793 - agents.factory - INFO -   Length: 35 chars
2025-01-16 10:30:48,794 - agents.factory - INFO - ================================================================================
```

## Debugging Specific Issues

### Check What's Being Sent to OpenAI

```bash
grep -A 10 "Request POST.*chat/completions" logs/orbiton_debug.log
```

This shows the exact JSON payload sent to the API.

### Check API Response Times

```bash
grep "Response:" logs/orbiton_debug.log | awk '{print $1, $2, $NF}'
```

### Find Token Usage

```bash
grep "usage" logs/orbiton_debug.log
```

### Debug Authentication Issues

```bash
grep -i "auth\|401\|403" logs/orbiton_debug.log
```

## Enabling Debug Mode in Your Code

If you're running the TUI from your own script:

```python
from console.app_tui import ConsoleTUIApp

config = {
    # ... your config ...
}

# Pass debug=True to enable logging
app = ConsoleTUIApp(config=config, debug=True)
app.run()
```

## Log Levels

The debug configuration enables these log levels:

| Logger | Level | What It Logs |
|--------|-------|--------------|
| `agents.factory` | DEBUG | Agent inputs/outputs |
| `spoon_ai` | DEBUG | All spoon_ai activity |
| `spoon_ai.llm` | DEBUG | LLM provider operations |
| `spoon_ai.llm.manager` | DEBUG | Provider initialization |
| `spoon_ai.llm.providers` | DEBUG | Provider-specific logs |
| `openai` | DEBUG | OpenAI SDK requests/responses |
| `httpx` | DEBUG | Low-level HTTP activity |

## Performance Impact

⚠️ **Warning:** Debug logging has performance overhead:

- Log file I/O adds latency (5-10ms per log entry)
- Console output can slow down execution
- Large log files can consume disk space

**Recommendation:** Only enable debug mode when troubleshooting.

## Disabling Debug Logging

To run without debug logging (normal mode):

```bash
# Use the regular run script
uv run python main.py

# Or explicitly pass debug=False
app = ConsoleTUIApp(config=config, debug=False)
```

## Log Rotation

To prevent logs from growing too large:

```bash
# Clear old logs
rm logs/orbiton_debug.log

# Or archive them
mv logs/orbiton_debug.log logs/orbiton_debug_$(date +%Y%m%d_%H%M%S).log
```

## Troubleshooting

### Log file not created?

Check that the `logs/` directory exists:
```bash
mkdir -p logs
```

### Permission denied?

```bash
chmod 755 logs
chmod 644 logs/orbiton_debug.log
```

### Too much output?

Reduce logging by adjusting log levels in `console/app_tui.py`:

```python
# Less verbose - only show INFO and above
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
```

## Examples

### Example 1: Debug Slow Responses

1. Enable debug logging: `uv run python run_debug.py`
2. Send a message
3. Check the log file:
   ```bash
   grep "AGENT INPUT\|AGENT OUTPUT\|Response:" logs/orbiton_debug.log | tail -20
   ```
4. Look at timestamps to see where time is spent

### Example 2: Debug API Errors

1. Enable debug logging
2. Trigger the error
3. Check for error messages:
   ```bash
   grep -i "error\|exception" logs/orbiton_debug.log | tail -10
   ```

### Example 3: Verify API Request Format

1. Enable debug logging
2. Send a message
3. Extract the request body:
   ```bash
   grep -A 5 '"messages":' logs/orbiton_debug.log | tail -20
   ```

This shows exactly what messages are being sent to the API.

## Additional Resources

- [OpenAI API Docs](https://platform.openai.com/docs/api-reference)
- [httpx Logging](https://www.python-httpx.org/logging/)
- [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
