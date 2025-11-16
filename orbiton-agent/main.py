#!/usr/bin/env python3
"""
Orbiton Agent - Main CLI Entry Point

A glass box CLI interface for AI agents that shows you how it thinks and works.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import spoon_ai
sys.path.insert(0, str(Path(__file__).parent.parent))

from orbiton_agent import __version__, __description__


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Start with full-screen TUI (default)
  %(prog)s --model claude-sonnet-4            # Use specific model
  %(prog)s --agent react-mcp                  # Use MCP-enabled agent
  %(prog)s --config custom-config.json        # Use custom configuration
  %(prog)s --debug                            # Enable debug mode
  %(prog)s --legacy                           # Use old sequential UI

The new full-screen TUI provides:
  • Scrollable history pane (top) + Fixed input bar (bottom)
  • Keyboard shortcuts: ESC (interrupt), Ctrl+L (clear), Ctrl+C (exit)
  • Clean separation of input and output
  • No message duplication

For more information, visit: https://github.com/XSpoonAi/prediction-agent-spoon
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="LLM model to use (e.g., claude-sonnet-4, gpt-4, gemini-pro)",
    )

    parser.add_argument(
        "--agent",
        type=str,
        choices=["react", "react-mcp"],
        help="Agent type to use (default: react)",
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to custom configuration file (JSON)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging",
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Disable session history saving",
    )

    parser.add_argument(
        "--history-dir",
        type=Path,
        help="Directory to save conversation history",
    )

    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy sequential UI (not recommended)",
    )

    return parser.parse_args()


def setup_logging(debug: bool = False):
    """Set up logging configuration."""
    import logging
    import sys

    level = logging.DEBUG if debug else logging.ERROR

    # Configure root logger to only show errors by default
    logging.basicConfig(
        level=level,
        format="%(message)s",  # Simplified format for cleaner output
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,  # Send logs to stderr to keep stdout clean
    )

    if not debug:
        # Suppress verbose logs from all libraries
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("anthropic").setLevel(logging.ERROR)
        logging.getLogger("openai").setLevel(logging.ERROR)
        logging.getLogger("spoon_ai").setLevel(logging.ERROR)
        logging.getLogger("fastmcp").setLevel(logging.ERROR)
        logging.getLogger("mcp").setLevel(logging.ERROR)
        logging.getLogger("asyncio").setLevel(logging.ERROR)

        # Suppress stdout/stderr from subprocesses (MCP tools)
        # This helps reduce the [GMCPT] type messages
        import os
        if not debug:
            # Redirect stderr for subprocesses to devnull
            os.environ["PYTHONWARNINGS"] = "ignore"


def main():
    """Main entry point for Orbiton Agent CLI."""
    args = parse_arguments()

    # Set up logging
    setup_logging(debug=args.debug)

    try:
        # Import console app (new TUI is default)
        if args.legacy:
            from console.app import ConsoleApp
        else:
            from console.app_tui import ConsoleTUIApp as ConsoleApp

        from config.manager import ConfigManager

        # Load configuration
        config_manager = ConfigManager(config_path=args.config)
        config = config_manager.load()

        # Override with command-line arguments
        if args.model:
            config["llm"]["default_model"] = args.model
        if args.agent:
            config["agent"]["type"] = args.agent
        if args.no_save:
            config["session"]["save_history"] = False
        if args.history_dir:
            config["session"]["history_dir"] = str(args.history_dir)

        # Create and run console app
        app = ConsoleApp(config=config, debug=args.debug)
        app.run()

    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        if args.debug:
            raise
        print(f"\n❌ Error: {e}", file=sys.stderr)
        print("Run with --debug for more information")
        sys.exit(1)


if __name__ == "__main__":
    main()
