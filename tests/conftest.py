"""Shared pytest fixtures for all tests."""
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest


@pytest.fixture
def sample_accounts_data() -> List[Dict[str, Any]]:
    """Sample accounts configuration for testing."""
    return [
        {"id": 1, "initial_balance": 1000},
        {"id": 2, "initial_balance": 1000},
        {"id": 3, "initial_balance": 1000},
        {"id": 4, "initial_balance": 1000},
        {"id": 5, "initial_balance": 1000},
    ]


@pytest.fixture
def sample_transfers_data() -> List[Dict[str, Any]]:
    """Sample transfers configuration for testing."""
    return [
        {"from": 1, "to": 2, "amount": 100},
        {"from": 2, "to": 3, "amount": 50},
        {"from": 3, "to": 4, "amount": 75},
        {"from": 4, "to": 5, "amount": 60},
    ]


@pytest.fixture
def opposing_transfers_data() -> List[Dict[str, Any]]:
    """Opposing transfers that trigger deadlock in Phase 1."""
    return [
        {"from": 1, "to": 2, "amount": 100},
        {"from": 2, "to": 1, "amount": 50},
        {"from": 3, "to": 4, "amount": 75},
        {"from": 4, "to": 3, "amount": 60},
    ]


@pytest.fixture
def sample_config(
    sample_accounts_data: List[Dict[str, Any]],
    sample_transfers_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Sample complete configuration for testing."""
    return {
        "accounts": sample_accounts_data,
        "transfers": sample_transfers_data,
        "simulation": {
            "thread_delay_seconds": 0.001,  # Shorter for tests
            "deadlock_timeout_seconds": 2,  # Shorter timeout for tests
            "verbose_logging": False,  # Less noise in tests
        },
    }


@pytest.fixture
def temp_log_file() -> Path:
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        log_path = Path(f.name)

    yield log_path

    # Cleanup
    if log_path.exists():
        log_path.unlink()
