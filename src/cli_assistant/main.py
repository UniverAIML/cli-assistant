"""
Головна точка входу для CLI Assistant.
Цей модуль обробляє аргументи командного рядка та запускає відповідний режим роботи.
"""

import sys
from typing import List, Optional

# Локальні імпорти компонентів нашого додатку
try:
    # Для звичайного запуску
    from .chat_assistant import ChatAssistant
    from .interactive_menu import InteractiveMenu
except ImportError:
    # Для PyInstaller та standalone запуску
    from cli_assistant.chat_assistant import ChatAssistant
    from cli_assistant.interactive_menu import InteractiveMenu


def main(args: Optional[List[str]] = None) -> None:
    """
    Головна точка входу для CLI Assistant додатку.

    Обробляє аргументи командного рядка та запускає відповідний режим:
    - Без аргументів: інтерактивне меню
    - menu/-m: інтерактивне меню
    - chat/-c: чат-асистент
    - help/-h: довідка

    Args:
        args: Аргументи командного рядка. Якщо None, використовує sys.argv[1:]
    """
    # Якщо аргументи не передані, беремо їх зі стандартного вводу
    if args is None:
        args = sys.argv[1:]

    # Якщо немає аргументів, запускаємо інтерактивне меню за замовчуванням
    if not args:
        try:
            # Створюємо та запускаємо інтерактивне меню
            menu = InteractiveMenu()
            menu.run()
            return
        except Exception as e:
            print(f"Error initializing interactive menu: {e}")
            return

    # Обробляємо команду меню
    if args[0] in ["menu", "--menu", "-m"]:
        try:
            # Створюємо та запускаємо інтерактивне меню
            menu = InteractiveMenu()
            menu.run()
            return
        except Exception as e:
            print(f"Error initializing interactive menu: {e}")
            return

    # Обробляємо команду чату
    if args[0] in ["chat", "--chat", "-c"]:
        try:
            # Створюємо та запускаємо чат-асистент
            assistant = ChatAssistant()
            assistant.chat_loop()
            return
        except RuntimeError as e:
            print(f"Error initializing chat assistant: {e}")
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            return

    # Обробляємо команду довідки
    if args[0] in ["--help", "-h", "help"]:
        print_help()
        return

    # TODO: Реалізувати обробку інших команд
    print(f"Command '{args[0]}' not recognized.")
    print("Use 'cli-assistant --help' for available commands.")


def print_help() -> None:
    """Виводить інформацію про довідку."""
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


# Точка входу для запуску як скрипт
if __name__ == "__main__":
    main()
