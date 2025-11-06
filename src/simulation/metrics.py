"""Metrics collection for simulation runs."""
from dataclasses import dataclass
from datetime import datetime
from typing import List

from src.models.transaction import Transaction


@dataclass
class SimulationMetrics:
    """Metrics collected during a simulation run."""

    phase: str  # "Phase 1" or "Phase 2"
    total_transfers: int
    successful_transfers: int
    failed_transfers: int
    duration_seconds: float
    deadlocked: bool
    transactions: List[Transaction]

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_transfers == 0:
            return 0.0
        return (self.successful_transfers / self.total_transfers) * 100

    def summary(self) -> str:
        """Generate a summary string of the metrics."""
        lines = [
            f"\n{'='*60}",
            f"SIMULATION METRICS - {self.phase}",
            f"{'='*60}",
            f"Total Transfers:      {self.total_transfers}",
            f"Successful:           {self.successful_transfers}",
            f"Failed:               {self.failed_transfers}",
            f"Success Rate:         {self.success_rate:.1f}%",
            f"Duration:             {self.duration_seconds:.2f} seconds",
            f"Deadlocked:           {'YES' if self.deadlocked else 'NO'}",
            f"{'='*60}\n",
        ]
        return "\n".join(lines)
