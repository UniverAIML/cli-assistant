"""
Модуль управління нотатками для персонального асистента.

Цей модуль забезпечує функціональність для управління нотатками з тегами та часовими мітками.

Основні компоненти:
- Note: клас для окремої нотатки
- NotesManager: менеджер для колекції нотаток
- NoteData: типізована структура для серіалізації

Функції:
- Створення, редагування, видалення нотаток
- Пошук по заголовку, змісту, тегам
- Автоматичні часові мітки
- Валідація даних
- Серіалізація в JSON
"""

from collections import UserDict
from typing import List, Optional, Dict, TypedDict
from datetime import datetime
import re
import json


class NoteData(TypedDict):
    """
    Типізоване представлення нотатки для статичної перевірки типів та серіалізації.

    Поля:
    - title: заголовок нотатки
    - content: зміст нотатки
    - tags: список тегів
    - created_at: дата/час створення
    - updated_at: дата/час останнього оновлення (опціонально)
    """

    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: Optional[str]


class Note:
    """
    Клас для зберігання інформації про нотатку включно з заголовком, змістом, тегами та часовими мітками.

    Можливості:
    - Автоматичні часові мітки створення та оновлення
    - Валідація заголовка
    - Управління тегами
    - Серіалізація в словник
    """

    def __init__(
        self, title: str, content: str = "", tags: Optional[List[str]] = None
    ) -> None:
        """
        Ініціалізує нову нотатку.

        Args:
            title: Заголовок нотатки (обов'язковий)
            content: Зміст нотатки (за замовчуванням пустий)
            tags: Список тегів (за замовчуванням пустий)

        Raises:
            ValueError: Якщо заголовок пустий
        """
        if not title or not title.strip():
            raise ValueError("Note title cannot be empty")

        self.title = title.strip()
        self.content = content
        self.tags = tags or []
        # Зберігаємо часову мітку створення з мікросекундами для точності
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.updated_at: Optional[str] = None

    def update_content(self, content: str) -> None:
        """
        Оновлює зміст нотатки та встановлює часову мітку оновлення.

        Args:
            content: Новий зміст нотатки
        """
        self.content = content
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def update_title(self, title: str) -> None:
        """
        Оновлює заголовок нотатки та встановлює часову мітку оновлення.

        Args:
            title: Новий заголовок нотатки

        Raises:
            ValueError: Якщо заголовок пустий
        """
        if not title or not title.strip():
            raise ValueError("Note title cannot be empty")

        self.title = title.strip()
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def add_tag(self, tag: str) -> None:
        """
        Додає тег до нотатки.

        Тег додається у нижньому регістрі, дублікати ігноруються.
        Оновлює часову мітку зміни нотатки.

        Args:
            tag: Тег для додавання
        """
        tag = tag.strip().lower()
        if tag and tag not in [t.lower() for t in self.tags]:
            self.tags.append(tag)
            self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def remove_tag(self, tag: str) -> None:
        """
        Видаляє тег з нотатки.

        Пошук тега виконується без урахування регістру.
        Оновлює часову мітку зміни нотатки якщо тег було знайдено.

        Args:
            tag: Тег для видалення
        """
        tag = tag.strip().lower()
        original_tags = self.tags[:]
        self.tags = [t for t in self.tags if t.lower() != tag]

        if len(self.tags) != len(original_tags):
            self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def has_tag(self, tag: str) -> bool:
        """
        Перевіряє чи містить нотатка конкретний тег.

        Пошук виконується без урахування регістру.

        Args:
            tag: Тег для перевірки

        Returns:
            bool: True якщо тег знайдено, False інакше
        """
        tag = tag.strip().lower()
        return tag in [t.lower() for t in self.tags]

    def search_in_content(self, query: str) -> bool:
        """
        Пошук запиту в заголовку, змісті або тегах нотатки.

        Пошук виконується без урахування регістру.

        Args:
            query: Пошуковий запит

        Returns:
            bool: True якщо запит знайдено, False інакше
        """
        query = query.lower()
        return (
            query in self.title.lower()
            or query in self.content.lower()
            or any(query in tag.lower() for tag in self.tags)
        )

    def __str__(self) -> str:
        tags_str = f", tags: {', '.join(self.tags)}" if self.tags else ""
        updated_str = f", updated: {self.updated_at}" if self.updated_at else ""
        return f"Note: {self.title}, created: {self.created_at}{updated_str}{tags_str}"

    def to_typed_dict(self) -> NoteData:
        """
        Повертає TypedDict представлення нотатки.

        Returns:
            NoteData: Словник з даними нотатки
        """
        return {
            "title": self.title,
            "content": self.content,
            "tags": self.tags[:],  # Create a copy
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_typed_dict(cls, data: NoteData) -> "Note":
        """
        Створює екземпляр Note з TypedDict даних.

        Args:
            data: Словник з даними нотатки

        Returns:
            Note: Новий екземпляр нотатки
        """
        note = cls.__new__(cls)  # Create instance without calling __init__
        note.title = data["title"]
        note.content = data["content"]
        note.tags = data["tags"][:]  # Create a copy
        note.created_at = data["created_at"]
        note.updated_at = data.get("updated_at")
        return note


class NotesManager(UserDict[str, Note]):
    """Class for storing and managing note records."""

    def __init__(self) -> None:
        super().__init__()
        self._next_id = 1

    def _generate_id(self) -> str:
        """Generate a unique ID for a note."""
        note_id = f"note_{self._next_id:04d}"
        self._next_id += 1
        # Ensure ID is unique
        while note_id in self.data:
            note_id = f"note_{self._next_id:04d}"
            self._next_id += 1
        return note_id

    def add_note(self, note: Note) -> str:
        """Add a note to the manager and return its ID."""
        note_id = self._generate_id()
        self.data[note_id] = note
        return note_id

    def create_note(
        self, title: str, content: str = "", tags: Optional[List[str]] = None
    ) -> str:
        """Create a new note and add it to the manager."""
        note = Note(title, content, tags)
        return self.add_note(note)

    def find_note(self, note_id: str) -> Optional[Note]:
        """Find a note by ID."""
        return self.data.get(note_id)

    def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID."""
        if note_id in self.data:
            del self.data[note_id]
            return True
        return False

    def search_notes(self, query: str) -> Dict[str, Note]:
        """Search for notes containing the query."""
        results = {}
        for note_id, note in self.data.items():
            if note.search_in_content(query):
                results[note_id] = note
        return results

    def get_notes_by_tag(self, tag: str) -> Dict[str, Note]:
        """Get all notes that have a specific tag."""
        results = {}
        for note_id, note in self.data.items():
            if note.has_tag(tag):
                results[note_id] = note
        return results

    def get_all_tags(self) -> List[str]:
        """Get all unique tags across all notes."""
        all_tags: set[str] = set()
        for note in self.data.values():
            all_tags.update(tag.lower() for tag in note.tags)
        return sorted(list(all_tags))

    def get_recent_notes(self, limit: int = 10) -> Dict[str, Note]:
        """Get the most recently created or updated notes."""

        def get_latest_time(note: Note) -> str:
            return note.updated_at or note.created_at

        sorted_items = sorted(
            self.data.items(), key=lambda x: get_latest_time(x[1]), reverse=True
        )

        return dict(sorted_items[:limit])

    def to_typed_dict(self) -> Dict[str, NoteData]:
        """Return the entire notes manager as mapping id -> NoteData."""
        return {note_id: note.to_typed_dict() for note_id, note in self.data.items()}

    def to_json(self) -> str:
        """Serialize the notes manager to JSON string."""
        data = {"notes": self.to_typed_dict(), "next_id": self._next_id}
        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "NotesManager":
        """Deserialize notes manager from JSON string."""
        try:
            data = json.loads(json_str)
            notes_manager = cls()

            # Load next_id if present
            if "next_id" in data:
                notes_manager._next_id = data["next_id"]

            # Load notes
            notes_data = data.get("notes", {})
            for note_id, note_data in notes_data.items():
                note = Note.from_typed_dict(note_data)
                notes_manager.data[note_id] = note

            return notes_manager
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid JSON data for NotesManager: {e}")

    def save_to_file(self, filepath: str) -> bool:
        """Save notes manager to JSON file."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.to_json())
            return True
        except (IOError, OSError) as e:
            print(f"Error saving notes to file: {e}")
            return False

    @classmethod
    def load_from_file(cls, filepath: str) -> "NotesManager":
        """Load notes manager from JSON file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                json_str = f.read()
            return cls.from_json(json_str)
        except (IOError, OSError) as e:
            print(f"Error loading notes from file: {e}. Creating new NotesManager.")
            return cls()
        except ValueError as e:
            print(f"Error parsing notes file: {e}. Creating new NotesManager.")
            return cls()

    def from_typed_dict(self, data: Dict[str, NoteData]) -> None:
        """Load notes from typed dict data."""
        self.data.clear()
        max_id = 0

        for note_id, note_data in data.items():
            note = Note.from_typed_dict(note_data)
            self.data[note_id] = note

            # Extract numeric part of ID to maintain sequence
            if note_id.startswith("note_"):
                try:
                    id_num = int(note_id.split("_")[1])
                    max_id = max(max_id, id_num)
                except (IndexError, ValueError):
                    pass

        self._next_id = max_id + 1
