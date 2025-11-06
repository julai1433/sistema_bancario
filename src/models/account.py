"""Account model with thread-safe operations."""
import threading
from typing import Any


class Account:
    """Thread-safe bank account with locking mechanism.

    Each account has its own lock for thread-safe operations.
    The lock is exposed publicly so banks can acquire multiple
    account locks for atomic multi-account transactions.
    """

    def __init__(self, account_id: int, initial_balance: float) -> None:
        """Initialize account with ID and initial balance.

        Args:
            account_id: Unique identifier for the account
            initial_balance: Starting balance for the account
        """
        self.id = account_id
        self._balance = initial_balance
        self.lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        """Deposit money into the account (thread-safe).

        Args:
            amount: Amount to deposit (must be positive)

        Raises:
            ValueError: If amount is negative
        """
        if amount < 0:
            raise ValueError("Deposit amount must be positive")

        with self.lock:
            self._balance += amount

    def withdraw(self, amount: float) -> None:
        """Withdraw money from the account (thread-safe).

        Args:
            amount: Amount to withdraw (must be positive)

        Raises:
            ValueError: If insufficient funds or negative amount
        """
        if amount < 0:
            raise ValueError("Withdrawal amount must be positive")

        with self.lock:
            if self._balance < amount:
                raise ValueError("Insufficient funds")
            self._balance -= amount

    def get_balance(self) -> float:
        """Get current account balance (thread-safe).

        Returns:
            Current balance
        """
        with self.lock:
            return self._balance

    def __repr__(self) -> str:
        """String representation of account."""
        return f"Account(id={self.id}, balance={self._balance})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Account-{self.id} (${self._balance:.2f})"
