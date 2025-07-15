import re
from datetime import datetime

class Field:
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Field value must be a string")
        self.value = value

    def __str__(self):
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
            raise ValueError("Name can contain only letters, spaces, hyphens, and apostrophes")
        super().__init__(stripped_value)
class Phone(Field):
    @staticmethod
    def _validate_phone(phone: str) -> bool:
        clean_phone = ''.join(filter(str.isdigit, phone)) # Remove non-digit characters
        pattern = r"^\d{10}$"
        return bool(re.fullmatch(pattern, clean_phone))

    def __init__(self, phone: str):
        clean_phone = ''.join(filter(str.isdigit, phone))
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
            day, month, year = map(int, value.split('.'))
            # Checking for leap year and 29.02
            if day == 29 and month == 2:
                from calendar import isleap
                if not isleap(year):
                    raise ValueError(f"{year} is not a leap year, so 29.02 does not exist")
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        # Checking that the date is in the past
        if date_obj >= datetime.now().date():
            raise ValueError("Birthday must be in the past")
        # Checking the year
        if not (1900 <= date_obj.year <= datetime.now().year - 1):
            raise ValueError("Year must be between 1900 and previous year")
        super().__init__(str(date_obj))
        self.date = date_obj
