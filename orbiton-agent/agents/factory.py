"""Agent factory for creating and managing AI agents."""

import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from spoon_ai.agents.spoon_react import SpoonReactAI
from spoon_ai.agents.spoon_react_mcp import SpoonReactMCP
from spoon_ai.chat import ChatBot, Memory
from spoon_ai.callbacks.base import BaseCallbackHandler
from spoon_ai.tools.mcp_tool import MCPTool
from spoon_ai.tools.tool_manager import ToolManager


class AgentFactory:
    """Factory for creating AI agents with proper configuration."""

    @staticmethod
    def _create_mcp_tools(mcp_config: dict) -> list:
        """
        Create MCP tools from configuration.

        Args:
            mcp_config: MCP configuration dictionary

        Returns:
            List of MCPTool instances
        """
        import os
        import logging

        logger = logging.getLogger(__name__)
        mcp_tools = []

        if not mcp_config.get("enabled", False):
            logger.info("MCP is disabled in configuration")
            return mcp_tools

        servers = mcp_config.get("servers", [])
        if not servers:
            logger.info("No MCP servers configured")
            return mcp_tools

        for server in servers:
            try:
                server_name = server.get("name", "unknown")
                server_config = server.get("config", {})

                # Replace environment variables in config
                if "env" in server_config:
                    env_vars = {}
                    for key, value in server_config["env"].items():
                        # Replace ${VAR} with actual environment variable
                        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                            env_var = value[2:-1]
                            env_value = os.getenv(env_var)
                            if env_value:
                                env_vars[key] = env_value
                            else:
                                logger.warning(f"Environment variable {env_var} not found for MCP server {server_name}")
                        else:
                            env_vars[key] = value
                    server_config["env"] = env_vars
                else:
                    env_vars = {}
                    server_config["env"] = env_vars

                # Suppress verbose output from MCP subprocesses
                # Add environment variables to reduce logging noise
                server_config["env"]["PYTHONWARNINGS"] = "ignore"
                server_config["env"]["PYTHONUNBUFFERED"] = "0"
                # For Node.js based MCP tools
                server_config["env"]["NODE_ENV"] = "production"
                server_config["env"]["NPM_CONFIG_LOGLEVEL"] = "error"

                # Create MCPTool instance
                mcp_tool = MCPTool(
                    name=server_name,
                    description=server.get("description", f"MCP tool: {server_name}"),
                    mcp_config=server_config
                )
                mcp_tools.append(mcp_tool)
                logger.info(f"Created MCP tool: {server_name}")

            except Exception as e:
                logger.error(f"Failed to create MCP tool for server {server.get('name', 'unknown')}: {e}")

        return mcp_tools

    @staticmethod
    def create_agent(
        agent_type: str,
        config: dict,
        callback_handler: Optional[BaseCallbackHandler] = None,
    ) -> Any:
        """
        Create an agent based on type and configuration.

        Args:
            agent_type: Type of agent ("react" or "react-mcp")
            config: Configuration dictionary
            callback_handler: Optional callback handler

        Returns:
            Configured agent instance

        Raises:
            ValueError: If agent type is unknown or configuration is invalid
        """
        # Validate agent type
        valid_types = ["react", "react-mcp"]
        if agent_type not in valid_types:
            raise ValueError(f"Unknown agent type: {agent_type}. Valid types: {valid_types}")

        # Extract configuration
        llm_config = config.get("llm", {})
        agent_config = config.get("agent", {})

        # Initialize ChatBot (which uses LLM Manager internally)
        try:
            import os
            from dotenv import load_dotenv

            # Force reload .env from orbiton-agent directory
            env_path = Path(__file__).parent.parent / ".env"
            if env_path.exists():
                load_dotenv(env_path, override=True)

            # Get base_url from environment if available
            base_url = os.getenv("BASE_URL") or llm_config.get("base_url")
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

            # Prepare callbacks list
            callbacks_list = [callback_handler] if callback_handler else []

            chatbot = ChatBot(
                llm_provider=llm_config.get("default_provider", "openai"),
                model_name=llm_config.get("default_model", "gpt-4o"),
                api_key=api_key,
                base_url=base_url,  # Support custom base_url
                callbacks=callbacks_list,
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize ChatBot: {e}")

        # Initialize memory if enabled
        memory = None
        if agent_config.get("memory_enabled", True):
            memory = Memory()

        # Create agent based on type
        try:
            if agent_type == "react":
                agent = SpoonReactAI(
                    llm=chatbot,
                    max_steps=agent_config.get("max_iterations", 10),
                )

            elif agent_type == "react-mcp":
                # Create MCP tools from configuration
                mcp_config = config.get("mcp", {})
                mcp_tools = AgentFactory._create_mcp_tools(mcp_config)

                # Create ToolManager with MCP tools
                if mcp_tools:
                    tool_manager = ToolManager(mcp_tools)
                    agent = SpoonReactMCP(
                        llm=chatbot,
                        max_steps=agent_config.get("max_iterations", 10),
                        tools=mcp_tools,
                    )
                else:
                    # No MCP tools configured, create basic agent
                    agent = SpoonReactMCP(
                        llm=chatbot,
                        max_steps=agent_config.get("max_iterations", 10),
                    )
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")

            return agent

        except Exception as e:
            raise ValueError(f"Failed to create {agent_type} agent: {e}")

    @staticmethod
    def list_available_agents() -> list[dict[str, str]]:
        """
        List available agent types.

        Returns:
            List of agent information dictionaries
        """
        return [
            {
                "type": "react",
                "name": "ReAct Agent",
                "description": "Standard ReAct agent with reasoning and action capabilities",
            },
            {
                "type": "react-mcp",
                "name": "ReAct MCP Agent",
                "description": "ReAct agent with Model Context Protocol support",
            },
        ]

    @staticmethod
    def get_agent_info(agent_type: str) -> Optional[dict[str, Any]]:
        """
        Get information about a specific agent type.

        Args:
            agent_type: Agent type identifier

        Returns:
            Agent information or None if not found
        """
        agents = AgentFactory.list_available_agents()
        for agent in agents:
            if agent["type"] == agent_type:
                return agent
        return None


class AgentSession:
    """Manages an agent session with state and execution control."""

    def __init__(self, agent: Any, config: dict):
        """
        Initialize agent session.

        Args:
            agent: Agent instance
            config: Configuration dictionary
        """
        import asyncio
        import logging

        self.agent = agent
        self.config = config
        self.executing = False
        self.interrupted = False

        # Create and reuse event loop for performance
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)

        # Setup logging for debugging
        self.logger = logging.getLogger(__name__)
        self._enable_debug_logging = config.get("debug", False)

    async def execute_async(self, user_input: str) -> str:
        """
        Execute user input with the agent (async).

        Args:
            user_input: User's message/query

        Returns:
            Agent's response

        Raises:
            Exception: If execution fails
        """
        if self.executing:
            raise RuntimeError("Agent is already executing")

        self.executing = True
        self.interrupted = False

        try:
            # Log input
            if self._enable_debug_logging:
                self.logger.info("=" * 80)
                self.logger.info("AGENT INPUT:")
                self.logger.info(f"  User Input: {user_input}")
                self.logger.info("=" * 80)

            # Run the agent (async)
            response = await self.agent.run(user_input)

            # Log response
            if self._enable_debug_logging:
                self.logger.info("=" * 80)
                self.logger.info("AGENT OUTPUT:")
                self.logger.info(f"  Response: {response[:200]}{'...' if len(response) > 200 else ''}")
                self.logger.info(f"  Length: {len(response)} chars")
                self.logger.info("=" * 80)

            return response

        except KeyboardInterrupt:
            self.interrupted = True
            raise

        except Exception as e:
            if self._enable_debug_logging:
                self.logger.error(f"Agent execution failed: {e}", exc_info=True)
            raise Exception(f"Agent execution failed: {e}")

        finally:
            self.executing = False

    def execute(self, user_input: str) -> str:
        """
        Execute user input with the agent (sync wrapper).

        Args:
            user_input: User's message/query

        Returns:
            Agent's response

        Raises:
            Exception: If execution fails
        """
        # Reuse the event loop created during initialization
        return self._event_loop.run_until_complete(self.execute_async(user_input))

    def interrupt(self):
        """Signal the agent to stop execution."""
        if self.executing:
            self.interrupted = True
            # Note: Actual interruption depends on agent implementation
            # For now, we just set the flag

    def reset(self):
        """Reset the agent session (clear memory)."""
        if hasattr(self.agent, 'memory') and self.agent.memory:
            self.agent.memory.clear()
        self.executing = False
        self.interrupted = False

    def is_executing(self) -> bool:
        """Check if agent is currently executing."""
        return self.executing

    def was_interrupted(self) -> bool:
        """Check if last execution was interrupted."""
        return self.interrupted

    def get_memory_size(self) -> int:
        """Get the current memory size (number of messages)."""
        if hasattr(self.agent, 'memory') and self.agent.memory:
            return len(self.agent.memory.messages)
        return 0

    def get_agent_type(self) -> str:
        """Get the type of agent."""
        if isinstance(self.agent, SpoonReactMCP):
            return "react-mcp"
        elif isinstance(self.agent, SpoonReactAI):
            return "react"
        return "unknown"

    def close(self):
        """Clean up resources (close event loop)."""
        if hasattr(self, '_event_loop') and self._event_loop and not self._event_loop.is_closed():
            self._event_loop.close()

    def __del__(self):
        """Destructor to ensure event loop is closed."""
        self.close()
