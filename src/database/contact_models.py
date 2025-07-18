from collections import UserDict
from typing import List, Optional, Dict, TypedDict
import re
import json
from datetime import datetime, date, timedelta


class Field:
    """Base class for record fields."""

    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Class for storing contact name. Required field."""

    def __init__(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        super().__init__(value.strip())


class Phone(Field):
    """Class for storing phone number with validation (10 digits)."""

    def __init__(self, value: str) -> None:
        if not self._validate_phone(value):
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)

    @staticmethod
    def _validate_phone(phone: str) -> bool:
        """Validate phone number format (exactly 10 digits)."""
        clean_phone = re.sub(r"[^0-9]", "", phone)
        return len(clean_phone) == 10 and clean_phone.isdigit()


class Birthday(Field):
    """Class for storing birthday with validation (DD.MM.YYYY format)."""

    def __init__(self, value: str) -> None:
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class ContactData(TypedDict):
    """Typed representation of a contact for static type checking and serialization."""

    name: str
    phones: List[str]
    birthday: Optional[str]


class Record:
    """Class for storing contact information including name, phone list and birthday."""

    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str) -> None:
        """Add a phone number to the record."""
        phone_obj = Phone(phone)
        if not self._phone_exists(phone_obj.value):
            self.phones.append(phone_obj)
        else:
            raise ValueError(f"Phone {phone} already exists for {self.name.value}")

    def remove_phone(self, phone: str) -> None:
        """Remove a phone number from the record."""
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Phone {phone} not found for {self.name.value}")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Edit an existing phone number."""
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError(f"Phone {old_phone} not found for {self.name.value}")

        # Validate new phone before changing
        new_phone_obj = Phone(new_phone)
        if self._phone_exists(new_phone_obj.value):
            raise ValueError(f"Phone {new_phone} already exists for {self.name.value}")

        phone_obj.value = new_phone_obj.value

    def find_phone(self, phone: str) -> Optional[Phone]:
        """Find a phone number in the record."""
        clean_phone = re.sub(r"[^0-9]", "", phone)
        for phone_obj in self.phones:
            if re.sub(r"[^0-9]", "", phone_obj.value) == clean_phone:
                return phone_obj
        return None

    def _phone_exists(self, phone: str) -> bool:
        """Check if phone number already exists in the record."""
        return self.find_phone(phone) is not None

    def add_birthday(self, birthday: str) -> None:
        """Add a birthday to the record."""
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

    def to_typed_dict(self) -> ContactData:
        """Return a TypedDict representation of the record (name + list of phones + birthday)."""
        return {
            "name": self.name.value,
            "phones": [p.value for p in self.phones],
            "birthday": self.birthday.value if self.birthday else None,
        }


class AddressBook(UserDict[str, Record]):
    """Class for storing and managing contact records."""

    def __init__(self) -> None:
        super().__init__()

    def add_record(self, record: Record) -> None:
        """Add a record to the address book."""
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        """Find a record by name."""
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Delete a record by name."""
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Contact {name} not found")

    def get_all_records(self) -> Dict[str, Record]:
        """Get all records in the address book."""
        return self.data.copy()

    def to_typed_dict(self) -> Dict[str, ContactData]:
        """Return the entire address book as mapping name -> ContactData."""
        return {name: record.to_typed_dict() for name, record in self.data.items()}

    def to_json(self) -> str:
        """Serialize the address book to JSON string."""
        return json.dumps(self.to_typed_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "AddressBook":
        """Deserialize address book from JSON string."""
        try:
            data = json.loads(json_str)
            address_book = cls()

            for name, contact_data in data.items():
                # Create record from contact data
                record = Record(contact_data["name"])

                # Add phones
                for phone in contact_data.get("phones", []):
                    record.add_phone(phone)

                # Add birthday if present
                if contact_data.get("birthday"):
                    record.add_birthday(contact_data["birthday"])

                address_book.add_record(record)

            return address_book
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid JSON data for AddressBook: {e}")

    def save_to_file(self, filepath: str) -> bool:
        """Save address book to JSON file."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.to_json())
            return True
        except (IOError, OSError) as e:
            print(f"Error saving address book to file: {e}")
            return False

    @classmethod
    def load_from_file(cls, filepath: str) -> "AddressBook":
        """Load address book from JSON file."""
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

    def get_upcoming_birthdays(self, days) -> List[Dict[str, str]]:
        """Get list of contacts with birthdays in the next 7 days."""
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
                        days_until_monday = days - birthday_this_year.weekday()
                        congratulation_date = birthday_this_year + timedelta(
                            days=days_until_monday
                        )

                    upcoming_birthdays.append(
                        {
                            "name": record.name.value,
                            "congratulation_date": congratulation_date.strftime(
                                "%Y.%m.%d"
                            ),
                        }
                    )

        return upcoming_birthdays
