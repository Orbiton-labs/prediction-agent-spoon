"""Theme and styling for Orbiton Agent console interface."""

from rich.theme import Theme
from rich import box

# Color Constants (following design.md specifications)
USER_COLOR = "cyan"
AGENT_COLOR = "green"
TOOL_ACTION_COLOR = "green"
TOOL_RESULT_COLOR = "cyan"
THINKING_COLOR = "dim cyan"
STATUS_COLOR = "yellow"
ERROR_COLOR = "red"
SUCCESS_COLOR = "green"
WARNING_COLOR = "magenta"
HEADER_PRIMARY = "bold white"
HEADER_SECONDARY = "dim white"
INFO_COLOR = "blue"

# Custom Rich Theme
orbiton_theme = Theme({
    "user": USER_COLOR,
    "agent": AGENT_COLOR,
    "tool.action": TOOL_ACTION_COLOR,
    "tool.result": TOOL_RESULT_COLOR,
    "thinking": THINKING_COLOR,
    "status": STATUS_COLOR,
    "error": ERROR_COLOR,
    "success": SUCCESS_COLOR,
    "warning": WARNING_COLOR,
    "header.primary": HEADER_PRIMARY,
    "header.secondary": HEADER_SECONDARY,
    "info": INFO_COLOR,
    # Additional styles
    "prompt": "bold cyan",
    "command": "bold magenta",
    "timestamp": "dim",
    "highlight": "bold yellow",
})

# Box Styles for Panels
HEADER_BOX = box.HEAVY
MESSAGE_BOX = box.ROUNDED
USER_BOX_STYLE = "cyan"  # Border color for user messages
AGENT_BOX_STYLE = "green"  # Border color for agent messages
TOOL_BOX = box.ROUNDED
ERROR_BOX = box.DOUBLE
INFO_BOX = box.ROUNDED

# Spinner Styles for Different States
SPINNER_THINKING = "dots12"
SPINNER_EXECUTING = "line"
SPINNER_PROCESSING = "arc"

# Tree Guide Styles
TREE_GUIDE_STYLE = "dim cyan"

# Symbols
SYMBOL_USER = ">"
SYMBOL_AGENT = "•"
SYMBOL_TOOL_ACTION = "▸"
SYMBOL_TOOL_RESULT = "↳"
SYMBOL_THINKING = "💭"
SYMBOL_SUCCESS = "✓"
SYMBOL_ERROR = "✗"
SYMBOL_WARNING = "⚠"
SYMBOL_INFO = "ℹ"
SYMBOL_EXPAND = "▶"
SYMBOL_COLLAPSE = "▼"

# Layout Constants
HEADER_HEIGHT = 3
FOOTER_HEIGHT = 1
MIN_TERMINAL_WIDTH = 80
MIN_TERMINAL_HEIGHT = 24

# Progressive Disclosure
AUTO_EXPAND_THRESHOLD = 5  # Lines
COLLAPSED_PREVIEW_LENGTH = 100  # Characters
