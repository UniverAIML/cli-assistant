"""
Красиве інтерактивне меню для персонального асистента.

Цей модуль забезпечує багату систему інтерактивного меню для управління контактами та нотатками.

Основні функції:
- Красиве меню з використанням Rich та Questionary
- Управління контактами (CRUD операції)
- Управління нотатками (CRUD операції)
- Інтеграція з AI чат-асистентом
- Search and filtering
- Кольорова тема та стилізація
- Потужні візуальні ефекти та анімації
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import questionary
from questionary import Style
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table
from rich.text import Text

from .chat_assistant import ChatAssistant
from .database.contact_models import Birthday, Name, Phone, Record
from .database.note_models import Note
from .enhanced_visual_effects import EnhancedVisualEffects
from .interactive_table import (
    show_interactive_contacts_table,
    show_interactive_notes_table,
    show_mouse_menu,
)

# Local imports
# Локальні імпорти
from .operations_manager import OperationsManager


class InteractiveMenu:
    """
    Красиве інтерактивне меню для персонального асистента.

    Використовує:
    - Rich для красивого форматування та таблиць
    - Questionary для інтерактивних промптів
    - OperationsManager для бізнес-логіки
    - ChatAssistant для AI функцій

    Функції:
    - Головне меню з навігацією
    - Підменю для контактів та нотаток
    - Форми для введення даних
    - Відображення результатів у таблицях
    - Інтеграція з AI асистентом
    """

    def __init__(self) -> None:
        """
        Ініціалізує інтерактивне меню з покращеними візуальними ефектами.

        Створює:
        - Rich console для форматування
        - OperationsManager для операцій
        - EnhancedVisualEffects для анімацій та ефектів
        - Кастомний стиль для questionary
        """
        # Ініціалізуємо Rich console для красивого виводу
        self.console = Console()

        # Ініціалізуємо покращені візуальні ефекти
        self.effects = EnhancedVisualEffects(self.console)

        # Ініціалізуємо менеджер операцій (Singleton)
        self.operations = OperationsManager.get_instance()

        # Кастомний стиль для questionary (темна тема з кольорами)
        self.custom_style = Style(
            [
                ("question", "bold fg:#61afef"),  # Синій для запитань
                ("answer", "fg:#98c379 bold"),  # Зелений для відповідей
                ("pointer", "fg:#e06c75 bold"),  # Червоний для вказівника
                ("highlighted", "fg:#e06c75 bold bg:#2c323c"),  # Підсвічений елемент
                ("selected", "fg:#98c379"),  # Зелений для обраного
                ("separator", "fg:#5c6370"),  # Сірий для роздільників
                ("instruction", "fg:#abb2bf"),  # Світло-сірий для інструкцій
                ("text", "fg:#dcdfe4"),  # Білий для тексту
                ("skipped", "fg:#5c6370 italic"),  # Курсив для пропущених
            ]
        )

        # Показуємо стартову анімацію
        self.effects.display_startup_sequence("CLI Assistant")

        # Показуємо кількість завантажених даних при старті
        data_summary = self.operations.get_data_summary()
        if data_summary["contacts"] > 0 or data_summary["notes"] > 0:
            self.effects.display_info_message(
                f"Loaded {data_summary['contacts']} contacts and {data_summary['notes']} notes from previous session.",
                "SYSTEM STATUS",
            )

    def display_startup_animation(self) -> None:
        """Відображає красиву стартову анімацію з покращеними ефектами."""
        self.effects.display_startup_sequence("CLI Assistant")

    def display_welcome(self) -> None:
        """Відображає красивий екран привітання з покращеними візуальними ефектами."""
        self.console.clear()

        # Використовуємо нові візуальні ефекти для заголовка
        self.effects.display_animated_title(
            "CLI Assistant", "🤖 Your Next-Generation Personal AI Assistant ✨"
        )

        # Додаємо розділювач з ефектами
        self.effects.create_gradient_rule("🌟 MAIN MENU 🌟")
        self.console.print()

    def display_contacts_table(self, records: Optional[List[Record]] = None) -> None:
        """Display contacts in an interactive table with search and mouse support."""
        if records is None:
            records = self.operations.get_all_contacts()

        if not records:
            self.effects.display_info_message(
                "No contacts found. Add a new contact to get started!",
                "CONTACTS DATABASE",
            )
            return

        # Show loading animation
        self.effects.display_loading_animation("Loading contacts...", 0.5)

        # Convert records to dict format for interactive table
        contacts_data = []
        for record in records:
            phones_str = (
                "; ".join(phone.value for phone in record.phones)
                if record.phones
                else "No phones"
            )
            birthday_str = record.birthday.value if record.birthday else "No birthday"

            contacts_data.append(
                {
                    "Name": record.name.value,
                    "Phones": phones_str,
                    "Birthday": birthday_str,
                }
            )

        # Show interactive table
        try:
            show_interactive_contacts_table(contacts_data)
        except Exception as e:
            # Fallback to regular table if interactive fails
            self.console.print(
                f"[yellow]Interactive mode failed, showing regular table: {e}[/yellow]"
            )
            self._display_fallback_contacts_table(records)

    def _display_fallback_contacts_table(self, records: List[Record]) -> None:
        """Fallback method for displaying contacts table."""
        # Create beautiful table with enhanced style
        table = Table(
            show_header=True,
            header_style="bold bright_white on blue",
            box=box.DOUBLE_EDGE,
            border_style="bright_blue",
            title="📞 CONTACTS DATABASE 📞",
            title_style="bold bright_magenta",
        )

        table.add_column("👤 Name", style="bold cyan", width=20)
        table.add_column("📱 Phones", style="bright_green", width=25)
        table.add_column("🎂 Birthday", style="bright_yellow", width=15)

        # Add rows with alternating styles
        for i, record in enumerate(records):
            phones_str = (
                "; ".join(phone.value for phone in record.phones)
                if record.phones
                else "❌ No phones"
            )
            birthday_str = record.birthday.value if record.birthday else "❓ Unknown"

            # Alternate row styles for better readability
            row_style = "dim" if i % 2 == 0 else "none"
            table.add_row(
                f"✨ {record.name.value}", phones_str, birthday_str, style=row_style
            )

        # Apply additional effects to table
        table = self.effects.create_fancy_table_style(table)
        self.console.print(table)

        # Show statistics
        self.console.print(
            f"\n[bold bright_green]📊 Total contacts: {len(records)}[/bold bright_green]"
        )

    def display_notes_table(self, notes_dict: Optional[Dict[str, Note]] = None) -> None:
        """Display notes in an interactive table with search and mouse support."""
        if notes_dict is None:
            notes_dict = self.operations.get_all_notes()

        if not notes_dict:
            self.effects.display_info_message(
                "No notes found. Create a new note to get started!", "NOTES DATABASE"
            )
            return

        # Show loading animation
        self.effects.display_loading_animation("Loading notes...", 0.5)

        # Convert notes to dict format for interactive table
        notes_data = []
        for note_id, note in notes_dict.items():
            content_preview = (
                note.content[:37] + "..." if len(note.content) > 40 else note.content
            )
            tags_str = (
                ", ".join(f"#{tag}" for tag in note.tags) if note.tags else "No tags"
            )
            created_date = note.created_at.split()[0] if note.created_at else "Unknown"

            notes_data.append(
                {
                    "ID": note_id,
                    "Title": note.title,
                    "Content": content_preview,
                    "Tags": tags_str,
                    "Created": created_date,
                }
            )

        # Show interactive table
        try:
            show_interactive_notes_table(notes_data)
        except Exception as e:
            # Fallback to regular table if interactive fails
            self.console.print(
                f"[yellow]Interactive mode failed, showing regular table: {e}[/yellow]"
            )
            self._display_fallback_notes_table(notes_dict)

    def _display_fallback_notes_table(self, notes_dict: Dict[str, Note]) -> None:
        """Fallback method for displaying notes table."""
        # Create beautiful table with enhanced style
        table = Table(
            show_header=True,
            header_style="bold bright_white on magenta",
            box=box.DOUBLE_EDGE,
            border_style="bright_magenta",
            title="📝 NOTES DATABASE 📝",
            title_style="bold bright_cyan",
        )

        table.add_column("🆔 ID", style="dim white", width=8)
        table.add_column("📋 Title", style="bold bright_cyan", width=20)
        table.add_column("📄 Content", style="bright_white", width=40)
        table.add_column("🏷️ Tags", style="bright_green", width=20)
        table.add_column("📅 Created", style="bright_yellow", width=12)

        for i, (note_id, note) in enumerate(notes_dict.items()):
            content_preview = (
                note.content[:37] + "..." if len(note.content) > 40 else note.content
            )
            tags_str = (
                ", ".join(f"#{tag}" for tag in note.tags) if note.tags else "❌ No tags"
            )
            created_date = (
                note.created_at.split()[0] if note.created_at else "❓ Unknown"
            )

            # Alternate row styles for better readability
            row_style = "dim" if i % 2 == 0 else "none"
            table.add_row(
                f"🔸 {note_id}",
                f"✨ {note.title}",
                content_preview,
                tags_str,
                created_date,
                style=row_style,
            )

        # Apply additional effects to table
        table = self.effects.create_fancy_table_style(table)
        self.console.print(table)

        # Show statistics
        self.console.print(
            f"\n[bold bright_green]📊 Total notes: {len(notes_dict)}[/bold bright_green]"
        )

    def add_contact(self) -> None:
        """Add a new contact with validation and enhanced visual effects."""
        self.effects.create_gradient_rule("✨ ADDING NEW CONTACT ✨")

        # Анимация загрузки формы
        self.effects.display_loading_animation("Preparing form...", 0.5)

        # Валідуємо ім'я використовуючи наш клас Name
        while True:
            name_input = questionary.text(
                "👤 Enter contact name:", style=self.custom_style
            ).ask()
            if not name_input:
                self.effects.display_error_message("Name cannot be empty!")
                return

            try:
                name_obj = Name(name_input)
                name = name_obj.value
                self.console.print(f"[green]✓ Valid name: {name}[/green]")
                break
            except ValueError as e:
                self.effects.display_error_message(f"Validation error: {e}")
                retry = questionary.confirm("Try again?", style=self.custom_style).ask()
                if not retry:
                    return

        phones: List[str] = []
        # Add phone numbers with enhanced UI
        while True:
            add_phone = questionary.confirm(
                "📱 Add phone number?", style=self.custom_style
            ).ask()
            if not add_phone:
                break

            phone = questionary.text(
                "📞 Enter phone number (10 digits):", style=self.custom_style
            ).ask()
            if phone:
                try:
                    # Валідуємо номер телефону використовуючи наш клас Phone
                    phone_obj = Phone(phone)
                    phones.append(phone_obj.value)  # Зберігаємо значення, а не об'єкт
                    self.console.print(
                        f"[green]✓ Valid number: {phone_obj.value}[/green]"
                    )
                except ValueError as e:
                    self.effects.display_error_message(f"Number validation error: {e}")
                    continue

            # Ask if user wants to add another phone
            if not questionary.confirm(
                "📱 Add another number?", style=self.custom_style
            ).ask():
                break

        birthday = None
        # Add birthday with enhanced UI
        add_birthday = questionary.confirm(
            "🎂 Add birthday?", style=self.custom_style
        ).ask()
        if add_birthday:
            while True:
                birthday_input = questionary.text(
                    "🗓️  Enter birthday (DD.MM.YYYY):", style=self.custom_style
                ).ask()
                if birthday_input:
                    try:
                        # Валідуємо день народження використовуючи наш клас Birthday
                        birthday_obj = Birthday(birthday_input)
                        birthday = birthday_obj.value
                        self.console.print(
                            f"[green]✓ Valid date: {birthday_obj.value}[/green]"
                        )
                        break
                    except ValueError as e:
                        self.effects.display_error_message(
                            f"Date validation error: {e}"
                        )
                        retry = questionary.confirm(
                            "Try again?", style=self.custom_style
                        ).ask()
                        if not retry:
                            break
                else:
                    break

        # Показываем анимацию сохранения
        self.effects.display_loading_animation("Saving contact...", 1.2)

        # Add the contact
        result = self.operations.add_contact(name, phones if phones else None, birthday)

        if result["success"]:
            self.effects.display_success_message(
                f"Contact '{name}' successfully added to database!"
            )
            self.effects.display_celebration_animation()
        else:
            self.effects.display_error_message(
                f"Error adding contact: {result['message']}"
            )

    def add_note(self) -> None:
        """Add a new note with tags and enhanced visual effects."""
        self.effects.create_gradient_rule("✨ ADDING NEW NOTE ✨")

        # Loading form animation
        self.effects.display_loading_animation("Preparing form...", 0.3)

        title = questionary.text("📝 Enter note title:", style=self.custom_style).ask()
        if not title:
            self.effects.display_error_message("Title cannot be empty!")
            return

        content = questionary.text(
            "📄 Enter note content:", style=self.custom_style
        ).ask()

        tags_input = questionary.text(
            "🏷️  Enter tags (comma-separated):", style=self.custom_style
        ).ask()

        tags = (
            [tag.strip() for tag in tags_input.split(",") if tag.strip()]
            if tags_input
            else []
        )

        # Show saving animation
        self.effects.display_loading_animation("Saving note...", 0.5)

        result = self.operations.add_note(title, content or "", tags)

        if result["success"]:
            self.effects.display_success_message(
                f"Note '{title}' successfully created!"
            )
            self.effects.display_celebration_animation()
        else:
            self.effects.display_error_message(
                f"Error creating note: {result['message']}"
            )

    def view_contact_details(self) -> None:
        """View detailed information about a contact."""
        contacts = self.operations.get_all_contacts()
        if not contacts:
            self.console.print("[yellow]No contacts available.[/yellow]")
            return

        # Select contact to view
        contact_choices = [record.name.value for record in contacts]
        name = questionary.select(
            "Select contact to view:", choices=contact_choices, style=self.custom_style
        ).ask()

        if not name:
            return

        result = self.operations.view_contact_details(name)

        if not result["success"]:
            self.console.print(f"[red]{result['message']}[/red]")
            return

        contact = result["contact"]

        # Create detailed view
        self.console.print()
        panel_content = f"""
