"""Unit tests for Account class."""
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.models.account import Account


class TestAccount:
    """Test cases for the Account class."""

    def test_account_creation(self) -> None:
        """Test creating an account with initial balance."""
        account = Account(account_id=1, initial_balance=1000.0)
        assert account.id == 1
        assert account.get_balance() == 1000.0

    def test_deposit(self) -> None:
        """Test depositing money into an account."""
        account = Account(account_id=1, initial_balance=1000.0)
        account.deposit(500.0)
        assert account.get_balance() == 1500.0

    def test_withdraw(self) -> None:
        """Test withdrawing money from an account."""
        account = Account(account_id=1, initial_balance=1000.0)
        account.withdraw(300.0)
        assert account.get_balance() == 700.0

    def test_withdraw_insufficient_funds(self) -> None:
        """Test withdrawal with insufficient funds raises error."""
        account = Account(account_id=1, initial_balance=1000.0)
        with pytest.raises(ValueError, match="Insufficient funds"):
            account.withdraw(1500.0)

    def test_concurrent_deposits(self) -> None:
        """Test multiple threads depositing concurrently."""
        account = Account(account_id=1, initial_balance=0.0)
        num_threads = 100
        amount_per_thread = 10.0

        def deposit_task() -> None:
            account.deposit(amount_per_thread)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(deposit_task) for _ in range(num_threads)]
            for future in futures:
                future.result()

        # Total should be num_threads * amount_per_thread
        expected_balance = num_threads * amount_per_thread
        assert account.get_balance() == expected_balance

    def test_concurrent_withdrawals(self) -> None:
        """Test multiple threads withdrawing concurrently."""
        num_threads = 100
        amount_per_thread = 10.0
        initial_balance = num_threads * amount_per_thread

        account = Account(account_id=1, initial_balance=initial_balance)

        def withdraw_task() -> None:
            account.withdraw(amount_per_thread)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(withdraw_task) for _ in range(num_threads)]
            for future in futures:
                future.result()

        # Balance should be zero after all withdrawals
        assert account.get_balance() == 0.0

    def test_get_balance(self) -> None:
        """Test reading account balance."""
        account = Account(account_id=42, initial_balance=2500.0)
        assert account.get_balance() == 2500.0

    def test_account_has_lock(self) -> None:
        """Test that account has a lock attribute for external locking."""
        account = Account(account_id=1, initial_balance=1000.0)
        assert hasattr(account, "lock")
        assert isinstance(account.lock, threading.Lock)
