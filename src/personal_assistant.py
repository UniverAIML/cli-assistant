"""
Модуль персонального асистента для управління контактами та нотатками.

Цей модуль забезпечує високорівневий інтерфейс для управління контактами
та нотатками з збереженням даних.

Основні функції:
- Управління контактами (додавання, пошук, редагування)
- Управління нотатками (створення, пошук, редагування)
- Валідація даних
- Автоматичне збереження змін
- Пошук та фільтрація
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, date

# Імпорти моделей даних
from cli_assistant.database.contact_models import AddressBook, Record
from cli_assistant.database.note_models import NotesManager, Note
from cli_assistant.database.data_manager import DataManager


class PersonalAssistant:
    """
    Персональний асистент для управління контактами та нотатками.

    Цей клас забезпечує високорівневий інтерфейс для управління контактами
    та нотатками з збереженням даних.

    Основні можливості:
    - Централізоване управління даними
    - Валідація введених даних
    - Автоматичне збереження змін
    - Пошук по контактам та нотаткам
    - Обробка помилок
    """

    def __init__(
        self, contacts_file: str = "contacts.json", notes_file: str = "notes.json"
    ):
        """
        Ініціалізує персональний асистент.

        Args:
            contacts_file: Шлях до файлу контактів
            notes_file: Шлях до файлу нотаток
        """
        # Створюємо менеджер даних для роботи з файлами
        self.data_manager = DataManager(contacts_file, notes_file)
        # Завантажуємо існуючі дані або створюємо нові колекції
        self.address_book, self.notes_manager = self.data_manager.load_data()

    def validate_phone(self, phone: str) -> bool:
        """
        Валідує формат номера телефону.

        Правила валідації:
        - Номер повинен містити рівно 10 цифр
        - Ігноруються всі не-цифрові символи (дужки, тире, пробіли)

        Args:
            phone: Рядок з номером телефону

        Returns:
            bool: True якщо номер валідний, False інакше
        """
        if not phone:
            return False

        # Видаляємо всі не-цифрові символи
        digits_only = re.sub(r"\D", "", phone)

        # Валідний номер телефону повинен мати рівно 10 цифр
        return len(digits_only) == 10

    def validate_email(self, email: str) -> bool:
        """
        Валідує формат електронної пошти.

        Правила валідації:
        - Базова перевірка формату email з використанням regex
        - Перевіряє наявність @ та домену

        Args:
            email: Рядок з електронною поштою

        Returns:
            bool: True якщо email валідний, False інакше
        """
        if not email:
            return False

        # Базовий regex для валідації email
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, email))

    def search_contacts(self, query: str) -> List[Record]:
        """
        Пошук контактів за іменем або номером телефону.

        Виконує пошук по:
        - Імені контакту (регістронезалежний)
        - Номеру телефону (точне співпадіння)

        Args:
            query: Пошуковий запит

        Returns:
            List[Record]: Список контактів що відповідають запиту
        """
        results = []
        query_lower = query.lower()

        for record in self.address_book.data.values():
            # Пошук за іменем
            if query_lower in record.name.value.lower():
                results.append(record)
                continue

            # Пошук за номером телефону
            if record.phones:
                for phone in record.phones:
                    if query in phone.value:
                        results.append(record)
                        break

        return results

    def search_notes(self, query: str) -> List[str]:
        """
        Пошук нотаток за заголовком, змістом або тегами.

        Виконує пошук по:
        - Заголовку нотатки (регістронезалежний)
        - Змісту нотатки (регістронезалежний)
        - Тегам (регістронезалежний)

        Args:
            query: Пошуковий запит

        Returns:
            List[str]: Список ID нотаток що відповідають запиту
        """
        results = []
        query_lower = query.lower()

        for note_id, note in self.notes_manager.data.items():
            # Пошук за заголовком
            if query_lower in note.title.lower():
                results.append(note_id)
                continue

            # Пошук за змістом
            if query_lower in note.content.lower():
                results.append(note_id)
                continue

            # Пошук за тегами
            if any(query_lower in tag.lower() for tag in note.tags):
                results.append(note_id)
                continue

        return results

    def get_upcoming_birthdays(self, days: int = 7) -> List[Dict[str, str]]:
        """
        Отримує контакти з найближчими днями народження.

        Args:
            days: Кількість днів для перегляду вперед

        Returns:
            List[Dict[str, str]]: Список записів з найближчими днями народження
        """
        return self.address_book.get_upcoming_birthdays(days)

    def save_data(self) -> bool:
        """
        Зберігає всі дані у файли.

        Returns:
            bool: True якщо збереження успішне, False інакше
        """
        return self.data_manager.save_data(self.address_book, self.notes_manager)

    def display_contacts_table(self, contacts: List[Record]) -> None:
        """
        Відображає контакти у табличному форматі.

        Args:
            contacts: Список записів контактів для відображення
        """
        if not contacts:
            print("No contacts found.")
            return

        print("\n=== Contacts ===")
        for record in contacts:
            print(f"Name: {record.name.value}")
            if record.phones:
                print(f"Phones: {', '.join(phone.value for phone in record.phones)}")
            if record.birthday:
                print(f"Birthday: {record.birthday.value}")
            print("-" * 20)

    def display_notes_table(self, notes: Optional[Dict[str, Note]] = None) -> None:
        """
        Відображає нотатки у табличному форматі.

        Args:
            notes: Словник нотаток, якщо None - відображає всі нотатки
        """
        if notes is None:
            notes = self.notes_manager.data

        if not notes:
            print("No notes found.")
            return

        print("\n=== Notes ===")
        for note_id, note in notes.items():
            print(f"ID: {note_id}")
            print(f"Title: {note.title}")
            print(f"Content: {note.content}")
            if note.tags:
                print(f"Tags: {', '.join(note.tags)}")
            print(f"Created: {note.created_at}")
            print(f"Updated: {note.updated_at}")
            print("-" * 20)
