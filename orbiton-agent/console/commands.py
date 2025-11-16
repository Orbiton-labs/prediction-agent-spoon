"""Command handlers and routing for Orbiton Agent console."""

from typing import Callable, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from rich.panel import Panel
from rich.table import Table


class CommandHandler:
    """Handler for console commands."""

    def __init__(self, app):
        """
        Initialize command handler.

        Args:
            app: ConsoleApp instance
        """
        self.app = app
        self.commands: Dict[str, Tuple[Callable, str, List[str]]] = {}
        self._register_commands()

    def _register_commands(self):
        """Register all available commands."""
        # Core commands
        self.register_command("/help", self._cmd_help, "Show help information", ["/h"])
        self.register_command("/clear", self._cmd_clear, "Clear the screen", ["/cls"])
        self.register_command("/exit", self._cmd_exit, "Exit the application", ["/quit", "/q"])
        self.register_command("/config", self._cmd_config, "Manage configuration")

        # Agent commands
        self.register_command("/agent", self._cmd_agent, "Manage agent settings")
        self.register_command("/model", self._cmd_model, "Manage model settings")

        # Session commands
        self.register_command("/history", self._cmd_history, "Show conversation history")
        self.register_command("/save", self._cmd_save, "Save conversation to file")

        # Development
        self.register_command("/test", self._cmd_test, "Test UI components (development)")

    def register_command(
        self,
        name: str,
        handler: Callable,
        description: str,
        aliases: Optional[List[str]] = None,
    ):
        """
        Register a command.

        Args:
            name: Command name (e.g., "/help")
            handler: Command handler function
            description: Command description
            aliases: List of command aliases
        """
        self.commands[name] = (handler, description, aliases or [])
        # Register aliases
        for alias in (aliases or []):
            self.commands[alias] = (handler, description, [])

    def execute(self, command_string: str) -> bool:
        """
        Execute a command.

        Args:
            command_string: Full command string (e.g., "/help")

        Returns:
            True if command was executed, False if unknown
        """
        cmd_parts = command_string.strip().split()
        cmd_name = cmd_parts[0].lower()
        cmd_args = cmd_parts[1:] if len(cmd_parts) > 1 else []

        if cmd_name in self.commands:
            handler, _, _ = self.commands[cmd_name]
            try:
                handler(cmd_args)
                return True
            except Exception as e:
                self.app.renderer.render_error(
                    f"Error executing command: {str(e)}", title="Command Error"
                )
                if self.app.debug:
                    raise
                return True
        else:
            self.app.renderer.render_warning(f"Unknown command: {cmd_name}")
            self.app.renderer.render_info("Type [cyan]/help[/] for available commands")
            return False

    def get_command_list(self) -> List[Tuple[str, str, List[str]]]:
        """
        Get list of all commands.

        Returns:
            List of (name, description, aliases) tuples
        """
        seen = set()
        commands = []
        for name, (_, description, aliases) in self.commands.items():
            if name not in seen:
                seen.add(name)
                seen.update(aliases)
                commands.append((name, description, aliases))
        return sorted(commands, key=lambda x: x[0])

    # Command implementations

    def _cmd_help(self, args: List[str]):
        """Show help information."""
        help_text = """
[bold]Available Commands:[/]

  [cyan]/help[/], [cyan]/h[/]              Show this help message
  [cyan]/clear[/], [cyan]/cls[/]           Clear the screen
  [cyan]/config[/]                         Show or manage configuration
  [cyan]/agent[/]                          Manage agent settings
  [cyan]/model[/]                          Manage model settings
  [cyan]/history[/]                        Show conversation history
  [cyan]/save[/] [file]                    Save conversation to file
  [cyan]/exit[/], [cyan]/quit[/], [cyan]/q[/]      Exit the application
  [cyan]/test[/]                           Test UI components (development)

[bold]Keyboard Shortcuts:[/]

  [cyan]ctrl+o[/]                 Expand/collapse detailed output (Phase 4)
  [cyan]ESC[/]                    Interrupt ongoing task
  [cyan]ctrl+c[/]                 Exit application
  [cyan]ctrl+l[/]                 Clear screen

[bold]Command Details:[/]

  [cyan]/config[/]                 Show current configuration
  [cyan]/config get <key>[/]       Get configuration value
  [cyan]/config set <key> <val>[/] Set configuration value

  [cyan]/agent[/]                  Show current agent
  [cyan]/agent list[/]             List available agents
  [cyan]/agent <type>[/]           Switch to agent type (react/mcp)

  [cyan]/model[/]                  Show current model
  [cyan]/model list[/]             List available models
  [cyan]/model <name>[/]           Switch to model

  [cyan]/history[/]                Show all conversation messages
  [cyan]/history <N>[/]            Show last N messages

  [cyan]/save[/]                   Save to default file
  [cyan]/save <file>[/]            Save to specific file

For more information, visit: https://github.com/XSpoonAi/prediction-agent-spoon
        """.strip()

        panel = Panel(
            help_text,
            title="📚 Help",
            title_align="left",
            border_style="info",
            padding=(1, 2),
        )
        self.app.console.print(panel)
        self.app.console.print()

    def _cmd_clear(self, args: List[str]):
        """Clear screen and re-render header."""
        self.app.renderer.clear_screen()
        self.app.renderer.render_header(
            agent_name="Orbiton Agent",
            model=self.app.current_model,
            cwd=Path.cwd(),
        )
        self.app.renderer.render_success("Screen cleared")

    def _cmd_exit(self, args: List[str]):
        """Exit the application."""
        # Auto-save if session manager exists
        if hasattr(self.app, 'session_manager') and self.app.session_manager:
            try:
                from state.persistence import SessionPersistence
                persistence = SessionPersistence()
                session_state = self.app.session_manager.get_session_state()
                persistence.auto_save(session_state)
                self.app.renderer.render_info("Session saved")
            except Exception as e:
                if self.app.debug:
                    self.app.renderer.render_warning(f"Failed to save session: {e}")

        self.app.shutdown()

    def _cmd_config(self, args: List[str]):
        """Manage configuration."""
        if not args:
            # Show current configuration
            self._show_config()
        elif args[0] == "get" and len(args) > 1:
            # Get specific config value
            key = args[1]
            value = self._get_config_value(key)
            if value is not None:
                self.app.renderer.render_info(f"[cyan]{key}[/] = {value}")
            else:
                self.app.renderer.render_warning(f"Configuration key not found: {key}")
        elif args[0] == "set" and len(args) > 2:
            # Set specific config value
            key = args[1]
            value = " ".join(args[2:])
            self._set_config_value(key, value)
        else:
            self.app.renderer.render_warning("Usage: /config [get|set] [key] [value]")

    def _show_config(self):
        """Show current configuration."""
        config_text = f"""
[bold]Current Configuration:[/]

[bold cyan]LLM:[/]
  • Provider: {self.app.config.get('llm', {}).get('default_provider', 'N/A')}
  • Model: {self.app.config.get('llm', {}).get('default_model', 'N/A')}
  • Temperature: {self.app.config.get('llm', {}).get('temperature', 'N/A')}
  • Max Tokens: {self.app.config.get('llm', {}).get('max_tokens', 'N/A')}

[bold cyan]Agent:[/]
  • Type: {self.app.config.get('agent', {}).get('type', 'N/A')}
  • Memory: {self.app.config.get('agent', {}).get('memory_enabled', 'N/A')}
  • Max Iterations: {self.app.config.get('agent', {}).get('max_iterations', 'N/A')}

[bold cyan]UI:[/]
  • Theme: {self.app.config.get('ui', {}).get('theme', 'N/A')}
  • Show Thinking: {self.app.config.get('ui', {}).get('show_thinking', 'N/A')}
  • Syntax Highlighting: {self.app.config.get('ui', {}).get('syntax_highlighting', 'N/A')}

[bold cyan]Session:[/]
  • Save History: {self.app.config.get('session', {}).get('save_history', 'N/A')}
  • History Dir: {self.app.config.get('session', {}).get('history_dir', 'N/A')}
        """.strip()

        panel = Panel(
            config_text,
            title="⚙️ Configuration",
            title_align="left",
            border_style="info",
            padding=(1, 2),
        )
        self.app.console.print(panel)
        self.app.console.print()

    def _get_config_value(self, key_path: str):
        """Get configuration value using dot notation."""
        parts = key_path.split(".")
        value = self.app.config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value

    def _set_config_value(self, key_path: str, value: str):
        """Set configuration value using dot notation."""
        # Try to parse value
        parsed_value = value
        if value.lower() == "true":
            parsed_value = True
        elif value.lower() == "false":
            parsed_value = False
        elif value.isdigit():
            parsed_value = int(value)
        else:
            try:
                parsed_value = float(value)
            except ValueError:
                pass  # Keep as string

        # Update config
        parts = key_path.split(".")
        config = self.app.config
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        config[parts[-1]] = parsed_value

        self.app.renderer.render_success(f"Set [cyan]{key_path}[/] = {parsed_value}")

    def _cmd_agent(self, args: List[str]):
        """Manage agent settings."""
        if not args or args[0] == "current":
            # Show current agent
            agent_type = self.app.agent_session.get_agent_type() if self.app.agent_session else "N/A"
            self.app.renderer.render_info(f"Current agent: [cyan]{agent_type}[/]")
        elif args[0] == "list":
            # List available agents
            agents = ["react", "mcp"]
            table = Table(title="Available Agents", show_header=True)
            table.add_column("Type", style="cyan")
            table.add_column("Description")
            table.add_row("react", "ReAct agent with reasoning and action")
            table.add_row("mcp", "ReAct agent with MCP server support")
            self.app.console.print(table)
            self.app.console.print()
        else:
            # Switch agent
            agent_type = args[0]
            if agent_type not in ["react", "mcp"]:
                self.app.renderer.render_warning(f"Unknown agent type: {agent_type}")
                self.app.renderer.render_info("Available: react, mcp")
                return

            # Update config and recreate agent
            self.app.config["agent"]["type"] = agent_type
            self.app.current_agent_type = agent_type

            try:
                from agents.factory import AgentFactory, AgentSession

                agent = AgentFactory.create_agent(
                    agent_type=agent_type,
                    config=self.app.config,
                    callback_handler=self.app.callback_handler,
                )
                self.app.agent_session = AgentSession(agent=agent, config=self.app.config)
                self.app.renderer.render_success(f"Switched to agent: [cyan]{agent_type}[/]")
            except Exception as e:
                self.app.renderer.render_error(f"Failed to switch agent: {e}", title="Agent Error")

    def _cmd_model(self, args: List[str]):
        """Manage model settings."""
        if not args or args[0] == "current":
            # Show current model
            self.app.renderer.render_info(f"Current model: [cyan]{self.app.current_model}[/]")
        elif args[0] == "list":
            # List available models
            table = Table(title="Available Models", show_header=True)
            table.add_column("Model", style="cyan")
            table.add_column("Provider")
            table.add_row("claude-sonnet-4", "Anthropic")
            table.add_row("claude-3-5-sonnet-20241022", "Anthropic")
            table.add_row("gpt-4", "OpenAI")
            table.add_row("gpt-4-turbo", "OpenAI")
            table.add_row("gemini-pro", "Google")
            self.app.console.print(table)
            self.app.console.print()
        else:
            # Switch model
            model = args[0]
            self.app.config["llm"]["default_model"] = model
            self.app.current_model = model

            # Recreate agent with new model
            try:
                from agents.factory import AgentFactory, AgentSession

                agent = AgentFactory.create_agent(
                    agent_type=self.app.current_agent_type,
                    config=self.app.config,
                    callback_handler=self.app.callback_handler,
                )
                self.app.agent_session = AgentSession(agent=agent, config=self.app.config)
                self.app.renderer.render_success(f"Switched to model: [cyan]{model}[/]")
            except Exception as e:
                self.app.renderer.render_error(f"Failed to switch model: {e}", title="Model Error")

    def _cmd_history(self, args: List[str]):
        """Show conversation history."""
        if not hasattr(self.app, 'session_manager') or not self.app.session_manager:
            self.app.renderer.render_warning("Session manager not initialized")
            return

        # Get number of messages to show
        limit = None
        if args and args[0].isdigit():
            limit = int(args[0])

        messages = self.app.session_manager.get_messages(limit=limit)

        if not messages:
            self.app.renderer.render_info("No conversation history")
            return

        # Display messages
        table = Table(title=f"Conversation History ({len(messages)} messages)", show_header=True)
        table.add_column("Time", style="dim")
        table.add_column("Role", style="cyan")
        table.add_column("Content")

        for msg in messages:
            timestamp = msg.timestamp.strftime("%H:%M:%S") if hasattr(msg, 'timestamp') else ""
            role = msg.role if hasattr(msg, 'role') else "unknown"
            content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
            table.add_row(timestamp, role, content)

        self.app.console.print(table)
        self.app.console.print()

    def _cmd_save(self, args: List[str]):
        """Save conversation to file."""
        if not hasattr(self.app, 'session_manager') or not self.app.session_manager:
            self.app.renderer.render_warning("Session manager not initialized")
            return

        # Get filename
        if args:
            filename = " ".join(args)
        else:
            # Default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.md"

        # Ensure .md extension
        if not filename.endswith(('.md', '.json', '.txt')):
            filename += '.md'

        try:
            from state.persistence import SessionPersistence
            persistence = SessionPersistence()
            session_state = self.app.session_manager.get_session_state()

            # Determine format from extension
            if filename.endswith('.json'):
                format_type = 'json'
            elif filename.endswith('.txt'):
                format_type = 'txt'
            else:
                format_type = 'md'

            # Export and save
            output_path = persistence.export_session(session_state, filename, format=format_type)
            self.app.renderer.render_success(f"Conversation saved to: [cyan]{output_path}[/]")

        except Exception as e:
            self.app.renderer.render_error(f"Failed to save conversation: {e}", title="Save Error")
            if self.app.debug:
                raise

    def _cmd_test(self, args: List[str]):
        """Test UI components (for development)."""
        from rich.tree import Tree

        self.app.renderer.render_info("Testing UI components...")
        self.app.console.print()

        # Test tool execution display
        tree = self.app.renderer.render_tool_action(
            "search_web", {"query": "Python rich library", "max_results": 10}
        )
        self.app.renderer.render_tool_result(
            "Found 10 results\n\n1. Rich Documentation\n2. GitHub Repository\n3. Tutorial...",
            tree,
            expandable=True,
            expanded=False,
        )
        self.app.renderer.render_tree(tree)

        # Test thinking mode
        self.app.renderer.render_thinking(
            "I should search for information about the Rich library first...",
            duration=1.5,
            expandable=True,
            expanded=False,
        )
        self.app.console.print()

        # Test messages
        self.app.renderer.render_success("Test completed successfully!")
        self.app.renderer.render_warning("This is a warning message")
        self.app.renderer.render_error("This is an error message", title="Test Error")
