"""Main entry point for CLI Assistant."""

import sys
from typing import List, Optional

# Initialize colorama for cross-platform colored output
from colorama import init

init(autoreset=True)

from .chat_assistant import ChatAssistant
from .interactive_menu import InteractiveMenu


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for the CLI Assistant application.

    Args:
        args: Command line arguments. If None, uses sys.argv[1:]
    """
    if args is None:
        args = sys.argv[1:]

    # If no arguments, start interactive menu by default
    if not args:
        try:
            menu = InteractiveMenu()
            menu.run()
            return
        except Exception as e:
            print(f"Error initializing interactive menu: {e}")
            return

    # Handle menu command
    if args[0] in ["menu", "--menu", "-m"]:
        try:
            menu = InteractiveMenu()
            menu.run()
            return
        except Exception as e:
            print(f"Error initializing interactive menu: {e}")
            return

    # Handle chat command
    if args[0] in ["chat", "--chat", "-c"]:
        try:
            assistant = ChatAssistant()
            assistant.chat_loop()
            return
        except RuntimeError as e:
            print(f"Error initializing chat assistant: {e}")
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            return

    # Handle help command
    if args[0] in ["--help", "-h", "help"]:
        print_help()
        return

    # TODO: Implement other command handling
    print(f"Command '{args[0]}' not recognized.")
    print("Use 'cli-assistant --help' for available commands.")


def print_help() -> None:
    """Print help information."""
    help_text = """
Usage: cli-assistant [command] [options]

Commands:
  (no command)     Start interactive menu (default)
  menu, -m         Start interactive menu
  chat, -c         Start chat assistant
  help, -h         Show this help message

Examples:
  cli-assistant           # Start interactive menu
  cli-assistant menu      # Start interactive menu
  cli-assistant chat      # Start chat assistant
  cli-assistant --help    # Show help

The interactive menu provides a beautiful interface for managing
contacts and notes with full AI assistant integration.
"""
    print(help_text)


if __name__ == "__main__":
    main()
