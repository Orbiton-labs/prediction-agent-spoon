# Phase 4: Interactive Features & Commands

## Objective
Implement interactive features including keyboard shortcuts, command system, progressive disclosure controls, and interruption handling to create a fully interactive CLI experience.

## Files to Create
- `orbiton-agent/console/commands.py` - Command handlers and routing
- `orbiton-agent/console/keybindings.py` - Keyboard shortcut management

## Todo List

### Keyboard Bindings (`keybindings.py`)
- [ ] Create `KeyBindingManager` class
- [ ] Implement `setup_bindings(app_instance)`:
  - [ ] Register key handlers with app
  - [ ] Return key binding configuration

#### Key Handlers to Implement
- [ ] Implement `handle_ctrl_o()`:
  - [ ] Get current cursor position / focused section
  - [ ] Toggle expandable section at cursor
  - [ ] Re-render affected section
  - [ ] Update display
- [ ] Implement `handle_esc()`:
  - [ ] Check if agent is executing
  - [ ] Call agent.interrupt()
  - [ ] Display interruption message
  - [ ] Clear status indicators
- [ ] Implement `handle_ctrl_c()`:
  - [ ] Confirm exit (if in conversation)
  - [ ] Call app.shutdown()
  - [ ] Clean exit
- [ ] Implement `handle_up_arrow()`:
  - [ ] Navigate to previous message (optional)
  - [ ] Or scroll history
- [ ] Implement `handle_down_arrow()`:
  - [ ] Navigate to next message (optional)
  - [ ] Or scroll history
- [ ] Implement `handle_ctrl_l()`:
  - [ ] Clear screen (preserve conversation)
  - [ ] Re-render from top

### Progressive Disclosure Logic
- [ ] Enhance `ExpandableSection` from Phase 2:
  - [ ] Add cursor tracking
  - [ ] Track section position in display
  - [ ] Support focus state
- [ ] Implement `SectionNavigator`:
  - [ ] Track all expandable sections
  - [ ] Navigate between sections
  - [ ] Get section at cursor position
  - [ ] Toggle section state
- [ ] Implement `toggle_section(section_id)`:
  - [ ] Update section state (expanded ↔ collapsed)
  - [ ] Re-render section
  - [ ] Update hints
- [ ] Implement section hints:
  - [ ] Collapsed: "(ctrl+o to expand)" + "+N lines"
  - [ ] Expanded: "(ctrl+o to collapse)"

### Command System (`commands.py`)
- [ ] Create `CommandHandler` class
- [ ] Implement command registry:
  - [ ] Dictionary mapping command names to handlers
  - [ ] Command metadata (description, usage, aliases)

#### Core Commands
- [ ] Implement `/help`:
  - [ ] Display available commands
  - [ ] Show keyboard shortcuts
  - [ ] Display tips and tricks
  - [ ] Render in formatted panel
- [ ] Implement `/clear`:
  - [ ] Clear conversation history
  - [ ] Clear expandable sections
  - [ ] Reset display
  - [ ] Confirm action (optional)
- [ ] Implement `/exit` or `/quit`:
  - [ ] Save session (optional)
  - [ ] Call app.shutdown()
  - [ ] Display goodbye message
- [ ] Implement `/config`:
  - [ ] Display current configuration
  - [ ] Support `/config get <key>`
  - [ ] Support `/config set <key> <value>`
  - [ ] Reload configuration
- [ ] Implement `/agent`:
  - [ ] List available agents: `/agent list`
  - [ ] Switch agent: `/agent <name>`
  - [ ] Show current agent: `/agent current`
  - [ ] Display agent capabilities
- [ ] Implement `/model`:
  - [ ] List available models: `/model list`
  - [ ] Switch model: `/model <name>`
  - [ ] Show current model: `/model current`
- [ ] Implement `/history`:
  - [ ] Display conversation history
  - [ ] Support filtering
  - [ ] Export to file (optional)
- [ ] Implement `/save`:
  - [ ] Save conversation to file
  - [ ] Support format options (json, md, txt)
  - [ ] Default filename with timestamp

#### Command Parsing
- [ ] Implement `parse_command(input_text)`:
  - [ ] Detect if input starts with "/"
  - [ ] Extract command name
  - [ ] Extract arguments
  - [ ] Return command object
- [ ] Implement `execute_command(command, args)`:
  - [ ] Look up handler in registry
  - [ ] Validate arguments
  - [ ] Execute handler
  - [ ] Return result
  - [ ] Handle errors (unknown command, invalid args)

### Interruption System
- [ ] Create `InterruptionHandler` class
- [ ] Implement `request_interrupt()`:
  - [ ] Set interruption flag
  - [ ] Signal agent session
  - [ ] Display status: "Interrupting..."
- [ ] Implement `handle_interruption()`:
  - [ ] Cancel ongoing LLM requests
  - [ ] Clean up partial results
  - [ ] Display interruption message
  - [ ] Reset state
  - [ ] Return to input prompt
- [ ] Integrate with agent session:
  - [ ] Check interruption flag in execute loop
  - [ ] Graceful cancellation
  - [ ] Preserve conversation state up to interruption

### Input Enhancement
- [ ] Enhance input handler from Phase 2:
  - [ ] Support command history (up/down arrows)
  - [ ] Support multi-line input (optional)
  - [ ] Auto-complete commands (tab)
  - [ ] Syntax highlighting for commands
- [ ] Implement `CommandCompleter`:
  - [ ] Auto-complete command names
  - [ ] Auto-complete arguments
  - [ ] Show suggestions

### Testing
- [ ] Test keyboard shortcuts:
  - [ ] ctrl+o toggles sections
  - [ ] ESC interrupts execution
  - [ ] ctrl+c exits gracefully
  - [ ] ctrl+l clears screen
- [ ] Test all commands:
  - [ ] `/help` displays help
  - [ ] `/clear` clears conversation
  - [ ] `/exit` quits app
  - [ ] `/config` manages configuration
  - [ ] `/agent` switches agents
  - [ ] `/model` switches models
  - [ ] `/history` shows history
  - [ ] `/save` saves conversation
- [ ] Test progressive disclosure:
  - [ ] Sections toggle correctly
  - [ ] Hints display appropriately
  - [ ] Navigation works
- [ ] Test interruption:
  - [ ] ESC stops agent during thinking
  - [ ] ESC stops agent during tool execution
  - [ ] State remains consistent after interruption
- [ ] Test command parsing:
  - [ ] Valid commands parse correctly
  - [ ] Invalid commands show error
  - [ ] Arguments parse correctly
- [ ] Test edge cases:
  - [ ] Rapid key presses
  - [ ] Interruption during interruption
  - [ ] Command during agent execution

## Expected Outcomes
- ✅ ctrl+o expands/collapses sections
- ✅ ESC interrupts agent gracefully
- ✅ All commands work correctly
- ✅ Progressive disclosure is smooth
- ✅ Command auto-completion works (if implemented)
- ✅ Keyboard shortcuts are intuitive
- ✅ Interruption doesn't break state
- ✅ Help system is comprehensive

## Dependencies
- Phase 1 completed (project structure)
- Phase 2 completed (console UI)
- Phase 3 completed (agent integration)
- `prompt_toolkit` library (for advanced input handling)

## Time Estimate
~2-3 hours

## User Experience Notes
- Commands should have intuitive names
- Keyboard shortcuts should follow common conventions
- Help should be easily discoverable
- Errors should be helpful, not cryptic
- Progressive disclosure should be smooth and not jarring
- Interruption should feel responsive
