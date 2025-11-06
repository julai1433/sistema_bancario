"""Logging configuration with colored console output and file logging."""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console."""

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.BLUE,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    SYMBOLS = {
        "DEBUG": "🔍",
        "INFO": "🔵",
        "WARNING": "🟡",
        "ERROR": "🔴",
        "CRITICAL": "🔥",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and symbols."""
        color = self.COLORS.get(record.levelname, "")
        symbol = self.SYMBOLS.get(record.levelname, "")

        # Add color to the level name
        record.levelname = f"{color}{symbol} {record.levelname}{Style.RESET_ALL}"

        # Format the message
        formatted = super().format(record)

        return formatted


def setup_logger(
    name: str = "sistema_bancario",
    log_file: Optional[Path] = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    verbose: bool = True,
) -> logging.Logger:
    """Set up logger with console and file handlers.

    Args:
        name: Logger name
        log_file: Path to log file (if None, creates timestamped file in logs/)
        console_level: Logging level for console output
        file_level: Logging level for file output
        verbose: If True, use DEBUG level for console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture everything

    # Clear existing handlers
    logger.handlers.clear()

    # Determine console level based on verbose flag
    if verbose:
        console_level = logging.DEBUG

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = ColoredFormatter(
        fmt="[%(threadName)-12s] %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler without colors
    if log_file is None:
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"simulation_{timestamp}.log"

    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.info(f"Logger initialized. Log file: {log_file}")

    return logger


def get_logger(name: str = "sistema_bancario") -> logging.Logger:
    """Get existing logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
