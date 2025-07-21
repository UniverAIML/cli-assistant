"""
Моделі для роботи з контактами в адресній книзі.

Цей модуль містить класи для:
- Базові поля контактів (ім'я, телефон, день народження)
- Запис контакту з валідацією
- Адресну книгу з функціями пошуку та управління
- Серіалізацію/десеріалізацію в JSON

Архітектура:
- Field - базовий клас для всіх полів
- Name, Phone, Birthday - спеціалізовані поля з валідацією
- Record - окремий контакт з набором полів
- AddressBook - колекція контактів з пошуком
"""

import json
import re
from collections import UserDict
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, TypedDict


class Field:
    """
    Базовий клас для полів запису.

    Забезпечує загальний інтерфейс для всіх типів полів контакту.
    Усі спеціалізовані поля наслідуються від цього класу.
    """

    def __init__(self, value: str) -> None:
        """
        Ініціалізує поле зі значенням.

        Args:
            value: Значення поля
        """
        self.value = value

    def __str__(self) -> str:
        """Повертає строкове представлення поля."""
        return str(self.value)


class Name(Field):
    """
    Клас для зберігання імені контакту. Обов'язкове поле.

    Валідація:
    - Не може бути пустим
    - Автоматично обрізає пробіли
    """

    def __init__(self, value: str) -> None:
        """
        Ініціалізує поле імені з валідацією.

        Args:
            value: Ім'я контакту

        Raises:
            ValueError: Якщо ім'я пусте або містить тільки пробіли
        """
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        super().__init__(value.strip())


class Phone(Field):
    """
    Клас для зберігання номера телефону з валідацією (10 цифр).

    Валідація:
    - Повинен містити рівно 10 цифр
    - Ігноруються всі не-цифрові символи при валідації
    """

    def __init__(self, value: str) -> None:
        """
        Ініціалізує поле телефону з валідацією.

        Args:
            value: Номер телефону

        Raises:
            ValueError: Якщо номер не містить рівно 10 цифр
        """
        if not self._validate_phone(value):
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)

    @staticmethod
    def _validate_phone(phone: str) -> bool:
        """
        Валідує формат номера телефону (рівно 10 цифр).

        Args:
            phone: Номер телефону для перевірки

        Returns:
            bool: True якщо номер валідний, False інакше
        """
        # Видаляємо всі не-цифрові символи
        clean_phone = re.sub(r"[^0-9]", "", phone)
        # Перевіряємо що залишилось рівно 10 цифр
        return len(clean_phone) == 10 and clean_phone.isdigit()


class Birthday(Field):
    """
    Клас для зберігання дня народження з валідацією (формат DD.MM.YYYY).

    Валідація:
    - Повинен бути у форматі DD.MM.YYYY
    - Повинен бути валідною датою
    """

    def __init__(self, value: str) -> None:
        """
        Ініціалізує поле дня народження з валідацією.

        Args:
            value: Дата народження у форматі DD.MM.YYYY

        Raises:
            ValueError: Якщо дата невалідна або у неправильному форматі
        """
        try:
            # Парсимо дату та зберігаємо як date об'єкт
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class ContactData(TypedDict):
    """
    Типізоване представлення контакту для статичної перевірки типів та серіалізації.

    Поля:
    - name: ім'я контакту
    - phones: список номерів телефонів
    - birthday: день народження (опціонально)
    """

    name: str
    phones: List[str]
    birthday: Optional[str]


