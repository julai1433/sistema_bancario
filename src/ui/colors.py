"""Color constants and formatting utilities."""
from colorama import Fore, Style


class Colors:
    """Color constants for console output."""

    # Basic colors
    BLUE = Fore.BLUE
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    WHITE = Fore.WHITE

    # Styles
    BRIGHT = Style.BRIGHT
    DIM = Style.DIM
    RESET = Style.RESET_ALL

    # Semantic colors
    INFO = BLUE
    SUCCESS = GREEN
    WARNING = YELLOW
    ERROR = RED
    HEADER = CYAN + BRIGHT
    MENU = MAGENTA + BRIGHT


def colored(text: str, color: str) -> str:
    """Return colored text.

    Args:
        text: Text to color
        color: Color code from Colors class

    Returns:
        Colored text string
    """
    return f"{color}{text}{Colors.RESET}"


def header(text: str) -> str:
    """Format text as header."""
    return colored(text, Colors.HEADER)


def success(text: str) -> str:
    """Format text as success message."""
    return colored(text, Colors.SUCCESS)


def error(text: str) -> str:
    """Format text as error message."""
    return colored(text, Colors.ERROR)


def warning(text: str) -> str:
    """Format text as warning message."""
    return colored(text, Colors.WARNING)


def info(text: str) -> str:
    """Format text as info message."""
    return colored(text, Colors.INFO)