[bold cyan]Name:[/bold cyan] {contact['name']}

[bold green]Phone Numbers:[/bold green]
{chr(10).join([f"  📞 {phone}" for phone in contact['phones']]) if contact['phones'] else "  No phone numbers"}

[bold red]Birthday:[/bold red]
  🎂 {contact['birthday'] if contact['birthday'] else "No birthday set"}
        """

        panel = Panel(
            panel_content.strip(),
            title=f"[bold blue]Contact Details[/bold blue]",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def view_note_details(self) -> None:
        """View detailed information about a note."""
        notes = self.operations.get_all_notes()
        if not notes:
            self.console.print("[yellow]No notes available.[/yellow]")
            return

        # Select note to view
        note_choices = []
        for note_id, note in notes.items():
            choice_text = f"{note_id}: {note.title}"
            note_choices.append(choice_text)

        choice = questionary.select(
            "Select note to view:", choices=note_choices, style=self.custom_style
        ).ask()

        if not choice:
            return

        note_id = choice.split(":")[0]
        result = self.operations.view_note_details(note_id)

        if not result["success"]:
            self.console.print(f"[red]{result['message']}[/red]")
            return

        note = result["note"]

        # Create detailed view
        self.console.print()
        panel_content = f"""
[bold cyan]ID:[/bold cyan] {note['id']}
[bold cyan]Title:[/bold cyan] {note['title']}

