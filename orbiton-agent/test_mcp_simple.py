#!/usr/bin/env python3
"""Simple test to verify MCP configuration without circular imports."""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_config():
    """Load configuration from defaults.json"""
    config_path = Path(__file__).parent / "config" / "defaults.json"
    with open(config_path) as f:
        return json.load(f)


def test_config_structure():
    """Test the MCP configuration structure."""
    print("\n" + "="*80)
    print("MCP Configuration Test")
    print("="*80)

    config = load_config()

    # Check agent type
    agent_config = config.get("agent", {})
    agent_type = agent_config.get("type")
    print(f"\n✓ Agent Type: {agent_type}")

    if agent_type != "react-mcp":
        print(f"  ⚠ Warning: Agent type is '{agent_type}', should be 'react-mcp' for MCP support")

    # Check MCP configuration
    mcp_config = config.get("mcp", {})
    mcp_enabled = mcp_config.get("enabled", False)
    mcp_servers = mcp_config.get("servers", [])

    print(f"\n✓ MCP Enabled: {mcp_enabled}")
    print(f"✓ MCP Servers Configured: {len(mcp_servers)}")

    if mcp_enabled and mcp_servers:
        print("\nConfigured MCP Servers:")
        for i, server in enumerate(mcp_servers, 1):
            name = server.get("name", "unknown")
            desc = server.get("description", "")
            srv_type = server.get("type", "unknown")

            print(f"\n  {i}. {name}")
            print(f"     Description: {desc}")
            print(f"     Type: {srv_type}")

            # Check configuration
            srv_config = server.get("config", {})
            if "command" in srv_config:
                print(f"     Command: {srv_config['command']}")
                print(f"     Args: {srv_config.get('args', [])}")

            if "env" in srv_config:
                print(f"     Environment Variables:")
                for key, value in srv_config["env"].items():
                    # Check if env var is set
                    if value.startswith("${") and value.endswith("}"):
                        env_var = value[2:-1]
                        env_value = os.getenv(env_var)
                        if env_value:
                            print(f"       ✓ {key}: ${env_var} (set)")
                        else:
                            print(f"       ✗ {key}: ${env_var} (NOT SET)")
                    else:
                        print(f"       ✓ {key}: {value}")

            if "url" in srv_config:
                print(f"     URL: {srv_config['url']}")

    # Check environment variables
    print("\n" + "="*80)
    print("Environment Variables Check")
    print("="*80)

    required_vars = {
        "OPENAI_API_KEY": "Required for LLM",
        "TAVILY_API_KEY": "Required for Tavily search (optional)",
    }

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✓ {var}: {masked} ({description})")
        else:
            print(f"✗ {var}: Not set ({description})")

    # Summary
    print("\n" + "="*80)
    print("Configuration Summary")
    print("="*80)

    if agent_type == "react-mcp" and mcp_enabled and mcp_servers:
        print("✓ MCP is properly configured!")
        print("\nNext steps:")
        print("1. Ensure required environment variables are set in .env")
        print("2. For Tavily search: set TAVILY_API_KEY")
        print("3. For SpoonAI tools: start the MCP server:")
        print("   python -m spoon_ai.tools.mcp_tools_collection")
        print("4. Run orbiton-agent: uv run main.py")
    else:
        print("⚠ MCP configuration incomplete")
        if agent_type != "react-mcp":
            print(f"  - Change agent type from '{agent_type}' to 'react-mcp'")
        if not mcp_enabled:
            print("  - Enable MCP in config")
        if not mcp_servers:
            print("  - Add MCP servers to configuration")

    print()


if __name__ == "__main__":
    test_config_structure()
