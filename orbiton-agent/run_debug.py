#!/usr/bin/env python3
"""Run Orbiton Agent TUI with debug logging enabled."""

import sys
from pathlib import Path

# Ensure logs directory exists
logs_dir = Path(__file__).parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Add parent to path for spoon_ai imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from console.app_tui import ConsoleTUIApp


def main():
    """Run the TUI app with debug logging."""
    # Load configuration
    import os
    from dotenv import load_dotenv

    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)

    config = {
        "llm": {
            "default_provider": "openai",
            "default_model": os.getenv("ORBITON_LLM_MODEL", "gpt-4o"),
            "base_url": os.getenv("BASE_URL"),
            "temperature": 0.7,
            "max_tokens": 4096,
        },
        "agent": {
            "type": "react-mcp",
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
            "auto_save_interval": 60,
        },
        "mcp": {
            "enabled": True,
            "servers": [
                {
                    "name": "gemini-cli",
                    "description": "Gemini CLI MCP tool",
                    "config": {
                        "command": "npx",
                        "args": ["-y", "gemini-mcp-tool"]
                    }
                }
            ]
        },
    }

    print("=" * 80)
    print("ORBITON AGENT - DEBUG MODE (MCP ENABLED)")
    print("=" * 80)
    print("\nDebug logging enabled:")
    print("  - All API requests/responses will be logged")
    print("  - Logs written to: logs/orbiton_debug.log")
    print("  - Console output will show debug messages")
    print("\nMCP Configuration:")
    print(f"  - Agent Type: {config['agent']['type']}")
    print(f"  - MCP Enabled: {config['mcp']['enabled']}")
    print(f"  - MCP Servers: {len(config['mcp']['servers'])}")
    for server in config['mcp']['servers']:
        print(f"    • {server['name']}: {server.get('description', 'No description')}")
    print("\n" + "=" * 80)
    print()

    # Run app with debug=True
    app = ConsoleTUIApp(config=config, debug=True)
    app.run()


if __name__ == "__main__":
    main()