[bold green]Content:[/bold green]
{note['content'] if note['content'] else "No content"}

[bold yellow]Tags:[/bold yellow]
{', '.join(note['tags']) if note['tags'] else "No tags"}

[bold red]Created:[/bold red] {note['created_at'] if note['created_at'] else "Unknown"}
{f"[bold red]Updated:[/bold red] {note['updated_at']}" if note['updated_at'] else ""}
        """

        panel = Panel(
            panel_content.strip(),
            title=f"[bold blue]Note Details[/bold blue]",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def edit_contact(self) -> None:
        """Edit an existing contact."""
        contacts = self.operations.get_all_contacts()
        if not contacts:
            self.console.print("[yellow]No contacts to edit.[/yellow]")
            return

        # Select contact to edit
        contact_choices = [record.name.value for record in contacts]
        name = questionary.select(
            "Select contact to edit:", choices=contact_choices, style=self.custom_style
        ).ask()

        if not name:
            return

        contact_info = self.operations.view_contact_details(name)
        if not contact_info["success"]:
            self.console.print(f"[red]{contact_info['message']}[/red]")
            return

        contact = contact_info["contact"]

        self.console.print(f"[bold cyan]Editing contact: {name}[/bold cyan]")
        self.console.print(
            f"Current phones: {'; '.join(contact['phones']) if contact['phones'] else 'None'}"
        )
        self.console.print(
            f"Current birthday: {contact['birthday'] if contact['birthday'] else 'None'}"
        )
        self.console.print()

        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Add phone",
                "Remove phone",
                "Change phone",
                "Add/Change birthday",
                "Cancel",
            ],
            style=self.custom_style,
        ).ask()

        if action == "Add phone":
            while True:
                phone = questionary.text(
                    "Enter new phone number (10 digits):", style=self.custom_style
                ).ask()
                if phone:
                    try:
                        # Валідуємо номер телефону
                        phone_obj = Phone(phone)
                        result = self.operations.edit_contact(
                            name, "add_phone", phone=phone_obj.value
                        )
                        if result["success"]:
                            self.console.print(f"[green]{result['message']}[/green]")
                        else:
                            self.console.print(f"[red]{result['message']}[/red]")
                        break
                    except ValueError as e:
                        self.console.print(f"[red]✗ {e}[/red]")
                        retry = questionary.confirm(
                            "Try again?", style=self.custom_style
                        ).ask()
                        if not retry:
                            break
                else:
                    break

        elif action == "Remove phone":
            if not contact["phones"]:
                self.console.print("[yellow]No phones to remove.[/yellow]")
                return

            phone = questionary.select(
                "Select phone to remove:",
                choices=contact["phones"],
                style=self.custom_style,
            ).ask()

            if phone:
                result = self.operations.edit_contact(name, "remove_phone", phone=phone)
                if result["success"]:
                    self.console.print(f"[green]{result['message']}[/green]")
                else:
                    self.console.print(f"[red]{result['message']}[/red]")

        elif action == "Change phone":
            if not contact["phones"]:
                self.console.print("[yellow]No phones to change.[/yellow]")
                return

            old_phone = questionary.select(
                "Select phone to change:",
                choices=contact["phones"],
                style=self.custom_style,
            ).ask()

            if old_phone:
                while True:
                    new_phone = questionary.text(
                        "Enter new phone number (10 digits):", style=self.custom_style
                    ).ask()
                    if new_phone:
                        try:
                            # Валідуємо новий номер телефону
                            phone_obj = Phone(new_phone)
                            result = self.operations.edit_contact(
                                name,
                                "change_phone",
                                phone=old_phone,
                                new_phone=phone_obj.value,
                            )
                            if result["success"]:
                                self.console.print(
                                    f"[green]{result['message']}[/green]"
                                )
                            else:
                                self.console.print(f"[red]{result['message']}[/red]")
                            break
                        except ValueError as e:
                            self.console.print(f"[red]✗ {e}[/red]")
                            retry = questionary.confirm(
                                "Try again?", style=self.custom_style
                            ).ask()
                            if not retry:
                                break
                    else:
                        break

        elif action == "Add/Change birthday":
            while True:
                birthday = questionary.text(
                    "Enter birthday (DD.MM.YYYY):", style=self.custom_style
                ).ask()
                if birthday:
                    try:
                        # Валідуємо день народження
                        birthday_obj = Birthday(birthday)
                        result = self.operations.edit_contact(
                            name, "add_birthday", birthday=birthday_obj.value
                        )
                        if result["success"]:
                            self.console.print(f"[green]{result['message']}[/green]")
                        else:
                            self.console.print(f"[red]{result['message']}[/red]")
                        break
                    except ValueError as e:
                        self.console.print(f"[red]✗ {e}[/red]")
                        retry = questionary.confirm(
                            "Try again?", style=self.custom_style
                        ).ask()
                        if not retry:
                            break
                else:
                    break

    def edit_note(self) -> None:
        """Edit an existing note."""
        notes = self.operations.get_all_notes()
        if not notes:
            self.console.print("[yellow]No notes to edit.[/yellow]")
            return

        # Select note to edit
        note_choices = []
        for note_id, note in notes.items():
            choice_text = f"{note_id}: {note.title}"
            note_choices.append(choice_text)

        choice = questionary.select(
            "Select note to edit:", choices=note_choices, style=self.custom_style
        ).ask()

        if not choice:
            return

        note_id = choice.split(":")[0]
        note_info = self.operations.view_note_details(note_id)

        if not note_info["success"]:
            self.console.print(f"[red]{note_info['message']}[/red]")
            return

        note = note_info["note"]

        self.console.print(f"[bold cyan]Editing note: {note['title']}[/bold cyan]")
        self.console.print(
            f"Current content: {note['content'][:50]}..."
            if len(note["content"]) > 50
            else f"Current content: {note['content']}"
        )
        self.console.print(
            f"Current tags: {', '.join(note['tags']) if note['tags'] else 'None'}"
        )
        self.console.print()

        action = questionary.select(
            "What would you like to do?",
            choices=["Edit title", "Edit content", "Add tag", "Remove tag", "Cancel"],
            style=self.custom_style,
        ).ask()

        if action == "Edit title":
            new_title = questionary.text(
                "Enter new title:", style=self.custom_style
            ).ask()
            if new_title:
                result = self.operations.edit_note(
                    note_id, "edit_title", title=new_title
                )
                if result["success"]:
                    self.console.print(f"[green]{result['message']}[/green]")
                else:
                    self.console.print(f"[red]{result['message']}[/red]")

        elif action == "Edit content":
            new_content = questionary.text(
                "Enter new content:", style=self.custom_style
            ).ask()
            if new_content:
                result = self.operations.edit_note(
                    note_id, "edit_content", content=new_content
                )
                if result["success"]:
                    self.console.print(f"[green]{result['message']}[/green]")
                else:
                    self.console.print(f"[red]{result['message']}[/red]")

        elif action == "Add tag":
            new_tag = questionary.text("Enter new tag:", style=self.custom_style).ask()
            if new_tag:
                result = self.operations.edit_note(note_id, "add_tag", tag=new_tag)
                if result["success"]:
                    self.console.print(f"[green]{result['message']}[/green]")
                else:
                    self.console.print(f"[red]{result['message']}[/red]")

        elif action == "Remove tag":
            if not note["tags"]:
                self.console.print("[yellow]No tags to remove.[/yellow]")
                return

            tag = questionary.select(
                "Select tag to remove:", choices=note["tags"], style=self.custom_style
            ).ask()

            if tag:
                result = self.operations.edit_note(note_id, "remove_tag", tag=tag)
                if result["success"]:
                    self.console.print(f"[green]{result['message']}[/green]")
                else:
                    self.console.print(f"[red]{result['message']}[/red]")

    def delete_contact(self) -> None:
        """Delete a contact."""
        contacts = self.operations.get_all_contacts()
        if not contacts:
            self.console.print("[yellow]No contacts to delete.[/yellow]")
            return

        # Select contact to delete
        contact_choices = [record.name.value for record in contacts]
        name = questionary.select(
            "Select contact to delete:",
            choices=contact_choices,
            style=self.custom_style,
        ).ask()

        if not name:
            return

        # Confirm deletion
        confirm = questionary.confirm(
            f"Are you sure you want to delete '{name}'?", style=self.custom_style
        ).ask()

        if confirm:
            result = self.operations.delete_contact(name)
            if result["success"]:
                self.console.print(f"[green]{result['message']}[/green]")
            else:
                self.console.print(f"[red]{result['message']}[/red]")

    def delete_note(self) -> None:
        """Delete a note."""
        notes = self.operations.get_all_notes()
        if not notes:
            self.console.print("[yellow]No notes to delete.[/yellow]")
            return

        # Select note to delete
        note_choices = []
        for note_id, note in notes.items():
            choice_text = f"{note_id}: {note.title}"
            note_choices.append(choice_text)

        choice = questionary.select(
            "Select note to delete:", choices=note_choices, style=self.custom_style
        ).ask()

        if not choice:
            return

        note_id = choice.split(":")[0]
        note_info = self.operations.view_note_details(note_id)

        if not note_info["success"]:
            self.console.print(f"[red]{note_info['message']}[/red]")
            return

        note = note_info["note"]

        # Confirm deletion
        confirm = questionary.confirm(
            f"Are you sure you want to delete note '{note['title']}'?",
            style=self.custom_style,
        ).ask()

        if confirm:
            result = self.operations.delete_note(note_id)
            if result["success"]:
                self.console.print(f"[green]{result['message']}[/green]")
            else:
                self.console.print(f"[red]{result['message']}[/red]")

    def ai_assistant_menu(self) -> None:
        """AI Assistant menu for natural language commands."""
        self.console.clear()
        self.console.print(
            Panel(
                "[bold magenta]AI Assistant[/bold magenta]",
                title="🤖 AI Assistant",
                subtitle="Natural Language Commands",
                style="bright_magenta",
            )
        )
        self.console.print(
            "[cyan]I am your AI Assistant. I can execute commands in natural language, for example:[/cyan]"
        )
        self.console.print(
            "[green]- Add a new contact John with number 123456789\n- Change phone for contact Alice\n- Show upcoming birthdays\n- Add a note about meeting tomorrow[/green]"
        )
        self.console.print(
            "[white]Type your command or 'back' to return to the menu.[/white]"
        )

        try:
            # Create AI assistant
            assistant = ChatAssistant()

            # Start custom chat loop
            while True:
                user_input = questionary.text(
                    "You:", style=self.custom_style
                ).ask()
                if not user_input or user_input.strip().lower() in [
                    "back",
                    "exit",
                    "quit",
                ]:
                    break

                # Process the command through AI assistant
                response = assistant.generate_response(user_input)

                # Display response with rich formatting
                self.console.print(
                    f"\n[bold green]Assistant:[/bold green] {response}\n"
                )

        except Exception as e:
            self.console.print(f"[red]Error initializing AI Assistant: {e}[/red]")
            input("Press Enter to continue...")

    def contacts_menu(self) -> None:
        """Contact management menu."""
        while True:
            self.console.clear()
            self.display_welcome()

            choice = questionary.select(
                "📞 Contact Management:",
                choices=[
                    "👤 Add Contact",
                    "📋 Show All Contacts",
                    "🔍 Search Contacts",
                    "👁️  View Contact Details",
                    "✏️  Edit Contact",
                    "🗑️  Delete Contact",
                    "🎂 Upcoming Birthdays",
                    "⬅️  Back to Main Menu",
                ],
                style=self.custom_style,
            ).ask()

            if choice == "⬅️  Back to Main Menu":
                break
            elif choice == "👤 Add Contact":
                self.add_contact()
            elif choice == "📋 Show All Contacts":
                self.console.print("\n[bold cyan]All Contacts:[/bold cyan]")
                contacts = self.operations.get_all_contacts()
                if contacts:
                    self.display_contacts_table(contacts)
                    self.console.print(
                        f"\n[green]Total contacts: {len(contacts)}[/green]"
                    )
                else:
                    self.console.print("[yellow]No contacts found.[/yellow]")
            elif choice == "🔍 Search Contacts":
                query = questionary.text(
                    "Enter search query:", style=self.custom_style
                ).ask()
                if query:
                    results = self.operations.search_contacts(query)
                    self.console.print(
                        f"\n[bold cyan]Search Results for '{query}':[/bold cyan]"
                    )
                    self.display_contacts_table(results)
            elif choice == "👁️  View Contact Details":
                self.view_contact_details()
            elif choice == "🎂 Upcoming Birthdays":
                days_input = questionary.text(
                    "Show birthdays in how many days? (default: 7)", style=self.custom_style
                ).ask()
                try:
                    days = int(days_input) if days_input and int(days_input) > 0 else 7
                except Exception:
                    days = 7
                upcoming = self.operations.get_upcoming_birthdays(days)
                self.console.print(f"\n[bold cyan]Upcoming Birthdays (next {days} days):[/bold cyan]")
                if upcoming:
                    # Convert upcoming birthdays to records for display
                    upcoming_records = []
                    for bday_info in upcoming:
                        record = self.operations.get_contact_by_name(bday_info["name"])
                        if record:
                            upcoming_records.append(record)
                    self.display_contacts_table(upcoming_records)
                else:
                    self.console.print("[yellow]No upcoming birthdays.[/yellow]")
            elif choice == "✏️  Edit Contact":
                self.edit_contact()
            elif choice == "🗑️  Delete Contact":
                self.delete_contact()

            if choice != "⬅️  Back to Main Menu":
                input("\nPress Enter to continue...")

    def notes_menu(self) -> None:
        """Notes management menu."""
        while True:
            self.console.clear()
            self.display_welcome()

            choice = questionary.select(
                "📝 Notes Management:",
                choices=[
                    "➕ Add Note",
                    "📄 Show All Notes",
                    "🔍 Search Notes",
                    "🏷️  Search by Tags",
                    "👁️  View Note Details",
                    "✏️  Edit Note",
                    "🗑️  Delete Note",
                    "⬅️  Back to Main Menu",
                ],
                style=self.custom_style,
            ).ask()

            if choice == "⬅️  Back to Main Menu":
                break
            elif choice == "➕ Add Note":
                self.add_note()
            elif choice == "📄 Show All Notes":
                self.console.print("\n[bold cyan]All Notes:[/bold cyan]")
                notes = self.operations.get_all_notes()
                self.display_notes_table(notes)
            elif choice == "🔍 Search Notes":
                query = questionary.text(
                    "Enter search query:", style=self.custom_style
                ).ask()
                if query:
                    results = self.operations.search_notes(query)
                    self.console.print(
                        f"\n[bold cyan]Search Results for '{query}':[/bold cyan]"
                    )
                    self.display_notes_table(results)
            elif choice == "🏷️  Search by Tags":
                tag = questionary.text(
                    "Enter tag to search:", style=self.custom_style
                ).ask()
                if tag:
                    results = self.operations.search_notes_by_tag(tag)
                    self.console.print(
                        f"\n[bold cyan]Notes with tag '{tag}':[/bold cyan]"
                    )
                    self.display_notes_table(results)
            elif choice == "👁️  View Note Details":
                self.view_note_details()
            elif choice == "✏️  Edit Note":
                self.edit_note()
            elif choice == "🗑️  Delete Note":
                self.delete_note()

            if choice != "⬅️  Back to Main Menu":
                input("\nPress Enter to continue...")

    def global_search(self) -> None:
        """Global search across contacts and notes."""
        self.console.clear()
        self.display_welcome()

        query = questionary.text(
            "🔍 Enter search query:", style=self.custom_style
        ).ask()
        if not query:
            return

        self.console.print(
            f"\n[bold cyan]Global Search Results for '{query}':[/bold cyan]"
        )

        results = self.operations.global_search(query)

        # Display contact results
        if results["contacts"]:
            self.console.print("\n[bold green]📞 Contacts:[/bold green]")
            self.display_contacts_table(results["contacts"])

        # Display note results
        if results["notes"]:
            self.console.print("\n[bold green]📝 Notes:[/bold green]")
            self.display_notes_table(results["notes"])

        if not results["contacts"] and not results["notes"]:
            self.console.print("[yellow]No results found.[/yellow]")

        input("\nPress Enter to continue...")

    def statistics_menu(self) -> None:
        """Display statistics about contacts and notes."""
        self.console.clear()
        self.display_welcome()

        stats = self.operations.get_statistics()

        # Create statistics panel
        stats_content = f"""
