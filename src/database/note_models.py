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
        # Зберігаємо дату та час створення нотатки у форматі з мікросекундами,
        # щоб точно зафіксувати момент створення
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
            "tags": self.tags[
                :
            ],  # Створюємо копію списку тегів, щоб уникнути небажаних змін оригінального списку
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
        # Створюємо порожній екземпляр Note без виклику __init__,
        # щоб відновити властивості з TypedDict даних без ініціалізації заново
        note = cls.__new__(cls)
        note.title = data["title"]
        note.content = data["content"]
        # Копіюємо список тегів з даних, щоб оригінальні дані залишалися незмінними
        note.tags = data["tags"][:]
        note.created_at = data["created_at"]
        note.updated_at = data.get("updated_at")
        return note


class NotesManager(UserDict[str, Note]):
    """
    Клас для зберігання та управління колекцією нотаток.

    Цей клас наслідує UserDict і забезпечує:
    - Унікальні ідентифікатори для кожної нотатки
    - Пошук нотаток за різними критеріями
    - Збереження та завантаження з файлів
    - Управління тегами та часовими мітками
    """

    def __init__(self) -> None:
        super().__init__()
        self._next_id = 1

    def _generate_id(self) -> str:
        """
        Генерує унікальний ідентифікатор для нової нотатки.

        Формат: "note_XXXX" де XXXX - 4-значне число з нулями спереду.
        Автоматично збільшує лічильник та перевіряє унікальність.

        Returns:
            str: Унікальний ідентифікатор нотатки
        """
        note_id = f"note_{self._next_id:04d}"
        self._next_id += 1
        # Перевіряємо, щоб згенерований ідентифікатор не дублював існуючі в менеджері нотаток
        while note_id in self.data:
            note_id = f"note_{self._next_id:04d}"
            self._next_id += 1
        return note_id

    def add_note(self, note: Note) -> str:
        """
        Додає готовий об'єкт нотатки до менеджера.

        Args:
            note: Об'єкт Note для додавання

        Returns:
            str: Згенерований ідентифікатор доданої нотатки
        """
        note_id = self._generate_id()
        self.data[note_id] = note
        return note_id

    def create_note(
        self, title: str, content: str = "", tags: Optional[List[str]] = None
    ) -> str:
        """
        Створює нову нотатку та додає її до менеджера.

        Зручний метод для створення нотатки з параметрів замість готового об'єкта.

        Args:
            title: Заголовок нотатки (обов'язковий)
            content: Зміст нотатки (за замовчуванням пустий)
            tags: Список тегів (за замовчуванням пустий)

        Returns:
            str: Ідентифікатор створеної нотатки

        Raises:
            ValueError: Якщо заголовок пустий
        """
        note = Note(title, content, tags)
        return self.add_note(note)

    def find_note(self, note_id: str) -> Optional[Note]:
        """
        Знаходить нотатку за її ідентифікатором.

        Args:
            note_id: Ідентифікатор нотатки для пошуку

        Returns:
            Optional[Note]: Об'єкт нотатки якщо знайдено, None якщо не знайдено
        """
        return self.data.get(note_id)

    def delete_note(self, note_id: str) -> bool:
        """
        Видаляє нотатку за її ідентифікатором.

        Args:
            note_id: Ідентифікатор нотатки для видалення

        Returns:
            bool: True якщо нотатку успішно видалено, False якщо нотатку не знайдено
        """
        if note_id in self.data:
            del self.data[note_id]
            return True
        return False

    def search_notes(self, query: str) -> Dict[str, Note]:
        """
        Шукає нотатки, які містять заданий запит.

        Пошук виконується у заголовках, змісті та тегах нотаток.
        Пошук нечутливий до регістру символів.

        Args:
            query: Текст для пошуку

        Returns:
            Dict[str, Note]: Словник з ID нотаток як ключами та об'єктами Note як значеннями
        """
        results = {}
        for note_id, note in self.data.items():
            if note.search_in_content(query):
                results[note_id] = note
        return results

    def get_notes_by_tag(self, tag: str) -> Dict[str, Note]:
        """
        Отримує всі нотатки, які мають конкретний тег.

        Пошук тегу виконується без урахування регістру символів.

        Args:
            tag: Тег для пошуку нотаток

        Returns:
            Dict[str, Note]: Словник з ID нотаток як ключами та об'єктами Note як значеннями
        """
        results = {}
        for note_id, note in self.data.items():
            if note.has_tag(tag):
                results[note_id] = note
        return results

    def get_all_tags(self) -> List[str]:
        """
        Отримує список всіх унікальних тегів зі всіх нотаток.

        Теги повертаються в нижньому регістрі та відсортовані за алфавітом.
        Дублікати автоматично видаляються.

        Returns:
            List[str]: Відсортований список унікальних тегів
        """
        all_tags: set[str] = set()
        for note in self.data.values():
            all_tags.update(tag.lower() for tag in note.tags)
        return sorted(list(all_tags))

    def get_recent_notes(self, limit: int = 10) -> Dict[str, Note]:
        """
        Отримує найновіші нотатки (створені або оновлені).

        Сортування виконується за часом останнього оновлення, якщо він є,
        або за часом створення, якщо оновлень не було.

        Args:
            limit: Максимальна кількість нотаток для повернення (за замовчуванням 10)

        Returns:
            Dict[str, Note]: Словник з найновішими нотатками, відсортованими за часом
        """

        def get_latest_time(note: Note) -> str:
            return note.updated_at or note.created_at

        sorted_items = sorted(
            self.data.items(), key=lambda x: get_latest_time(x[1]), reverse=True
        )

        return dict(sorted_items[:limit])

    def to_typed_dict(self) -> Dict[str, NoteData]:
        """
        Перетворює весь менеджер нотаток у словник TypedDict структур.

        Корисно для серіалізації та передачі даних між компонентами.

        Returns:
            Dict[str, NoteData]: Словник де ключі - ID нотаток, значення - NoteData структури
        """
        return {note_id: note.to_typed_dict() for note_id, note in self.data.items()}

    def to_json(self) -> str:
        """
        Серіалізує менеджер нотаток у JSON рядок.

        Включає всі нотатки та внутрішній лічильник для відновлення стану.
        Використовує UTF-8 кодування для підтримки українських символів.

        Returns:
            str: JSON представлення менеджера нотаток
        """
        data = {"notes": self.to_typed_dict(), "next_id": self._next_id}
        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "NotesManager":
        """
        Десеріалізує менеджер нотаток з JSON рядка.

        Відновлює всі нотатки та внутрішній стан лічильника ID.

        Args:
            json_str: JSON рядок з даними менеджера нотаток

        Returns:
            NotesManager: Новий екземпляр менеджера з відновленими даними

        Raises:
            ValueError: Якщо JSON дані некоректні або пошкоджені
        """
        try:
            data = json.loads(json_str)
            notes_manager = cls()

            # Завантажуємо значення для наступного ідентифікатора (_next_id) з JSON,
            # якщо воно вказане у даних
            if "next_id" in data:
                notes_manager._next_id = data["next_id"]

            # Завантажуємо всі нотатки з розділу "notes", відновлюючи їх у менеджері
            notes_data = data.get("notes", {})
            for note_id, note_data in notes_data.items():
                note = Note.from_typed_dict(note_data)
                notes_manager.data[note_id] = note

            return notes_manager
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid JSON data for NotesManager: {e}")

    def save_to_file(self, filepath: str) -> bool:
        """
        Зберігає менеджер нотаток у JSON файл.

        Args:
            filepath: Шлях до файлу для збереження

        Returns:
            bool: True якщо збереження успішне, False у разі помилки
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.to_json())
            return True
        except (IOError, OSError) as e:
            print(f"Error saving notes to file: {e}")
            return False

    @classmethod
    def load_from_file(cls, filepath: str) -> "NotesManager":
        """
        Завантажує менеджер нотаток з JSON файла.

        Якщо файл не існує або пошкоджений, створює новий порожній менеджер.

        Args:
            filepath: Шлях до файлу для завантаження

        Returns:
            NotesManager: Менеджер з завантаженими даними або новий порожній менеджер
        """
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
        """
        Завантажує нотатки з словника TypedDict структур.

        Очищує поточні дані та завантажує нові нотатки.
        Автоматично відновлює правильну послідовність ID.

        Args:
            data: Словник з даними нотаток (ID -> NoteData)
        """
        self.data.clear()
        max_id = 0

        for note_id, note_data in data.items():
            note = Note.from_typed_dict(note_data)
            self.data[note_id] = note

            # Виділяємо числову частину з ідентифікатора (після "note_"),
            # щоб зберегти правильну послідовність для наступного ID
            if note_id.startswith("note_"):
                try:
                    id_num = int(note_id.split("_")[1])
                    max_id = max(max_id, id_num)
                except (IndexError, ValueError):
                    pass

        self._next_id = max_id + 1
