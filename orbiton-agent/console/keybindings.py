"""Keyboard bindings for Orbiton Agent console."""

from typing import Optional
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys


class KeyBindingManager:
    """Manages keyboard shortcuts for the console application."""

    def __init__(self, app):
        """
        Initialize key binding manager.

        Args:
            app: ConsoleApp instance
        """
        self.app = app
        self.bindings = KeyBindings()
        self._setup_bindings()

    def _setup_bindings(self):
        """Set up all keyboard bindings."""

        # ctrl+o: Toggle expand/collapse sections
        @self.bindings.add('c-o')
        def _(event):
            """Toggle expandable sections."""
            self.handle_ctrl_o()

        # ESC: Interrupt agent execution
        @self.bindings.add(Keys.Escape)
        def _(event):
            """Interrupt ongoing agent execution."""
            self.handle_esc()

        # ctrl+l: Clear screen
        @self.bindings.add('c-l')
        def _(event):
            """Clear screen and preserve conversation."""
            self.handle_ctrl_l()

        # ctrl+c is handled by default prompt_toolkit behavior
        # It will raise KeyboardInterrupt which we handle in the main loop

    def get_bindings(self) -> KeyBindings:
        """
        Get the key bindings object.

        Returns:
            KeyBindings object for prompt_toolkit
        """
        return self.bindings

    def handle_ctrl_o(self):
        """
        Handle ctrl+o: Toggle expandable section.

        In Phase 4 MVP, this will toggle the last expandable section.
        In future, this could toggle sections based on cursor position.
        """
        if not hasattr(self.app, 'section_manager') or not self.app.section_manager:
            self.app.renderer.render_warning("Section manager not available")
            return

        # Get the last expandable section
        sections = self.app.section_manager.get_all_sections()
        if not sections:
            self.app.renderer.render_info("No expandable sections available")
            return

        # Toggle the last section
        last_section = sections[-1]
        section_id = id(last_section)

        # Toggle state
        current_state = self.app.section_manager.is_expanded(section_id)
        new_state = not current_state
        self.app.section_manager.set_expanded(section_id, new_state)

        # Show feedback
        state_text = "expanded" if new_state else "collapsed"
        self.app.renderer.render_info(f"Section {state_text}")

    def handle_esc(self):
        """
        Handle ESC: Interrupt agent execution.

        This will gracefully stop the currently running agent.
        """
        if not self.app.agent_session:
            return

        # Check if agent is currently executing
        if hasattr(self.app.agent_session, '_executing') and self.app.agent_session._executing:
            self.app.renderer.render_warning("⚠ Interrupting agent...")
            self.app.agent_session.interrupt()

            # Show interruption message
            self.app.console.print()
            self.app.renderer.render_info("Agent execution interrupted")
        else:
            # Not currently executing, just show info
            self.app.renderer.render_info("No agent execution to interrupt")

    def handle_ctrl_l(self):
        """
        Handle ctrl+l: Clear screen but preserve conversation.

        This is similar to /clear command but triggered by keyboard.
        """
        from pathlib import Path

        self.app.renderer.clear_screen()
        self.app.renderer.render_header(
            agent_name="Orbiton Agent",
            model=self.app.current_model,
            cwd=Path.cwd(),
        )
        self.app.renderer.render_info("Screen cleared (ctrl+l)")


class SectionNavigator:
    """
    Manages navigation between expandable sections.

    This is a more advanced feature that could be implemented
    in a future version to allow navigating between sections
    with arrow keys.
    """

    def __init__(self, section_manager):
        """
        Initialize section navigator.

        Args:
            section_manager: SectionManager instance
        """
        self.section_manager = section_manager
        self.current_section_index = 0

    def next_section(self):
        """Move to the next expandable section."""
        sections = self.section_manager.get_all_sections()
        if sections:
            self.current_section_index = (self.current_section_index + 1) % len(sections)
            return sections[self.current_section_index]
        return None

    def previous_section(self):
        """Move to the previous expandable section."""
        sections = self.section_manager.get_all_sections()
        if sections:
            self.current_section_index = (self.current_section_index - 1) % len(sections)
            return sections[self.current_section_index]
        return None

    def get_current_section(self):
        """Get the currently focused section."""
        sections = self.section_manager.get_all_sections()
        if sections and 0 <= self.current_section_index < len(sections):
            return sections[self.current_section_index]
        return None

    def toggle_current_section(self):
        """Toggle the currently focused section."""
        section = self.get_current_section()
        if section:
            section_id = id(section)
            current_state = self.section_manager.is_expanded(section_id)
            self.section_manager.set_expanded(section_id, not current_state)
            return not current_state
        return None


class InterruptionHandler:
    """
    Handles graceful interruption of agent execution.

    This class manages the interruption state and ensures
    proper cleanup when the user interrupts an operation.
    """

    def __init__(self, agent_session):
        """
        Initialize interruption handler.

        Args:
            agent_session: AgentSession instance
        """
        self.agent_session = agent_session
        self.interruption_requested = False

    def request_interrupt(self):
        """Request interruption of current execution."""
        self.interruption_requested = True
        if self.agent_session:
            self.agent_session.interrupt()

    def handle_interruption(self):
        """
        Handle the interruption.

        This method should be called after an interruption
        to clean up state and prepare for the next operation.
        """
        self.interruption_requested = False
        # Additional cleanup can be added here

    def is_interrupted(self) -> bool:
        """
        Check if interruption was requested.

        Returns:
            True if interruption was requested
        """
        return self.interruption_requested

    def reset(self):
        """Reset the interruption state."""
        self.interruption_requested = False
