"""
Assistant Stub Class - contains method stubs for all PersonalAssistant functionality.
This class provides a template for implementing assistant features with AI integration.
"""

from typing import List, Dict, Optional, Any, cast
from datetime import datetime
import json
import re

# Import the real AddressBook classes using absolute imports
from address_book.class_addressBook import AddressBook
from address_book.class_record_main import Record
from address_book.base_field_classes import Name, Phone, Birthday


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

    # Core functionality methods
    def save_data(self, filename: str = "address_book.json") -> str:
        """Save address book and notes data."""
        params = {"filename": filename}
        self._log_method_call("save_data", params)

        try:
            import json

            data = {
                "contacts": self.address_book.to_dict(),
                "notes": {},  # Empty for now
                "saved_at": datetime.now().isoformat(),
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return f"Data saved to {filename}"
        except Exception as e:
            return f"Error saving data: {str(e)}"

    def load_data(self, filename: str = "address_book.json") -> str:
        """Load existing data."""
        params = {"filename": filename}
        self._log_method_call("load_data", params)

        try:
            import json

            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load contacts
            if "contacts" in data:
                self.address_book.from_dict(data["contacts"])

            return f"Data loaded from {filename}"
        except FileNotFoundError:
            return f"File {filename} not found"
        except Exception as e:
            return f"Error loading data: {str(e)}"

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format (10 digits)."""
        params = {"phone": phone}
        self._log_method_call("validate_phone", params)
        try:
            Phone(phone)  # If this doesn't raise an exception, phone is valid
            return True
        except ValueError:
            return False

    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        params = {"email": email}
        self._log_method_call("validate_email", params)
        # Simple email validation for now
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    # Display methods
    def display_welcome(self) -> None:
        """Display beautiful welcome screen."""
        self._log_method_call("display_welcome", {})

    def display_contacts_table(self, records: Optional[List[Any]] = None) -> None:
        """Display contacts in a beautiful table."""
        if records is None:
            records = self.address_book.get_all_records()

        params = {"records_count": len(records) if records else 0}
        self._log_method_call("display_contacts_table", params)

        if not records:
            print("No contacts found.")
            return

        print(f"\n{'='*60}")
        print(f"{'CONTACTS':^60}")
        print(f"{'='*60}")
        print(f"{'Name':<20} {'Phone(s)':<20} {'Birthday':<15}")
        print(f"{'-'*60}")

        for record in records:
            # Handle both Record objects and dict objects for backward compatibility
            if hasattr(record, "name"):  # Record object
                name = record.name.value
                phones_str = (
                    "; ".join([p.value for p in record.phones])
                    if record.phones
                    else "N/A"
                )
                birthday_str = record.birthday.value if record.birthday else "N/A"
            else:  # Dict object (for compatibility with old tests)
                name = record.get("name", "Unknown")
                phones_str = record.get("phone", "N/A")
                birthday_str = record.get("birthday", "N/A")

            print(f"{name:<20} {phones_str:<20} {birthday_str:<15}")

        print(f"{'='*60}")
        print(f"Total contacts: {len(records)}")
        print()

    def display_notes_table(self, notes_dict: Optional[Dict[str, Any]] = None) -> None:
        """Display notes in a beautiful table."""
        params = {"notes_count": len(notes_dict) if notes_dict else 0}
        self._log_method_call("display_notes_table", params)

    # Data retrieval methods
    def get_upcoming_birthdays(self, days: int = 7) -> List[Any]:
        """Get contacts with upcoming birthdays."""
        params = {"days": days}
        self._log_method_call("get_upcoming_birthdays", params)
        result = self.address_book.get_upcoming_birthdays(days)
        return cast(List[Any], result)

    def search_contacts(self, query: str) -> List[Any]:
        """Search contacts by name or phone."""
        params = {"query": query}
        self._log_method_call("search_contacts", params)
        result = self.address_book.search_contacts(query)
        return cast(List[Any], result)

    def search_notes(self, query: str) -> Dict[str, Any]:
        """Search notes by title, content, or tags."""
        params = {"query": query}
        self._log_method_call("search_notes", params)
        return {}  # Stub returns empty dict

    # Contact management methods
    def add_contact(
        self,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        birthday: Optional[str] = None,
    ) -> str:
        """Add a new contact with validation."""
        params = {"name": name, "phone": phone, "birthday": birthday}
        self._log_method_call("add_contact", params)

        # If no name provided, this is a stub call from old tests
        if name is None:
            return "add_contact() called - stub mode (no parameters provided)"

        try:
            # Create new record
            record = Record(name)

            # Add phone if provided
            if phone:
                record.add_phone(phone)

            # Add birthday if provided
            if birthday:
                record.add_birthday(birthday)

            # Add to address book
            self.address_book.add_record(record)

            return f"Contact '{name}' added successfully."

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

        if self.address_book.delete(name):
            return f"Contact '{name}' deleted successfully."
        else:
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

    # Menu methods
    def contacts_menu(self) -> None:
        """Contact management menu."""
        self._log_method_call("contacts_menu", {})

    def notes_menu(self) -> None:
        """Notes management menu."""
        self._log_method_call("notes_menu", {})

    def ai_assistant_menu(self) -> None:
        """AI Assistant menu for natural language commands."""
        self._log_method_call("ai_assistant_menu", {})

    def global_search(self) -> None:
        """Global search across contacts and notes."""
        self._log_method_call("global_search", {})

    # Main application method
    def run(self) -> None:
        """Main application loop."""
        self._log_method_call("run", {})

        # Show welcome and current state
        print("=== Personal Assistant ===")
        stats = self.get_statistics()
        print(f"Total contacts: {stats['total_contacts']}")
        print(f"Contacts with phones: {stats['contacts_with_phones']}")
        print(f"Contacts with birthdays: {stats['contacts_with_birthdays']}")

        # Show some contacts if any exist
        if stats["total_contacts"] > 0:
            print("\nCurrent contacts:")
            self.display_contacts_table()

        print("Assistant is ready for AI commands!")
        print("==========================")

    # Additional utility methods found in the original code
    def export_data(self, format_type: str = "json") -> str:
        """Export data in specified format."""
        params = {"format_type": format_type}
        self._log_method_call("export_data", params)

        try:
            if format_type.lower() == "json":
                filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                return self.save_data(filename)
            else:
                return f"Format '{format_type}' not supported. Available: json"
        except Exception as e:
            return f"Error exporting data: {str(e)}"

    def import_data(self, file_path: str) -> str:
        """Import data from file."""
        params = {"file_path": file_path}
        self._log_method_call("import_data", params)
        return self.load_data(file_path)

    def backup_data(self) -> None:
        """Create data backup."""
        self._log_method_call("backup_data", {})

    def restore_data(self, backup_path: str) -> None:
        """Restore data from backup."""
        params = {"backup_path": backup_path}
        self._log_method_call("restore_data", params)

    # Settings and configuration methods
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        self._log_method_call("get_settings", {})
        return {}

    def update_settings(self, settings: Dict[str, Any]) -> None:
        """Update application settings."""
        params = {"settings": settings}
        self._log_method_call("update_settings", params)

    def reset_settings(self) -> None:
        """Reset settings to default."""
        self._log_method_call("reset_settings", {})

    # Statistics and analytics methods
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        self._log_method_call("get_statistics", {})

        # Get stats from address book
        contact_stats = self.address_book.get_stats()

        return {
            "total_contacts": contact_stats["total_contacts"],
            "contacts_with_phones": contact_stats["with_phones"],
            "contacts_with_birthdays": contact_stats["with_birthdays"],
            "total_notes": 0,  # No notes system yet
            "last_updated": datetime.now().isoformat(),
        }

    def generate_report(self, report_type: str = "summary") -> None:
        """Generate data report."""
        params = {"report_type": report_type}
        self._log_method_call("generate_report", params)

    # Advanced search methods
    def advanced_contact_search(self, criteria: Dict[str, Any]) -> List[Any]:
        """Advanced contact search with multiple criteria."""
        params = {"criteria": criteria}
        self._log_method_call("advanced_contact_search", params)

        results = []
        all_contacts = self.address_book.get_all_records()

        for contact in all_contacts:
            matches = True

            # Check name criteria
            if "name" in criteria:
                name_query = criteria["name"].lower()
                if name_query not in contact.name.value.lower():
                    matches = False

            # Check phone criteria
            if "phone" in criteria and matches:
                phone_query = criteria["phone"]
                phone_found = any(
                    phone_query in phone.value for phone in contact.phones
                )
                if not phone_found:
                    matches = False

            # Check birthday criteria
            if "has_birthday" in criteria and matches:
                has_birthday = contact.birthday is not None
                if criteria["has_birthday"] != has_birthday:
                    matches = False

            if matches:
                results.append(contact)

        return results

    def advanced_note_search(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced note search with multiple criteria."""
        params = {"criteria": criteria}
        self._log_method_call("advanced_note_search", params)
        return {}

    # Batch operations
    def batch_add_contacts(self, contacts_data: List[Dict[str, Any]]) -> None:
        """Add multiple contacts at once."""
        params = {"contacts_count": len(contacts_data)}
        self._log_method_call("batch_add_contacts", params)

    def batch_add_notes(self, notes_data: List[Dict[str, Any]]) -> None:
        """Add multiple notes at once."""
        params = {"notes_count": len(notes_data)}
        self._log_method_call("batch_add_notes", params)

    def batch_delete_items(self, item_type: str, item_ids: List[str]) -> None:
        """Delete multiple items at once."""
        params = {"item_type": item_type, "count": len(item_ids)}
        self._log_method_call("batch_delete_items", params)

    # Natural language processing methods (AI integration)
    def parse_natural_language_command(self, command: str) -> Dict[str, Any]:
        """Parse natural language command using AI."""
        params = {"command": command}
        self._log_method_call("parse_natural_language_command", params)
        return {"intent": "unknown", "entities": [], "confidence": 0.0}

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        params = {"text": text}
        self._log_method_call("extract_entities", params)
        return {"PERSON": [], "ORG": [], "DATE": [], "PHONE": [], "EMAIL": []}

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        params = {"text": text}
        self._log_method_call("analyze_sentiment", params)
        return {"sentiment": "neutral", "confidence": 0.5}

    def auto_categorize_note(self, note_content: str) -> List[str]:
        """Auto-categorize note based on content."""
        params = {
            "note_content": (
                note_content[:50] + "..." if len(note_content) > 50 else note_content
            )
        }
        self._log_method_call("auto_categorize_note", params)
        return ["general"]

    def suggest_tags(self, text: str) -> List[str]:
        """Suggest tags for note based on content."""
        params = {"text": text[:50] + "..." if len(text) > 50 else text}
        self._log_method_call("suggest_tags", params)
        return ["suggestion1", "suggestion2"]

    # Voice and speech methods (potential future features)
    def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text."""
        params = {"audio_size": len(audio_data)}
        self._log_method_call("speech_to_text", params)
        return "transcribed text"

    def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech."""
        params = {"text": text}
        self._log_method_call("text_to_speech", params)
        return b"audio_data"

    # Integration methods
    def sync_with_cloud(self) -> None:
        """Sync data with cloud service."""
        self._log_method_call("sync_with_cloud", {})

    def export_to_calendar(self, contact_name: str) -> None:
        """Export contact birthday to calendar."""
        params = {"contact_name": contact_name}
        self._log_method_call("export_to_calendar", params)

    def send_notification(self, message: str, notification_type: str = "info") -> None:
        """Send system notification."""
        params = {"message": message, "type": notification_type}
        self._log_method_call("send_notification", params)
