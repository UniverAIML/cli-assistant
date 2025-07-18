import re
from datetime import datetime, date, timedelta


class Field:
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Field value must be a string")
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    def __init__(self, value: str):
        # Auto deleted spases on front and back
        stripped_value = value.strip()
        # Check on empty string
        if not stripped_value:
            raise ValueError("Name cannot be empty or whitespace only")
        # Checking length
        if not (1 <= len(stripped_value) <= 100):
            raise ValueError("Name must be between 1 and 100 characters")
        # Checking for valid characters.
        pattern = r"^[a-zA-Z\s\-']{1,100}$"
        if not re.fullmatch(pattern, stripped_value):
            raise ValueError(
                f"Name can contain only letters, spaces, hyphens, and apostrophes. DO NOT MATCH Pattern: {pattern}"
            )
        super().__init__(stripped_value)


class Phone(Field):
    @staticmethod
    def _validate_phone(phone: str) -> bool:
        clean_phone = "".join(filter(str.isdigit, phone))  # Remove non-digit characters
        pattern = r"^\d{10}$"
        return bool(re.fullmatch(pattern, clean_phone))

    def __init__(self, phone: str):
        clean_phone = "".join(filter(str.isdigit, phone))
        if not self._validate_phone(phone):
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(clean_phone)


class Birthday(Field):
    def __init__(self, value: str):
        pattern = r"\d{2}\.\d{2}\.\d{4}"
        if not re.fullmatch(pattern, value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            day, month, year = map(int, value.split("."))
            # Checking for leap year and 29.02
            if day == 29 and month == 2:
                from calendar import isleap

                if not isleap(year):
                    raise ValueError(
                        f"{year} is not a leap year, so 29.02 does not exist"
                    )
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        # Checking that the date is in the past
        if date_obj >= datetime.now().date():
            raise ValueError("Birthday must be in the past")
        # Checking the year
        if not (1900 <= date_obj.year <= datetime.now().year - 1):
            raise ValueError("Year must be between 1900 and previous year")
        super().__init__(str(date_obj))
        self.date = date_obj

    def days_to_next_birthday(self) -> int:
        """Calculate days until next birthday."""
        today = date.today()
        birthday = self.date
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

        # If birthday already passed this year, look for next year
        if next_birthday < today:
            year += 1
            while True:
                try:
                    next_birthday = birthday.replace(year=year)
                    break
                except ValueError:
                    year += 1
                    continue

        return (next_birthday - today).days
