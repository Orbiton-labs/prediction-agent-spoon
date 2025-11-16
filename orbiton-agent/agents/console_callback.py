"""Console callback handler for capturing agent events and displaying in UI."""

import time
from typing import Any, Optional
from datetime import datetime

from rich.live import Live
from rich.panel import Panel
from rich.tree import Tree

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from spoon_ai.callbacks.base import BaseCallbackHandler
from console.renderer import Renderer
from console.theme import SPINNER_THINKING, SYMBOL_THINKING


class ConsoleCallbackHandler(BaseCallbackHandler):
    """Callback handler that displays agent activity in the console UI."""

    def __init__(self, renderer: Renderer):
        """
        Initialize console callback handler.

        Args:
            renderer: Renderer instance for UI updates
        """
        super().__init__()
        self.renderer = renderer

        # State tracking
        self.current_tool: Optional[str] = None
        self.current_tree: Optional[Tree] = None
        self.thinking_buffer: list[str] = []
        self.thinking_start_time: Optional[float] = None
        self.tool_start_time: Optional[float] = None
        self.live_display: Optional[Live] = None

        # Configuration
        self.show_thinking = True
        self.stream_tokens = True

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any) -> None:
        """
        Called when LLM starts.

        Args:
            serialized: Serialized LLM
            prompts: Input prompts
            **kwargs: Additional arguments
        """
        self.thinking_buffer = []
        self.thinking_start_time = time.time()

        # Show status
        if self.show_thinking:
            self.renderer.console.print(
                f"[thinking]{SYMBOL_THINKING} Thinking...[/]",
                end=""
            )

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """
        Called when LLM generates a new token.

        Args:
            token: New token
            **kwargs: Additional arguments
        """
        # Accumulate thinking tokens
        self.thinking_buffer.append(token)

        # Stream to console if enabled
        if self.stream_tokens and self.show_thinking:
            self.renderer.console.print(token, end="", style="thinking")

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """
        Called when LLM finishes.

        Args:
            response: LLM response
            **kwargs: Additional arguments
        """
        if self.thinking_start_time:
            duration = time.time() - self.thinking_start_time

            if self.show_thinking and self.thinking_buffer:
                # Clear the thinking line
                self.renderer.console.print()

                # Show thinking summary
                thinking_text = "".join(self.thinking_buffer)
                if thinking_text.strip():
                    self.renderer.render_thinking(
                        thinking_text,
                        duration=duration,
                        expandable=True,
                        expanded=False
                    )
            elif self.show_thinking:
                # Just show duration
                self.renderer.console.print(f" ({duration:.1f}s)")

            self.thinking_start_time = None
            self.thinking_buffer = []

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """
        Called when LLM encounters an error.

        Args:
            error: Error exception
            **kwargs: Additional arguments
        """
        self.renderer.render_error(str(error), title="LLM Error")
        self.thinking_buffer = []
        self.thinking_start_time = None

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        **kwargs: Any
    ) -> None:
        """
        Called when tool execution starts.

        Args:
            serialized: Serialized tool
            input_str: Tool input
            **kwargs: Additional arguments
        """
        # Extract tool name and arguments
        tool_name = serialized.get("name", "unknown_tool")
        self.current_tool = tool_name
        self.tool_start_time = time.time()

        # Parse arguments from input_str (simple approach)
        try:
            # Try to parse as dict or use as string
            import json
            if input_str.strip().startswith("{"):
                args = json.loads(input_str)
            else:
                args = {"input": input_str}
        except:
            args = {"input": input_str}

        # Format arguments for display
        args_str = self._format_tool_args(args)

        # Display tool call in simple format: > ToolName('params')
        from console.theme import SYMBOL_TOOL_ACTION
        tool_call_text = f"[tool.action]{SYMBOL_TOOL_ACTION} {tool_name}({args_str})[/]"
        self.renderer.console.print(f"\n{tool_call_text}")

        # Store the current tree as None (we'll just print directly)
        self.current_tree = None

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """
        Called when tool execution ends.

        Args:
            output: Tool output
            **kwargs: Additional arguments
        """
        # Display tool result in simple format: ↳ ToolResponse
        from console.theme import SYMBOL_TOOL_RESULT

        # Truncate very long outputs for readability
        display_output = output[:300] + "..." if len(output) > 300 else output

        result_text = f"[tool.result]{SYMBOL_TOOL_RESULT} {display_output}[/]"
        self.renderer.console.print(result_text)

        # Calculate execution time
        if self.tool_start_time:
            duration = time.time() - self.tool_start_time
            if duration > 0.1:  # Only show if meaningful
                self.renderer.console.print(
                    f"[dim]  Completed in {duration:.2f}s[/]"
                )

        self.renderer.console.print()  # Empty line for spacing

        # Reset state
        self.current_tool = None
        self.current_tree = None
        self.tool_start_time = None

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """
        Called when tool execution errors.

        Args:
            error: Error exception
            **kwargs: Additional arguments
        """
        # Display error in simple format
        from console.theme import SYMBOL_ERROR

        error_msg = f"[error]{SYMBOL_ERROR} {str(error)}[/]"
        self.renderer.console.print(error_msg)
        self.renderer.console.print()  # Empty line for spacing

        # Reset state
        self.current_tool = None
        self.current_tree = None
        self.tool_start_time = None

    def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        """
        Called when agent takes an action.

        Args:
            action: Agent action
            **kwargs: Additional arguments
        """
        # Optional: Log agent decisions
        pass

    def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        """
        Called when agent finishes.

        Args:
            finish: Finish information
            **kwargs: Additional arguments
        """
        # Extract final output
        if hasattr(finish, 'return_values'):
            output = finish.return_values.get('output', '')
            if output:
                self.renderer.render_agent_message(
                    output,
                    timestamp=datetime.now()
                )
        elif hasattr(finish, 'output'):
            self.renderer.render_agent_message(
                finish.output,
                timestamp=datetime.now()
            )

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        **kwargs: Any
    ) -> None:
        """
        Called when chain starts.

        Args:
            serialized: Serialized chain
            inputs: Chain inputs
            **kwargs: Additional arguments
        """
        # Optional: Track chain execution
        pass

    def on_chain_end(self, outputs: dict[str, Any], **kwargs: Any) -> None:
        """
        Called when chain ends.

        Args:
            outputs: Chain outputs
            **kwargs: Additional arguments
        """
        # Optional: Track chain completion
        pass

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """
        Called when chain errors.

        Args:
            error: Error exception
            **kwargs: Additional arguments
        """
        self.renderer.render_error(str(error), title="Chain Error")

    def on_text(self, text: str, **kwargs: Any) -> None:
        """
        Called when text is generated.

        Args:
            text: Generated text
            **kwargs: Additional arguments
        """
        # Optional: Handle intermediate text
        pass

    # Helper methods

    def _format_tool_args(self, arguments: dict) -> str:
        """
        Format tool arguments for display.

        Args:
            arguments: Tool arguments dictionary

        Returns:
            Formatted arguments string
        """
        if not arguments:
            return ""

        formatted = []
        for key, value in arguments.items():
            # Truncate long values
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."

            # Add quotes for strings
            if isinstance(value, str):
                value_str = f'"{value_str}"'

            formatted.append(f"{key}={value_str}")

        return ", ".join(formatted)

    def set_show_thinking(self, show: bool):
        """Enable or disable thinking display."""
        self.show_thinking = show

    def set_stream_tokens(self, stream: bool):
        """Enable or disable token streaming."""
        self.stream_tokens = stream
