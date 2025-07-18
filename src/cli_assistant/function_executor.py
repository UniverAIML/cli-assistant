"""Function Executor module implementing Command and Strategy patterns."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol
import logging

from .assistant_stub import AssistantStub
from .function_definitions import FunctionDefinitions


class FunctionResult:
    """Value object representing the result of a function execution."""

    def __init__(self, success: bool, message: str, data: Optional[Any] = None):
        self.success = success
        self.message = message
        self.data = data

    def __str__(self) -> str:
        return self.message


class CommandInterface(Protocol):
    """Protocol for command objects."""

    def execute(self) -> FunctionResult:
        """Execute the command and return result."""
        ...


class BaseCommand(ABC):
    """Abstract base class for all commands implementing Command pattern."""

    def __init__(self, assistant: AssistantStub, arguments: Dict[str, Any]):
        self.assistant = assistant
        self.arguments = arguments
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def execute(self) -> FunctionResult:
        """Execute the command and return result."""
        pass

    def _safe_execute(self, operation_name: str) -> FunctionResult:
        """Safely execute an operation with error handling."""
        try:
            return self._execute_operation()
        except Exception as e:
            error_msg = f"❌ Error executing {operation_name}: {str(e)}"
            self.logger.error(error_msg)
            return FunctionResult(False, error_msg)

    @abstractmethod
    def _execute_operation(self) -> FunctionResult:
        """Execute the specific operation logic."""
        pass


# Contact Commands
class AddContactCommand(BaseCommand):
    """Command for adding a new contact."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("add_contact")

    def _execute_operation(self) -> FunctionResult:
        name = self.arguments.get("name", "")
        phones = self.arguments.get("phones", [])
        birthday = self.arguments.get("birthday", "")

        if not name:
            return FunctionResult(False, "❌ Contact name is required")

        self.assistant.add_contact()

        message = f"✅ Successfully added contact: {name}"
        if phones:
            message += f" with {len(phones)} phone(s)"

        return FunctionResult(True, message, {"name": name, "phones": phones})


class SearchContactsCommand(BaseCommand):
    """Command for searching contacts."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("search_contacts")

    def _execute_operation(self) -> FunctionResult:
        query = self.arguments.get("query", "")
        contacts = self.assistant.search_contacts(query)

        if contacts and len(contacts) > 0:
            return FunctionResult(
                True,
                f"📞 Found {len(contacts)} contact(s) matching '{query}'",
                contacts,
            )
        else:
            return FunctionResult(False, f"❌ No contacts found matching '{query}'")


class ShowContactsCommand(BaseCommand):
    """Command for showing all contacts."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("show_contacts")

    def _execute_operation(self) -> FunctionResult:
        self.assistant.display_contacts_table()
        contacts: List[Any] = []  # Assume empty result for stub

        if contacts:
            return FunctionResult(
                True, f"📞 Here are all your contacts ({len(contacts)} total)", contacts
            )
        else:
            return FunctionResult(
                True, "📞 No contacts found. Add some contacts first!"
            )


class EditContactCommand(BaseCommand):
    """Command for editing a contact."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("edit_contact")

    def _execute_operation(self) -> FunctionResult:
        name = self.arguments.get("name", "")
        action = self.arguments.get("action", "")

        if not name:
            return FunctionResult(False, "❌ Contact name is required")

        self.assistant.edit_contact()

        return FunctionResult(
            True, f"✅ Successfully edited contact: {name} (action: {action})"
        )


class DeleteContactCommand(BaseCommand):
    """Command for deleting a contact."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("delete_contact")

    def _execute_operation(self) -> FunctionResult:
        name = self.arguments.get("name", "")

        if not name:
            return FunctionResult(False, "❌ Contact name is required")

        self.assistant.delete_contact()

        return FunctionResult(True, f"✅ Successfully deleted contact: {name}")


