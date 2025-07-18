"""Function Executor module for AI Assistant using OperationsManager."""

from typing import Dict, Any, List, Optional
import logging

from .operations_manager import OperationsManager
from .function_definitions import FunctionDefinitions


class FunctionResult:
    """Value object representing the result of a function execution."""

    def __init__(self, success: bool, message: str, data: Optional[Any] = None):
        self.success = success
        self.message = message
        self.data = data

    def __str__(self) -> str:
        return self.message


class FunctionExecutor:
    """Executor for function calls using OperationsManager."""

    def __init__(self, operations: Optional[OperationsManager] = None):
        """Initialize the function executor."""
        self.operations = operations or OperationsManager()
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute_function_call(
        self, function_call: Dict[str, Any], user_input: str
    ) -> str:
        """Execute a function call and return formatted result."""
        try:
            function_name = function_call.get("function")
            arguments = function_call.get("arguments", {})

            if not function_name:
                return "❌ No function specified"

            # Execute the function
            result = self._execute_function(function_name, arguments)

            # Save data after successful operations
            if result.success:
                self.operations.save_data()

            return str(result)

        except Exception as e:
            self.logger.error(f"Error executing function call: {e}")
            return f"❌ Error executing function: {str(e)}"

    def _execute_function(
        self, function_name: str, arguments: Dict[str, Any]
    ) -> FunctionResult:
        """Execute a specific function by name."""

        # Contact functions
        if function_name == "add_contact":
            return self._add_contact(arguments)
        elif function_name == "search_contacts":
            return self._search_contacts(arguments)
        elif function_name == "show_contacts":
            return self._show_contacts(arguments)
        elif function_name == "edit_contact":
            return self._edit_contact(arguments)
        elif function_name == "delete_contact":
            return self._delete_contact(arguments)
        elif function_name == "view_contact_details":
            return self._view_contact_details(arguments)
        elif function_name == "get_upcoming_birthdays":
            return self._get_upcoming_birthdays(arguments)

        # Note functions
        elif function_name == "add_note":
            return self._add_note(arguments)
        elif function_name == "search_notes":
            return self._search_notes(arguments)
        elif function_name == "show_notes":
            return self._show_notes(arguments)
        elif function_name == "edit_note":
            return self._edit_note(arguments)
        elif function_name == "delete_note":
            return self._delete_note(arguments)
        elif function_name == "view_note_details":
            return self._view_note_details(arguments)
        elif function_name == "search_notes_by_tag":
            return self._search_notes_by_tag(arguments)

        # General functions
        elif function_name == "global_search":
            return self._global_search(arguments)
        elif function_name == "get_statistics":
            return self._get_statistics(arguments)

        else:
            return FunctionResult(False, f"❌ Unknown function: {function_name}")

    # Contact function implementations
    def _add_contact(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Add a new contact."""
        name = arguments.get("name")
        phones = arguments.get("phones", [])
        birthday = arguments.get("birthday")

        if not name:
            return FunctionResult(False, "❌ Name is required")

        result = self.operations.add_contact(name, phones, birthday)

        if result["success"]:
            return FunctionResult(True, f"✅ {result['message']}")
        else:
            return FunctionResult(False, f"❌ {result['message']}")

    def _search_contacts(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Search contacts by name or phone."""
        query = arguments.get("query", "")

        if not query:
            return FunctionResult(False, "❌ Search query is required")

        contacts = self.operations.search_contacts(query)

        if not contacts:
            return FunctionResult(True, f"🔍 No contacts found matching '{query}'")

        # Format results
        result_text = f"🔍 Found {len(contacts)} contact(s) matching '{query}':\\n"
        for contact in contacts:
            phones = (
                "; ".join(phone.value for phone in contact.phones)
                if contact.phones
                else "No phones"
            )
            birthday = contact.birthday.value if contact.birthday else "No birthday"
            result_text += f"• {contact.name.value} - {phones} - {birthday}\\n"

        return FunctionResult(True, result_text)

    def _show_contacts(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Show all contacts."""
        contacts = self.operations.get_all_contacts()

        if not contacts:
            return FunctionResult(True, "📋 No contacts found")

        result_text = f"📋 All contacts ({len(contacts)} total):\\n"
        for contact in contacts:
            phones = (
                "; ".join(phone.value for phone in contact.phones)
                if contact.phones
                else "No phones"
            )
            birthday = contact.birthday.value if contact.birthday else "No birthday"
            result_text += f"• {contact.name.value} - {phones} - {birthday}\\n"

        return FunctionResult(True, result_text)

    def _edit_contact(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Edit an existing contact."""
        name = arguments.get("name")
        action = arguments.get("action")

        if not name or not action:
            return FunctionResult(False, "❌ Name and action are required")

        # Get additional parameters based on action
        kwargs = {}
        if action in ["add_phone", "remove_phone"]:
            kwargs["phone"] = arguments.get("phone")
        elif action == "change_phone":
            kwargs["phone"] = arguments.get("phone")
            kwargs["new_phone"] = arguments.get("new_phone")
        elif action == "add_birthday":
            kwargs["birthday"] = arguments.get("birthday")

        result = self.operations.edit_contact(name, action, **kwargs)

        if result["success"]:
            return FunctionResult(True, f"✅ {result['message']}")
        else:
            return FunctionResult(False, f"❌ {result['message']}")

    def _delete_contact(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Delete a contact."""
        name = arguments.get("name")

        if not name:
            return FunctionResult(False, "❌ Name is required")

        result = self.operations.delete_contact(name)

        if result["success"]:
            return FunctionResult(True, f"✅ {result['message']}")
        else:
            return FunctionResult(False, f"❌ {result['message']}")

    def _view_contact_details(self, arguments: Dict[str, Any]) -> FunctionResult:
        """View detailed information about a contact."""
        name = arguments.get("name")

        if not name:
            return FunctionResult(False, "❌ Name is required")

        result = self.operations.view_contact_details(name)

        if not result["success"]:
            return FunctionResult(False, f"❌ {result['message']}")

        contact = result["contact"]
        result_text = f"👤 Contact Details for '{contact['name']}':\\n"

        if contact["phones"]:
            result_text += f"📞 Phones: {', '.join(contact['phones'])}\\n"
        else:
            result_text += "📞 No phone numbers\\n"

        if contact["birthday"]:
            result_text += f"🎂 Birthday: {contact['birthday']}\\n"
        else:
            result_text += "🎂 No birthday set\\n"

        return FunctionResult(True, result_text)

    def _get_upcoming_birthdays(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Get contacts with upcoming birthdays."""
        days = arguments.get("days", 7)

        try:
            days = int(days)
        except (ValueError, TypeError):
            days = 7

        upcoming = self.operations.get_upcoming_birthdays()

        if not upcoming:
            return FunctionResult(
                True, f"🎂 No upcoming birthdays in the next {days} days"
            )

        result_text = f"🎂 Upcoming birthdays ({len(upcoming)} found):\\n"
        for birthday_info in upcoming:
            result_text += (
                f"• {birthday_info['name']} - {birthday_info['congratulation_date']}\\n"
            )

        return FunctionResult(True, result_text)

    # Note function implementations
    def _add_note(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Add a new note."""
        title = arguments.get("title")
        content = arguments.get("content", "")
        tags = arguments.get("tags", [])

        if not title:
            return FunctionResult(False, "❌ Title is required")

        result = self.operations.add_note(title, content, tags)

        if result["success"]:
            return FunctionResult(True, f"✅ {result['message']}")
        else:
            return FunctionResult(False, f"❌ {result['message']}")

    def _search_notes(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Search notes by title, content, or tags."""
        query = arguments.get("query", "")

        if not query:
            return FunctionResult(False, "❌ Search query is required")

        notes = self.operations.search_notes(query)

        if not notes:
            return FunctionResult(True, f"🔍 No notes found matching '{query}'")

        result_text = f"🔍 Found {len(notes)} note(s) matching '{query}':\\n"
        for note_id, note in notes.items():
            content_preview = (
                note.content[:50] + "..." if len(note.content) > 50 else note.content
            )
            tags_str = ", ".join(note.tags) if note.tags else "No tags"
            result_text += (
                f"• {note.title} ({note_id}) - {content_preview} - Tags: {tags_str}\\n"
            )

        return FunctionResult(True, result_text)

    def _show_notes(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Show all notes."""
        notes = self.operations.get_all_notes()

        if not notes:
            return FunctionResult(True, "📄 No notes found")

        result_text = f"📄 All notes ({len(notes)} total):\\n"
        for note_id, note in notes.items():
            content_preview = (
                note.content[:50] + "..." if len(note.content) > 50 else note.content
            )
            tags_str = ", ".join(note.tags) if note.tags else "No tags"
            result_text += (
                f"• {note.title} ({note_id}) - {content_preview} - Tags: {tags_str}\\n"
            )

        return FunctionResult(True, result_text)

    def _edit_note(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Edit an existing note."""
        note_id = arguments.get("note_id")
        action = arguments.get("action")

        if not note_id or not action:
            return FunctionResult(False, "❌ Note ID and action are required")

        # Get additional parameters based on action
        kwargs = {}
        if action == "edit_title":
            kwargs["title"] = arguments.get("title")
        elif action == "edit_content":
            kwargs["content"] = arguments.get("content")
        elif action in ["add_tag", "remove_tag"]:
            kwargs["tag"] = arguments.get("tag")

        result = self.operations.edit_note(note_id, action, **kwargs)

        if result["success"]:
            return FunctionResult(True, f"✅ {result['message']}")
        else:
            return FunctionResult(False, f"❌ {result['message']}")

    def _delete_note(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Delete a note."""
        note_id = arguments.get("note_id")

        if not note_id:
            return FunctionResult(False, "❌ Note ID is required")

        result = self.operations.delete_note(note_id)

        if result["success"]:
            return FunctionResult(True, f"✅ {result['message']}")
        else:
            return FunctionResult(False, f"❌ {result['message']}")

    def _view_note_details(self, arguments: Dict[str, Any]) -> FunctionResult:
        """View detailed information about a note."""
        note_id = arguments.get("note_id")

        if not note_id:
            return FunctionResult(False, "❌ Note ID is required")

        result = self.operations.view_note_details(note_id)

        if not result["success"]:
            return FunctionResult(False, f"❌ {result['message']}")

        note = result["note"]
        result_text = f"📝 Note Details for '{note['title']}' (ID: {note['id']}):\\n"
        result_text += f"Content: {note['content']}\\n"

        if note["tags"]:
            result_text += f"🏷️  Tags: {', '.join(note['tags'])}\\n"
        else:
            result_text += "🏷️  No tags\\n"

        result_text += f"📅 Created: {note['created_at']}\\n"

        if note["updated_at"]:
            result_text += f"📝 Updated: {note['updated_at']}\\n"

        return FunctionResult(True, result_text)

    def _search_notes_by_tag(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Search notes by specific tag."""
        tag = arguments.get("tag")

        if not tag:
            return FunctionResult(False, "❌ Tag is required")

        notes = self.operations.search_notes_by_tag(tag)

        if not notes:
            return FunctionResult(True, f"🏷️  No notes found with tag '{tag}'")

        result_text = f"🏷️  Found {len(notes)} note(s) with tag '{tag}':\\n"
        for note_id, note in notes.items():
            content_preview = (
                note.content[:50] + "..." if len(note.content) > 50 else note.content
            )
            result_text += f"• {note.title} ({note_id}) - {content_preview}\\n"

        return FunctionResult(True, result_text)

    # General function implementations
    def _global_search(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Search across both contacts and notes."""
        query = arguments.get("query", "")

        if not query:
            return FunctionResult(False, "❌ Search query is required")

        results = self.operations.global_search(query)

        contacts = results["contacts"]
        notes = results["notes"]

        if not contacts and not notes:
            return FunctionResult(True, f"🔍 No results found for '{query}'")

        result_text = f"🔍 Global search results for '{query}':\\n"

        if contacts:
            result_text += f"\\n📞 Contacts ({len(contacts)} found):\\n"
            for contact in contacts:
                phones = (
                    "; ".join(phone.value for phone in contact.phones)
                    if contact.phones
                    else "No phones"
                )
                result_text += f"• {contact.name.value} - {phones}\\n"

        if notes:
            result_text += f"\\n📝 Notes ({len(notes)} found):\\n"
            for note_id, note in notes.items():
                content_preview = (
                    note.content[:50] + "..."
                    if len(note.content) > 50
                    else note.content
                )
                result_text += f"• {note.title} ({note_id}) - {content_preview}\\n"

        return FunctionResult(True, result_text)

    def _get_statistics(self, arguments: Dict[str, Any]) -> FunctionResult:
        """Get statistics about contacts and notes."""
        stats = self.operations.get_statistics()

        result_text = "📊 Statistics:\\n"
        result_text += f"📞 Total contacts: {stats['total_contacts']}\\n"
        result_text += f"📝 Total notes: {stats['total_notes']}\\n"
        result_text += f"📞 Contacts with phones: {stats['contacts_with_phones']}\\n"
        result_text += (
            f"🎂 Contacts with birthdays: {stats['contacts_with_birthdays']}\\n"
        )
        result_text += f"🏷️  Notes with tags: {stats['notes_with_tags']}\\n"

        return FunctionResult(True, result_text)
