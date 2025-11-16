"""Session persistence for Orbiton Agent."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from .session import SessionState, ConversationMessage


class SessionPersistence:
    """Handles saving and loading of session state."""

    def __init__(self, history_dir: Optional[str] = None):
        """
        Initialize session persistence.

        Args:
            history_dir: Directory to store session files (default: ~/.orbiton/history)
        """
        self.history_dir = Path(history_dir or "~/.orbiton/history").expanduser()
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_state: SessionState, path: Optional[str] = None) -> Path:
        """
        Save session to file.

        Args:
            session_state: SessionState to save
            path: Optional custom path (default: auto-generated in history_dir)

        Returns:
            Path to saved file
        """
        if path:
            save_path = Path(path)
        else:
            # Auto-generate filename
            timestamp = session_state.created_at.strftime("%Y%m%d_%H%M%S")
            filename = f"session_{session_state.session_id[:8]}_{timestamp}.json"
            save_path = self.history_dir / filename

        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to JSON
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(session_state.to_dict(), f, indent=2, ensure_ascii=False)

        return save_path

    def load_session(self, path: str) -> Optional[SessionState]:
        """
        Load session from file.

        Args:
            path: Path to session file

        Returns:
            SessionState or None if loading fails
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SessionState.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading session: {e}")
            return None

    def list_sessions(self, directory: Optional[str] = None) -> List[Dict]:
        """
        List all sessions in directory.

        Args:
            directory: Directory to scan (default: history_dir)

        Returns:
            List of session metadata dictionaries
        """
        scan_dir = Path(directory) if directory else self.history_dir
        if not scan_dir.exists():
            return []

        sessions = []
        for file_path in scan_dir.glob("session_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                sessions.append(
                    {
                        "path": str(file_path),
                        "session_id": data.get("session_id", "unknown"),
                        "created_at": data.get("created_at", "unknown"),
                        "updated_at": data.get("updated_at", "unknown"),
                        "message_count": len(data.get("messages", [])),
                        "agent": data.get("current_agent", "unknown"),
                        "model": data.get("current_model", "unknown"),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                # Skip invalid files
                continue

        # Sort by updated_at (newest first)
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session file.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False otherwise
        """
        # Find session file
        for file_path in self.history_dir.glob(f"session_{session_id[:8]}_*.json"):
            try:
                file_path.unlink()
                return True
            except OSError:
                return False
        return False

    def export_session(
        self, session_state: SessionState, filename: str, format: str = "md"
    ) -> Path:
        """
        Export session to a formatted file.

        Args:
            session_state: SessionState to export
            filename: Output filename
            format: Export format ("md", "json", "txt")

        Returns:
            Path to exported file
        """
        # Ensure proper extension
        if format == "md" and not filename.endswith(".md"):
            filename += ".md"
        elif format == "json" and not filename.endswith(".json"):
            filename += ".json"
        elif format == "txt" and not filename.endswith(".txt"):
            filename += ".txt"

        # Use current directory or history dir
        if "/" in filename or "\\" in filename:
            export_path = Path(filename)
        else:
            export_path = Path.cwd() / filename

        if format == "md":
            content = self._format_markdown(session_state)
        elif format == "json":
            content = json.dumps(session_state.to_dict(), indent=2, ensure_ascii=False)
        else:  # txt
            content = self._format_text(session_state)

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(content)

        return export_path

    def auto_save(self, session_state: SessionState) -> Optional[Path]:
        """
        Auto-save session (called periodically or on exit).

        Args:
            session_state: SessionState to save

        Returns:
            Path to saved file or None if no messages
        """
        # Don't save empty sessions
        if not session_state.messages:
            return None

        return self.save_session(session_state)

    def _format_markdown(self, session_state: SessionState) -> str:
        """Format session as markdown."""
        lines = []

        # Header
        lines.append(f"# Orbiton Agent Conversation")
        lines.append(f"")
        lines.append(f"**Session ID:** {session_state.session_id}")
        lines.append(f"**Created:** {session_state.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Updated:** {session_state.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Agent:** {session_state.current_agent}")
        lines.append(f"**Model:** {session_state.current_model}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

        # Messages
        for msg in session_state.messages:
            timestamp = msg.timestamp.strftime("%H:%M:%S")

            if msg.role == "user":
                lines.append(f"## 👤 User [{timestamp}]")
                lines.append(f"")
                lines.append(msg.content)
                lines.append(f"")
            elif msg.role == "agent":
                lines.append(f"## 🤖 Agent [{timestamp}]")
                lines.append(f"")
                lines.append(msg.content)
                lines.append(f"")
            elif msg.role == "system":
                lines.append(f"## 🔧 System [{timestamp}]")
                lines.append(f"")
                lines.append(msg.content)
                lines.append(f"")

        # Tool executions
        if session_state.tool_executions:
            lines.append(f"---")
            lines.append(f"")
            lines.append(f"## 🛠️ Tool Executions ({len(session_state.tool_executions)})")
            lines.append(f"")

            for tool in session_state.tool_executions:
                timestamp = tool.timestamp.strftime("%H:%M:%S")
                lines.append(f"### {tool.tool_name} [{timestamp}]")
                lines.append(f"")
                lines.append(f"**Arguments:**")
                lines.append(f"```json")
                lines.append(json.dumps(tool.arguments, indent=2))
                lines.append(f"```")
                lines.append(f"")
                lines.append(f"**Result:** {tool.result[:200]}...")
                lines.append(f"")
                lines.append(f"**Execution Time:** {tool.execution_time:.2f}s")
                if tool.error:
                    lines.append(f"")
                    lines.append(f"**Error:** {tool.error}")
                lines.append(f"")

        return "\n".join(lines)

    def _format_text(self, session_state: SessionState) -> str:
        """Format session as plain text."""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("ORBITON AGENT CONVERSATION")
        lines.append("=" * 80)
        lines.append(f"Session ID: {session_state.session_id}")
        lines.append(f"Created: {session_state.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Updated: {session_state.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Agent: {session_state.current_agent}")
        lines.append(f"Model: {session_state.current_model}")
        lines.append("=" * 80)
        lines.append("")

        # Messages
        for msg in session_state.messages:
            timestamp = msg.timestamp.strftime("%H:%M:%S")
            role_display = {
                "user": "USER",
                "agent": "AGENT",
                "system": "SYSTEM",
            }.get(msg.role, msg.role.upper())

            lines.append(f"[{timestamp}] {role_display}:")
            lines.append(msg.content)
            lines.append("")
            lines.append("-" * 80)
            lines.append("")

        return "\n".join(lines)


class AutoSaver:
    """
    Handles automatic session saving.

    This runs in the background and periodically saves the session.
    """

    def __init__(self, session_manager, persistence: SessionPersistence, interval: int = 60):
        """
        Initialize auto-saver.

        Args:
            session_manager: SessionManager instance
            persistence: SessionPersistence instance
            interval: Save interval in seconds
        """
        self.session_manager = session_manager
        self.persistence = persistence
        self.interval = interval
        self.running = False
        self._thread = None

    def start(self):
        """Start auto-save in background."""
        import threading

        if self.running:
            return

        self.running = True

        def _auto_save_loop():
            import time

            while self.running:
                time.sleep(self.interval)
                if self.running:
                    try:
                        session_state = self.session_manager.get_session_state()
                        self.persistence.auto_save(session_state)
                    except Exception:
                        # Silent fail - don't interrupt main app
                        pass

        self._thread = threading.Thread(target=_auto_save_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop auto-save and perform final save (non-blocking)."""
        import threading

        self.running = False

        # Perform final save in background to avoid blocking UI shutdown
        def _final_save():
            try:
                session_state = self.session_manager.get_session_state()
                self.persistence.auto_save(session_state)
            except Exception:
                pass

        # Run final save in daemon thread (non-blocking)
        final_save_thread = threading.Thread(target=_final_save, daemon=True)
        final_save_thread.start()

        # Don't wait for auto-save thread - let it finish in background
        # This ensures fast shutdown
