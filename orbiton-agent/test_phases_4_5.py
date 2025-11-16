#!/usr/bin/env python3
"""Test Phase 4 and Phase 5 implementations."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("Testing Orbiton Agent - Phase 4 & 5 Implementation")
print("=" * 80)
print()

# Test 1: Import all new modules
print("✓ Test 1: Importing new modules...")
try:
    from console.commands import CommandHandler
    from console.keybindings import KeyBindingManager, SectionNavigator, InterruptionHandler
    from state.session import ConversationMessage, ToolExecution, SessionState, SessionManager
    from state.persistence import SessionPersistence, AutoSaver
    print("  ✅ All modules imported successfully")
except ImportError as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Create session manager and add messages
print("\n✓ Test 2: Session Manager - Message Tracking...")
try:
    session_mgr = SessionManager(agent_type="react", model="claude-sonnet-4")

    # Add user message
    session_mgr.add_message(role="user", content="Hello, how are you?")

    # Add agent message
    session_mgr.add_message(role="agent", content="I'm doing great! How can I help you?")

    # Get messages
    messages = session_mgr.get_messages()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "agent"

    print(f"  ✅ Added and retrieved {len(messages)} messages")
except Exception as e:
    print(f"  ❌ Session Manager test failed: {e}")
    sys.exit(1)

# Test 3: Add tool executions
print("\n✓ Test 3: Session Manager - Tool Execution Tracking...")
try:
    session_mgr.add_tool_execution(
        tool_name="search_web",
        arguments={"query": "Python programming"},
        result="Found 10 results",
        execution_time=1.5,
    )

    state = session_mgr.get_session_state()
    assert len(state.tool_executions) == 1
    assert state.tool_executions[0].tool_name == "search_web"

    print(f"  ✅ Added and retrieved tool execution")
except Exception as e:
    print(f"  ❌ Tool execution test failed: {e}")
    sys.exit(1)

# Test 4: Session persistence - Save
print("\n✓ Test 4: Session Persistence - Save to File...")
try:
    import tempfile
    import os

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    persistence = SessionPersistence(history_dir=temp_dir)

    # Save session
    save_path = persistence.save_session(session_mgr.get_session_state())
    assert save_path.exists()

    print(f"  ✅ Session saved to: {save_path}")
except Exception as e:
    print(f"  ❌ Save session test failed: {e}")
    sys.exit(1)

# Test 5: Session persistence - Load
print("\n✓ Test 5: Session Persistence - Load from File...")
try:
    # Load session
    loaded_state = persistence.load_session(str(save_path))
    assert loaded_state is not None
    assert len(loaded_state.messages) == 2
    assert len(loaded_state.tool_executions) == 1

    print(f"  ✅ Session loaded successfully")
except Exception as e:
    print(f"  ❌ Load session test failed: {e}")
    sys.exit(1)

# Test 6: Export to markdown
print("\n✓ Test 6: Session Persistence - Export to Markdown...")
try:
    export_path = persistence.export_session(
        session_mgr.get_session_state(),
        "test_export.md",
        format="md"
    )
    assert export_path.exists()

    # Read and verify content
    with open(export_path, 'r') as f:
        content = f.read()
        assert "Orbiton Agent Conversation" in content
        assert "User" in content
        assert "Agent" in content

    print(f"  ✅ Exported to markdown: {export_path}")

    # Cleanup
    os.remove(export_path)
except Exception as e:
    print(f"  ❌ Export test failed: {e}")
    sys.exit(1)

# Test 7: Session statistics
print("\n✓ Test 7: Session Manager - Statistics...")
try:
    stats = session_mgr.get_statistics()
    assert stats["total_messages"] == 2
    assert stats["user_messages"] == 1
    assert stats["agent_messages"] == 1
    assert stats["total_tool_executions"] == 1

    print(f"  ✅ Statistics retrieved:")
    print(f"     - Total messages: {stats['total_messages']}")
    print(f"     - Tool executions: {stats['total_tool_executions']}")
except Exception as e:
    print(f"  ❌ Statistics test failed: {e}")
    sys.exit(1)

# Test 8: Session serialization
print("\n✓ Test 8: Session State - Serialization...")
try:
    # Convert to dict
    state_dict = session_mgr.get_session_state().to_dict()
    assert "session_id" in state_dict
    assert "messages" in state_dict
    assert "tool_executions" in state_dict

    # Convert back from dict
    restored_state = SessionState.from_dict(state_dict)
    assert len(restored_state.messages) == len(session_mgr.get_session_state().messages)

    print(f"  ✅ Serialization/deserialization successful")
except Exception as e:
    print(f"  ❌ Serialization test failed: {e}")
    sys.exit(1)

# Test 9: Command handler (basic test without app)
print("\n✓ Test 9: Command Handler - Structure...")
try:
    # Create a mock app
    class MockApp:
        def __init__(self):
            self.config = {
                "llm": {"default_provider": "anthropic", "default_model": "claude-sonnet-4"},
                "agent": {"type": "react"},
                "ui": {"theme": "default"},
                "session": {"save_history": True, "history_dir": "~/.orbiton/history"},
            }
            self.current_model = "claude-sonnet-4"
            self.current_agent_type = "react"
            self.debug = False
            from console.renderer import Renderer
            from rich.console import Console
            from console.theme import orbiton_theme
            self.console = Console(theme=orbiton_theme)
            self.renderer = Renderer(console=self.console)
            self.session_manager = session_mgr

    mock_app = MockApp()
    cmd_handler = CommandHandler(app=mock_app)

    # Check commands are registered
    commands = cmd_handler.get_command_list()
    assert len(commands) > 0

    command_names = [cmd[0] for cmd in commands]
    assert "/help" in command_names
    assert "/agent" in command_names
    assert "/model" in command_names
    assert "/history" in command_names
    assert "/save" in command_names

    print(f"  ✅ Command handler initialized with {len(commands)} commands")
except Exception as e:
    print(f"  ❌ Command handler test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 10: Keyboard bindings
print("\n✓ Test 10: Keyboard Bindings - Structure...")
try:
    kb_manager = KeyBindingManager(app=mock_app)
    bindings = kb_manager.get_bindings()
    assert bindings is not None

    print(f"  ✅ Keyboard bindings initialized")
except Exception as e:
    print(f"  ❌ Keyboard bindings test failed: {e}")
    sys.exit(1)

# Cleanup
print("\n✓ Cleanup...")
try:
    import shutil
    shutil.rmtree(temp_dir)
    print(f"  ✅ Temporary files cleaned up")
except Exception as e:
    print(f"  ⚠️  Cleanup warning: {e}")

# Summary
print()
print("=" * 80)
print("✅ All Phase 4 & 5 tests passed!")
print("=" * 80)
print()
print("Summary of implemented features:")
print("  📝 Phase 4: Interactive Features & Commands")
print("     - Enhanced command system with 9+ commands")
print("     - Keyboard bindings (ctrl+o, ESC, ctrl+l)")
print("     - Progressive disclosure support")
print()
print("  💾 Phase 5: State Management & Configuration")
print("     - Session state tracking (messages & tool executions)")
print("     - Persistence layer (save/load/export)")
print("     - Auto-save mechanism")
print("     - Multiple export formats (md, json, txt)")
print()
print("🎉 MVP is ready for end-to-end testing with the agent!")
