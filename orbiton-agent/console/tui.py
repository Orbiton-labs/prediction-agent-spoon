"""Full-screen TUI layout using prompt_toolkit."""

import asyncio
from datetime import datetime
from typing import Optional, List, Callable
from pathlib import Path

from prompt_toolkit import Application
from prompt_toolkit.layout import (
    Layout,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
    FormattedTextControl,
    BufferControl,
    Float,
    FloatContainer,
    ConditionalContainer,
)
from prompt_toolkit.layout.containers import Container
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import FormattedText, HTML
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.styles import Style

from .theme import (
    SYMBOL_USER,
    SYMBOL_AGENT,
    SYMBOL_TOOL_ACTION,
    SYMBOL_TOOL_RESULT,
    SYMBOL_THINKING,
)


class TUIApp:
    """Full-screen Terminal User Interface Application."""

    def __init__(
        self,
        agent_name: str = "Orbiton Agent",
        model: str = "unknown",
        on_input: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize TUI application.

        Args:
            agent_name: Name of the agent
            model: Model name
            on_input: Callback function when user submits input
        """
        self.agent_name = agent_name
        self.model = model
        self.on_input = on_input
        self.running = False

        # History messages (list of FormattedText)
        self.history_messages: List[FormattedText] = []

        # Status line
        self.status_text = ""
        self.show_status = False

        # Create buffers and controls
        self._create_layout()
        self._create_key_bindings()

        # Build application
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self._get_style(),
            full_screen=True,  # Fill entire terminal
            mouse_support=True,
            erase_when_done=True,  # Clean up on exit
        )

    def _create_layout(self):
        """Create the full-screen layout."""
        # Header window (compact)
        self.header_control = FormattedTextControl(
            text=self._get_header_text,
            focusable=False,
        )
        header = Window(
            content=self.header_control,
            height=2,  # Compact header
            style="class:header",
            dont_extend_height=True,
        )

        # History pane (scrollable with BufferControl for proper scrolling)
        self.history_buffer = Buffer(read_only=True)
        self.history_control = BufferControl(
            buffer=self.history_buffer,
            focusable=False,
        )
        history_pane = Window(
            content=self.history_control,
            wrap_lines=True,
            style="class:history",
            scroll_offsets=0,  # Allow scrolling to the very bottom
        )

        # Status line (optional, between history and input)
        self.status_control = FormattedTextControl(
            text=self._get_status_text,
            focusable=False,
        )
        status_line = ConditionalContainer(
            Window(
                content=self.status_control,
                height=1,
                style="class:status",
                dont_extend_height=True,
            ),
            filter=Condition(lambda: self.show_status),
        )

        # Separator line above input (top border)
        input_separator_top = Window(
            char="─",  # Horizontal line character
            height=1,
            style="class:input-separator",
            dont_extend_height=True,
        )

        # Input bar (fixed at bottom)
        self.input_field = TextArea(
            prompt=HTML(f"<prompt>{SYMBOL_USER}</prompt> "),
            height=1,
            multiline=False,
            wrap_lines=False,
            style="class:input",
            focusable=True,
            dont_extend_height=True,
        )
        # Access the internal buffer for resetting
        self.input_buffer = self.input_field.buffer

        # Separator line below input (bottom border)
        input_separator_bottom = Window(
            char="─",  # Horizontal line character
            height=1,
            style="class:input-separator",
            dont_extend_height=True,
        )

        # Shortcuts hint
        shortcuts_control = FormattedTextControl(
            text=self._get_shortcuts_text,
            focusable=False,
        )
        shortcuts = Window(
            content=shortcuts_control,
            height=1,
            style="class:shortcuts",
            dont_extend_height=True,
        )

        # Main layout: Header | History | Status | [Top Line] Input [Bottom Line] | Shortcuts
        self.layout = Layout(
            HSplit([
                header,
                history_pane,
                status_line,
                input_separator_top,
                self.input_field,
                input_separator_bottom,
                shortcuts,
            ])
        )

    def _create_key_bindings(self):
        """Create keyboard shortcuts."""
        self.kb = KeyBindings()

        @self.kb.add("enter")
        def handle_enter(event):
            """Handle Enter key - submit input."""
            text = self.input_buffer.text.strip()
            if text:
                # Add user message to history
                self.add_user_message(text)

                # Clear input buffer
                self.input_buffer.reset()

                # Call callback
                if self.on_input:
                    # Run in background to avoid blocking UI
                    asyncio.create_task(self._handle_input(text))

        @self.kb.add("escape")
        def handle_escape(event):
            """Handle ESC - interrupt."""
            self.set_status("Interrupted by user", style="warning")
            # TODO: Add interrupt logic

        @self.kb.add("c-c")
        def handle_exit(event):
            """Handle Ctrl+C - exit."""
            event.app.exit()

        @self.kb.add("c-t")
        def handle_todos(event):
            """Handle Ctrl+T - show todos."""
            self.add_info_message("TODO: Show todos list")

        @self.kb.add("c-o")
        def handle_expand(event):
            """Handle Ctrl+O - expand/collapse."""
            self.add_info_message("TODO: Expand/collapse last section")

        @self.kb.add("c-l")
        def handle_clear(event):
            """Handle Ctrl+L - clear screen."""
            self.clear_history()

    async def _handle_input(self, text: str):
        """
        Handle user input in background.

        Args:
            text: User input text
        """
        if self.on_input:
            try:
                await asyncio.to_thread(self.on_input, text)
            except Exception as e:
                self.add_error_message(f"Error: {str(e)}")

    def _get_style(self) -> Style:
        """Get application style that syncs with terminal theme."""
        return Style.from_dict({
            # Use terminal default colors for main areas
            # Header - subtle inverse for contrast
            "header": "reverse bold",
            "header.secondary": "dim",

            # History pane - use terminal defaults
            "history": "",  # Use terminal default colors
            "user": "ansibrightcyan bold",  # Respects terminal theme
            "agent": "ansibrightgreen",
            "tool.action": "ansigreen",
            "tool.result": "ansicyan",
            "thinking": "dim italic",
            "success": "ansibrightgreen",
            "error": "ansibrightred bold",
            "warning": "ansiyellow",
            "info": "dim",

            # Status line - subtle background
            "status": "reverse",

            # Input - use terminal defaults
            "input": "",  # Terminal default
            "input-separator": "ansicyan",  # Separator lines
            "prompt": "ansibrightcyan bold",

            # Shortcuts - dim to not distract
            "shortcuts": "dim",
            "shortcut.key": "ansicyan",
        })

    def _get_header_text(self) -> FormattedText:
        """Get header text (compact, single line)."""
        cwd = str(Path.cwd()).replace(str(Path.home()), "~")
        return FormattedText([
            ("class:header", f" {self.agent_name} "),
            ("class:header.secondary", f"• {self.model} • {cwd} "),
        ])

    def _update_history_buffer(self):
        """Update history buffer with all messages."""
        if not self.history_messages:
            text = "  Type your message below and press Enter to start...\n"
        else:
            # Convert FormattedText messages to plain text
            # (BufferControl doesn't support formatted text styling directly)
            lines = []
            for msg in self.history_messages:
                # Extract text from FormattedText tuples
                line_text = "".join(text for style, text in msg)
                lines.append(line_text)
            text = "\n".join(lines)

        # Update buffer document
        self.history_buffer.set_document(
            Document(text=text, cursor_position=len(text)),
            bypass_readonly=True
        )

    def _get_status_text(self) -> FormattedText:
        """Get status text."""
        if self.status_text:
            return FormattedText([
                ("class:status", f" {self.status_text} "),
            ])
        return FormattedText([])

    def _get_shortcuts_text(self) -> FormattedText:
        """Get shortcuts hint text."""
        return FormattedText([
            ("class:shortcuts", " "),
            ("class:shortcut.key", "esc"),
            ("class:shortcuts", " interrupt • "),
            ("class:shortcut.key", "ctrl+t"),
            ("class:shortcuts", " todos • "),
            ("class:shortcut.key", "ctrl+o"),
            ("class:shortcuts", " expand • "),
            ("class:shortcut.key", "ctrl+l"),
            ("class:shortcuts", " clear • "),
            ("class:shortcut.key", "ctrl+c"),
            ("class:shortcuts", " exit "),
        ])

    def _on_text_insert(self, buffer):
        """Handle text insertion in input buffer."""
        # Can be used for auto-completion or other features
        pass

    # Public API for adding messages

    def add_user_message(self, message: str, timestamp: Optional[datetime] = None):
        """
        Add user message to history.

        Args:
            message: User message
            timestamp: Optional timestamp
        """
        prefix = f"{SYMBOL_USER} "
        if timestamp:
            ts = timestamp.strftime("%H:%M:%S")
            prefix = f"[{ts}] {prefix}"

        msg = FormattedText([
            ("class:user", prefix),
            ("", message),
        ])
        self.history_messages.append(msg)
        self._scroll_to_bottom()

    def add_agent_message(self, message: str, timestamp: Optional[datetime] = None):
        """
        Add agent message to history.

        Args:
            message: Agent message
            timestamp: Optional timestamp
        """
        prefix = f"{SYMBOL_AGENT} "
        if timestamp:
            ts = timestamp.strftime("%H:%M:%S")
            prefix = f"[{ts}] {prefix}"

        msg = FormattedText([
            ("class:agent", prefix),
            ("", message),
        ])
        self.history_messages.append(msg)
        self._scroll_to_bottom()

    def add_tool_action(self, tool_name: str, args: dict):
        """
        Add tool action to history.

        Args:
            tool_name: Tool name
            args: Tool arguments
        """
        # Format arguments with better display
        if args:
            # Truncate long argument values
            formatted_args = []
            for k, v in args.items():
                v_str = str(v)
                if len(v_str) > 50:
                    v_str = v_str[:47] + "..."
                formatted_args.append(f"{k}={v_str}")
            args_str = ", ".join(formatted_args)
        else:
            args_str = ""

        # Clean format: > ToolName(params)
        msg = FormattedText([
            ("class:tool.action", f"{SYMBOL_TOOL_ACTION} {tool_name}({args_str})"),
        ])
        self.history_messages.append(msg)
        self._scroll_to_bottom()

    def add_tool_result(self, result: str):
        """
        Add tool result to history.

        Args:
            result: Tool result
        """
        # Truncate long results but show more context
        display_result = result[:300] + "..." if len(result) > 300 else result

        # Clean format: ↳ ToolResponse (with minimal indent)
        msg = FormattedText([
            ("class:tool.result", f"{SYMBOL_TOOL_RESULT} {display_result}"),
        ])
        self.history_messages.append(msg)
        self._scroll_to_bottom()

    def add_thinking(self, text: str, duration: Optional[float] = None):
        """
        Add thinking message to history.

        Args:
            text: Thinking text
            duration: Thinking duration in seconds
        """
        duration_str = f"{duration:.1f}s" if duration else ""
        msg = FormattedText([
            ("class:thinking", f"  {SYMBOL_THINKING} Thought for {duration_str}"),
        ])
        self.history_messages.append(msg)
        self._scroll_to_bottom()

    def add_success_message(self, message: str):
        """Add success message to history."""
        msg = FormattedText([
            ("class:success", f"  ✓ {message}"),
        ])
        self.history_messages.append(msg)
        self._scroll_to_bottom()

    def add_error_message(self, message: str):
        """Add error message to history."""
        msg = FormattedText([
            ("class:error", f"  ✗ {message}"),
        ])
        self.history_messages.append(msg)
        self._scroll_to_bottom()

    def add_warning_message(self, message: str):
        """Add warning message to history."""
        msg = FormattedText([
            ("class:warning", f"  ⚠ {message}"),
        ])
        self.history_messages.append(msg)
        self._scroll_to_bottom()

    def add_info_message(self, message: str):
        """Add info message to history."""
        msg = FormattedText([
            ("class:info", f"  {message}"),
        ])
        self.history_messages.append(msg)
        self._scroll_to_bottom()

    def set_status(self, text: str, style: str = "status"):
        """
        Set status line text.

        Args:
            text: Status text
            style: Style class
        """
        self.status_text = text
        self.show_status = bool(text)
        self.app.invalidate()

    def clear_status(self):
        """Clear status line."""
        self.status_text = ""
        self.show_status = False
        self.app.invalidate()

    def clear_history(self):
        """Clear history pane."""
        self.history_messages.clear()
        self._update_history_buffer()
        self.app.invalidate()

    def _scroll_to_bottom(self):
        """Scroll history to bottom."""
        # Update buffer with new messages
        self._update_history_buffer()
        # Invalidate to redraw
        self.app.invalidate()

    def run(self):
        """Run the TUI application."""
        self.running = True
        try:
            self.app.run()
        finally:
            self.running = False

    async def run_async(self):
        """Run the TUI application asynchronously."""
        self.running = True
        try:
            await self.app.run_async()
        finally:
            self.running = False

    def exit(self):
        """Exit the application."""
        self.app.exit()


# Example usage
if __name__ == "__main__":
    def on_user_input(text: str):
        """Handle user input."""
        tui.add_agent_message(f"You said: {text}")
        tui.add_tool_action("search_web", {"query": text, "max_results": 10})
        tui.add_tool_result("Found 10 results...")
        tui.add_thinking("Processing results...", duration=1.5)

    tui = TUIApp(
        agent_name="Orbiton Agent",
        model="claude-sonnet-4",
        on_input=on_user_input,
    )

    # Add welcome message
    tui.add_info_message("Welcome to Orbiton Agent!")
    tui.add_info_message("Type your message and press Enter to start.")

    tui.run()
