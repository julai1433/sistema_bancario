"""Main entry point for the banking system simulation."""
from src.ui.menu import InteractiveMenu


def main() -> None:
    """Run the interactive menu."""
    menu = InteractiveMenu()
    menu.run()


if __name__ == "__main__":
    main()
