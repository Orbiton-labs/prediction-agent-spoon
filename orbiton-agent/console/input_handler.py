"""Input handling for Orbiton Agent console."""

from typing import Optional, Callable
from rich.console import Console
from rich.prompt import Prompt
from rich.rule import Rule

from .theme import SYMBOL_USER


class InputHandler:
    """Handles user input in the console."""

    def __init__(self, console: Console):
        """
        Initialize input handler.

        Args:
            console: Rich Console instance
        """
        self.console = console
        self.history: list[str] = []
        self.history_index: int = -1

    def get_input(self, prompt: str = "", multiline: bool = False) -> Optional[str]:
        """
        Get user input with bottom input box (always at bottom of screen).

        Args:
            prompt: Prompt text (default uses theme symbol)
            multiline: Whether to support multi-line input

        Returns:
            User input or None if interrupted
        """
        if not prompt:
            prompt = f"[prompt]{SYMBOL_USER}[/] "

        try:
            # Show input box at bottom (with top and bottom lines)
            self.console.print(Rule(style="cyan", characters="─"))

            if multiline:
                user_input = self._get_multiline_input(prompt)
            else:
                # Simple input with bottom border
                self.console.print(prompt, end="")
                user_input = input()

                if user_input:
                    self.history.append(user_input)
                    self.history_index = len(self.history)

            # Show bottom border
            self.console.print(Rule(style="cyan", characters="─"))

            return user_input

        except (KeyboardInterrupt, EOFError):
            return None

    def _get_multiline_input(self, prompt: str) -> str:
        """
        Get multi-line input (until empty line or EOF).

        Args:
            prompt: Prompt text

        Returns:
            Combined multi-line input
        """
        lines = []
        self.console.print(f"{prompt} [dim](empty line to finish)[/]")

        while True:
            try:
                line = input("  ")
                if not line:  # Empty line ends input
                    break
                lines.append(line)
            except (KeyboardInterrupt, EOFError):
                break

        full_input = "\n".join(lines)
        if full_input:
            self.history.append(full_input)
            self.history_index = len(self.history)

        return full_input

    def get_history(self, limit: Optional[int] = None) -> list[str]:
        """
        Get input history.

        Args:
            limit: Maximum number of items to return

        Returns:
            List of previous inputs
        """
        if limit:
            return self.history[-limit:]
        return self.history.copy()

    def clear_history(self):
        """Clear input history."""
        self.history.clear()
        self.history_index = -1
