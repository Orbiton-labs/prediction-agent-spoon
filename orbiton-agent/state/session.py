"""Session state management for Orbiton Agent."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class ConversationMessage:
    """Represents a single message in the conversation."""

    role: str  # "user", "agent", or "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: Optional[List[Dict]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tool_calls": self.tool_calls,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ConversationMessage":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            tool_calls=data.get("tool_calls"),
        )


@dataclass
class ToolExecution:
    """Represents a tool execution."""

    tool_name: str
    arguments: Dict[str, Any]
    result: str
    execution_time: float  # seconds
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "result": self.result,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ToolExecution":
        """Create from dictionary."""
        return cls(
            tool_name=data["tool_name"],
            arguments=data["arguments"],
            result=data["result"],
            execution_time=data["execution_time"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            error=data.get("error"),
        )


@dataclass
class SessionState:
    """Represents the state of a conversation session."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[ConversationMessage] = field(default_factory=list)
    tool_executions: List[ToolExecution] = field(default_factory=list)
    current_agent: str = "react"
    current_model: str = "claude-sonnet-4"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [msg.to_dict() for msg in self.messages],
            "tool_executions": [tool.to_dict() for tool in self.tool_executions],
            "current_agent": self.current_agent,
            "current_model": self.current_model,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SessionState":
        """Create from dictionary."""
        return cls(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            messages=[ConversationMessage.from_dict(msg) for msg in data.get("messages", [])],
            tool_executions=[
                ToolExecution.from_dict(tool) for tool in data.get("tool_executions", [])
            ],
            current_agent=data.get("current_agent", "react"),
            current_model=data.get("current_model", "claude-sonnet-4"),
            metadata=data.get("metadata", {}),
        )


class SessionManager:
    """Manages the current session state."""

    def __init__(self, agent_type: str = "react", model: str = "claude-sonnet-4"):
        """
        Initialize session manager.

        Args:
            agent_type: Initial agent type
            model: Initial model name
        """
        self.session_state = SessionState(
            current_agent=agent_type,
            current_model=model,
        )

    def create_session(self) -> SessionState:
        """
        Create a new session.

        Returns:
            New SessionState
        """
        self.session_state = SessionState()
        return self.session_state

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
        tool_calls: Optional[List[Dict]] = None,
    ):
        """
        Add a message to the conversation.

        Args:
            role: Message role (user/agent/system)
            content: Message content
            metadata: Optional metadata
            tool_calls: Optional tool calls
        """
        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {},
            tool_calls=tool_calls,
        )
        self.session_state.messages.append(message)
        self.session_state.updated_at = datetime.now()

    def add_tool_execution(
        self,
        tool_name: str,
        arguments: Dict,
        result: str,
        execution_time: float,
        error: Optional[str] = None,
    ):
        """
        Add a tool execution record.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            result: Tool result
            execution_time: Execution time in seconds
            error: Optional error message
        """
        tool_execution = ToolExecution(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            execution_time=execution_time,
            error=error,
        )
        self.session_state.tool_executions.append(tool_execution)
        self.session_state.updated_at = datetime.now()

    def get_messages(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[ConversationMessage]:
        """
        Get conversation messages.

        Args:
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of ConversationMessage
        """
        messages = self.session_state.messages[offset:]
        if limit:
            messages = messages[:limit]
        return messages

    def get_context(self, max_tokens: Optional[int] = None) -> List[Dict]:
        """
        Get conversation context formatted for LLM.

        Args:
            max_tokens: Maximum token budget (optional)

        Returns:
            List of message dictionaries for LLM
        """
        # Format messages for LLM
        context = []
        for msg in self.session_state.messages:
            context.append(
                {
                    "role": msg.role,
                    "content": msg.content,
                }
            )

        # If max_tokens specified, truncate from beginning
        # (This is a simple implementation - could be improved)
        if max_tokens:
            # Rough estimate: 4 characters per token
            total_chars = sum(len(msg["content"]) for msg in context)
            if total_chars > max_tokens * 4:
                # Remove oldest messages until under budget
                while context and total_chars > max_tokens * 4:
                    removed = context.pop(0)
                    total_chars -= len(removed["content"])

        return context

    def clear_history(self):
        """Clear conversation history."""
        self.session_state.messages.clear()
        self.session_state.tool_executions.clear()
        self.session_state.updated_at = datetime.now()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get session statistics.

        Returns:
            Dictionary with statistics
        """
        total_messages = len(self.session_state.messages)
        user_messages = sum(1 for msg in self.session_state.messages if msg.role == "user")
        agent_messages = sum(1 for msg in self.session_state.messages if msg.role == "agent")
        total_tools = len(self.session_state.tool_executions)
        avg_execution_time = (
            sum(tool.execution_time for tool in self.session_state.tool_executions) / total_tools
            if total_tools > 0
            else 0
        )

        return {
            "session_id": self.session_state.session_id,
            "created_at": self.session_state.created_at,
            "updated_at": self.session_state.updated_at,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "agent_messages": agent_messages,
            "total_tool_executions": total_tools,
            "avg_tool_execution_time": avg_execution_time,
            "current_agent": self.session_state.current_agent,
            "current_model": self.session_state.current_model,
        }

    def get_session_state(self) -> SessionState:
        """
        Get the current session state.

        Returns:
            SessionState object
        """
        return self.session_state

    def load_session_state(self, session_state: SessionState):
        """
        Load a session state.

        Args:
            session_state: SessionState to load
        """
        self.session_state = session_state

    def update_agent(self, agent_type: str):
        """
        Update current agent type.

        Args:
            agent_type: New agent type
        """
        self.session_state.current_agent = agent_type
        self.session_state.updated_at = datetime.now()

    def update_model(self, model: str):
        """
        Update current model.

        Args:
            model: New model name
        """
        self.session_state.current_model = model
        self.session_state.updated_at = datetime.now()
