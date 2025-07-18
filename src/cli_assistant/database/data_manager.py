"""
Модуль управління даними для збереження AddressBook та NotesManager.

Цей модуль забезпечує функціональність для збереження та завантаження даних
AddressBook та NotesManager з використанням JSON серіалізації.

Основні функції:
- Серіалізація об'єктів в JSON формат
- Десеріалізація JSON в об'єкти
- Обробка помилок файлових операцій
- Підтримка legacy форматів
- Резервне копіювання даних
"""

import json
from pathlib import Path
from .contact_models import AddressBook
from .note_models import NotesManager
from typing import Dict, Any, Tuple, Optional


class DataManager:
    """
    Управляє збереженням даних AddressBook та NotesManager з використанням JSON серіалізації.

    Цей клас обробляє збереження та завантаження екземплярів AddressBook та NotesManager
    на/з диску, забезпечуючи чітке розділення обов'язків між зберіганням даних та бізнес-логікою.

    Функції:
    - Збереження контактів у JSON файл
    - Завантаження контактів з JSON файлу
    - Збереження нотаток у JSON файл
    - Завантаження нотаток з JSON файлу
    - Обробка помилок та винятків
    - Підтримка legacy форматів файлів
    """

    def __init__(
        self,
        contacts_filename: str = "addressbook.json",
        notes_filename: Optional[str] = None,
    ) -> None:
        """
        Ініціалізує DataManager з вказаними іменами файлів.

        Args:
            contacts_filename (str): Ім'я файлу для збереження контактів. За замовчуванням "addressbook.json"
            notes_filename (Optional[str]): Ім'я файлу для збереження нотаток.
                                          Якщо None, генерується на основі contacts_filename
        """
        self.contacts_filename = contacts_filename

        # Обробляємо legacy формат з одним файлом
        if notes_filename is None:
            if contacts_filename.endswith(".json"):
                # Якщо файл контактів addressbook.json, то нотатки addressbook_notes.json
                self.notes_filename = contacts_filename.replace(".json", "_notes.json")
            else:
                # Якщо файл без розширення, додаємо _notes.json
                self.notes_filename = contacts_filename + "_notes.json"
        else:
            self.notes_filename = notes_filename

        # Створюємо Path об'єкти для зручної роботи з файлами
        self.contacts_filepath = Path(self.contacts_filename)
        self.notes_filepath = Path(self.notes_filename)

    def save_contacts(self, address_book: AddressBook) -> bool:
        """
        Save AddressBook data to file using JSON serialization.

        Args:
            address_book (AddressBook): The AddressBook instance to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        return address_book.save_to_file(str(self.contacts_filepath))

    def save_notes(self, notes_manager: NotesManager) -> bool:
        """
        Save NotesManager data to file using JSON serialization.

        Args:
            notes_manager (NotesManager): The NotesManager instance to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        return notes_manager.save_to_file(str(self.notes_filepath))

    def save_data(
        self, address_book: AddressBook, notes_manager: Optional[NotesManager] = None
    ) -> bool:
        """
        Save both AddressBook and NotesManager data.

        Args:
            address_book (AddressBook): The AddressBook instance to save
            notes_manager (Optional[NotesManager]): The NotesManager instance to save

        Returns:
            bool: True if all saves were successful, False otherwise
        """
        contacts_saved = self.save_contacts(address_book)
        notes_saved = True

        if notes_manager is not None:
            notes_saved = self.save_notes(notes_manager)

        return contacts_saved and notes_saved

    def load_contacts(self) -> AddressBook:
        """
        Load AddressBook data from file using JSON deserialization.

        Returns:
            AddressBook: Loaded AddressBook instance, or new empty one if file not found
        """
        return AddressBook.load_from_file(str(self.contacts_filepath))

    def load_notes(self) -> NotesManager:
        """
        Load NotesManager data from file using JSON deserialization.

        Returns:
            NotesManager: Loaded NotesManager instance, or new empty one if file not found
        """
        return NotesManager.load_from_file(str(self.notes_filepath))

    def load_data(self) -> Tuple[AddressBook, NotesManager]:
        """
        Load both AddressBook and NotesManager data from files.

        Returns:
            Tuple[AddressBook, NotesManager]: Loaded instances or new empty ones if files not found
        """
        address_book = self.load_contacts()
        notes_manager = self.load_notes()
        return address_book, notes_manager

    def contacts_file_exists(self) -> bool:
        """
        Check if the contacts data file exists.

        Returns:
            bool: True if file exists, False otherwise
        """
        return self.contacts_filepath.exists()

    def notes_file_exists(self) -> bool:
        """
        Check if the notes data file exists.

        Returns:
            bool: True if file exists, False otherwise
        """
        return self.notes_filepath.exists()

    def file_exists(self) -> bool:
        """
        Check if any data files exist.

        Returns:
            bool: True if any file exists, False otherwise
        """
        return self.contacts_file_exists() or self.notes_file_exists()

    def get_contacts_file_size(self) -> int:
        """
        Get size of the contacts data file in bytes.

        Returns:
            int: File size in bytes, or 0 if file doesn't exist
        """
        try:
            return (
                self.contacts_filepath.stat().st_size
                if self.contacts_filepath.exists()
                else 0
            )
        except OSError:
            return 0

    def get_notes_file_size(self) -> int:
        """
        Get size of the notes data file in bytes.

        Returns:
            int: File size in bytes, or 0 if file doesn't exist
        """
        try:
            return (
                self.notes_filepath.stat().st_size
                if self.notes_filepath.exists()
                else 0
            )
        except OSError:
            return 0

    def delete_contacts_file(self) -> bool:
        """
        Delete the contacts data file.

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if self.contacts_filepath.exists():
                self.contacts_filepath.unlink()
                return True
            return False
        except OSError as e:
            print(f"Error deleting contacts file: {e}")
            return False

    def delete_notes_file(self) -> bool:
        """
        Delete the notes data file.

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if self.notes_filepath.exists():
                self.notes_filepath.unlink()
                return True
            return False
        except OSError as e:
            print(f"Error deleting notes file: {e}")
            return False
