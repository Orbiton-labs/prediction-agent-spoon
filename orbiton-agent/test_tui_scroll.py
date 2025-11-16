#!/usr/bin/env python3
"""Test TUI auto-scroll functionality."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_scroll():
    """Test that TUI scrolls to bottom when messages are added."""
    from console.tui import TUIApp
    import time

    def on_user_input(text: str):
        """Handle user input - add lots of messages to test scrolling."""
        if text.strip().lower() == 'test':
            # Add many messages to force scrolling
            for i in range(50):
                tui.add_agent_message(f"Message {i+1} - This is a test message to verify auto-scrolling works correctly.")
                if i % 10 == 0:
                    tui.add_tool_action("test_tool", {"iteration": i})
                    tui.add_tool_result(f"Result for iteration {i}")
        else:
            tui.add_agent_message(f"You said: {text}")

    print("=" * 60)
    print("TUI Auto-Scroll Test")
    print("=" * 60)
    print("\nCreating TUI with scroll fix...")

    tui = TUIApp(
        agent_name="Orbiton Agent (Scroll Test)",
        model="test-model",
        on_input=on_user_input,
    )

    # Add welcome messages
    tui.add_info_message("TUI Auto-Scroll Test")
    tui.add_info_message("Type 'test' and press Enter to add 50 messages.")
    tui.add_info_message("The view should automatically scroll to the bottom.")
    tui.add_info_message("")
    tui.add_success_message("✓ Scroll fix applied - using BufferControl with cursor positioning")
    tui.add_info_message("")

    print("✓ TUI created with scroll fix")
    print("\nLaunching TUI...")
    print("Type 'test' to add 50 messages and verify auto-scroll works.")
    print("Press Ctrl+C to exit.\n")

    try:
        tui.run()
    except KeyboardInterrupt:
        print("\nTest completed!")

if __name__ == '__main__':
    test_scroll()
