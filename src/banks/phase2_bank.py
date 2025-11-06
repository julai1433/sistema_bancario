"""Phase 2 Bank implementation - DEADLOCK FREE (Ordered locking)."""
from typing import List, Tuple

from src.banks.base_bank import Bank
from src.models.account import Account
from src.utils.logger import get_logger

logger = get_logger()


class Phase2Bank(Bank):
    """Phase 2 Bank implementation with deadlock prevention.

    This implementation PREVENTS DEADLOCK by acquiring locks in a
    CONSISTENT GLOBAL ORDER (sorted by account ID), which breaks
    the circular wait condition.

    Example with same scenario as Phase 1:
        Thread-1: transfer(Account-1, Account-2, 100)
        Thread-2: transfer(Account-2, Account-1, 50)

        Both threads will lock in order: Account-1 first, then Account-2
        Thread-1 locks Account-1, locks Account-2, completes
        Thread-2 waits for Account-1, then locks Account-2, completes
        => NO DEADLOCK (no circular wait)

    Coffman Condition Broken:
        4. Circular Wait: PREVENTED by global ordering
           - All threads acquire locks in the same order (ascending ID)
           - No thread can wait in a cycle
           - Without circular wait, deadlock is impossible

    Other conditions still hold but are insufficient:
        1. Mutual Exclusion: Still present (locks are exclusive)
        2. Hold and Wait: Still present (thread holds locks while waiting)
        3. No Preemption: Still present (locks not forcibly taken)
    """

    def __init__(self, accounts: List[Account]) -> None:
        """Initialize Phase2Bank.

        Args:
            accounts: List of Account objects
        """
        super().__init__(accounts)

    def transfer(
        self, from_account_id: int, to_account_id: int, amount: float
    ) -> None:
        """Transfer money between accounts - DEADLOCK FREE.

        Acquires locks in SORTED ORDER by account ID (global ordering).
        This prevents circular wait and guarantees no deadlock.

        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID
            amount: Amount to transfer

        Raises:
            ValueError: If transfer is invalid (same account, insufficient funds)
            KeyError: If account doesn't exist
        """
        if from_account_id == to_account_id:
            raise ValueError("Cannot transfer to the same account")

        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        # Get accounts
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)

        logger.debug(
            f"Starting transfer: {from_account} → {to_account} (${amount:.2f})"
        )

        # DEADLOCK-FREE: Sort accounts by ID to ensure global ordering
        # This prevents circular wait condition
        first_account, second_account = self._get_ordered_accounts(
            from_account, to_account
        )

        logger.debug(
            f"Lock acquisition order (sorted): {first_account} then {second_account}"
        )

        # Acquire locks in sorted order
        logger.debug(f"Attempting to acquire lock on {first_account}")
        first_account.lock.acquire()
        try:
            logger.debug(f"✓ Acquired lock on {first_account}")

            logger.debug(f"Attempting to acquire lock on {second_account}")
            second_account.lock.acquire()
            try:
                logger.debug(f"✓ Acquired lock on {second_account}")

                # Perform transfer (critical section)
                current_balance = from_account._balance
                if current_balance < amount:
                    raise ValueError(
                        f"Insufficient funds in {from_account} "
                        f"(has ${current_balance:.2f}, needs ${amount:.2f})"
                    )

                # Execute transfer
                from_account._balance -= amount
                to_account._balance += amount

                logger.info(
                    f"✓ Transfer completed: {from_account} → {to_account} "
                    f"(${amount:.2f})"
                )

            finally:
                second_account.lock.release()
                logger.debug(f"Released lock on {second_account}")

        finally:
            first_account.lock.release()
            logger.debug(f"Released lock on {first_account}")

    @staticmethod
    def _get_ordered_accounts(
        account1: Account, account2: Account
    ) -> Tuple[Account, Account]:
        """Get accounts in sorted order by ID.

        This ensures a consistent global ordering for lock acquisition,
        which prevents circular wait.

        Args:
            account1: First account
            account2: Second account

        Returns:
            Tuple of (lower_id_account, higher_id_account)
        """
        if account1.id < account2.id:
            return (account1, account2)
        else:
            return (account2, account1)
