"""
Operations Manager for Personal Assistant.

This module provides a unified interface for all contact and note operations
that can be used by both the interactive menu and AI assistant.
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import re
import sys
import os

# Add the parent directory to the Python path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.contact_models import AddressBook, Record
from database.note_models import NotesManager, Note
from database.data_manager import DataManager


class OperationsManager:
    """
    Unified manager for all contact and note operations.

    This class provides a clean interface for all operations that can be used
    by both the interactive menu system and the AI assistant.
    """

    def __init__(self) -> None:
        """Initialize the operations manager."""
        self.data_manager = DataManager()
        self.address_book, self.notes_manager = self.data_manager.load_data()

    def save_data(self) -> bool:
        """Save all data to disk."""
        result = self.data_manager.save_data(self.address_book, self.notes_manager)
        return bool(result)

    def get_data_summary(self) -> Dict[str, int]:
        """Get summary of loaded data."""
        return {
            "contacts": len(self.address_book.data),
            "notes": len(self.notes_manager.data),
        }

    # Contact Operations
    def add_contact(
        self,
        name: str,
        phones: Optional[List[str]] = None,
        birthday: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a new contact.

        Args:
            name: Contact name
            phones: List of phone numbers
            birthday: Birthday in DD.MM.YYYY format

        Returns:
            Dict with success status and message
        """
        try:
            # Check if contact already exists
            existing_record = self.address_book.find(name)
            if existing_record:
                return {
                    "success": False,
                    "message": f"Contact '{name}' already exists",
                    "existing": True,
                }

            # Create new record
            record = Record(name)

            # Add phones if provided
            if phones:
                for phone in phones:
                    try:
                        record.add_phone(phone)
                    except ValueError as e:
                        return {
                            "success": False,
                            "message": f"Invalid phone number '{phone}': {e}",
                        }

            # Add birthday if provided
            if birthday:
                try:
                    record.add_birthday(birthday)
                except ValueError as e:
                    return {
                        "success": False,
                        "message": f"Invalid birthday format: {e}",
                    }

            # Add to address book
            self.address_book.add_record(record)

            # Save data to file
            save_success = self.save_data()
            if not save_success:
                return {
                    "success": False,
                    "message": f"Contact '{name}' added but failed to save to file",
                }

            return {
                "success": True,
                "message": f"Contact '{name}' added successfully",
                "record": record,
            }

        except ValueError as e:
            return {"success": False, "message": f"Error creating contact: {e}"}

    def search_contacts(self, query: str) -> List[Record]:
        """
        Search contacts by name or phone.

        Args:
            query: Search query

        Returns:
            List of matching records
        """
        query = query.lower()
        results = []

        for record in self.address_book.data.values():
            # Search in name
            if query in record.name.value.lower():
                results.append(record)
                continue

            # Search in phone numbers
            for phone in record.phones:
                if query in phone.value:
                    results.append(record)
                    break

        return results

    def get_all_contacts(self) -> List[Record]:
        """Get all contacts."""
        return list(self.address_book.data.values())

    def get_contact_by_name(self, name: str) -> Optional[Record]:
        """Get contact by name."""
        result = self.address_book.find(name)
        return result if isinstance(result, Record) else None

    def edit_contact(self, name: str, action: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Edit an existing contact.

        Args:
            name: Contact name
            action: Action to perform (add_phone, remove_phone, change_phone, add_birthday)
            **kwargs: Additional parameters based on action

        Returns:
            Dict with success status and message
        """
        record = self.address_book.find(name)
        if not record:
            return {"success": False, "message": f"Contact '{name}' not found"}

        try:
            if action == "add_phone":
                phone = kwargs.get("phone")
                if not phone:
                    return {"success": False, "message": "Phone number is required"}
                record.add_phone(phone)
                self.save_data()
                return {
                    "success": True,
                    "message": f"Phone '{phone}' added successfully",
                }

            elif action == "remove_phone":
                phone = kwargs.get("phone")
                if not phone:
                    return {"success": False, "message": "Phone number is required"}
                record.remove_phone(phone)
                self.save_data()
                return {
                    "success": True,
                    "message": f"Phone '{phone}' removed successfully",
                }

            elif action == "change_phone":
                old_phone = kwargs.get("phone")
                new_phone = kwargs.get("new_phone")
                if not old_phone or not new_phone:
                    return {
                        "success": False,
                        "message": "Both old and new phone numbers are required",
                    }
                record.edit_phone(old_phone, new_phone)
                self.save_data()
                return {
                    "success": True,
                    "message": f"Phone changed from '{old_phone}' to '{new_phone}'",
                }

            elif action == "add_birthday":
                birthday = kwargs.get("birthday")
                if not birthday:
                    return {"success": False, "message": "Birthday is required"}
                record.add_birthday(birthday)
                self.save_data()
                return {"success": True, "message": f"Birthday set to '{birthday}'"}

            else:
                return {"success": False, "message": f"Unknown action: {action}"}

        except ValueError as e:
            return {"success": False, "message": str(e)}

    def delete_contact(self, name: str) -> Dict[str, Any]:
        """
        Delete a contact.

        Args:
            name: Contact name

        Returns:
            Dict with success status and message
        """
        try:
            self.address_book.delete(name)
            self.save_data()
            return {
                "success": True,
                "message": f"Contact '{name}' deleted successfully",
            }
        except ValueError as e:
            return {"success": False, "message": str(e)}

    def get_upcoming_birthdays(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get contacts with upcoming birthdays.

        Args:
            days: Number of days ahead to check

        Returns:
            List of contact data with upcoming birthdays
        """
        result = self.address_book.get_upcoming_birthdays(days)
        return result if isinstance(result, list) else []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about contacts and notes.

        Returns:
            Dict with statistics
        """
        contact_count = len(self.address_book.data)
        note_count = len(self.notes_manager.data)

        # Count contacts with birthdays
        contacts_with_birthdays = sum(
            1 for record in self.address_book.data.values() if record.birthday
        )

        # Count contacts with phones
        contacts_with_phones = sum(
            1 for record in self.address_book.data.values() if record.phones
        )

        # Count notes with tags
        notes_with_tags = sum(
            1 for note in self.notes_manager.data.values() if note.tags
        )

        return {
            "total_contacts": contact_count,
            "total_notes": note_count,
            "contacts_with_birthdays": contacts_with_birthdays,
            "contacts_with_phones": contacts_with_phones,
            "notes_with_tags": notes_with_tags,
        }

    # Note Operations
    def add_note(
        self, title: str, content: str, tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a new note.

        Args:
            title: Note title
            content: Note content
            tags: List of tags

        Returns:
            Dict with success status and message
        """
        try:
            if tags is None:
                tags = []

            note_id = self.notes_manager.create_note(title, content, tags)
            
            # Save data to file
            save_success = self.save_data()
            if not save_success:
                return {
                    "success": False,
                    "message": f"Note '{title}' added but failed to save to file",
                }
            
            return {
                "success": True,
                "message": f"Note '{title}' added successfully",
                "note_id": note_id,
            }
        except ValueError as e:
            return {"success": False, "message": f"Error creating note: {e}"}

    def search_notes(self, query: str) -> Dict[str, Note]:
        """
        Search notes by title, content, or tags.

        Args:
            query: Search query

        Returns:
            Dict of matching notes
        """
        result = self.notes_manager.search_notes(query)
        return result if isinstance(result, dict) else {}

    def get_all_notes(self) -> Dict[str, Note]:
        """Get all notes."""
        result = self.notes_manager.data
        return result if isinstance(result, dict) else {}

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """Get note by ID."""
        result = self.notes_manager.find_note(note_id)
        return result if isinstance(result, Note) else None

    def edit_note(self, note_id: str, action: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Edit an existing note.

        Args:
            note_id: Note ID
            action: Action to perform (edit_title, edit_content, add_tag, remove_tag)
            **kwargs: Additional parameters based on action

        Returns:
            Dict with success status and message
        """
        note = self.notes_manager.find_note(note_id)
        if not note:
            return {"success": False, "message": f"Note with ID '{note_id}' not found"}

        try:
            if action == "edit_title":
                title = kwargs.get("title")
                if not title:
                    return {"success": False, "message": "Title is required"}
                note.title = title
                note.updated_at = datetime.now().isoformat()
                self.save_data()
                return {"success": True, "message": "Title updated successfully"}

            elif action == "edit_content":
                content = kwargs.get("content")
                if content is None:
                    return {"success": False, "message": "Content is required"}
                note.content = content
                note.updated_at = datetime.now().isoformat()
                self.save_data()
                return {"success": True, "message": "Content updated successfully"}

            elif action == "add_tag":
                tag = kwargs.get("tag")
                if not tag:
                    return {"success": False, "message": "Tag is required"}
                note.add_tag(tag)
                self.save_data()
                return {"success": True, "message": f"Tag '{tag}' added successfully"}

            elif action == "remove_tag":
                tag = kwargs.get("tag")
                if not tag:
                    return {"success": False, "message": "Tag is required"}
                note.remove_tag(tag)
                self.save_data()
                return {"success": True, "message": f"Tag '{tag}' removed successfully"}

            else:
                return {"success": False, "message": f"Unknown action: {action}"}

        except ValueError as e:
            return {"success": False, "message": str(e)}

    def delete_note(self, note_id: str) -> Dict[str, Any]:
        """
        Delete a note.

        Args:
            note_id: Note ID

        Returns:
            Dict with success status and message
        """
        if self.notes_manager.delete_note(note_id):
            self.save_data()
            return {"success": True, "message": "Note deleted successfully"}
        else:
            return {
                "success": False,
                "message": "Note not found or could not be deleted",
            }

    def search_notes_by_tag(self, tag: str) -> Dict[str, Note]:
        """
        Search notes by tag.

        Args:
            tag: Tag to search for

        Returns:
            Dict of matching notes
        """
        result = self.notes_manager.get_notes_by_tag(tag)
        return result if isinstance(result, dict) else {}

    def global_search(self, query: str) -> Dict[str, Any]:
        """
        Search across both contacts and notes.

        Args:
            query: Search query

        Returns:
            Dict with contacts and notes results
        """
        return {
            "contacts": self.search_contacts(query),
            "notes": self.search_notes(query),
        }

    # View operations
    def view_contact_details(self, name: str) -> Dict[str, Any]:
        """
        Get detailed view of a contact.

        Args:
            name: Contact name

        Returns:
            Dict with contact details or error message
        """
        record = self.address_book.find(name)
        if not record:
            return {"success": False, "message": f"Contact '{name}' not found"}

        return {
            "success": True,
            "contact": {
                "name": record.name.value,
                "phones": [phone.value for phone in record.phones],
                "birthday": record.birthday.value if record.birthday else None,
            },
        }

    def view_note_details(self, note_id: str) -> Dict[str, Any]:
        """
        Get detailed view of a note.

        Args:
            note_id: Note ID

        Returns:
            Dict with note details or error message
        """
        note = self.notes_manager.find_note(note_id)
        if not note:
            return {"success": False, "message": f"Note with ID '{note_id}' not found"}

        return {
            "success": True,
            "note": {
                "id": note_id,
                "title": note.title,
                "content": note.content,
                "tags": note.tags,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            },
        }
