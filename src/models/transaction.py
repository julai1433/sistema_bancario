"""Transaction record dataclass."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """Record of a transfer between two accounts.

    This is an immutable record of a transaction attempt,
    used for logging and metrics collection.
    """

    from_account_id: int
    to_account_id: int
    amount: float
    timestamp: datetime
    success: bool
    thread_name: str
    error_message: Optional[str] = None

    def __str__(self) -> str:
        """Human-readable string representation."""
        status = "SUCCESS" if self.success else "FAILED"
        base = (
            f"[{self.timestamp.strftime('%H:%M:%S.%f')[:-3]}] "
            f"{self.thread_name}: "
            f"Account-{self.from_account_id} → Account-{self.to_account_id} "
            f"${self.amount:.2f} [{status}]"
        )
        if self.error_message:
            return f"{base} - {self.error_message}"
        return base