class ViewContactDetailsCommand(BaseCommand):
    """Command for viewing contact details."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("view_contact_details")

    def _execute_operation(self) -> FunctionResult:
        name = self.arguments.get("name", "")

        if not name:
            return FunctionResult(False, "❌ Contact name is required")

        self.assistant.view_contact_details()

        return FunctionResult(True, f"📞 Showing details for contact: {name}")


# Note Commands
class AddNoteCommand(BaseCommand):
    """Command for adding a new note."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("add_note")

    def _execute_operation(self) -> FunctionResult:
        title = self.arguments.get("title", "")
        content = self.arguments.get("content", "")
        tags = self.arguments.get("tags", [])

        if not title:
            return FunctionResult(False, "❌ Note title is required")

        self.assistant.add_note()

        message = f"📝 Successfully added note: '{title}'"
        if tags:
            message += f" with {len(tags)} tag(s)"

        return FunctionResult(True, message, {"title": title, "tags": tags})


class SearchNotesCommand(BaseCommand):
    """Command for searching notes."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("search_notes")

    def _execute_operation(self) -> FunctionResult:
        query = self.arguments.get("query", "")
        notes_result = self.assistant.search_notes(query)

        if notes_result and len(notes_result) > 0:
            return FunctionResult(
                True,
                f"📝 Found {len(notes_result)} note(s) matching '{query}'",
                notes_result,
            )
        else:
            return FunctionResult(False, f"❌ No notes found matching '{query}'")


class ShowNotesCommand(BaseCommand):
    """Command for showing all notes."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("show_notes")

    def _execute_operation(self) -> FunctionResult:
        self.assistant.display_notes_table()
        notes: List[Any] = []  # Assume empty result for stub

        if notes:
            return FunctionResult(
                True, f"📝 Here are all your notes ({len(notes)} total)", notes
            )
        else:
            return FunctionResult(True, "📝 No notes found. Create some notes first!")


class EditNoteCommand(BaseCommand):
    """Command for editing a note."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("edit_note")

    def _execute_operation(self) -> FunctionResult:
        note_id = self.arguments.get("note_id", "")
        action = self.arguments.get("action", "")

        if not note_id:
            return FunctionResult(False, "❌ Note ID is required")

        self.assistant.edit_note()

        return FunctionResult(
            True, f"✅ Successfully edited note: {note_id} (action: {action})"
        )


class DeleteNoteCommand(BaseCommand):
    """Command for deleting a note."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("delete_note")

    def _execute_operation(self) -> FunctionResult:
        note_id = self.arguments.get("note_id", "")

        if not note_id:
            return FunctionResult(False, "❌ Note ID is required")

        self.assistant.delete_note()

        return FunctionResult(True, f"✅ Successfully deleted note: {note_id}")


class ViewNoteDetailsCommand(BaseCommand):
    """Command for viewing note details."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("view_note_details")

    def _execute_operation(self) -> FunctionResult:
        note_id = self.arguments.get("note_id", "")

        if not note_id:
            return FunctionResult(False, "❌ Note ID is required")

        self.assistant.view_note_details()

        return FunctionResult(True, f"📝 Showing details for note: {note_id}")


class SearchNotesByTagCommand(BaseCommand):
    """Command for searching notes by tag."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("search_notes_by_tag")

    def _execute_operation(self) -> FunctionResult:
        tag = self.arguments.get("tag", "")

        if not tag:
            return FunctionResult(False, "❌ Tag is required")

        notes_result = self.assistant.search_notes(tag)

        if notes_result and len(notes_result) > 0:
            return FunctionResult(
                True,
                f"📝 Found {len(notes_result)} note(s) with tag '{tag}'",
                notes_result,
            )
        else:
            return FunctionResult(False, f"❌ No notes found with tag '{tag}'")


