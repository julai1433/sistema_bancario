"""Abstract base class for bank implementations."""
from abc import ABC, abstractmethod
from typing import Dict, List

from src.models.account import Account


class Bank(ABC):
    """Abstract base class for bank implementations.

    Subclasses must implement the transfer method with their
    specific lock acquisition strategy.
    """

    def __init__(self, accounts: List[Account]) -> None:
        """Initialize bank with accounts.

        Args:
            accounts: List of Account objects
        """
        self.accounts: Dict[int, Account] = {acc.id: acc for acc in accounts}

    def get_account(self, account_id: int) -> Account:
        """Get account by ID.

        Args:
            account_id: Account identifier

        Returns:
            Account object

        Raises:
            KeyError: If account doesn't exist
        """
        if account_id not in self.accounts:
            raise KeyError(f"Account {account_id} not found")
        return self.accounts[account_id]

    def get_total_balance(self) -> float:
        """Calculate total balance across all accounts.

        Returns:
            Sum of all account balances
        """
        return sum(account.get_balance() for account in self.accounts.values())

    @abstractmethod
    def transfer(
        self, from_account_id: int, to_account_id: int, amount: float
    ) -> None:
        """Transfer money between accounts.

        This method must be implemented by subclasses with their
        specific lock acquisition strategy.

        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID
            amount: Amount to transfer

        Raises:
            ValueError: If transfer is invalid
            KeyError: If account doesn't exist
        """
        pass

    def __repr__(self) -> str:
        """String representation of bank."""
        return f"{self.__class__.__name__}({len(self.accounts)} accounts)"
