"""Configuration loading utilities."""
import json
from pathlib import Path
from typing import Any, Dict, List


class ConfigLoader:
    """Loads and validates configuration from JSON files."""

    @staticmethod
    def load(config_path: Path) -> Dict[str, Any]:
        """Load configuration from JSON file.

        Args:
            config_path: Path to configuration JSON file

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Validate configuration structure
        ConfigLoader._validate(config)

        return config

    @staticmethod
    def _validate(config: Dict[str, Any]) -> None:
        """Validate configuration structure.

        Args:
            config: Configuration dictionary

        Raises:
            ValueError: If configuration is invalid
        """
        # Check required top-level keys
        required_keys = ["accounts", "transfers", "simulation"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")

        # Validate accounts
        if not isinstance(config["accounts"], list):
            raise ValueError("'accounts' must be a list")

        for i, account in enumerate(config["accounts"]):
            if not isinstance(account, dict):
                raise ValueError(f"Account {i} must be a dictionary")
            if "id" not in account or "initial_balance" not in account:
                raise ValueError(
                    f"Account {i} must have 'id' and 'initial_balance' fields"
                )
            if not isinstance(account["id"], int):
                raise ValueError(f"Account {i} 'id' must be an integer")
            if not isinstance(account["initial_balance"], (int, float)):
                raise ValueError(
                    f"Account {i} 'initial_balance' must be a number"
                )

        # Validate transfers
        if not isinstance(config["transfers"], list):
            raise ValueError("'transfers' must be a list")

        for i, transfer in enumerate(config["transfers"]):
            if not isinstance(transfer, dict):
                raise ValueError(f"Transfer {i} must be a dictionary")
            required_transfer_keys = ["from", "to", "amount"]
            for key in required_transfer_keys:
                if key not in transfer:
                    raise ValueError(f"Transfer {i} must have '{key}' field")
            if not isinstance(transfer["from"], int):
                raise ValueError(f"Transfer {i} 'from' must be an integer")
            if not isinstance(transfer["to"], int):
                raise ValueError(f"Transfer {i} 'to' must be an integer")
            if not isinstance(transfer["amount"], (int, float)):
                raise ValueError(f"Transfer {i} 'amount' must be a number")
            if transfer["amount"] <= 0:
                raise ValueError(f"Transfer {i} 'amount' must be positive")

        # Validate simulation settings
        if not isinstance(config["simulation"], dict):
            raise ValueError("'simulation' must be a dictionary")

        simulation = config["simulation"]
        if "thread_delay_seconds" not in simulation:
            raise ValueError("simulation must have 'thread_delay_seconds'")
        if "deadlock_timeout_seconds" not in simulation:
            raise ValueError("simulation must have 'deadlock_timeout_seconds'")
        if "verbose_logging" not in simulation:
            raise ValueError("simulation must have 'verbose_logging'")

    @staticmethod
    def load_default() -> Dict[str, Any]:
        """Load default configuration from config/config.json.

        Returns:
            Configuration dictionary
        """
        config_path = Path("config/config.json")
        return ConfigLoader.load(config_path)