class Record:
    """
    Клас для зберігання інформації про контакт включаючи ім'я, список телефонів та день народження.

    Можливості:
    - Валідація всіх полів при створенні
    - Управління множинними номерами телефонів
    - Зберігання дня народження з валідацією
    - Пошук та редагування інформації
    """

    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str) -> None:
        """
        Додає новий номер телефону до запису.

        Перевіряє чи номер вже не існує перед додаванням.
        Валідує формат номера телефону.

        Args:
            phone: Номер телефону для додавання

        Raises:
            ValueError: Якщо номер вже існує або має невалідний формат
        """
        phone_obj = Phone(phone)
        if not self._phone_exists(phone_obj.value):
            self.phones.append(phone_obj)
        else:
            raise ValueError(f"Phone {phone} already exists for {self.name.value}")

    def remove_phone(self, phone: str) -> None:
        """
        Видаляє номер телефону з запису.

        Шукає номер телефону в списку та видаляє його.

        Args:
            phone: Номер телефону для видалення

        Raises:
            ValueError: Якщо номер не знайдено
        """
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Phone {phone} not found for {self.name.value}")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """
        Редагує існуючий номер телефону.

        Знаходить старий номер та замінює його новим після валідації.

        Args:
            old_phone: Поточний номер телефону
            new_phone: Новий номер телефону

        Raises:
            ValueError: Якщо старий номер не знайдено або новий номер вже існує
        """
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError(f"Phone {old_phone} not found for {self.name.value}")

        # Валідуємо новий номер перед зміною
        new_phone_obj = Phone(new_phone)
        if self._phone_exists(new_phone_obj.value):
            raise ValueError(f"Phone {new_phone} already exists for {self.name.value}")

        phone_obj.value = new_phone_obj.value

    def find_phone(self, phone: str) -> Optional[Phone]:
        """
        Знаходить номер телефону в записі.

        Порівнює номери телефонів ігноруючи форматування (дужки, тире, пробіли).

        Args:
            phone: Номер телефону для пошуку

        Returns:
            Optional[Phone]: Об'єкт Phone якщо знайдено, None інакше
        """
        clean_phone = re.sub(r"[^0-9]", "", phone)
        for phone_obj in self.phones:
            if re.sub(r"[^0-9]", "", phone_obj.value) == clean_phone:
                return phone_obj
        return None

    def _phone_exists(self, phone: str) -> bool:
        """
        Перевіряє чи номер телефону вже існує в записі.

        Args:
            phone: Номер телефону для перевірки

        Returns:
            bool: True якщо номер існує, False інакше
        """
        return self.find_phone(phone) is not None

    def add_birthday(self, birthday: str) -> None:
        """
        Додає день народження до запису.

        Args:
            birthday: Дата народження у форматі DD.MM.YYYY

        Raises:
            ValueError: Якщо формат дати невалідний
        """
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

    def to_typed_dict(self) -> ContactData:
        """
        Повертає TypedDict представлення запису (ім'я + список телефонів + день народження).

        Returns:
            ContactData: Словник з даними контакту
        """
        return {
            "name": self.name.value,
            "phones": [p.value for p in self.phones],
            "birthday": self.birthday.value if self.birthday else None,
        }


class AddressBook(UserDict[str, Record]):
    """
    Клас для зберігання та управління записами контактів.

    Цей клас наслідує UserDict і забезпечує:
    - Додавання, пошук та видалення контактів
    - Пошук контактів за іменем, телефоном та днем народження
    - Серіалізацію та завантаження з файлів
    - Управління днями народження та нагадуваннями
    """

    def __init__(self) -> None:
        super().__init__()

    def add_record(self, record: Record) -> None:
        """
        Додає запис до адресної книги.

        Args:
            record: Запис контакту для додавання
        """
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        """
        Знаходить запис за ім'ям.

        Args:
            name: Ім'я контакту для пошуку

        Returns:
            Optional[Record]: Запис якщо знайдено, None інакше
        """
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """
        Видаляє запис за ім'ям.

        Args:
            name: Ім'я контакту для видалення

        Raises:
            ValueError: Якщо контакт не знайдено
        """
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Contact {name} not found")

    def get_all_records(self) -> Dict[str, Record]:
        """
        Отримує всі записи в адресній книзі.

        Returns:
            Dict[str, Record]: Копія словника з усіма записами
        """
        return self.data.copy()

    def to_typed_dict(self) -> Dict[str, ContactData]:
        """
        Повертає всю адресну книгу як словник name -> ContactData.

        Returns:
            Dict[str, ContactData]: Словник з даними всіх контактів
        """
        return {name: record.to_typed_dict() for name, record in self.data.items()}

    def to_json(self) -> str:
        """
        Серіалізує адресну книгу у JSON рядок.

        Використовує UTF-8 кодування для підтримки українських символів.

        Returns:
            str: JSON представлення адресної книги
        """
        return json.dumps(self.to_typed_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "AddressBook":
        """
        Десеріалізує адресну книгу з JSON рядка.

        Args:
            json_str: JSON рядок з даними адресної книги

        Returns:
            AddressBook: Новий екземпляр адресної книги з відновленими даними

        Raises:
            ValueError: Якщо JSON дані некоректні або пошкоджені
        """
        try:
            data = json.loads(json_str)
            address_book = cls()

            for name, contact_data in data.items():
                # Створюємо запис з даних контакту
                record = Record(contact_data["name"])

                # Додаємо телефони
                for phone in contact_data.get("phones", []):
                    record.add_phone(phone)

                # Додаємо день народження якщо вказано
                if contact_data.get("birthday"):
                    record.add_birthday(contact_data["birthday"])

                address_book.add_record(record)

            return address_book
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid JSON data for AddressBook: {e}")

    def save_to_file(self, filepath: str) -> bool:
        """
        Зберігає адресну книгу у JSON файл.

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
            print(f"Error saving address book to file: {e}")
            return False

    @classmethod
    def load_from_file(cls, filepath: str) -> "AddressBook":
        """
        Завантажує адресну книгу з JSON файла.

        Якщо файл не існує або пошкоджений, створює нову порожню адресну книгу.

        Args:
            filepath: Шлях до файлу для завантаження

        Returns:
            AddressBook: Адресна книга з завантаженими даними або нова порожня книга
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                json_str = f.read()
            return cls.from_json(json_str)
        except (IOError, OSError) as e:
            print(
                f"Error loading address book from file: {e}. Creating new AddressBook."
            )
            return cls()
        except ValueError as e:
            print(f"Error parsing address book file: {e}. Creating new AddressBook.")
            return cls()

    def get_upcoming_birthdays(self, days: int = 7) -> List[Dict[str, str]]:
        """
        Отримує список контактів з днями народження в наступні кілька днів.

        Args:
            days: Кількість днів для перегляду вперед (за замовчуванням 7)

        Returns:
            List[Dict[str, str]]: Список словників з інформацією про дні народження.
            Кожен словник містить:
            - name: ім'я контакту
            - birthday_date: оригінальна дата дня народження (YYYY.MM.DD)
            - congratulation_date: дата для привітання (YYYY.MM.DD, з урахуванням переносу вихідних)
        """
        upcoming_birthdays: List[Dict[str, str]] = []
        today = date.today()

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday <= days:
                    congratulation_date = birthday_this_year
                    if birthday_this_year.weekday() >= 5:  # 5 = субота, 6 = неділя
                        # Переносимо на наступний понеділок
                        days_until_monday = 7 - birthday_this_year.weekday()
                        congratulation_date = birthday_this_year + timedelta(
                            days=days_until_monday
                        )

                    upcoming_birthdays.append(
                        {
                            "name": record.name.value,
                            "birthday_date": birthday_this_year.strftime("%Y.%m.%d"),
                            "congratulation_date": congratulation_date.strftime(
                                "%Y.%m.%d"
                            ),
                        }
                    )

        return upcoming_birthdays
