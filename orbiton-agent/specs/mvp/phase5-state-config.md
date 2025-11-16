# Phase 5: State Management & Configuration

## Objective
Implement robust configuration management and state persistence to support session continuity, configuration flexibility, and conversation history.

## Files to Create
- `orbiton-agent/config/__init__.py`
- `orbiton-agent/config/manager.py` - Configuration loading and management
- `orbiton-agent/config/schema.py` - Configuration validation
- `orbiton-agent/state/__init__.py`
- `orbiton-agent/state/session.py` - Session state management
- `orbiton-agent/state/persistence.py` - State persistence layer

## Todo List

### Configuration Package (`config/`)

#### Schema Definition (`schema.py`)
- [ ] Create `ConfigSchema` using Pydantic:
  - [ ] `llm` section:
    - [ ] `default_provider` (str)
    - [ ] `default_model` (str)
    - [ ] `temperature` (float, 0.0-1.0)
    - [ ] `max_tokens` (int)
    - [ ] `timeout` (int, seconds)
  - [ ] `agent` section:
    - [ ] `type` (str, default: "react")
    - [ ] `memory_enabled` (bool)
    - [ ] `max_iterations` (int)
    - [ ] `tools` (list of str)
  - [ ] `ui` section:
    - [ ] `theme` (str, default: "default")
    - [ ] `show_thinking` (bool, default: True)
    - [ ] `auto_expand_threshold` (int, lines)
    - [ ] `syntax_highlighting` (bool, default: True)
  - [ ] `session` section:
    - [ ] `save_history` (bool, default: True)
    - [ ] `history_dir` (str, default: "~/.orbiton/history")
    - [ ] `auto_save_interval` (int, seconds)
  - [ ] `mcp` section (optional):
    - [ ] `enabled` (bool)
    - [ ] `servers` (list of server configs)
- [ ] Add validation methods
- [ ] Add default values

#### Configuration Manager (`manager.py`)
- [ ] Create `ConfigManager` class
- [ ] Implement `__init__(config_path=None)`:
  - [ ] Set default config path
  - [ ] Load configuration
- [ ] Implement `load()`:
  - [ ] Load from config.json if exists
  - [ ] Load from .env for API keys
  - [ ] Merge with defaults
  - [ ] Validate against schema
  - [ ] Return config object
- [ ] Implement `save(config)`:
  - [ ] Validate config
  - [ ] Write to config.json
  - [ ] Preserve formatting
- [ ] Implement `get(key_path)`:
  - [ ] Support dot notation: "llm.temperature"
  - [ ] Return value or None
- [ ] Implement `set(key_path, value)`:
  - [ ] Support dot notation
  - [ ] Validate value
  - [ ] Update in-memory config
- [ ] Implement `reload()`:
  - [ ] Re-load from disk
  - [ ] Notify listeners (optional)
- [ ] Implement `validate()`:
  - [ ] Check all required fields
  - [ ] Validate types and ranges
  - [ ] Return validation result
- [ ] Add environment variable support:
  - [ ] Load .env file
  - [ ] Override config with env vars
  - [ ] Pattern: `ORBITON_LLM_MODEL` → `llm.model`

### State Management Package (`state/`)

#### Session State (`session.py`)
- [ ] Create `ConversationMessage` dataclass:
  - [ ] `role` (user/agent/system)
  - [ ] `content` (str)
  - [ ] `timestamp` (datetime)
  - [ ] `metadata` (dict)
  - [ ] `tool_calls` (list, optional)
- [ ] Create `ToolExecution` dataclass:
  - [ ] `tool_name` (str)
  - [ ] `arguments` (dict)
  - [ ] `result` (str)
  - [ ] `execution_time` (float)
  - [ ] `error` (str, optional)
- [ ] Create `SessionState` class:
  - [ ] `session_id` (str, UUID)
  - [ ] `created_at` (datetime)
  - [ ] `updated_at` (datetime)
  - [ ] `messages` (list of ConversationMessage)
  - [ ] `tool_executions` (list of ToolExecution)
  - [ ] `current_agent` (str)
  - [ ] `current_model` (str)
  - [ ] `metadata` (dict)
