# Phase 2: Console UI Components (Rich Library)

## Objective
Build the visual interface components using the Rich library to create the "glass box" CLI experience with headers, message display, tool visualization, and status indicators.

## Files to Create
- `orbiton-agent/console/__init__.py`
- `orbiton-agent/console/app.py` - Main console application
- `orbiton-agent/console/renderer.py` - UI rendering engine
- `orbiton-agent/console/theme.py` - Color schemes and styling
- `orbiton-agent/console/input_handler.py` - User input management

## Todo List

### Package Setup
- [ ] Create `console/` directory
- [ ] Create `console/__init__.py`

### Theme System (`theme.py`)
- [ ] Define color constants:
  - [ ] USER_COLOR = "cyan" (for user messages)
  - [ ] AGENT_COLOR = "green" (for agent messages)
  - [ ] TOOL_ACTION_COLOR = "green" (for tool actions ▸)
  - [ ] TOOL_RESULT_COLOR = "cyan" (for tool results ↳)
  - [ ] THINKING_COLOR = "dim cyan" (for thinking mode)
  - [ ] STATUS_COLOR = "yellow" (for status messages)
  - [ ] ERROR_COLOR = "red" (for errors)
  - [ ] HEADER_PRIMARY = "bold white" (for header primary info)
  - [ ] HEADER_SECONDARY = "dim white" (for header secondary info)
- [ ] Create Rich Theme object with custom styles
- [ ] Define box styles (rounded, double, heavy for panels)
- [ ] Define spinner types for different states

### Renderer Engine (`renderer.py`)
- [ ] Implement `render_header()`:
  - [ ] Display "Orbiton Agent | Model | Working Directory"
  - [ ] Two-tone styling (primary bold, secondary dimmed)
  - [ ] Use Panel with custom border style
- [ ] Implement `render_user_message(message)`:
  - [ ] Format: "> {message}"
  - [ ] Style with USER_COLOR
- [ ] Implement `render_agent_message(message)`:
  - [ ] Format: "• {message}"
  - [ ] Support markdown rendering
  - [ ] Style with AGENT_COLOR
- [ ] Implement `render_tool_action(tool_name, args)`:
  - [ ] Format: "▸ {tool_name}({args})"
  - [ ] Syntax highlighting for arguments
  - [ ] Tree node structure
  - [ ] TOOL_ACTION_COLOR styling
- [ ] Implement `render_tool_result(result, expandable=False)`:
  - [ ] Format: "↳ {summary}"
  - [ ] Show hints: "(ctrl+o to expand)" if expandable
  - [ ] Show line counts: "+N lines" for collapsed content
  - [ ] Support syntax highlighting for code results
  - [ ] TOOL_RESULT_COLOR styling
- [ ] Implement `render_thinking(text, streaming=True)`:
  - [ ] Use Live display for streaming
  - [ ] Format: "💭 Thought for Xs (ctrl+o to show thinking)"
  - [ ] THINKING_COLOR styling
  - [ ] Support expandable thinking content
- [ ] Implement `render_status(message, spinner=True)`:
  - [ ] Format: "* {message} (esc to interrupt)"
  - [ ] Spinner animation
  - [ ] STATUS_COLOR styling
- [ ] Implement `render_error(message)`:
  - [ ] Format with ERROR_COLOR
  - [ ] Panel with border for visibility

### Progressive Disclosure System
- [ ] Create `ExpandableSection` class:
  - [ ] Track section ID
  - [ ] Track expanded/collapsed state
  - [ ] Store full content
  - [ ] Generate summary/preview
- [ ] Implement `SectionManager`:
  - [ ] Register expandable sections
  - [ ] Toggle section state
  - [ ] Get section by ID
  - [ ] Track cursor position for ctrl+o

### Input Handler (`input_handler.py`)
- [ ] Implement `get_user_input()`:
  - [ ] Use Rich Console.input() with formatting
  - [ ] Support multi-line input (optional)
  - [ ] Handle empty input
  - [ ] Return formatted text
- [ ] Implement keyboard event handling:
  - [ ] Detect ctrl+o for expand/collapse
  - [ ] Detect ESC for interruption
  - [ ] Detect ctrl+c for exit

### Main Console App (`app.py`)
- [ ] Create `ConsoleApp` class:
  - [ ] Initialize Rich Console
  - [ ] Load theme
  - [ ] Initialize renderer
  - [ ] Track conversation history
  - [ ] Track expandable sections
- [ ] Implement `run()` method:
  - [ ] Display header
  - [ ] Main input loop
  - [ ] Handle user commands
  - [ ] Coordinate rendering
- [ ] Implement `display_welcome()`:
  - [ ] Show welcome message
  - [ ] Display available commands
  - [ ] Show keyboard shortcuts
- [ ] Implement `clear_screen()`:
  - [ ] Clear console (preserve header)
- [ ] Implement `shutdown()`:
  - [ ] Cleanup resources
  - [ ] Display goodbye message

### Testing
- [ ] Test header rendering
- [ ] Test message display (user and agent)
- [ ] Test tool action/result rendering
- [ ] Test thinking mode display
- [ ] Test status line with spinner
- [ ] Test progressive disclosure toggle
- [ ] Test input handling
- [ ] Test with mock conversation data
- [ ] Verify colors and styling
- [ ] Test on different terminal sizes

## Expected Outcomes
- ✅ Header displays correctly with context
- ✅ User and agent messages render with proper formatting
- ✅ Tool usage shows hierarchically (▸ action → ↳ result)
- ✅ Thinking mode streams in real-time
- ✅ Progressive disclosure works (expandable sections)
- ✅ Status line shows with spinner
- ✅ User can input messages
- ✅ UI matches design.md specifications

## Dependencies
- `rich` library (already available)
- Phase 1 completed (basic project structure)

## Time Estimate
~2-3 hours

## Reference
See `specs/design.md` for detailed UI/UX specifications and the "glass box" design philosophy.
