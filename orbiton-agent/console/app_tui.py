"""Main console application with full-screen TUI layout."""

import sys
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add parent to path for spoon_ai imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from console.tui import TUIApp
from console.commands import CommandHandler
from agents.factory import AgentFactory, AgentSession
from state.session import SessionManager
from state.persistence import SessionPersistence, AutoSaver
from spoon_ai.callbacks.base import BaseCallbackHandler
import os
from contextlib import contextmanager


@contextmanager
def suppress_subprocess_output(debug=False):
    """
    Context manager to suppress stdout/stderr from subprocesses.

    This helps prevent MCP tool debug messages from appearing in the UI.
    """
    if debug:
        # Don't suppress in debug mode
        yield
        return

    # Save original file descriptors
    original_stdout_fd = os.dup(1)
    original_stderr_fd = os.dup(2)

    try:
        # Redirect to devnull at the file descriptor level
        # This catches output from subprocesses too
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, 1)
        os.dup2(devnull_fd, 2)
        os.close(devnull_fd)

        yield

    finally:
        # Restore original file descriptors
        os.dup2(original_stdout_fd, 1)
        os.dup2(original_stderr_fd, 2)
        os.close(original_stdout_fd)
        os.close(original_stderr_fd)


class TUICallbackHandler(BaseCallbackHandler):
    """Callback handler that updates the TUI."""

    def __init__(self, tui: TUIApp):
        """
        Initialize TUI callback handler.

        Args:
            tui: TUI application instance
        """
        super().__init__()
        self.tui = tui
        self.show_thinking = True
        self._last_status = None  # Cache to avoid redundant updates

    def on_llm_start(self, **kwargs):
        """Called when LLM starts."""
        if self.show_thinking and self._last_status != "thinking":
            self._last_status = "thinking"
            self.tui.set_status("Thinking...", style="thinking")

    def on_llm_new_token(self, token: str, **kwargs):
        """Called when LLM generates a new token."""
        # No-op for performance - token streaming disabled
        pass

    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes."""
        self._last_status = None
        self.tui.clear_status()

    def on_llm_error(self, error: Exception, **kwargs):
        """Called when LLM encounters an error."""
        self._last_status = None
        self.tui.add_error_message(f"LLM Error: {str(error)}")
        self.tui.clear_status()

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when tool execution starts."""
        tool_name = serialized.get("name", "unknown_tool")

        # Parse arguments properly for better display
        try:
            import json
            if input_str.strip().startswith("{"):
                args = json.loads(input_str)
            else:
                # For simple string inputs
                args = {"query": input_str[:50] + "..." if len(input_str) > 50 else input_str}
        except:
            args = {"input": input_str[:50] + "..." if len(input_str) > 50 else input_str}

        self.tui.add_tool_action(tool_name, args)

        if self._last_status != f"tool_{tool_name}":
            self._last_status = f"tool_{tool_name}"
            self.tui.set_status(f"Executing {tool_name}...", style="status")

    def on_tool_end(self, output: str, **kwargs):
        """Called when tool execution ends."""
        self._last_status = None

        # Filter out MCP debug messages (lines starting with [GMCPT], [MCP], etc.)
        if output:
            lines = output.split('\n')
            filtered_lines = [
                line for line in lines
                if not (
                    line.strip().startswith('[GMCPT]') or
                    line.strip().startswith('[MCP]') or
                    line.strip().startswith('> [GMCPT]') or
                    'listening on stdio' in line or
                    'ctrl+l clear' in line or
                    'ctrl+c exit' in line
                )
            ]
            output = '\n'.join(filtered_lines).strip()

        # Truncate very long outputs for performance
        truncated_output = output[:500] if len(output) > 500 else output

        # Only add if there's actual content after filtering
        if truncated_output:
            self.tui.add_tool_result(truncated_output)

        self.tui.clear_status()

    def on_tool_error(self, error: Exception, **kwargs):
        """Called when tool execution errors."""
        self._last_status = None
        self.tui.add_error_message(f"Tool Error: {str(error)}")
        self.tui.clear_status()

    def on_agent_finish(self, finish, **kwargs):
        """Called when agent finishes."""
        # Extract final output
        if hasattr(finish, 'return_values'):
            output = finish.return_values.get('output', '')
            if output:
                self.tui.add_agent_message(output)
        elif hasattr(finish, 'output'):
            self.tui.add_agent_message(finish.output)

    def on_chain_error(self, error: Exception, **kwargs):
        """Called when chain errors."""
        self.tui.add_error_message(f"Chain Error: {str(error)}")

    def set_show_thinking(self, show: bool):
        """Enable or disable thinking display."""
        self.show_thinking = show


