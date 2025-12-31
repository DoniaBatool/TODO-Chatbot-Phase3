"""
Main Entry Point for Todo Console Application

Run this module to start the application.
"""

from .cli import TodoCLI


def main() -> None:
    """Main entry point for the application."""
    try:
        cli = TodoCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue.\n")


if __name__ == "__main__":
    main()

