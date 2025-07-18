"""
Assistant Stub Class - contains method stubs for all PersonalAssistant functionality.
This class provides a template for implementing assistant features with AI integration.
"""

from typing import List, Dict, Optional, Any, cast, Union
from datetime import datetime
import json
import re

# Import the real AddressBook classes using absolute imports
from database.contact_models import AddressBook, Record, Name, Phone, Birthday


class AssistantStub:
    """
    Stub class containing all methods from PersonalAssistant with logging functionality.
    Each method logs its name and parameters when called.
    """

    def __init__(self) -> None:
        """Initialize the assistant stub."""
        self.address_book = AddressBook()
        self._log_method_call("__init__", {})

    def _log_method_call(self, method_name: str, params: Dict[str, Any]) -> None:
        """Log method calls with parameters."""
        # Debug logging disabled
        pass

    # Data retrieval methods
    def get_upcoming_birthdays(self, days: int = 7) -> List[Any]:
        """Get contacts with upcoming birthdays."""
        params = {"days": days}
        self._log_method_call("get_upcoming_birthdays", params)
        # Note: The actual AddressBook.get_upcoming_birthdays() doesn't take days parameter
        # It's hardcoded to 7 days
        result = self.address_book.get_upcoming_birthdays()
        return cast(List[Any], result)

    def search_contacts(self, query: str) -> List[Any]:
        """Search contacts by name or phone."""
        params = {"query": query}
        self._log_method_call("search_contacts", params)

        # Implement search functionality since AddressBook doesn't have it
        results = []
        query_lower = query.lower()

        for record in self.address_book.get_all_records().values():
            # Search by name
            if query_lower in record.name.value.lower():
                results.append(record)
                continue

            # Search by phone
            for phone in record.phones:
                if query in phone.value:
                    results.append(record)
                    break

        return cast(List[Any], results)

    def search_notes(self, query: str) -> Dict[str, Any]:
        """Search notes by title, content, or tags."""
        params = {"query": query}
        self._log_method_call("search_notes", params)
        return {}  # Stub returns empty dict

    # Contact management methods
    def add_contact(
        self,
        name: str,
        phones: Optional[List[str]] = None,
        birthday: Optional[str] = None,
    ) -> str:
        """Add a new contact with validation."""

        try:
            # Create new record
            record = Record(name)

            # Add phones if provided
            if phones:
                for phone in phones:
                    if phone:  # Skip empty phone numbers
                        record.add_phone(phone)

            # Add birthday if provided
            if birthday:
                record.add_birthday(birthday)

            # Add to address book
            self.address_book.add_record(record)

            phone_count = len(phones) if phones else 0
            return f"Contact '{name}' added successfully with {phone_count} phone(s)."

        except ValueError as e:
            return f"Error adding contact: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    def view_contact_details(self, name: Optional[str] = None) -> str:
        """View detailed information about a contact."""
        params = {"name": name}
        self._log_method_call("view_contact_details", params)

        # If no name provided, this is a stub call from old tests
        if name is None:
            return "view_contact_details() called - stub mode (no parameters provided)"

        record = self.address_book.find(name)
        if record:
            return str(record)
        else:
            return f"Contact '{name}' not found."

    def edit_contact(
        self,
        name: Optional[str] = None,
        field: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
    ) -> str:
        """Edit an existing contact."""
        params = {
            "name": name,
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
        }
        self._log_method_call("edit_contact", params)

        # If no name provided, this is a stub call from old tests
        if name is None:
            return "edit_contact() called - stub mode (no parameters provided)"

        record = self.address_book.find(name)
        if not record:
            return f"Contact '{name}' not found."

        try:
            if field and field.lower() == "phone":
                if old_value and new_value:
                    record.edit_phone(old_value, new_value)
                    return f"Phone updated for '{name}'."
                elif new_value:
                    record.add_phone(new_value)
                    return f"Phone added to '{name}'."
                else:
                    return "Please provide old_value and new_value for phone editing."

            elif field and field.lower() == "birthday":
                if new_value:
                    record.add_birthday(new_value)
                    return f"Birthday updated for '{name}'."
                else:
                    return "Please provide new birthday value."

            else:
                return f"Field '{field}' is not editable. Available fields: phone, birthday"

        except ValueError as e:
            return f"Error editing contact: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    def delete_contact(self, name: Optional[str] = None) -> str:
        """Delete a contact."""
        params = {"name": name}
        self._log_method_call("delete_contact", params)

        # If no name provided, this is a stub call from old tests
        if name is None:
            return "delete_contact() called - stub mode (no parameters provided)"

        try:
            self.address_book.delete(name)
            return f"Contact '{name}' deleted successfully."
        except ValueError:
            return f"Contact '{name}' not found."

    # Note management methods
    def add_note(self) -> None:
        """Add a new note with tags."""
        self._log_method_call("add_note", {})

    def view_note_details(self) -> None:
        """View detailed information about a note."""
        self._log_method_call("view_note_details", {})

    def edit_note(self) -> None:
        """Edit an existing note."""
        self._log_method_call("edit_note", {})

    def delete_note(self) -> None:
        """Delete a note."""
        self._log_method_call("delete_note", {})