[bold cyan]Total Contacts:[/bold cyan] {stats['total_contacts']}
[bold cyan]Total Notes:[/bold cyan] {stats['total_notes']}

[bold green]Contact Details:[/bold green]
  📞 With phone numbers: {stats['contacts_with_phones']}
  🎂 With birthdays: {stats['contacts_with_birthdays']}

[bold yellow]Note Details:[/bold yellow]
  🏷️  With tags: {stats['notes_with_tags']}
        """

        panel = Panel(
            stats_content.strip(),
            title="[bold blue]📊 Statistics[/bold blue]",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)
        input("\nPress Enter to continue...")

    def run(self) -> None:
        """Головний цикл додатку з покращеними візуальними ефектами."""
        while True:
            self.console.clear()
            self.display_welcome()

            # Используем визуальные эффекты для отображения меню
            menu_options = [
                "📞 Manage Contacts",
                "📝 Manage Notes",
                "🔍 Global Search",
                "📊 Statistics",
                "🤖 AI Assistant",
                "🚪 Exit",
            ]

            choice = questionary.select(
                "🌟 What would you like to do?",
                choices=menu_options,
                style=self.custom_style,
            ).ask()

            if choice == "🚪 Exit":
                # Красиве прощання з анімацією
                self.effects.display_loading_animation("Shutting down...", 0.3)
                goodbye_msg = self.effects.create_rainbow_text(
                    "Thank you for using CLI Assistant!"
                )
                self.console.print(Align.center(goodbye_msg))
                self.effects.display_celebration_animation()
                self.console.print(
                    Align.center(Text("Goodbye! 👋✨", style="bold bright_yellow"))
                )
                break
            elif choice == "📞 Manage Contacts":
                self.contacts_menu()
            elif choice == "📝 Manage Notes":
                self.notes_menu()
            elif choice == "🔍 Global Search":
                self.global_search()
            elif choice == "📊 Statistics":
                self.statistics_menu()
            elif choice == "🤖 AI Assistant":
                self.ai_assistant_menu()


def main() -> None:
    """Main function for interactive menu with enhanced error handling."""
    try:
        app = InteractiveMenu()
        app.run()
    except KeyboardInterrupt:
        console = Console()
        effects = EnhancedVisualEffects(console)
        console.clear()
        effects.display_info_message(
            "Application interrupted by user.\nGoodbye! 👋✨", "PROGRAM INTERRUPTION"
        )
    except Exception as e:
        console = Console()
        effects = EnhancedVisualEffects(console)
        console.clear()
        effects.display_error_message(f"An error occurred: {e}\nGoodbye! 👋")


if __name__ == "__main__":
    main()
