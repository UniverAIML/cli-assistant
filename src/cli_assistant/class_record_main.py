from typing import List, Optional
from cli_assistant.base_field_classes import Name, Phone, Birthday

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
            
    def find_phone(self, phone: str):
        target_phone = Phone(phone)
        for p in self.phones:
            if p.value == target_phone.value:
                return p
        return None