from datetime import datetime, timedelta
from typing import Optional

from .base_field_classes import Birthday


class BirthdayManagementMixin:
    def __init__(self) -> None:
        self.birthday: Optional[Birthday] = None

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def remove_birthday(self) -> None:
        self.birthday = None

    def days_to_birthday(self) -> Optional[int]:
        if not self.birthday:
            return None
        today = datetime.now().date()
        birthday = self.birthday.date
        year = today.year
        # Спробувати створити наступний день народження у поточному році
        try:
            next_birthday = birthday.replace(year=year)
        except ValueError:
            # Якщо день не існує (наприклад, 29.02 у невисокосний рік), шукаємо наступний високосний рік
            while True:
                year += 1
                try:
                    next_birthday = birthday.replace(year=year)
                    break
                except ValueError:
                    continue
        if next_birthday < today:
            # Якщо день народження вже був цього року, шукаємо наступний рік
            year += 1
            while True:
                try:
                    next_birthday = birthday.replace(year=year)
                    break
                except ValueError:
                    year += 1
                    continue
        return int((next_birthday - today).days)