- [ ] Implement `SessionManager` class:
  - [ ] `create_session()` → new SessionState
  - [ ] `add_message(role, content, metadata)`
  - [ ] `add_tool_execution(tool_execution)`
  - [ ] `get_messages(limit=None, offset=0)`
  - [ ] `get_context(max_tokens=None)` → formatted for LLM
  - [ ] `clear_history()`
  - [ ] `get_statistics()` → message count, tool count, etc.

#### Persistence Layer (`persistence.py`)
- [ ] Create `SessionPersistence` class
- [ ] Implement `save_session(session_state, path=None)`:
  - [ ] Serialize SessionState to JSON
  - [ ] Save to file
  - [ ] Handle errors gracefully
- [ ] Implement `load_session(path)`:
  - [ ] Load JSON from file
  - [ ] Deserialize to SessionState
  - [ ] Validate structure
  - [ ] Return SessionState or None
- [ ] Implement `list_sessions(directory)`:
  - [ ] Scan history directory
  - [ ] Return list of session metadata
  - [ ] Sort by date (newest first)
- [ ] Implement `delete_session(session_id)`:
  - [ ] Remove session file
  - [ ] Confirm deletion
- [ ] Implement `export_session(session_id, format="md")`:
  - [ ] Support markdown format
  - [ ] Support JSON format
  - [ ] Support text format
  - [ ] Return formatted string

#### Auto-save Mechanism
- [ ] Create `AutoSaver` class:
  - [ ] Background thread for periodic saves
  - [ ] Save on significant events (every N messages)
  - [ ] Save on exit
- [ ] Implement `start_auto_save(session_manager, interval)`:
  - [ ] Start background thread
  - [ ] Periodic save loop
- [ ] Implement `stop_auto_save()`:
  - [ ] Stop thread gracefully
  - [ ] Final save

### Integration with Console App
- [ ] Update `ConsoleApp` to use ConfigManager:
  - [ ] Load config on startup
  - [ ] Apply UI preferences
  - [ ] Configure agent with settings
- [ ] Update `ConsoleApp` to use SessionManager:
  - [ ] Create session on startup
  - [ ] Track messages
  - [ ] Track tool executions
  - [ ] Auto-save enabled
- [ ] Update commands to use state:
  - [ ] `/config` uses ConfigManager
  - [ ] `/history` uses SessionManager
  - [ ] `/save` uses SessionPersistence
  - [ ] `/clear` clears SessionState

### Testing
- [ ] Test configuration loading:
  - [ ] Load from defaults.json
  - [ ] Load from custom path
  - [ ] Override with .env
  - [ ] Validation catches errors
- [ ] Test configuration management:
  - [ ] Get values with dot notation
  - [ ] Set values and save
  - [ ] Reload configuration
- [ ] Test session state:
  - [ ] Add messages
  - [ ] Add tool executions
  - [ ] Retrieve messages
  - [ ] Get context for LLM
  - [ ] Clear history
- [ ] Test persistence:
  - [ ] Save session to file
  - [ ] Load session from file
  - [ ] List sessions
  - [ ] Delete session
  - [ ] Export in different formats
- [ ] Test auto-save:
  - [ ] Periodic saves work
  - [ ] Save on exit
  - [ ] No data loss
- [ ] Test integration:
  - [ ] Config changes apply immediately
  - [ ] Session persists across restarts (optional for MVP)
  - [ ] Commands interact with state correctly

## Expected Outcomes
- ✅ Configuration loads from multiple sources
- ✅ Configuration can be modified at runtime
- ✅ Session state tracks all interactions
- ✅ Conversations can be saved and loaded
- ✅ Auto-save prevents data loss
- ✅ Export works in multiple formats
- ✅ Config validation prevents invalid settings

## Dependencies
- Phase 1 completed (project structure)
- Phase 2 completed (console UI)
- Phase 3 completed (agent integration)
- Phase 4 completed (commands)
- `pydantic` library (for config validation)
- `python-dotenv` library (for .env loading)

## Time Estimate
~2-3 hours

## File Structure After Phase 5
```
orbiton-agent/
├── config/
│   ├── __init__.py
│   ├── manager.py
│   ├── schema.py
│   └── defaults.json
├── state/
│   ├── __init__.py
│   ├── session.py
│   └── persistence.py
└── ...
```

## Notes
- Configuration should support hot-reload where possible
- Session state should be thread-safe (if needed)
- Auto-save should not block main thread
- Consider privacy: don't save API keys in session files
- Export format should be human-readable (markdown preferred)
