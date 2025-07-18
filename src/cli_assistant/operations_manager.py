"""
Менеджер операцій для персонального асистента.

Цей модуль забезпечує уніфікований інтерфейс для всіх операцій з контактами та нотатками,
який може використовуватися як інтерактивним меню, так і AI асистентом.

Основні функції:
- Управління контактами (додавання, пошук, редагування, видалення)
- Управління нотатками (створення, пошук, редагування, видалення)
- Глобальний пошук по всіх даних
- Статистика та аналітика
- Збереження та завантаження даних
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta

import re
import os

# Імпорти моделей та менеджерів даних
from .database.contact_models import AddressBook, Record
from .database.note_models import NotesManager, Note
from .database.data_manager import DataManager


class OperationsManager:
    """
    Уніфікований менеджер для всіх операцій з контактами та нотатками.

    Цей клас забезпечує чистий інтерфейс для всіх операцій, який може використовуватися
    як системою інтерактивного меню, так і AI асистентом.

    Основні можливості:
    - Централізоване управління даними
    - Уніфікований API для різних інтерфейсів
    - Автоматичне збереження змін
    - Валідація даних
    - Обробка помилок
    """

    def __init__(self) -> None:
        """
        Ініціалізує менеджер операцій.

        Створює:
        - DataManager для роботи з файлами
        - AddressBook для контактів
        - NotesManager для нотаток
        """
        self.data_manager = DataManager()
        self.address_book, self.notes_manager = self.data_manager.load_data()

    def save_data(self) -> bool:
        """
        Зберігає всі дані на диск.

        Returns:
            bool: True якщо збереження успішне, False інакше
        """
        result = self.data_manager.save_data(self.address_book, self.notes_manager)
        return bool(result)

    def get_data_summary(self) -> Dict[str, int]:
        """
        Отримує зведення завантажених даних.

        Returns:
            Dict з кількістю контактів та нотаток
        """
        return {
            "contacts": len(self.address_book.data),
            "notes": len(self.notes_manager.data),
        }

    # =====================================
    # Операції з контактами
    # =====================================
    def add_contact(
        self,
        name: str,
        phones: Optional[List[str]] = None,
        birthday: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Додає новий контакт до адресної книги.

        Процес додавання:
        1. Перевіряє чи контакт вже існує
        2. Створює новий запис з валідацією
        3. Додає телефони (якщо надані)
        4. Додає день народження (якщо наданий)
        5. Зберігає дані в файл

        Args:
            name: Ім'я контакту (обов'язкове)
            phones: Список номерів телефонів (опціонально)
            birthday: День народження у форматі DD.MM.YYYY (опціонально)

        Returns:
            Dict з результатом операції:
            - success: bool - чи успішна операція
            - message: str - повідомлення про результат
            - existing: bool - чи контакт вже існує (опціонально)
            - record: Record - створений запис (опціонально)
        """
        try:
            # Перевіряємо чи контакт з таким ім'ям вже існує
            existing_record = self.address_book.find(name)
            if existing_record:
                return {
                    "success": False,
                    "message": f"Contact '{name}' already exists",
                    "existing": True,
                }

            # Створюємо новий запис контакту
            record = Record(name)

            # Додаємо телефони якщо вони надані
            if phones:
                for phone in phones:
                    try:
                        # Валідуємо та додаємо кожен телефон
                        record.add_phone(phone)
                    except ValueError as e:
                        return {
                            "success": False,
                            "message": f"Invalid phone number '{phone}': {e}",
                        }

            # Додаємо день народження якщо наданий
            if birthday:
                try:
                    # Валідуємо формат дати та додаємо
                    record.add_birthday(birthday)
                except ValueError as e:
                    return {
                        "success": False,
                        "message": f"Invalid birthday format: {e}",
                    }

            # Додаємо запис до адресної книги
            self.address_book.add_record(record)

            # Зберігаємо дані в файл
            save_success = self.save_data()
            if not save_success:
                return {
                    "success": False,
                    "message": f"Contact '{name}' added but failed to save to file",
                }

            return {
                "success": True,
                "message": f"Contact '{name}' added successfully",
                "record": record,
            }

        except ValueError as e:
            return {"success": False, "message": f"Error creating contact: {e}"}

    def search_contacts(self, query: str) -> List[Record]:
        """
        Шукає контакти за ім'ям або номером телефону.

        Пошук виконується за наступними критеріями:
        1. Частковий збіг з ім'ям контакту (регістр ігнорується)
        2. Частковий збіг з будь-яким номером телефону

        Args:
            query: Рядок для пошуку

        Returns:
            List[Record]: Список контактів що відповідають критеріям пошуку
        """
        # Перетворюємо запит в нижній регістр для пошуку без урахування регістру
        query = query.lower()
        results = []

        # Проходимо по всіх записах в адресній книзі
        for record in self.address_book.data.values():
            # Шукаємо збіг в імені
            if query in record.name.value.lower():
                results.append(record)
                continue  # Переходимо до наступного запису

            # Шукаємо збіг в номерах телефонів
            for phone in record.phones:
                if query in phone.value:
                    results.append(record)
                    break  # Виходимо з циклу телефонів, додаємо запис тільки один раз

        return results

    def get_all_contacts(self) -> List[Record]:
        """
        Отримує всі контакти з адресної книги.

        Returns:
            List[Record]: Список всіх контактів у вигляді Record об'єктів
        """
        return list(self.address_book.data.values())

    def get_contact_by_name(self, name: str) -> Optional[Record]:
        """
        Отримує контакт за ім'ям.

        Args:
            name: Ім'я контакту для пошуку

        Returns:
            Optional[Record]: Запис контакту якщо знайдено, None інакше
        """
        result = self.address_book.find(name)
        return result if isinstance(result, Record) else None

    def edit_contact(self, name: str, action: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Редагує існуючий контакт.

        Підтримує наступні дії:
        - add_phone: додати новий телефон
        - remove_phone: видалити телефон
        - change_phone: змінити телефон
        - add_birthday: додати день народження

        Args:
            name: Ім'я контакту для редагування
            action: Дія для виконання
            **kwargs: Додаткові параметри залежно від дії:
                - phone: номер телефону
                - new_phone: новий номер телефону (для change_phone)
                - birthday: день народження у форматі DD.MM.YYYY

        Returns:
            Dict[str, Any]: Результат операції з статусом успіху та повідомленням
        """
        # Шукаємо контакт за ім'ям
        record = self.address_book.find(name)
        if not record:
            return {"success": False, "message": f"Contact '{name}' not found"}

        try:
            if action == "add_phone":
                # Додаємо новий телефон
                phone = kwargs.get("phone")
                if not phone:
                    return {"success": False, "message": "Phone number is required"}
                record.add_phone(phone)
                self.save_data()
                return {
                    "success": True,
                    "message": f"Phone '{phone}' added successfully",
                }

            elif action == "remove_phone":
                # Видаляємо телефон
                phone = kwargs.get("phone")
                if not phone:
                    return {"success": False, "message": "Phone number is required"}
                record.remove_phone(phone)
                self.save_data()
                return {
                    "success": True,
                    "message": f"Phone '{phone}' removed successfully",
                }

            elif action == "change_phone":
                # Змінюємо телефон
                old_phone = kwargs.get("phone")
                new_phone = kwargs.get("new_phone")
                if not old_phone or not new_phone:
                    return {
                        "success": False,
                        "message": "Both old and new phone numbers are required",
                    }
                record.edit_phone(old_phone, new_phone)
                self.save_data()
                return {
                    "success": True,
                    "message": f"Phone changed from '{old_phone}' to '{new_phone}'",
                }

            elif action == "add_birthday":
                # Додаємо день народження
                birthday = kwargs.get("birthday")
                if not birthday:
                    return {"success": False, "message": "Birthday is required"}
                record.add_birthday(birthday)
                self.save_data()
                return {"success": True, "message": f"Birthday set to '{birthday}'"}

            else:
                return {"success": False, "message": f"Unknown action: {action}"}

        except ValueError as e:
            return {"success": False, "message": str(e)}

    def delete_contact(self, name: str) -> Dict[str, Any]:
        """
        Видаляє контакт з адресної книги.

        Args:
            name: Ім'я контакту для видалення

        Returns:
            Dict[str, Any]: Результат операції з статусом та повідомленням
        """
        try:
            # Видаляємо контакт з адресної книги
            self.address_book.delete(name)
            # Зберігаємо зміни в файл
            self.save_data()
            return {
                "success": True,
                "message": f"Contact '{name}' deleted successfully",
            }
        except ValueError as e:
            return {"success": False, "message": str(e)}

    def get_upcoming_birthdays(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Отримує контакти з днями народження що наближаються.

        Args:
            days: Кількість днів наперед для перевірки (за замовчуванням 7)

        Returns:
            List[Dict[str, Any]]: Список контактів з інформацією про дні народження
        """
        # Викликаємо метод адресної книги з параметром days
        result = self.address_book.get_upcoming_birthdays(days)
        return result if isinstance(result, list) else []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Отримує статистику про контакти та нотатки.

        Збирає наступну інформацію:
        - Загальна кількість контактів
        - Загальна кількість нотаток
        - Кількість контактів з днями народження
        - Кількість контактів з телефонами
        - Кількість нотаток з тегами

        Returns:
            Dict[str, Any]: Словник зі статистичними даними
        """
        # Підраховуємо загальну кількість контактів та нотаток
        contact_count = len(self.address_book.data)
        note_count = len(self.notes_manager.data)

        # Підраховуємо контакти з днями народження
        contacts_with_birthdays = sum(
            1 for record in self.address_book.data.values() if record.birthday
        )

        # Підраховуємо контакти з телефонами
        contacts_with_phones = sum(
            1 for record in self.address_book.data.values() if record.phones
        )

        # Підраховуємо нотатки з тегами
        notes_with_tags = sum(
            1 for note in self.notes_manager.data.values() if note.tags
        )

        return {
            "total_contacts": contact_count,
            "total_notes": note_count,
            "contacts_with_birthdays": contacts_with_birthdays,
            "contacts_with_phones": contacts_with_phones,
            "notes_with_tags": notes_with_tags,
        }

    # =====================================
    # Операції з нотатками
    # =====================================
    def add_note(
        self, title: str, content: str, tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Додає нову нотатку.

        Створює нову нотатку з заголовком, змістом та тегами.
        Автоматично встановлює часову мітку створення.

        Args:
            title: Заголовок нотатки (обов'язковий)
            content: Зміст нотатки
            tags: Список тегів для нотатки (опціонально)

        Returns:
            Dict[str, Any]: Результат операції з статусом та повідомленням
        """
        try:
            # Встановлюємо пустий список тегів якщо не надано
            if tags is None:
                tags = []

            # Створюємо нову нотатку через менеджер нотаток
            note_id = self.notes_manager.create_note(title, content, tags)

            # Зберігаємо дані в файл
            save_success = self.save_data()
            if not save_success:
                return {
                    "success": False,
                    "message": f"Note '{title}' added but failed to save to file",
                }

            return {
                "success": True,
                "message": f"Note '{title}' added successfully",
                "note_id": note_id,
            }
        except ValueError as e:
            return {"success": False, "message": f"Error creating note: {e}"}

    def search_notes(self, query: str) -> Dict[str, Note]:
        """
        Шукає нотатки за заголовком, змістом або тегами.

        Пошук виконується за наступними критеріями:
        - Частковий збіг з заголовком (регістр ігнорується)
        - Частковий збіг зі змістом (регістр ігнорується)
        - Частковий збіг з будь-яким тегом (регістр ігнорується)

        Args:
            query: Рядок для пошуку

        Returns:
            Dict[str, Note]: Словник знайдених нотаток (ID -> Note)
        """
        result = self.notes_manager.search_notes(query)
        return result if isinstance(result, dict) else {}

    def get_all_notes(self) -> Dict[str, Note]:
        """
        Отримує всі нотатки.

        Returns:
            Dict[str, Note]: Словник всіх нотаток (ID -> Note)
        """
        result = self.notes_manager.data
        return result if isinstance(result, dict) else {}

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """
        Отримує нотатку за її ID.

        Args:
            note_id: Унікальний ідентифікатор нотатки

        Returns:
            Optional[Note]: Об'єкт нотатки якщо знайдено, None інакше
        """
        result = self.notes_manager.find_note(note_id)
        return result if isinstance(result, Note) else None

    def edit_note(self, note_id: str, action: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Редагує існуючу нотатку.

        Підтримує наступні дії:
        - edit_title: змінити заголовок
        - edit_content: змінити зміст
        - add_tag: додати тег
        - remove_tag: видалити тег

        Args:
            note_id: ID нотатки для редагування
            action: Дія для виконання
            **kwargs: Додаткові параметри залежно від дії:
                - title: новий заголовок
                - content: новий зміст
                - tag: тег для додавання/видалення

        Returns:
            Dict[str, Any]: Результат операції з статусом та повідомленням
        """
        # Шукаємо нотатку за ID
        note = self.notes_manager.find_note(note_id)
        if not note:
            return {"success": False, "message": f"Note with ID '{note_id}' not found"}

        try:
            if action == "edit_title":
                # Змінюємо заголовок
                title = kwargs.get("title")
                if not title:
                    return {"success": False, "message": "Title is required"}
                note.title = title
                note.updated_at = datetime.now().isoformat()
                self.save_data()
                return {"success": True, "message": "Title updated successfully"}

            elif action == "edit_content":
                # Змінюємо зміст
                content = kwargs.get("content")
                if content is None:
                    return {"success": False, "message": "Content is required"}
                note.content = content
                note.updated_at = datetime.now().isoformat()
                self.save_data()
                return {"success": True, "message": "Content updated successfully"}

            elif action == "add_tag":
                # Додаємо тег
                tag = kwargs.get("tag")
                if not tag:
                    return {"success": False, "message": "Tag is required"}
                note.add_tag(tag)
                self.save_data()
                return {"success": True, "message": f"Tag '{tag}' added successfully"}

            elif action == "remove_tag":
                # Видаляємо тег
                tag = kwargs.get("tag")
                if not tag:
                    return {"success": False, "message": "Tag is required"}
                note.remove_tag(tag)
                self.save_data()
                return {"success": True, "message": f"Tag '{tag}' removed successfully"}

            else:
                return {"success": False, "message": f"Unknown action: {action}"}

        except ValueError as e:
            return {"success": False, "message": str(e)}

    def delete_note(self, note_id: str) -> Dict[str, Any]:
        """
        Видаляє нотатку за її унікальним ідентифікатором.

        Процес видалення:
        1. Викликає метод видалення в менеджері нотаток
        2. Зберігає зміни в файл (якщо видалення успішне)
        3. Повертає результат операції

        Args:
            note_id: Унікальний ідентифікатор нотатки для видалення

        Returns:
            Dict[str, Any]: Результат операції з полями:
                - success: булевий статус операції
                - message: повідомлення про результат
        """
        # Намагаємося видалити нотатку через менеджер нотаток
        if self.notes_manager.delete_note(note_id):
            # Зберігаємо зміни після успішного видалення
            self.save_data()
            return {"success": True, "message": "Note deleted successfully"}
        else:
            return {
                "success": False,
                "message": "Note not found or could not be deleted",
            }

    def search_notes_by_tag(self, tag: str) -> Dict[str, Note]:
        """
        Шукає нотатки за конкретним тегом.

        Виконує пошук нотаток, які містять точний збіг з вказаним тегом.
        Корисно для категоризації та фільтрації нотаток.

        Args:
            tag: Тег для пошуку (точний збіг)

        Returns:
            Dict[str, Note]: Словник нотаток що містять вказаний тег.
                Ключ - ID нотатки, значення - об'єкт Note.
                Повертає пустий словник якщо нотатки не знайдені.
        """
        # Викликаємо метод пошуку за тегом в менеджері нотаток
        result = self.notes_manager.get_notes_by_tag(tag)
        # Повертаємо результат або пустий словник
        return result if isinstance(result, dict) else {}

    def global_search(self, query: str) -> Dict[str, Any]:
        """
        Виконує глобальний пошук по всіх контактах та нотатках.

        Комбінує результати пошуку з контактів та нотаток в один результат.
        Корисно для швидкого пошуку інформації в усіх даних асистента.

        Пошук виконується за такими критеріями:
        - Контакти: пошук по імені та номерах телефонів
        - Нотатки: пошук по заголовку, змісту та тегах

        Args:
            query: Рядок для пошуку (без урахування регістру)

        Returns:
            Dict[str, Any]: Результати пошуку з полями:
                - contacts: List[Record] - знайдені контакти
                - notes: Dict[str, Note] - знайдені нотатки
        """
        return {
            # Шукаємо в контактах
            "contacts": self.search_contacts(query),
            # Шукаємо в нотатках
            "notes": self.search_notes(query),
        }

    # View operations
    def view_contact_details(self, name: str) -> Dict[str, Any]:
        """
        Отримує детальну інформацію про контакт.

        Повертає повну інформацію про контакт включно з усіма телефонами
        та днем народження якщо він встановлений.

        Args:
            name: Ім'я контакту для отримання деталей

        Returns:
            Dict[str, Any]: Детальна інформація про контакт або повідомлення про помилку:
                При успіху:
                - success: True
                - contact: словник з полями name, phones, birthday
                При помилці:
                - success: False
                - message: повідомлення про помилку
        """
        # Шукаємо контакт за ім'ям
        record = self.address_book.find(name)
        if not record:
            return {"success": False, "message": f"Contact '{name}' not found"}

        # Формуємо детальну інформацію про контакт
        return {
            "success": True,
            "contact": {
                "name": record.name.value,
                "phones": [phone.value for phone in record.phones],
                "birthday": record.birthday.value if record.birthday else None,
            },
        }

    def view_note_details(self, note_id: str) -> Dict[str, Any]:
        """
        Отримує детальну інформацію про нотатку.

        Повертає повну інформацію про нотатку включно з усіма метаданими:
        заголовок, зміст, теги, дати створення та оновлення.

        Args:
            note_id: Унікальний ідентифікатор нотатки

        Returns:
            Dict[str, Any]: Детальна інформація про нотатку або повідомлення про помилку:
                При успіху:
                - success: True
                - note: словник з полями id, title, content, tags, created_at, updated_at
                При помилці:
                - success: False
                - message: повідомлення про помилку
        """
        # Шукаємо нотатку за ID
        note = self.notes_manager.find_note(note_id)
        if not note:
            return {"success": False, "message": f"Note with ID '{note_id}' not found"}

        # Формуємо детальну інформацію про нотатку
        return {
            "success": True,
            "note": {
                "id": note_id,
                "title": note.title,
                "content": note.content,
                "tags": note.tags,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            },
        }
