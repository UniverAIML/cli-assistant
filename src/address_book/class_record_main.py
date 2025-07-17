from typing import Any, Dict, List, Optional, TypedDict

from .base_field_classes import Birthday, Name, Phone


class ContactData(TypedDict):
    """Typed representation of a contact for static type checking and serialization."""

    name: str
    phones: List[str]
    birthday: Optional[str]


class Record:
    def __init__(self, name: str):
        # Name validation through the Name class
        self.name = Name(name)
        # Creating an empty list of phones
        self.phones: List[Phone] = []
        # Birthday defaults to None
        self.birthday: Optional[Birthday] = None
        # Email defaults to None (for future extension)
        self.email: Optional[str] = None

    def add_phone(self, phone: str) -> None:
        new_phone = Phone(phone)
        # Checking for duplicates (normalized value)
        for p in self.phones:
            if p.value == new_phone.value:
                raise ValueError("Phone already exists in contact")
        self.phones.append(new_phone)

    def remove_phone(self, phone: str) -> None:
        target_phone = Phone(phone)
        for p in self.phones:
            if p.value == target_phone.value:
                self.phones.remove(p)
                return
        raise ValueError("Phone not found in contact")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        old_phone_obj = Phone(old_phone)
        new_phone_obj = Phone(new_phone)
        # Checking if old_phone exists
        for index, p in enumerate(self.phones):
            if p.value == old_phone_obj.value:
                # Checking if new_phone already exists
                if any(phone.value == new_phone_obj.value for phone in self.phones):
                    raise ValueError("New phone already exists in contact")
                # Updating the value
                self.phones[index] = new_phone_obj
                return
        raise ValueError("Old phone not found in contact")

    def find_phone(self, phone: str) -> Optional[Phone]:
        target_phone = Phone(phone)
        for p in self.phones:
            if p.value == target_phone.value:
                return p
        return None

    def add_birthday(self, birthday: str) -> None:
        """Add a birthday to the record."""
        self.birthday = Birthday(birthday)

    def to_dict(self) -> Dict[str, Any]:
        birthday_value = getattr(self, "birthday", None)
        return {
            "name": self.name.value,
            "phones": [p.value for p in getattr(self, "phones", [])],
            "birthday": (
                birthday_value.date.strftime("%d.%m.%Y") if birthday_value else None
            ),
        }

    def to_typed_dict(self) -> ContactData:
        """Return a TypedDict representation of the record."""
        return {
            "name": self.name.value,
            "phones": [p.value for p in self.phones],
            "birthday": self.birthday.value if self.birthday else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Record":
        record = cls(data["name"])
        for phone in data.get("phones", []):
            record.add_phone(phone)
        if data.get("birthday"):
            record.birthday = Birthday(data["birthday"])
        return record

    def __str__(self) -> str:
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"
