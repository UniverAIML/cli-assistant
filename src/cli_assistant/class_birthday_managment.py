from datetime import datetime, timedelta
from typing import Optional
from cli_assistant.base_field_classes import Birthday

class BirthdayManagementMixin:
    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def remove_birthday(self) -> None:
        self.birthday = None

    def days_to_birthday(self) -> Optional[int]:
        if not self.birthday:
            return None
        today = datetime.now().date()
        birthday = self.birthday.date
        next_birthday = birthday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = birthday.replace(year=today.year + 1)
        return (next_birthday - today).days