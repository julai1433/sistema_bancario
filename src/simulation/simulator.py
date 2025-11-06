"""Transaction simulator for concurrent transfers."""
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime
from typing import Any, Dict, List, Type

from src.banks.base_bank import Bank
from src.models.account import Account
from src.models.transaction import Transaction
from src.simulation.metrics import SimulationMetrics
from src.utils.logger import get_logger

logger = get_logger()


class TransactionSimulator:
    """Simulates concurrent bank transfers."""

    def __init__(
        self,
        bank_class: Type[Bank],
        accounts_data: List[Dict[str, Any]],
        transfers_data: List[Dict[str, Any]],
        thread_delay: float = 0.01,
        timeout_seconds: float = 10.0,
    ) -> None:
        """Initialize the simulator.

        Args:
            bank_class: Bank class to use (Phase1Bank or Phase2Bank)
            accounts_data: List of account configurations
            transfers_data: List of transfer configurations
            thread_delay: Delay for Phase1Bank (deadlock trigger)
            timeout_seconds: Max time to wait before declaring deadlock
        """
        self.bank_class = bank_class
        self.accounts_data = accounts_data
        self.transfers_data = transfers_data
        self.thread_delay = thread_delay
        self.timeout_seconds = timeout_seconds
        self.transactions: List[Transaction] = []
        self.transactions_lock = threading.Lock()

    def run(self) -> SimulationMetrics:
        """Run the simulation.

        Returns:
            SimulationMetrics with results
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting simulation with {self.bank_class.__name__}")
        logger.info(f"Accounts: {len(self.accounts_data)}")
        logger.info(f"Transfers: {len(self.transfers_data)}")
        logger.info(f"Timeout: {self.timeout_seconds}s")
        logger.info(f"{'='*60}\n")

        # Create accounts
        accounts = [
            Account(
                account_id=acc["id"],
                initial_balance=acc["initial_balance"],
            )
            for acc in self.accounts_data
        ]

        # Create bank (pass thread_delay for Phase1Bank)
        if hasattr(self.bank_class, "__init__") and "thread_delay" in str(
            self.bank_class.__init__.__code__.co_varnames
        ):
            bank = self.bank_class(accounts, thread_delay=self.thread_delay)
        else:
            bank = self.bank_class(accounts)

        initial_balance = bank.get_total_balance()
        logger.info(f"Initial total balance: ${initial_balance:.2f}\n")

        # Reset transactions
        self.transactions = []

        # Run transfers concurrently
        start_time = time.time()
        deadlocked = False

        try:
            self._execute_transfers_concurrently(bank)
        except FuturesTimeoutError:
            deadlocked = True
            logger.error(
                f"\n{'!'*60}\n"
                f"DEADLOCK DETECTED - Simulation timed out after "
                f"{self.timeout_seconds}s\n"
                f"{'!'*60}\n"
            )

        duration = time.time() - start_time

        # Calculate metrics
        successful = sum(1 for t in self.transactions if t.success)
        failed = sum(1 for t in self.transactions if not t.success)

        final_balance = bank.get_total_balance()
        logger.info(f"\nFinal total balance: ${final_balance:.2f}")

        # Verify balance conservation
        if abs(initial_balance - final_balance) > 0.01:
            logger.error(
                f"WARNING: Balance not conserved! "
                f"Difference: ${abs(initial_balance - final_balance):.2f}"
            )

        metrics = SimulationMetrics(
            phase=self.bank_class.__name__,
            total_transfers=len(self.transfers_data),
            successful_transfers=successful,
            failed_transfers=failed,
            duration_seconds=duration,
            deadlocked=deadlocked,
            transactions=self.transactions,
        )

        logger.info(metrics.summary())

        return metrics

    def _execute_transfers_concurrently(self, bank: Bank) -> None:
        """Execute all transfers concurrently.

        Args:
            bank: Bank instance to use

        Raises:
            TimeoutError: If execution exceeds timeout (indicates deadlock)
        """

        def transfer_task(transfer_data: Dict[str, Any]) -> None:
            """Execute a single transfer and record it."""
            from_id = transfer_data["from"]
            to_id = transfer_data["to"]
            amount = transfer_data["amount"]
            thread_name = threading.current_thread().name

            timestamp = datetime.now()
            success = False
            error_message = None

            try:
                bank.transfer(from_id, to_id, amount)
                success = True
            except Exception as e:
                error_message = str(e)
                logger.error(f"Transfer failed: {e}")

            # Record transaction
            transaction = Transaction(
                from_account_id=from_id,
                to_account_id=to_id,
                amount=amount,
                timestamp=timestamp,
                success=success,
                thread_name=thread_name,
                error_message=error_message,
            )

            with self.transactions_lock:
                self.transactions.append(transaction)

        # Execute transfers in parallel
        max_workers = min(len(self.transfers_data), 20)  # Limit concurrency
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(transfer_task, transfer)
                for transfer in self.transfers_data
            ]

            # Wait for all to complete or timeout
            for future in futures:
                future.result(timeout=self.timeout_seconds)
