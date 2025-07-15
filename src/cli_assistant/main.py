"""Main entry point for CLI Assistant."""

import sys
from typing import List, Optional

try:
    from .chat_assistant import ChatAssistant
except ImportError:
    from chat_assistant import ChatAssistant


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for the CLI Assistant application.
    
    Args:
        args: Command line arguments. If None, uses sys.argv[1:]
    """
    if args is None:
        args = sys.argv[1:]
    
    print("CLI Assistant v0.1.0")
    print("A CLI tool for development workflows with AI chat capabilities")
    
    # If no arguments or --chat argument, start chat mode
    if not args or (args and args[0] in ["chat", "--chat", "-c"]):
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
  chat, -c, --chat    Start interactive chat mode (default)
  help, -h, --help    Show this help message

Chat Mode:
  The assistant uses spaCy for natural language processing.
  You can ask questions, request text analysis, or just chat!
  
  Available chat commands:
  - Type 'help' for chat-specific help
  - Type 'exit' or 'quit' to end the conversation
  - Press Ctrl+C to force quit

Examples:
  cli-assistant                 # Start chat mode
  cli-assistant chat            # Start chat mode explicitly
  cli-assistant --help          # Show this help
    """
    print(help_text)


if __name__ == "__main__":
    main()
