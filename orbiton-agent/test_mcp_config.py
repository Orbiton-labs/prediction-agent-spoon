#!/usr/bin/env python3
"""Test script to verify MCP configuration."""

import sys
import json
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.factory import AgentFactory
from agents.console_callback import ConsoleCallbackHandler
from console.renderer import Renderer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from defaults.json"""
    config_path = Path(__file__).parent / "config" / "defaults.json"
    with open(config_path) as f:
        return json.load(f)


async def test_mcp_tools_creation():
    """Test MCP tools creation from configuration."""
    print("\n" + "="*80)
    print("TEST 1: MCP Tools Creation")
    print("="*80)

    config = load_config()
    mcp_config = config.get("mcp", {})

    print(f"\nMCP Enabled: {mcp_config.get('enabled', False)}")
    print(f"MCP Servers Configured: {len(mcp_config.get('servers', []))}")

    # Test tool creation
    mcp_tools = AgentFactory._create_mcp_tools(mcp_config)

    print(f"\nMCP Tools Created: {len(mcp_tools)}")
    for tool in mcp_tools:
        print(f"  - {tool.name}: {tool.description}")

    return mcp_tools


async def test_agent_creation():
    """Test MCP-enabled agent creation."""
    print("\n" + "="*80)
    print("TEST 2: Agent Creation")
    print("="*80)

    config = load_config()
    agent_type = config.get("agent", {}).get("type", "react")

    print(f"\nAgent Type: {agent_type}")

    try:
        # Create renderer and callback handler
        renderer = Renderer()
        callback_handler = ConsoleCallbackHandler(renderer)

        # Create agent
        agent = AgentFactory.create_agent(
            agent_type=agent_type,
            config=config,
            callback_handler=callback_handler
        )

        print(f"✓ Agent created successfully: {type(agent).__name__}")

        # Check if agent has MCP tools
        if hasattr(agent, 'available_tools'):
            tool_count = len(agent.available_tools.tool_map)
            print(f"✓ Agent has {tool_count} tools available")

            if tool_count > 0:
                print("\nAvailable tools:")
                for tool_name in agent.available_tools.tool_map.keys():
                    print(f"  - {tool_name}")
        else:
            print("⚠ Agent doesn't have available_tools attribute")

        return agent

    except Exception as e:
        print(f"✗ Failed to create agent: {e}")
        logger.exception("Agent creation failed")
        return None


async def test_mcp_tool_parameters():
    """Test loading MCP tool parameters from server."""
    print("\n" + "="*80)
    print("TEST 3: MCP Tool Parameter Loading")
    print("="*80)

    config = load_config()
    mcp_tools = AgentFactory._create_mcp_tools(config.get("mcp", {}))

    if not mcp_tools:
        print("⚠ No MCP tools to test")
        return

    for tool in mcp_tools:
        print(f"\nTesting tool: {tool.name}")
        try:
            # Try to load parameters (with timeout)
            print(f"  Loading parameters from MCP server...")
            await asyncio.wait_for(tool.ensure_parameters_loaded(), timeout=10)

            if tool.parameters:
                print(f"  ✓ Parameters loaded successfully")
                print(f"  Parameters: {json.dumps(tool.parameters, indent=2)[:200]}...")
            else:
                print(f"  ⚠ No parameters loaded")

        except asyncio.TimeoutError:
            print(f"  ✗ Timeout loading parameters (server may not be running)")
        except Exception as e:
            print(f"  ✗ Error loading parameters: {e}")


async def test_simple_query():
    """Test a simple query with the MCP-enabled agent."""
    print("\n" + "="*80)
    print("TEST 4: Simple Query")
    print("="*80)

    config = load_config()

    try:
        # Create agent
        renderer = Renderer()
        callback_handler = ConsoleCallbackHandler(renderer)
        agent = AgentFactory.create_agent(
            agent_type="react-mcp",
            config=config,
            callback_handler=callback_handler
        )

        # Simple test query
        query = "What tools do you have available?"
        print(f"\nQuery: {query}")
        print("\nAgent Response:")
        print("-" * 80)

        response = await agent.run(query)
        print(response)
        print("-" * 80)

    except Exception as e:
        print(f"✗ Query failed: {e}")
        logger.exception("Query execution failed")


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("MCP Configuration Test Suite")
    print("="*80)

    # Test 1: MCP tools creation
    await test_mcp_tools_creation()

    # Test 2: Agent creation
    await test_agent_creation()

    # Test 3: MCP tool parameter loading
    # Note: This will only work if MCP servers are running
    await test_mcp_tool_parameters()

    # Test 4: Simple query
    # Uncomment to test a full agent query (requires MCP servers)
    # await test_simple_query()

    print("\n" + "="*80)
    print("Test Suite Complete")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
