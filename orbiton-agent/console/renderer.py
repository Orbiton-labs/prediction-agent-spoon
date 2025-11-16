"""UI rendering engine for Orbiton Agent console."""

import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.text import Text

from .theme import (
    orbiton_theme,
    SYMBOL_USER,
    SYMBOL_AGENT,
    SYMBOL_TOOL_ACTION,
    SYMBOL_TOOL_RESULT,
    SYMBOL_THINKING,
    SYMBOL_SUCCESS,
    SYMBOL_ERROR,
    SYMBOL_WARNING,
    SYMBOL_EXPAND,
    SYMBOL_COLLAPSE,
    HEADER_BOX,
    MESSAGE_BOX,
    USER_BOX_STYLE,
    AGENT_BOX_STYLE,
    TOOL_BOX,
    ERROR_BOX,
    TREE_GUIDE_STYLE,
    AUTO_EXPAND_THRESHOLD,
    COLLAPSED_PREVIEW_LENGTH,
)


class Renderer:
    """Handles all UI rendering for the console."""

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize renderer.

        Args:
            console: Rich Console instance. If None, creates new one.
        """
        self.console = console or Console(theme=orbiton_theme)

    def render_header(self, agent_name: str = "Orbiton Agent", model: str = "", cwd: str = ""):
        """
        Render header with context information.

        Args:
            agent_name: Name of the agent
            model: Model name being used
            cwd: Current working directory
        """
        if not cwd:
            cwd = os.getcwd()

        # Make path more readable (use ~ for home)
        cwd = str(Path(cwd)).replace(str(Path.home()), "~")

        header_text = f"[header.primary]{agent_name}[/]"
        if model:
            header_text += f" [header.secondary]• {model}[/]"
        header_text += f"\n[header.secondary]{cwd}[/]"

        panel = Panel(
            header_text,
            box=HEADER_BOX,
            border_style="header.primary",
            padding=(0, 2),
        )
        self.console.print(panel)

    def render_user_message(self, message: str, timestamp: Optional[datetime] = None):
        """
        Render user message (clean, no box).

        Args:
            message: User's message
            timestamp: Optional timestamp
        """
        prefix = f"[user]{SYMBOL_USER}[/]"
        if timestamp:
            ts = timestamp.strftime("%H:%M:%S")
            prefix = f"[dim]{ts}[/] {prefix}"

        self.console.print(f"{prefix} {message}")
        self.console.print()  # Empty line for spacing

    def render_agent_message(self, message: str, timestamp: Optional[datetime] = None):
        """
        Render agent message (clean, no box) with markdown support.

        Args:
            message: Agent's message
            timestamp: Optional timestamp
        """
        prefix = f"[agent]{SYMBOL_AGENT}[/]"
        if timestamp:
            ts = timestamp.strftime("%H:%M:%S")
            prefix = f"[dim]{ts}[/] {prefix}"

        self.console.print(prefix)

        # Try to render as markdown if it contains markdown syntax
        if any(marker in message for marker in ["```", "**", "*", "#", "-", ">"]):
            try:
                md = Markdown(message)
                self.console.print(md)
            except Exception:
                # Fall back to plain text
                self.console.print(f"  {message}")
        else:
            self.console.print(f"  {message}")

        self.console.print()  # Empty line for spacing

    def render_tool_action(
        self,
        tool_name: str,
        arguments: dict,
        tree_parent: Optional[Tree] = None,
    ) -> Tree:
        """
        Render tool action in tree format.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            tree_parent: Optional parent tree node

        Returns:
            Tree node for this action
        """
        # Format arguments
        args_str = self._format_tool_args(arguments)
        action_text = f"[tool.action]{SYMBOL_TOOL_ACTION} {tool_name}({args_str})[/]"

        if tree_parent is None:
            # Create new tree
            tree = Tree(action_text, guide_style=TREE_GUIDE_STYLE)
            return tree
        else:
            # Add to existing tree
            return tree_parent.add(action_text)

    def render_tool_result(
        self,
        result: str,
        tree_node: Tree,
        expandable: bool = False,
        expanded: bool = False,
        section_id: Optional[str] = None,
    ):
        """
        Render tool result with progressive disclosure.

        Args:
            result: Tool result text
            tree_node: Tree node to add result to
            expandable: Whether result can be expanded
            expanded: Whether result is currently expanded
            section_id: ID for tracking expandable section
        """
        if expandable and not expanded:
            # Show collapsed preview
            lines = result.split("\n")
            line_count = len(lines)
            preview = result[:COLLAPSED_PREVIEW_LENGTH]
            if len(result) > COLLAPSED_PREVIEW_LENGTH:
                preview += "..."

            result_text = f"[tool.result]{SYMBOL_TOOL_RESULT} {preview}[/]"
            hint_text = f" [dim](ctrl+o to expand) +{line_count} lines[/]"
            tree_node.add(result_text + hint_text)
        else:
            # Show full result
            # Try to detect if it's code and apply syntax highlighting
            lang = self._detect_code_language(result)
            if lang and len(result.split("\n")) > 1:
                syntax = Syntax(result, lang, theme="monokai", line_numbers=False)
                tree_node.add(syntax)
            else:
                result_text = f"[tool.result]{SYMBOL_TOOL_RESULT} {result}[/]"
                if expandable:
                    result_text += " [dim](ctrl+o to collapse)[/]"
                tree_node.add(result_text)

    def render_thinking(
        self,
        text: str,
        duration: Optional[float] = None,
        expandable: bool = True,
        expanded: bool = False,
    ):
        """
        Render thinking mode display.

        Args:
            text: Thinking content
            duration: How long agent thought (in seconds)
            expandable: Whether thinking can be expanded
            expanded: Whether thinking is currently expanded
        """
        if expanded:
            # Show full thinking content
            panel = Panel(
                text,
                title=f"{SYMBOL_THINKING} Thinking",
                title_align="left",
                border_style="thinking",
                padding=(1, 2),
            )
            self.console.print(panel)
        else:
            # Show collapsed thinking indicator
            duration_str = f"{duration:.1f}s" if duration else ""
            hint = f"[thinking]{SYMBOL_THINKING} Thought for {duration_str} [dim](ctrl+o to show thinking)[/][/]"
            self.console.print(hint)

    def render_status(self, message: str, spinner: bool = True):
        """
        Render status line (used with Rich Live or Status).

        Args:
            message: Status message
            spinner: Whether to show spinner

        Returns:
            Formatted status text
        """
        status_text = f"[status]{message}[/]"
        if not spinner:
            return status_text
        return status_text + " [dim](esc to interrupt)[/]"

    def render_error(self, message: str, title: str = "Error"):
        """
        Render error message.

        Args:
            message: Error message
            title: Error title
        """
        panel = Panel(
            f"[error]{message}[/]",
            title=f"{SYMBOL_ERROR} {title}",
            title_align="left",
            border_style="error",
            box=ERROR_BOX,
            padding=(1, 2),
        )
        self.console.print(panel)

    def render_success(self, message: str):
        """
        Render success message.

        Args:
            message: Success message
        """
        self.console.print(f"[success]{SYMBOL_SUCCESS} {message}[/]")

    def render_warning(self, message: str):
        """
        Render warning message.

        Args:
            message: Warning message
        """
        self.console.print(f"[warning]{SYMBOL_WARNING} {message}[/]")

    def render_info(self, message: str):
        """
        Render info message.

        Args:
            message: Info message
        """
        self.console.print(f"[info]{message}[/]")

    def render_tree(self, tree: Tree):
        """
        Render a complete tree structure.

        Args:
            tree: Tree to render
        """
        self.console.print(tree)
        self.console.print()  # Empty line for spacing

    def clear_screen(self):
        """Clear the console screen."""
        self.console.clear()

    def print_rule(self, title: str = "", style: str = "dim"):
        """
        Print a horizontal rule/divider.

        Args:
            title: Optional title for the rule
            style: Style for the rule
        """
        self.console.rule(title, style=style)

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

    def _detect_code_language(self, text: str) -> Optional[str]:
        """
        Detect programming language from code text.

        Args:
            text: Code text

        Returns:
            Language identifier or None
        """
        # Simple heuristics for common languages
        if "def " in text and ":" in text:
            return "python"
        if "function " in text or "const " in text or "=>" in text:
            return "javascript"
        if "{" in text and "}" in text and ";" in text:
            if "public " in text or "private " in text:
                return "java"
            return "javascript"
        if "#!/bin/bash" in text or "#!/bin/sh" in text:
            return "bash"

        return None

    def should_expand(self, content: str) -> bool:
        """
        Determine if content should be expandable.

        Args:
            content: Content to check

        Returns:
            True if content should be expandable
        """
        lines = content.split("\n")
        return len(lines) > AUTO_EXPAND_THRESHOLD


class ExpandableSection:
    """Represents an expandable section of content."""

    def __init__(
        self,
        section_id: str,
        content: str,
        section_type: str = "tool_result",
        metadata: Optional[dict] = None,
    ):
        """
        Initialize expandable section.

        Args:
            section_id: Unique identifier
            content: Full content
            section_type: Type of section (tool_result, thinking, etc.)
            metadata: Optional metadata
        """
        self.section_id = section_id
        self.content = content
        self.section_type = section_type
        self.metadata = metadata or {}
        self.expanded = False

    def toggle(self):
        """Toggle expanded state."""
        self.expanded = not self.expanded

    def get_preview(self, max_length: int = COLLAPSED_PREVIEW_LENGTH) -> str:
        """
        Get preview of content.

        Args:
            max_length: Maximum length of preview

        Returns:
            Preview string
        """
        if len(self.content) <= max_length:
            return self.content

        return self.content[:max_length] + "..."


class SectionManager:
    """Manages expandable sections."""

    def __init__(self):
        """Initialize section manager."""
        self.sections: dict[str, ExpandableSection] = {}
        self._id_counter = 0

    def register(
        self,
        content: str,
        section_type: str = "tool_result",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Register a new expandable section.

        Args:
            content: Section content
            section_type: Type of section
            metadata: Optional metadata

        Returns:
            Section ID
        """
        section_id = f"{section_type}_{self._id_counter}"
        self._id_counter += 1

        section = ExpandableSection(
            section_id=section_id,
            content=content,
            section_type=section_type,
            metadata=metadata,
        )
        self.sections[section_id] = section

        return section_id

    def get(self, section_id: str) -> Optional[ExpandableSection]:
        """Get section by ID."""
        return self.sections.get(section_id)

    def toggle(self, section_id: str) -> bool:
        """
        Toggle section expanded state.

        Args:
            section_id: Section to toggle

        Returns:
            New expanded state, or False if section not found
        """
        section = self.sections.get(section_id)
        if section:
            section.toggle()
            return section.expanded
        return False

    def get_last_section(self) -> Optional[ExpandableSection]:
        """Get the most recently added section."""
        if not self.sections:
            return None
        return list(self.sections.values())[-1]
