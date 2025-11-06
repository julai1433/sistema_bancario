"""Unit tests for Phase1Bank (deadlock-prone implementation)."""
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.banks.phase1_bank import Phase1Bank
from src.models.account import Account


class TestPhase1Bank:
    """Test cases for Phase1Bank class."""

    def test_simple_transfer(self) -> None:
        """Test a simple transfer between two accounts."""
        accounts = [
            Account(account_id=1, initial_balance=1000.0),
            Account(account_id=2, initial_balance=1000.0),
        ]
        bank = Phase1Bank(accounts, thread_delay=0.0)  # No delay for simple test

        bank.transfer(from_account_id=1, to_account_id=2, amount=100.0)

        assert bank.get_account(1).get_balance() == 900.0
        assert bank.get_account(2).get_balance() == 1100.0

    def test_transfer_updates_balances(self) -> None:
        """Test that transfer correctly updates both account balances."""
        accounts = [
            Account(account_id=1, initial_balance=500.0),
            Account(account_id=2, initial_balance=300.0),
        ]
        bank = Phase1Bank(accounts, thread_delay=0.0)

        initial_total = bank.get_total_balance()

        bank.transfer(from_account_id=1, to_account_id=2, amount=200.0)

        # Verify balances updated correctly
        assert bank.get_account(1).get_balance() == 300.0
        assert bank.get_account(2).get_balance() == 500.0

        # Verify total balance unchanged
        assert bank.get_total_balance() == initial_total

    def test_transfer_insufficient_funds(self) -> None:
        """Test transfer with insufficient funds."""
        accounts = [
            Account(account_id=1, initial_balance=100.0),
            Account(account_id=2, initial_balance=1000.0),
        ]
        bank = Phase1Bank(accounts, thread_delay=0.0)

        with pytest.raises(ValueError, match="Insufficient funds"):
            bank.transfer(from_account_id=1, to_account_id=2, amount=200.0)

    def test_transfer_same_account(self) -> None:
        """Test that transferring to same account raises error."""
        accounts = [Account(account_id=1, initial_balance=1000.0)]
        bank = Phase1Bank(accounts, thread_delay=0.0)

        with pytest.raises(ValueError, match="Cannot transfer to the same account"):
            bank.transfer(from_account_id=1, to_account_id=1, amount=100.0)

    def test_transfer_negative_amount(self) -> None:
        """Test that negative transfer amount raises error."""
        accounts = [
            Account(account_id=1, initial_balance=1000.0),
            Account(account_id=2, initial_balance=1000.0),
        ]
        bank = Phase1Bank(accounts, thread_delay=0.0)

        with pytest.raises(ValueError, match="Transfer amount must be positive"):
            bank.transfer(from_account_id=1, to_account_id=2, amount=-100.0)

    def test_sequential_transfers(self) -> None:
        """Test multiple sequential transfers."""
        accounts = [
            Account(account_id=1, initial_balance=1000.0),
            Account(account_id=2, initial_balance=1000.0),
            Account(account_id=3, initial_balance=1000.0),
        ]
        bank = Phase1Bank(accounts, thread_delay=0.0)

        bank.transfer(1, 2, 100.0)
        bank.transfer(2, 3, 200.0)
        bank.transfer(3, 1, 50.0)

        assert bank.get_account(1).get_balance() == 950.0
        assert bank.get_account(2).get_balance() == 900.0
        assert bank.get_account(3).get_balance() == 1150.0

    @pytest.mark.timeout(3)
    @pytest.mark.deadlock
    def test_opposing_transfers_may_deadlock(self) -> None:
        """Test that opposing transfers CAN cause deadlock in Phase 1.

        NOTE: This test may pass OR timeout depending on thread scheduling.
        The deadlock is not guaranteed to occur, but is possible.
        For a more reliable deadlock demonstration, run the full simulation.
        """
        pytest.skip(
            "Skipping deadlock test to avoid hanging during unit tests. "
            "Deadlock will be demonstrated in integration tests and simulation."
        )
