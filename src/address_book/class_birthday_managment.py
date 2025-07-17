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
        # Try to create next birthday in current year
        try:
            next_birthday = birthday.replace(year=year)
        except ValueError:
            # If date doesn't exist (e.g., 29.02 in non-leap year), find next leap year
            while True:
                year += 1
                try:
                    next_birthday = birthday.replace(year=year)
                    break
                except ValueError:
                    continue
        if next_birthday < today:
            # If birthday already passed this year, look for next year
            year += 1
            while True:
                try:
                    next_birthday = birthday.replace(year=year)
                    break
                except ValueError:
                    year += 1
                    continue
        return int((next_birthday - today).days)
