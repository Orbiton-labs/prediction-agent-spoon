"""Configuration management for Orbiton Agent."""

import json
import os
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration loading, validation, and updates."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ConfigManager.

        Args:
            config_path: Path to custom config file. If None, uses defaults.
        """
        self.config_path = config_path
        self.config: dict[str, Any] = {}
        self._defaults_path = Path(__file__).parent / "defaults.json"

    def load(self) -> dict[str, Any]:
        """
        Load configuration from defaults, custom config, and environment variables.

        Priority (highest to lowest):
        1. Environment variables
        2. Custom config file (if provided)
        3. Defaults

        Returns:
            Loaded configuration dictionary
        """
        # Load defaults
        self.config = self._load_defaults()

        # Load custom config if provided
        if self.config_path and self.config_path.exists():
            custom_config = self._load_json(self.config_path)
            self.config = self._merge_configs(self.config, custom_config)

        # Load and apply environment variables
        load_dotenv()
        self._apply_env_overrides()

        return self.config

    def _load_defaults(self) -> dict[str, Any]:
        """Load default configuration."""
        if not self._defaults_path.exists():
            raise FileNotFoundError(f"Defaults file not found: {self._defaults_path}")
        return self._load_json(self._defaults_path)

    def _load_json(self, path: Path) -> dict[str, Any]:
        """Load JSON file."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}")

    def _merge_configs(self, base: dict, override: dict) -> dict:
        """
        Recursively merge two configuration dictionaries.

        Args:
            base: Base configuration
            override: Override configuration

        Returns:
            Merged configuration
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        # Map environment variables to config paths
        env_mappings = {
            "ORBITON_LLM_MODEL": ("llm", "default_model"),
            "ORBITON_LLM_PROVIDER": ("llm", "default_provider"),
            "ORBITON_LLM_TEMPERATURE": ("llm", "temperature", float),
            "ORBITON_LLM_MAX_TOKENS": ("llm", "max_tokens", int),
            "ORBITON_AGENT_TYPE": ("agent", "type"),
            "ORBITON_UI_THEME": ("ui", "theme"),
            "ORBITON_UI_SHOW_THINKING": ("ui", "show_thinking", self._str_to_bool),
            "ORBITON_SESSION_SAVE_HISTORY": ("session", "save_history", self._str_to_bool),
            "ORBITON_SESSION_HISTORY_DIR": ("session", "history_dir"),
        }

        for env_var, mapping in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Parse mapping (key1, key2, optional_converter)
                keys = mapping[:-1] if len(mapping) > 2 and callable(mapping[-1]) else mapping
                converter = mapping[-1] if len(mapping) > 2 and callable(mapping[-1]) else None

                # Apply converter if provided
                if converter:
                    try:
                        value = converter(value)
                    except (ValueError, TypeError):
                        continue

                # Set value in config
                self._set_nested(self.config, keys, value)

    def _set_nested(self, config: dict, keys: tuple, value: Any):
        """Set a nested configuration value."""
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    @staticmethod
    def _str_to_bool(value: str) -> bool:
        """Convert string to boolean."""
        return value.lower() in ("true", "1", "yes", "on")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., "llm.temperature")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., "llm.temperature")
            value: Value to set
        """
        keys = key_path.split(".")
        self._set_nested(self.config, tuple(keys), value)

    def save(self, path: Optional[Path] = None):
        """
        Save configuration to file.

        Args:
            path: Path to save to. If None, uses config_path or raises error.
        """
        save_path = path or self.config_path

        if not save_path:
            raise ValueError("No save path provided and no config_path set")

        with open(save_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def reload(self) -> dict[str, Any]:
        """Reload configuration from disk."""
        return self.load()

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required_fields = [
            "llm.default_provider",
            "llm.default_model",
            "agent.type",
        ]

        for field in required_fields:
            if self.get(field) is None:
                errors.append(f"Required field missing: {field}")

        # Validate temperature range
        temp = self.get("llm.temperature")
        if temp is not None and not (0.0 <= temp <= 1.0):
            errors.append(f"Invalid temperature: {temp} (must be between 0.0 and 1.0)")

        # Validate max_tokens
        max_tokens = self.get("llm.max_tokens")
        if max_tokens is not None and max_tokens < 1:
            errors.append(f"Invalid max_tokens: {max_tokens} (must be positive)")

        # Validate agent type
        valid_agent_types = ["react", "react-mcp"]
        agent_type = self.get("agent.type")
        if agent_type and agent_type not in valid_agent_types:
            errors.append(f"Invalid agent type: {agent_type} (must be one of {valid_agent_types})")

        return (len(errors) == 0, errors)
