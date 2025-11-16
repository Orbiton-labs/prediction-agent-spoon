"""Simple demo of the TUI layout (no agent required)."""

import sys
import time
import random
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from console.tui import TUIApp


def simulate_agent_response(tui: TUIApp, user_input: str):
    """
    Simulate an agent processing a message.

    Args:
        tui: TUI application instance
        user_input: User's input text
    """
    # Simulate thinking
    tui.set_status("Thinking...", style="thinking")
    time.sleep(0.5)

    # Simulate agent response
    responses = [
        f"I understand you're asking about: '{user_input}'",
        "Let me search for that information...",
        "Here's what I found based on current market data:",
        "The prediction markets suggest interesting trends in this area.",
    ]

    response = random.choice(responses)
    tui.add_agent_message(response)
    tui.clear_status()

    # Simulate tool usage (sometimes)
    if random.random() > 0.5:
        tui.set_status("Searching web...", style="status")
        time.sleep(0.3)

        tui.add_tool_action(
            "search_web",
            {"query": user_input[:30], "max_results": 10}
        )

        time.sleep(0.5)

        tui.add_tool_result(
            "Found 10 results:\n"
            "1. Prediction Market Analysis - 2024\n"
            "2. Token Price Trends\n"
            "3. Market Sentiment Overview\n"
            "...(7 more results)"
        )

        tui.clear_status()

    # Simulate thinking summary
    tui.add_thinking(
        "Analyzing market data and trends...",
        duration=1.2
    )

    # Final response
    final_responses = [
        "Based on the available data, here are the key insights...",
        "The market indicators suggest a positive trend.",
        "This is an interesting question that requires deeper analysis.",
        "Let me know if you need more specific information!",
    ]

    tui.add_agent_message(random.choice(final_responses))


def main():
    """Run the TUI demo."""

    def on_user_input(text: str):
        """Handle user input."""
        # Simulate agent processing
        simulate_agent_response(tui, text)

    # Create TUI
    tui = TUIApp(
        agent_name="Orbiton Agent (Demo)",
        model="claude-sonnet-4",
        on_input=on_user_input,
    )

    # Add welcome messages
    tui.add_success_message("Demo mode active - simulated responses")
    tui.add_info_message("")
    tui.add_info_message("Welcome to Orbiton TUI Demo!")
    tui.add_info_message("")
    tui.add_info_message("This is a demonstration of the full-screen TUI layout.")
    tui.add_info_message("Try typing a message and pressing Enter.")
    tui.add_info_message("")
    tui.add_info_message("Features:")
    tui.add_info_message("  • Scrollable history pane (top)")
    tui.add_info_message("  • Fixed input bar (bottom)")
    tui.add_info_message("  • Keyboard shortcuts (see bottom bar)")
    tui.add_info_message("")
    tui.add_info_message("Try these commands:")
    tui.add_info_message("  • Type any message to see simulated response")
    tui.add_info_message("  • Press ctrl+l to clear history")
    tui.add_info_message("  • Press ctrl+c to exit")
    tui.add_info_message("")

    # Add some example conversation
    tui.add_user_message("What is the current state of prediction markets?")
    tui.add_agent_message(
        "Prediction markets are seeing increased adoption in 2024. "
        "Key platforms like Polymarket and Augur are showing strong growth."
    )
    tui.add_tool_action("fetch_market_data", {"market": "polymarket", "timeframe": "30d"})
    tui.add_tool_result("Total volume: $1.2B | Active markets: 450 | Users: 125K")
    tui.add_thinking("Analyzing market trends and user behavior...", duration=0.8)
    tui.add_agent_message(
        "The data shows strong growth trends. Would you like me to dive deeper into "
        "any specific aspect?"
    )
    tui.add_info_message("")
    tui.add_info_message("↑ Example conversation above ↑")
    tui.add_info_message("Now try typing your own message below!")
    tui.add_info_message("")

    # Run the TUI
    tui.run()


if __name__ == "__main__":
    main()