class ConsoleTUIApp:
    """Main console application with full-screen TUI."""

    def __init__(self, config: dict, debug: bool = False):
        """
        Initialize console TUI application.

        Args:
            config: Configuration dictionary
            debug: Debug mode flag
        """
        self.config = config
        self.debug = debug

        # Configure logging for debugging
        import logging
        import warnings

        if debug:
            # Enable detailed debug logging
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('logs/orbiton_debug.log'),
                    logging.StreamHandler()
                ]
            )

            # Enable spoon_ai debug logs
            logging.getLogger("spoon_ai").setLevel(logging.DEBUG)
            logging.getLogger("spoon_ai.llm").setLevel(logging.DEBUG)
            logging.getLogger("spoon_ai.llm.manager").setLevel(logging.DEBUG)
            logging.getLogger("spoon_ai.llm.providers").setLevel(logging.DEBUG)

            # Enable OpenAI SDK debug logging
            logging.getLogger("openai").setLevel(logging.DEBUG)
            logging.getLogger("httpx").setLevel(logging.DEBUG)

            # Enable agent debug logging
            logging.getLogger("agents.factory").setLevel(logging.DEBUG)

            print(f"[DEBUG] Logging enabled - logs will be written to logs/orbiton_debug.log")

        else:
            # Suppress spoon_ai logs
            logging.getLogger("spoon_ai").setLevel(logging.WARNING)
            logging.getLogger("spoon_ai.llm").setLevel(logging.WARNING)
            logging.getLogger("spoon_ai.llm.manager").setLevel(logging.WARNING)
            logging.getLogger("spoon_ai.llm.providers").setLevel(logging.WARNING)

            # Suppress deprecation warnings
            warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Get config values
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

        # Create TUI
        self.tui = TUIApp(
            agent_name="Orbiton Agent",
            model=self.current_model,
            on_input=self._handle_user_input,
        )

        # Initialize callback handler
        self.callback_handler = TUICallbackHandler(tui=self.tui)
        self.callback_handler.set_show_thinking(
            config.get("ui", {}).get("show_thinking", True)
        )

        # Initialize agent
        try:
            # Add debug flag to config for AgentSession logging
            agent_config = {**config, "debug": debug}

            # Suppress stdout/stderr during agent initialization to hide MCP tool init messages
            # Only do this in non-debug mode
            if not debug:
                import sys
                import os
                # Save original stdout/stderr
                original_stdout = sys.stdout
                original_stderr = sys.stderr
                # Redirect to devnull
                devnull = open(os.devnull, 'w')
                sys.stdout = devnull
                sys.stderr = devnull

            try:
                # Create agent with callback handler to show tool usage in TUI
                agent = AgentFactory.create_agent(
                    agent_type=self.current_agent_type,
                    config=agent_config,
                    callback_handler=self.callback_handler,
                )
                self.agent_session = AgentSession(agent=agent, config=agent_config)
            finally:
                # Restore stdout/stderr
                if not debug:
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    devnull.close()
        except Exception as e:
            if debug:
                raise
            # If agent creation fails, set to None and show error
            self.agent_session = None
            self._agent_init_error = str(e)

        # Command handler (Phase 4) - Must be after agent_session is initialized
        self._setup_command_wrapper()

        # Override help command for TUI-specific display
        self._setup_tui_commands()

        # Show welcome message
        self._show_welcome()

    def _setup_command_wrapper(self):
        """Set up command handler with TUI-specific wrapper."""
        # Create a wrapper class that makes TUI compatible with CommandHandler
        class TUIWrapper:
            def __init__(self, tui_app):
                self.tui = tui_app.tui
                self.config = tui_app.config
                self.debug = tui_app.debug
                self.current_model = tui_app.current_model
                self.current_agent_type = tui_app.current_agent_type
                self.agent_session = tui_app.agent_session
                self.session_manager = tui_app.session_manager

                # Create a minimal renderer wrapper
                class TUIRenderer:
                    def __init__(self, tui):
                        self.tui = tui
                        # Create a mock console for Rich operations
                        self.console = self._create_mock_console()

                    def _create_mock_console(self):
                        """Create a mock console that routes to TUI messages."""
                        import re

                        # Compile ANSI regex once for performance
                        ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')

                        class MockConsole:
                            def __init__(self, tui):
                                self.tui = tui
                                self._ansi_pattern = ansi_pattern

                            def print(self, *args, **kwargs):
                                """Convert print to TUI message (simplified for performance)."""
                                # Fast path: simple string conversion without Rich overhead
                                text_parts = []
                                for arg in args:
                                    arg_str = str(arg)
                                    # Remove ANSI codes if present
                                    if '\x1b[' in arg_str:
                                        arg_str = self._ansi_pattern.sub('', arg_str)
                                    text_parts.append(arg_str)

                                message = " ".join(text_parts)
                                if message.strip():
                                    self.tui.add_info_message(message)

                        return MockConsole(self.tui)

                    def render_info(self, msg):
                        self.tui.add_info_message(msg)

                    def render_success(self, msg):
                        self.tui.add_success_message(msg)

                    def render_warning(self, msg):
                        self.tui.add_warning_message(msg)

                    def render_error(self, msg, title="Error"):
                        self.tui.add_error_message(f"{title}: {msg}")

                    def clear_screen(self):
                        self.tui.clear_history()

                    def render_header(self, agent_name, model, cwd):
                        # TUI header is static
                        pass

                self.renderer = TUIRenderer(self.tui)
                # Set console to the mock console from renderer
                self.console = self.renderer.console

            def shutdown(self):
                self.tui.running = False

        self._wrapper = TUIWrapper(self)
        self.command_handler = CommandHandler(app=self._wrapper)

    def _setup_tui_commands(self):
        """Override specific commands for TUI-friendly display."""
        # Override the help command with TUI-specific version
        def tui_help_command(args):
            """Show help information in TUI format."""
            self.tui.add_info_message("")
            self.tui.add_info_message("=" * 70)
            self.tui.add_info_message("ORBITON AGENT - AVAILABLE COMMANDS")
            self.tui.add_info_message("=" * 70)
            self.tui.add_info_message("")

            # Core Commands
            self.tui.add_info_message("CORE COMMANDS:")
            self.tui.add_info_message("  /help, /h              - Show this help message")
            self.tui.add_info_message("  /clear, /cls           - Clear the screen")
            self.tui.add_info_message("  /exit, /quit, /q       - Exit the application")
            self.tui.add_info_message("")

            # Configuration
            self.tui.add_info_message("CONFIGURATION:")
            self.tui.add_info_message("  /config                - Show current configuration")
            self.tui.add_info_message("  /config get <key>      - Get configuration value")
            self.tui.add_info_message("  /config set <key> <val> - Set configuration value")
            self.tui.add_info_message("")

            # Agent Management
            self.tui.add_info_message("AGENT MANAGEMENT:")
            self.tui.add_info_message("  /agent                 - Show current agent")
            self.tui.add_info_message("  /agent list            - List available agents")
            self.tui.add_info_message("  /agent <type>          - Switch agent (react/mcp)")
            self.tui.add_info_message("")

            # Model Management
            self.tui.add_info_message("MODEL MANAGEMENT:")
            self.tui.add_info_message("  /model                 - Show current model")
            self.tui.add_info_message("  /model list            - List available models")
            self.tui.add_info_message("  /model <name>          - Switch to model")
            self.tui.add_info_message("")

            # Session Management
            self.tui.add_info_message("SESSION MANAGEMENT:")
            self.tui.add_info_message("  /history               - Show all conversation history")
            self.tui.add_info_message("  /history <N>           - Show last N messages")
            self.tui.add_info_message("  /save                  - Save to default file")
            self.tui.add_info_message("  /save <file>           - Save to specific file (.md/.json/.txt)")
            self.tui.add_info_message("")

            # Keyboard Shortcuts
            self.tui.add_info_message("KEYBOARD SHORTCUTS:")
            self.tui.add_info_message("  ESC                    - Interrupt ongoing task")
            self.tui.add_info_message("  Ctrl+L                 - Clear screen")
            self.tui.add_info_message("  Ctrl+C                 - Exit application")
            self.tui.add_info_message("")

            # Examples
            self.tui.add_info_message("EXAMPLES:")
            self.tui.add_info_message("  /agent list            - See available agents")
            self.tui.add_info_message("  /model gpt-4           - Switch to GPT-4")
            self.tui.add_info_message("  /history 5             - Show last 5 messages")
            self.tui.add_info_message("  /save my_chat.md       - Save conversation")
            self.tui.add_info_message("  /config get llm.model  - Check current model")
            self.tui.add_info_message("")
            self.tui.add_info_message("=" * 70)
            self.tui.add_info_message("")

        # Register the TUI help command
        self.command_handler.commands["/help"] = (
            tui_help_command,
            "Show help information",
            ["/h"]
        )
        self.command_handler.commands["/h"] = (
            tui_help_command,
            "Show help information",
            []
        )

    def _show_welcome(self):
        """Show welcome message."""
        if self.agent_session:
            agent_type = self.agent_session.get_agent_type()
            self.tui.add_success_message(f"Agent ready: {agent_type}")
        else:
            self.tui.add_error_message("Agent failed to initialize")

        self.tui.add_info_message("")
        self.tui.add_info_message("Welcome to Orbiton - Your Prediction Market Research Partner")
        self.tui.add_info_message("")
        self.tui.add_info_message("I'm a worldly-wise AI specializing in prediction markets.")
        self.tui.add_info_message("Type your question and press Enter to start.")
        self.tui.add_info_message("")
        self.tui.add_info_message("Commands: /help, /clear, /config, /exit")
        self.tui.add_info_message("")

    def _handle_user_input(self, text: str):
        """
        Handle user input (called from TUI).

        Args:
            text: User input text
        """
        # Check if it's a command
        if text.startswith("/"):
            # Use the CommandHandler from Phase 4
            self.command_handler.execute(text)
            return

        # Track user message in session (Phase 5)
        self.session_manager.add_message(role="user", content=text)

        # Process with agent
        self._process_message(text)

    # Old command methods removed - now using CommandHandler from Phase 4

    def _process_message(self, message: str):
        """
        Process user message with agent.

        Args:
            message: User message
        """
        # Check if agent is initialized
        if not self.agent_session:
            self.tui.add_error_message(
                f"Agent failed to initialize: {getattr(self, '_agent_init_error', 'Unknown error')}"
            )
            self.tui.add_info_message("Please check your configuration and API keys.")
            return

        try:
            # Execute with agent
            # Note: This is a synchronous call, which will block the UI
            # In a production app, we'd want to run this in a background thread
            # and update the UI asynchronously

            self.tui.set_status("Processing...", style="status")

            # Execute agent with callbacks enabled
            # The callbacks will show tool usage and responses
            response = self.agent_session.execute(message)

            # Track agent response in session (Phase 5)
            if response and isinstance(response, str):
                self.session_manager.add_message(role="agent", content=response)
                self.tui.add_agent_message(response)

            self.tui.clear_status()

        except KeyboardInterrupt:
            self.tui.add_warning_message("Interrupted by user")
            self.tui.clear_status()
            self.agent_session.interrupt()

        except Exception as e:
            self.tui.add_error_message(f"Execution Error: {str(e)}")
            self.tui.clear_status()
            if self.debug:
                raise

    def run(self):
        """Run the TUI application."""
        try:
            # Start auto-save if enabled (Phase 5)
            if self.config.get("session", {}).get("save_history", True):
                self.auto_saver.start()

            self.tui.run()
        except KeyboardInterrupt:
            pass
        finally:
            # Stop auto-saver and save final state (Phase 5)
            self.auto_saver.stop()
            self.tui.add_info_message("Goodbye! 👋")

    async def run_async(self):
        """Run the TUI application asynchronously."""
        try:
            # Start auto-save if enabled (Phase 5)
            if self.config.get("session", {}).get("save_history", True):
                self.auto_saver.start()

            await self.tui.run_async()
        except KeyboardInterrupt:
            pass
        finally:
            # Stop auto-saver and save final state (Phase 5)
            self.auto_saver.stop()
            self.tui.add_info_message("Goodbye! 👋")


def main():
    """Main entry point."""
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

    app = ConsoleTUIApp(config=config, debug=True)
    app.run()


if __name__ == "__main__":
    main()
