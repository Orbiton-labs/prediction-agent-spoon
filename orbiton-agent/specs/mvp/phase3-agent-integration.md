# Phase 3: Agent Integration & Callbacks

## Objective
Integrate the Orbiton console UI with existing spoon_ai agents, implementing custom callback handlers to capture and display agent actions, tool usage, and thinking processes in real-time.

## Files to Create
- `orbiton-agent/agents/__init__.py`
- `orbiton-agent/agents/factory.py` - Agent factory and initialization
- `orbiton-agent/agents/console_callback.py` - Custom callback handler for console

## Todo List

### Package Setup
- [ ] Create `agents/` directory
- [ ] Create `agents/__init__.py`

### Console Callback Handler (`console_callback.py`)
- [ ] Create `ConsoleCallbackHandler` class extending `BaseCallbackHandler`
- [ ] Add constructor:
  - [ ] Accept `renderer` parameter (from console.renderer)
  - [ ] Accept `console` parameter (Rich Console instance)
  - [ ] Initialize state tracking (current_tool, thinking_buffer, etc.)

#### Callback Methods to Implement
- [ ] Implement `on_llm_start(serialized, prompts, **kwargs)`:
  - [ ] Display status: "Agent is thinking..."
  - [ ] Show spinner
  - [ ] Initialize thinking buffer
- [ ] Implement `on_llm_new_token(token, **kwargs)`:
  - [ ] Stream token to Live display
  - [ ] Update thinking buffer
  - [ ] Render thinking mode in real-time
  - [ ] Handle special tokens (thinking markers)
- [ ] Implement `on_llm_end(response, **kwargs)`:
  - [ ] Finalize thinking display
  - [ ] Clear status if no tools to execute
- [ ] Implement `on_llm_error(error, **kwargs)`:
  - [ ] Display error message
  - [ ] Clear status
  - [ ] Log error details
- [ ] Implement `on_tool_start(serialized, input_str, **kwargs)`:
  - [ ] Extract tool name and arguments
  - [ ] Render tool action: "▸ tool_name(args)"
  - [ ] Update status: "Executing {tool_name}..."
  - [ ] Track tool execution start time
- [ ] Implement `on_tool_end(output, **kwargs)`:
  - [ ] Process tool output
  - [ ] Determine if output should be expandable
  - [ ] Render tool result: "↳ summary"
  - [ ] Register expandable section if needed
  - [ ] Calculate execution time
  - [ ] Clear tool status
- [ ] Implement `on_tool_error(error, **kwargs)`:
  - [ ] Render error result
  - [ ] Display error message
  - [ ] Clear tool status
- [ ] Implement `on_agent_action(action, **kwargs)`:
  - [ ] Track agent decision-making
  - [ ] Optional: Display reasoning (if available)
- [ ] Implement `on_agent_finish(finish, **kwargs)`:
  - [ ] Display final response
  - [ ] Clear all status indicators
  - [ ] Render completion message
- [ ] Implement `on_chain_start(serialized, inputs, **kwargs)`:
  - [ ] Optional: Display chain beginning
- [ ] Implement `on_chain_end(outputs, **kwargs)`:
  - [ ] Optional: Display chain completion

#### Helper Methods
- [ ] Implement `_should_expand_output(output, max_lines=5)`:
  - [ ] Check output length
  - [ ] Determine if progressive disclosure needed
  - [ ] Return boolean
- [ ] Implement `_create_summary(output, max_chars=100)`:
  - [ ] Generate short summary of output
  - [ ] Add line count hint
  - [ ] Return formatted summary
- [ ] Implement `_detect_code_language(text)`:
  - [ ] Detect programming language for syntax highlighting
  - [ ] Return language identifier
- [ ] Implement `_format_args(args)`:
  - [ ] Format tool arguments for display
  - [ ] Handle long arguments
  - [ ] Return formatted string

### Agent Factory (`factory.py`)
- [ ] Create `AgentFactory` class
- [ ] Implement `create_agent(agent_type, config, callback_handler)`:
  - [ ] Support "react" → SpoonReactAI
  - [ ] Support "react-mcp" → SpoonReactMCP
  - [ ] Load configuration from config
  - [ ] Initialize LLMManager
  - [ ] Attach callback handler
  - [ ] Return configured agent instance
- [ ] Implement `list_available_agents()`:
  - [ ] Return list of supported agent types
  - [ ] Include descriptions
- [ ] Implement `get_agent_info(agent_type)`:
  - [ ] Return agent capabilities
  - [ ] Return required configuration
  - [ ] Return supported tools
- [ ] Add error handling:
  - [ ] Invalid agent type
  - [ ] Missing configuration
  - [ ] LLM initialization failures

### Integration Layer
- [ ] Create `AgentSession` class:
  - [ ] Wrap agent instance
  - [ ] Manage conversation state
  - [ ] Handle interruptions
  - [ ] Track execution state
- [ ] Implement `execute(user_input)`:
  - [ ] Validate input
  - [ ] Call agent with input
  - [ ] Handle exceptions
  - [ ] Return response
- [ ] Implement `interrupt()`:
  - [ ] Signal agent to stop
  - [ ] Cancel ongoing LLM calls
  - [ ] Clean up state
- [ ] Implement `reset()`:
  - [ ] Clear conversation history
  - [ ] Reset agent state
  - [ ] Reinitialize if needed

### Testing
- [ ] Test callback handler with mock agent
- [ ] Test tool execution display:
  - [ ] Simple tool with short output
  - [ ] Tool with long output (expandable)
  - [ ] Tool with code output (syntax highlighting)
  - [ ] Tool with error
- [ ] Test thinking mode streaming
- [ ] Test agent creation via factory
- [ ] Test SpoonReactAI integration
- [ ] Test SpoonReactMCP integration (if MCP configured)
- [ ] Test interruption handling
- [ ] Test error scenarios:
  - [ ] LLM API errors
  - [ ] Tool execution errors
  - [ ] Invalid inputs
- [ ] Verify callback timing (events trigger in correct order)
- [ ] Test with real agent conversation

## Expected Outcomes
- ✅ Console callback handler captures all agent events
- ✅ Tool usage displays in real-time as hierarchy
- ✅ Thinking mode streams token-by-token
- ✅ Agent factory creates configured agents
- ✅ Integration with SpoonReactAI works
- ✅ Progressive disclosure triggers for long outputs
- ✅ Errors display properly
- ✅ Interruption stops agent gracefully

## Dependencies
- Phase 1 completed (project structure)
- Phase 2 completed (console UI components)
- `spoon_ai.agents` (existing in parent project)
- `spoon_ai.callbacks.base.BaseCallbackHandler` (existing)
- `spoon_ai.llm.LLMManager` (existing)

## Time Estimate
~3-4 hours

## Integration Points
- `console.renderer` for UI rendering
- `spoon_ai.agents.SpoonReactAI` for main agent
- `spoon_ai.agents.SpoonReactMCP` for MCP support
- `spoon_ai.callbacks.base.BaseCallbackHandler` as base class
- `spoon_ai.llm.LLMManager` for LLM initialization

## Notes
- Callbacks fire in this order: llm_start → new_token (multiple) → llm_end → tool_start → tool_end → agent_finish
- Some agents may not fire all callbacks depending on their implementation
- Thinking mode tokens may need special parsing (check for <thinking> tags)
- MCP tools may have different output formats than standard tools