# Utility Commands
class GlobalSearchCommand(BaseCommand):
    """Command for global search across contacts and notes."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("global_search")

    def _execute_operation(self) -> FunctionResult:
        query = self.arguments.get("query", "")

        if not query:
            return FunctionResult(False, "❌ Search query is required")

        contacts = self.assistant.search_contacts(query)
        notes_result = self.assistant.search_notes(query)

        contact_count = len(contacts) if contacts else 0
        note_count = len(notes_result) if notes_result else 0
        total_results = contact_count + note_count

        if total_results > 0:
            return FunctionResult(
                True,
                f"🔍 Global search found {total_results} result(s): {contact_count} contact(s) and {note_count} note(s) matching '{query}'",
                {"contacts": contacts, "notes": notes_result},
            )
        else:
            return FunctionResult(False, f"❌ No results found for '{query}'")


class GetStatisticsCommand(BaseCommand):
    """Command for getting statistics."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("get_statistics")

    def _execute_operation(self) -> FunctionResult:
        stats = self.assistant.get_statistics()

        if stats:
            return FunctionResult(True, f"📊 Statistics: {stats}", stats)
        else:
            return FunctionResult(True, "📊 No statistics available yet.")


class GetUpcomingBirthdaysCommand(BaseCommand):
    """Command for getting upcoming birthdays."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("get_upcoming_birthdays")

    def _execute_operation(self) -> FunctionResult:
        days = self.arguments.get("days", 7)
        birthdays = self.assistant.get_upcoming_birthdays(days)

        if birthdays and len(birthdays) > 0:
            return FunctionResult(
                True,
                f"🎂 Found {len(birthdays)} upcoming birthday(s) in the next {days} days",
                birthdays,
            )
        else:
            return FunctionResult(
                True, f"🎂 No upcoming birthdays in the next {days} days"
            )


class ShowHelpCommand(BaseCommand):
    """Command for showing help."""

    def execute(self) -> FunctionResult:
        return self._safe_execute("show_help")

    def _execute_operation(self) -> FunctionResult:
        return FunctionResult(True, FunctionDefinitions.HELP_MESSAGE)


class FunctionExecutor:
    """
    Main executor class implementing Factory and Strategy patterns.
    Handles function call execution using command objects.
    """

    def __init__(self, assistant: AssistantStub):
        self.assistant = assistant
        self.logger = logging.getLogger(self.__class__.__name__)

        # Command factory registry using Strategy pattern
        self._command_registry: Dict[str, type[BaseCommand]] = {
            # Contact commands
            "add_contact": AddContactCommand,
            "search_contacts": SearchContactsCommand,
            "show_contacts": ShowContactsCommand,
            "edit_contact": EditContactCommand,
            "delete_contact": DeleteContactCommand,
            "view_contact_details": ViewContactDetailsCommand,
            # Note commands
            "add_note": AddNoteCommand,
            "search_notes": SearchNotesCommand,
            "show_notes": ShowNotesCommand,
            "edit_note": EditNoteCommand,
            "delete_note": DeleteNoteCommand,
            "view_note_details": ViewNoteDetailsCommand,
            "search_notes_by_tag": SearchNotesByTagCommand,
            # Utility commands
            "global_search": GlobalSearchCommand,
            "get_statistics": GetStatisticsCommand,
            "get_upcoming_birthdays": GetUpcomingBirthdaysCommand,
            "show_help": ShowHelpCommand,
        }

    def execute_function_call(
        self, function_call: Dict[str, Any], user_input: str
    ) -> str:
        """
        Execute a function call using the appropriate command.

        Args:
            function_call: Dictionary containing function name and arguments
            user_input: Original user input for context

        Returns:
            String response from the executed function
        """
        function_name = function_call.get("function")
        arguments = function_call.get("arguments", {})

        # Add user input to arguments for commands that might need it
        if "query" not in arguments and user_input:
            arguments["query"] = user_input

        self.logger.info(f"🔧 Executing: {function_name}({arguments})")

        # Check if function is registered
        if function_name not in self._command_registry:
            return f"❌ Unknown function: {function_name}"

        try:
            # Create and execute command using Factory pattern
            command_class = self._command_registry[function_name]
            command = command_class(self.assistant, arguments)
            result = command.execute()

            return str(result)

        except Exception as e:
            error_msg = f"❌ Error executing {function_name}: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def register_command(
        self, function_name: str, command_class: type[BaseCommand]
    ) -> None:
        """Register a new command class for a function name."""
        self._command_registry[function_name] = command_class

    def get_available_functions(self) -> List[str]:
        """Get list of all available function names."""
        return list(self._command_registry.keys())
