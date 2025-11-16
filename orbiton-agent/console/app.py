"""Main console application for Orbiton Agent."""

import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.live import Live
from rich.panel import Panel

# Add parent to path for spoon_ai imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from console.renderer import Renderer, SectionManager
from console.input_handler import InputHandler
from console.theme import orbiton_theme, SPINNER_THINKING
from console.commands import CommandHandler
from console.keybindings import KeyBindingManager
from agents.factory import AgentFactory, AgentSession
from agents.console_callback import ConsoleCallbackHandler
from state.session import SessionManager
from state.persistence import SessionPersistence, AutoSaver


class ConsoleApp:
    """Main console application for Orbiton Agent."""

    def __init__(self, config: dict, debug: bool = False):
        """
        Initialize console application.

        Args:
            config: Configuration dictionary
            debug: Debug mode flag
        """
        self.config = config
        self.debug = debug

        # Configure logging for spoon_ai (suppress if not debug)
        if not debug:
            import logging
            import warnings

            # Suppress spoon_ai logs
            logging.getLogger("spoon_ai").setLevel(logging.WARNING)
            logging.getLogger("spoon_ai.llm").setLevel(logging.WARNING)
            logging.getLogger("spoon_ai.llm.manager").setLevel(logging.WARNING)
            logging.getLogger("spoon_ai.llm.providers").setLevel(logging.WARNING)

            # Suppress deprecation warnings
            warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Initialize Rich console
        self.console = Console(theme=orbiton_theme)

        # Initialize components
        self.renderer = Renderer(console=self.console)
        self.input_handler = InputHandler(console=self.console)
        self.section_manager = SectionManager()

        # State
        self.running = False
        self.current_model = config.get("llm", {}).get("default_model", "unknown")
        self.current_agent_type = config.get("agent", {}).get("type", "react")

        # Session management (Phase 5)
        self.session_manager = SessionManager(
            agent_type=self.current_agent_type,
            model=self.current_model,
        )

        # Persistence (Phase 5)
        history_dir = config.get("session", {}).get("history_dir", "~/.orbiton/history")
        self.persistence = SessionPersistence(history_dir=history_dir)

        # Auto-save (Phase 5)
        auto_save_interval = config.get("session", {}).get("auto_save_interval", 60)
        self.auto_saver = AutoSaver(
            session_manager=self.session_manager,
            persistence=self.persistence,
            interval=auto_save_interval,
        )

        # Command handler (Phase 4)
        self.command_handler = CommandHandler(app=self)

        # Keyboard bindings (Phase 4)
        self.key_binding_manager = KeyBindingManager(app=self)

        # Initialize agent (Phase 3)
        self.callback_handler = ConsoleCallbackHandler(renderer=self.renderer)
        self.callback_handler.set_show_thinking(config.get("ui", {}).get("show_thinking", True))

        try:
            agent = AgentFactory.create_agent(
                agent_type=self.current_agent_type,
                config=config,
                callback_handler=self.callback_handler,
            )
            self.agent_session = AgentSession(agent=agent, config=config)
        except Exception as e:
            if debug:
                raise
            # If agent creation fails, set to None and show warning later
            self.agent_session = None
            self._agent_init_error = str(e)

    def run(self):
        """Main application loop."""
        self.running = True

        try:
            # Start auto-save if enabled
            if self.config.get("session", {}).get("save_history", True):
                self.auto_saver.start()

            # Display header
            self.renderer.render_header(
                agent_name="Orbiton Agent",
                model=self.current_model,
                cwd=Path.cwd(),
            )

            # Display welcome message
            self._display_welcome()

            # Main loop
            while self.running:
                # Get user input
                user_input = self.input_handler.get_input()

                # Handle None (Ctrl+C or EOF)
                if user_input is None:
                    self.shutdown()
                    break

                # Skip empty input
                if not user_input.strip():
                    continue

                # Check if it's a command
                if user_input.startswith("/"):
                    self.command_handler.execute(user_input)
                    continue

                # Track user message in session (Phase 5)
                self.session_manager.add_message(role="user", content=user_input)

                # Add user message to conversation history (above the input box)
                self.renderer.render_user_message(user_input)

                # Process with agent
                self._process_message(user_input)

        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            self.renderer.render_error(str(e), title="Application Error")
            if self.debug:
                raise
        finally:
            # Stop auto-saver
            self.auto_saver.stop()

    def _display_welcome(self):
        """Display welcome message and help."""
        # Check if agent initialized successfully
        agent_status = ""
        if self.agent_session:
            agent_type = self.agent_session.get_agent_type()
            agent_status = f"[green]✓[/] Agent ready: [cyan]{agent_type}[/]"
        else:
            agent_status = f"[red]✗[/] Agent failed to initialize"

        welcome_text = f"""
Welcome to [bold cyan]Orbiton[/] - Your Prediction Market Research Partner

{agent_status}

I'm a worldly-wise AI specializing in prediction markets. I cut through the noise
to deliver insights that matter - no fluff, just facts. Let's dive in.

[bold]Quick Start:[/]
  • Type your question and press Enter
  • Use [cyan]/help[/] for commands
  • Press [cyan]ctrl+o[/] to expand/collapse details (coming in Phase 4)
  • Press [cyan]ESC[/] to interrupt, [cyan]ctrl+c[/] to exit

[bold]What I Can Research:[/]
  • Token price trends and market movements
  • Liquidity pool analysis (Uniswap and beyond)
  • Wallet behavior and holder distribution
  • Trading patterns and market sentiment
        """.strip()

        panel = Panel(
            welcome_text,
            title="✨ Welcome",
            title_align="left",
            border_style="info",
            padding=(1, 2),
        )
        self.console.print(panel)
        self.console.print()


    def _process_message(self, message: str):
        """
        Process user message with agent.

        Args:
            message: User message
        """
        # Check if agent is initialized
        if not self.agent_session:
            self.renderer.render_error(
                f"Agent failed to initialize: {getattr(self, '_agent_init_error', 'Unknown error')}\n\n"
                "Please check your configuration and API keys.",
                title="Agent Error"
            )
            return

        try:
            self.console.print()  # Spacing

            # Execute with agent
            response = self.agent_session.execute(message)

            # Track agent response in session (Phase 5)
            if response and isinstance(response, str):
                self.session_manager.add_message(role="agent", content=response)

                # Only display if not already shown via callbacks
                if not hasattr(self.callback_handler, '_response_shown'):
                    self.renderer.render_agent_message(
                        response,
                        timestamp=datetime.now() if self.config.get("ui", {}).get("show_timestamps") else None
                    )

        except KeyboardInterrupt:
            self.renderer.render_warning("Interrupted by user")
            self.agent_session.interrupt()

        except Exception as e:
            self.renderer.render_error(str(e), title="Execution Error")
            if self.debug:
                raise

    def shutdown(self):
        """Shutdown the application."""
        self.running = False
        self.console.print()
        self.console.print("[bold cyan]Goodbye! 👋[/]")
        self.console.print()


def main():
    """Main entry point (for testing)."""
    # Simple test configuration
    config = {
        "llm": {
            "default_provider": "anthropic",
            "default_model": "claude-sonnet-4",
            "temperature": 0.7,
            "max_tokens": 4096,
        },
        "agent": {
            "type": "react",
            "memory_enabled": True,
            "max_iterations": 10,
        },
        "ui": {
            "theme": "default",
            "show_thinking": True,
            "show_timestamps": False,
        },
        "session": {
            "save_history": True,
            "history_dir": "~/.orbiton/history",
        },
    }

    app = ConsoleApp(config=config, debug=True)
    app.run()


if __name__ == "__main__":
    main()
