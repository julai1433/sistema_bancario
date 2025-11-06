"""Phase 1 Bank implementation - DEADLOCK PRONE (Naive approach)."""
import time
from typing import List

from src.banks.base_bank import Bank
from src.models.account import Account
from src.utils.logger import get_logger

logger = get_logger()


class Phase1Bank(Bank):
    """Phase 1 Bank implementation with deadlock vulnerability.

    This implementation acquires locks in ARRIVAL ORDER (not sorted),
    which can cause circular wait and deadlock when opposing transfers
    are executed concurrently.

    Example deadlock scenario:
        Thread-1: transfer(Account-1, Account-2, 100)
        Thread-2: transfer(Account-2, Account-1, 50)

        Thread-1 locks Account-1, waits for Account-2
        Thread-2 locks Account-2, waits for Account-1
        => DEADLOCK (circular wait)

    Coffman Conditions Satisfied:
        1. Mutual Exclusion: Locks are mutually exclusive
        2. Hold and Wait: Thread holds one lock while waiting for another
        3. No Preemption: Locks cannot be forcibly taken
        4. Circular Wait: Thread-1 waits for Thread-2's resource and vice versa
    """

    def __init__(self, accounts: List[Account], thread_delay: float = 0.01) -> None:
        """Initialize Phase1Bank.

        Args:
            accounts: List of Account objects
            thread_delay: Artificial delay between lock acquisitions (increases
                         deadlock probability for demonstration)
        """
        super().__init__(accounts)
        self.thread_delay = thread_delay

    def transfer(
        self, from_account_id: int, to_account_id: int, amount: float
    ) -> None:
        """Transfer money between accounts - DEADLOCK PRONE.

        Acquires locks in arrival order (origin first, then destination).
        This is the NAIVE approach that can cause deadlock.

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

        # DEADLOCK-PRONE: Acquire locks in arrival order (not sorted)
        # This allows circular wait condition
        logger.debug(f"Attempting to acquire lock on {from_account}")
        from_account.lock.acquire()
        try:
            logger.debug(f"✓ Acquired lock on {from_account}")

            # CRITICAL: Sleep between lock acquisitions
            # This increases the window for deadlock to occur
            if self.thread_delay > 0:
                logger.debug(
                    f"Sleeping {self.thread_delay}s (deadlock trigger window)"
                )
                time.sleep(self.thread_delay)

            logger.debug(f"Attempting to acquire lock on {to_account}")
            to_account.lock.acquire()
            try:
                logger.debug(f"✓ Acquired lock on {to_account}")

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
                to_account.lock.release()
                logger.debug(f"Released lock on {to_account}")

        finally:
            from_account.lock.release()
            logger.debug(f"Released lock on {from_account}")
