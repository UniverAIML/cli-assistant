"""Personal Assistant module for contacts and notes management."""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, date

from database.contact_models import AddressBook, Record
from database.note_models import NotesManager, Note
from database.data_manager import DataManager


class PersonalAssistant:
    """
    Personal Assistant for managing contacts and notes.

    This class provides a high-level interface for managing contacts
    and notes with data persistence.
    """

    def __init__(
        self, contacts_file: str = "contacts.json", notes_file: str = "notes.json"
    ):
        """
        Initialize Personal Assistant.

        Args:
            contacts_file: Path to contacts file
            notes_file: Path to notes file
        """
        self.data_manager = DataManager(contacts_file, notes_file)
        self.address_book, self.notes_manager = self.data_manager.load_data()

    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone number format.

        Args:
            phone: Phone number string

        Returns:
            bool: True if valid, False otherwise
        """
        if not phone:
            return False

        # Remove all non-digits
        digits_only = re.sub(r"\D", "", phone)

        # Valid phone number should have exactly 10 digits
        return len(digits_only) == 10

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email string

        Returns:
            bool: True if valid, False otherwise
        """
        if not email:
            return False

        # Basic email validation regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, email))

    def search_contacts(self, query: str) -> List[Record]:
        """
        Search contacts by name or phone.

        Args:
            query: Search query

        Returns:
            List of matching records
        """
        results = []
        query_lower = query.lower()

        for record in self.address_book.data.values():
            # Search by name
            if query_lower in record.name.value.lower():
                results.append(record)
                continue

            # Search by phone
            if record.phones:
                for phone in record.phones:
                    if query in phone.value:
                        results.append(record)
                        break

        return results

    def search_notes(self, query: str) -> List[str]:
        """
        Search notes by title, content, or tags.

        Args:
            query: Search query

        Returns:
            List of matching note IDs
        """
        results = []
        query_lower = query.lower()

        for note_id, note in self.notes_manager.data.items():
            # Search by title
            if query_lower in note.title.lower():
                results.append(note_id)
                continue

            # Search by content
            if query_lower in note.content.lower():
                results.append(note_id)
                continue

            # Search by tags
            if any(query_lower in tag.lower() for tag in note.tags):
                results.append(note_id)
                continue

        return results

    def get_upcoming_birthdays(self, days: int = 7) -> List[Dict[str, str]]:
        """
        Get contacts with upcoming birthdays.

        Args:
            days: Number of days to look ahead (currently not used, fixed to 7)

        Returns:
            List of records with upcoming birthdays
        """
        return self.address_book.get_upcoming_birthdays()

    def save_data(self) -> bool:
        """
        Save all data to files.

        Returns:
            bool: True if successful, False otherwise
        """
        return self.data_manager.save_data(self.address_book, self.notes_manager)

    def display_contacts_table(self, contacts: List[Record]) -> None:
        """
        Display contacts in a table format.

        Args:
            contacts: List of contact records
        """
        if not contacts:
            print("No contacts found.")
            return

        print("\n=== Contacts ===")
        for record in contacts:
            print(f"Name: {record.name.value}")
            if record.phones:
                print(f"Phones: {', '.join(phone.value for phone in record.phones)}")
            if record.birthday:
                print(f"Birthday: {record.birthday.value}")
            print("-" * 20)

    def display_notes_table(self, notes: Optional[Dict[str, Note]] = None) -> None:
        """
        Display notes in a table format.

        Args:
            notes: Dictionary of notes, if None displays all notes
        """
        if notes is None:
            notes = self.notes_manager.data

        if not notes:
            print("No notes found.")
            return

        print("\n=== Notes ===")
        for note_id, note in notes.items():
            print(f"ID: {note_id}")
            print(f"Title: {note.title}")
            print(f"Content: {note.content}")
            if note.tags:
                print(f"Tags: {', '.join(note.tags)}")
            print(f"Created: {note.created_at}")
            print(f"Updated: {note.updated_at}")
            print("-" * 20)
