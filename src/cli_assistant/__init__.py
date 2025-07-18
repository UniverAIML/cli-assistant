"""CLI Assistant - A CLI tool for development workflows."""

__version__ = "0.1.0"
__author__ = "Univer AI ML"

from .chat_assistant import ChatAssistant

# Імпорти для зручного використання
from .operations_manager import OperationsManager

__all__ = ["OperationsManager", "ChatAssistant"]
