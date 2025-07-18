"""CLI Assistant - A CLI tool for development workflows."""

__version__ = "0.1.0"
__author__ = "Univer AI ML"

# Імпорти для зручного використання
from .operations_manager import OperationsManager
from .chat_assistant import ChatAssistant

__all__ = ["OperationsManager", "ChatAssistant"]
