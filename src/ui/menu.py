"""Interactive menu for the banking system simulation."""
import sys
from pathlib import Path
from typing import Any, Dict

from src.banks.phase1_bank import Phase1Bank
from src.banks.phase2_bank import Phase2Bank
from src.simulation.simulator import TransactionSimulator
from src.ui.colors import Colors, colored, error, header, info, success
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger


class InteractiveMenu:
    """Interactive menu for running simulations."""

    def __init__(self) -> None:
        """Initialize the menu."""
        self.config: Dict[str, Any] = {}
        self.logger_initialized = False

    def run(self) -> None:
        """Run the interactive menu loop."""
        self.show_welcome()

        while True:
            self.show_menu()
            choice = input(colored("\nEnter your choice: ", Colors.MENU)).strip()

            if choice == "1":
                self.run_phase1()
            elif choice == "2":
                self.run_phase2()
            elif choice == "3":
                self.run_both_phases()
            elif choice == "4":
                self.show_config()
            elif choice == "5":
                self.load_config()
            elif choice == "6":
                print(success("\nGoodbye! 👋\n"))
                sys.exit(0)
            else:
                print(error("\n❌ Invalid choice. Please try again.\n"))

    def show_welcome(self) -> None:
        """Display welcome message."""
        print(header("\n" + "=" * 60))
        print(header("    SISTEMA BANCARIO - DEADLOCK DEMONSTRATION"))
        print(header("    Concurrent Banking System Simulation"))
        print(header("=" * 60))
        print(
            info(
                "\nThis simulation demonstrates deadlock in concurrent systems:\n"
                "  • Phase 1: Deadlock-prone (naive lock acquisition)\n"
                "  • Phase 2: Deadlock-free (ordered lock acquisition)\n"
            )
        )

    def show_menu(self) -> None:
        """Display main menu."""
        print(header("\n" + "-" * 60))
        print(colored("MAIN MENU", Colors.MENU))
        print(header("-" * 60))
        print(colored("1.", Colors.MENU) + " Run Phase 1 (Deadlock-Prone)")
        print(colored("2.", Colors.MENU) + " Run Phase 2 (Deadlock-Free)")
        print(colored("3.", Colors.MENU) + " Run Both Phases (Comparison)")
        print(colored("4.", Colors.MENU) + " Show Current Configuration")
        print(colored("5.", Colors.MENU) + " Load Configuration File")
        print(colored("6.", Colors.MENU) + " Exit")
        print(header("-" * 60))

    def load_config(self) -> None:
        """Load configuration from file."""
        print(info("\nLoading default configuration..."))
        try:
            self.config = ConfigLoader.load_default()
            print(success("✓ Configuration loaded successfully!"))
            print(
                info(
                    f"  • {len(self.config['accounts'])} accounts\n"
                    f"  • {len(self.config['transfers'])} transfers\n"
                )
            )
        except Exception as e:
            print(error(f"❌ Failed to load configuration: {e}"))

    def show_config(self) -> None:
        """Display current configuration."""
        if not self.config:
            self.load_config()

        print(header("\n" + "=" * 60))
        print(header("CURRENT CONFIGURATION"))
        print(header("=" * 60))

        print(info(f"\nAccounts ({len(self.config['accounts'])}):"))
        for acc in self.config["accounts"][:5]:  # Show first 5
            print(f"  • Account-{acc['id']}: ${acc['initial_balance']:.2f}")
        if len(self.config["accounts"]) > 5:
            print(f"  ... and {len(self.config['accounts']) - 5} more")

        print(info(f"\nTransfers ({len(self.config['transfers'])}):"))
        for i, transfer in enumerate(self.config["transfers"][:5], 1):
            print(
                f"  {i}. Account-{transfer['from']} → "
                f"Account-{transfer['to']}: ${transfer['amount']:.2f}"
            )
        if len(self.config["transfers"]) > 5:
            print(f"  ... and {len(self.config['transfers']) - 5} more")

        print(info("\nSimulation Settings:"))
        sim = self.config["simulation"]
        print(f"  • Thread Delay: {sim['thread_delay_seconds']}s")
        print(f"  • Deadlock Timeout: {sim['deadlock_timeout_seconds']}s")
        print(f"  • Verbose Logging: {sim['verbose_logging']}")
        print()

    def ensure_config_and_logger(self) -> None:
        """Ensure configuration is loaded and logger is initialized."""
        if not self.config:
            self.load_config()

        if not self.logger_initialized:
            setup_logger(verbose=self.config["simulation"]["verbose_logging"])
            self.logger_initialized = True

    def run_phase1(self) -> None:
        """Run Phase 1 simulation."""
        self.ensure_config_and_logger()

        print(header("\n" + "=" * 60))
        print(header("RUNNING PHASE 1 - DEADLOCK-PRONE"))
        print(header("=" * 60))
        print(
            info(
                "\nThis may deadlock and timeout. Press Ctrl+C to interrupt.\n"
            )
        )

        try:
            simulator = TransactionSimulator(
                bank_class=Phase1Bank,
                accounts_data=self.config["accounts"],
                transfers_data=self.config["transfers"],
                thread_delay=self.config["simulation"]["thread_delay_seconds"],
                timeout_seconds=self.config["simulation"][
                    "deadlock_timeout_seconds"
                ],
            )

            metrics = simulator.run()

            if metrics.deadlocked:
                print(error("\n❌ DEADLOCK OCCURRED (as expected in Phase 1)"))
            else:
                print(success("\n✓ Simulation completed (no deadlock this time)"))

        except KeyboardInterrupt:
            print(error("\n\n❌ Simulation interrupted by user.\n"))

    def run_phase2(self) -> None:
        """Run Phase 2 simulation."""
        self.ensure_config_and_logger()

        print(header("\n" + "=" * 60))
        print(header("RUNNING PHASE 2 - DEADLOCK-FREE"))
        print(header("=" * 60))
        print(info("\nThis should complete without deadlock.\n"))

        try:
            simulator = TransactionSimulator(
                bank_class=Phase2Bank,
                accounts_data=self.config["accounts"],
                transfers_data=self.config["transfers"],
                timeout_seconds=self.config["simulation"][
                    "deadlock_timeout_seconds"
                ],
            )

            metrics = simulator.run()

            if metrics.deadlocked:
                print(
                    error(
                        "\n❌ UNEXPECTED: Phase 2 deadlocked "
                        "(this should not happen!)"
                    )
                )
            else:
                print(success("\n✓ Simulation completed successfully!"))

        except KeyboardInterrupt:
            print(error("\n\n❌ Simulation interrupted by user.\n"))

    def run_both_phases(self) -> None:
        """Run both phases for comparison."""
        self.ensure_config_and_logger()

        print(header("\n" + "=" * 60))
        print(header("RUNNING BOTH PHASES - COMPARISON"))
        print(header("=" * 60))

        input(colored("\nPress Enter to start Phase 1...", Colors.MENU))
        self.run_phase1()

        input(colored("\nPress Enter to start Phase 2...", Colors.MENU))
        self.run_phase2()

        print(header("\n" + "=" * 60))
        print(header("COMPARISON COMPLETE"))
        print(header("=" * 60))
        print(
            info(
                "\nPhase 1 should demonstrate deadlock.\n"
                "Phase 2 should complete successfully.\n"
            )
        )
