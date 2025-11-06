"""Unit tests for Phase2Bank (deadlock-free implementation)."""
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from src.banks.phase2_bank import Phase2Bank
from src.models.account import Account


class TestPhase2Bank:
    """Test cases for Phase2Bank class."""

    def test_simple_transfer(self) -> None:
        """Test a simple transfer between two accounts."""
        accounts = [
            Account(account_id=1, initial_balance=1000.0),
            Account(account_id=2, initial_balance=1000.0),
        ]
        bank = Phase2Bank(accounts)

        bank.transfer(from_account_id=1, to_account_id=2, amount=100.0)

        assert bank.get_account(1).get_balance() == 900.0
        assert bank.get_account(2).get_balance() == 1100.0

    def test_transfer_updates_balances(self) -> None:
        """Test that transfer correctly updates both account balances."""
        accounts = [
            Account(account_id=1, initial_balance=500.0),
            Account(account_id=2, initial_balance=300.0),
        ]
        bank = Phase2Bank(accounts)

        initial_total = bank.get_total_balance()

        bank.transfer(from_account_id=1, to_account_id=2, amount=200.0)

        # Verify balances updated correctly
        assert bank.get_account(1).get_balance() == 300.0
        assert bank.get_account(2).get_balance() == 500.0

        # Verify total balance unchanged
        assert bank.get_total_balance() == initial_total

    def test_opposing_transfers_no_deadlock(self) -> None:
        """Test that opposing transfers complete without deadlock.

        This should complete successfully, unlike Phase 1.
        """
        accounts = [
            Account(account_id=1, initial_balance=1000.0),
            Account(account_id=2, initial_balance=1000.0),
        ]
        bank = Phase2Bank(accounts)

        def transfer1() -> None:
            bank.transfer(1, 2, 100.0)

        def transfer2() -> None:
            bank.transfer(2, 1, 50.0)

        # Run opposing transfers concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(transfer1)
            future2 = executor.submit(transfer2)

            # Both should complete without deadlock
            future1.result(timeout=2)
            future2.result(timeout=2)

        # Final balances should reflect both transfers
        # Account 1: 1000 - 100 + 50 = 950
        # Account 2: 1000 + 100 - 50 = 1050
        assert bank.get_account(1).get_balance() == 950.0
        assert bank.get_account(2).get_balance() == 1050.0

    def test_lock_acquisition_sorted_order(self) -> None:
        """Test that locks are always acquired in sorted order by account ID."""
        accounts = [
            Account(account_id=5, initial_balance=1000.0),
            Account(account_id=2, initial_balance=1000.0),
        ]
        bank = Phase2Bank(accounts)

        # Transfer from higher ID to lower ID
        # Should still lock in order: 2 then 5
        bank.transfer(from_account_id=5, to_account_id=2, amount=100.0)

        assert bank.get_account(5).get_balance() == 900.0
        assert bank.get_account(2).get_balance() == 1100.0

        # Transfer from lower ID to higher ID
        # Should lock in order: 2 then 5
        bank.transfer(from_account_id=2, to_account_id=5, amount=50.0)

        assert bank.get_account(2).get_balance() == 1050.0
        assert bank.get_account(5).get_balance() == 950.0

    def test_many_concurrent_transfers(self) -> None:
        """Test many concurrent opposing transfers complete successfully."""
        accounts = [
            Account(account_id=1, initial_balance=10000.0),
            Account(account_id=2, initial_balance=10000.0),
            Account(account_id=3, initial_balance=10000.0),
            Account(account_id=4, initial_balance=10000.0),
        ]
        bank = Phase2Bank(accounts)

        initial_total = bank.get_total_balance()

        # Create many opposing transfers
        transfers = [
            (1, 2, 10.0),
            (2, 1, 15.0),
            (3, 4, 20.0),
            (4, 3, 25.0),
            (1, 3, 5.0),
            (3, 1, 8.0),
            (2, 4, 12.0),
            (4, 2, 18.0),
        ] * 10  # Repeat 10 times = 80 transfers

        def do_transfer(from_id: int, to_id: int, amount: float) -> None:
            bank.transfer(from_id, to_id, amount)

        # Execute all transfers concurrently
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(do_transfer, from_id, to_id, amount)
                for from_id, to_id, amount in transfers
            ]

            # All should complete without deadlock
            for future in as_completed(futures, timeout=5):
                future.result()

        # Total balance should remain unchanged
        assert bank.get_total_balance() == initial_total

    def test_get_ordered_accounts(self) -> None:
        """Test the _get_ordered_accounts helper method."""
        account1 = Account(account_id=5, initial_balance=1000.0)
        account2 = Account(account_id=2, initial_balance=1000.0)

        # Should return in order: (2, 5)
        first, second = Phase2Bank._get_ordered_accounts(account1, account2)
        assert first.id == 2
        assert second.id == 5

        # Reverse order should return same result
        first, second = Phase2Bank._get_ordered_accounts(account2, account1)
        assert first.id == 2
        assert second.id == 5
