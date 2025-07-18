"""
Визначення функцій та системних промптів для чат-асистента.

Цей модуль містить:
- Системний промпт для AI асистента
- Повідомлення довідки
- Визначення всіх доступних функцій для роботи з контактами та нотатками
- Схеми параметрів для кожної функції
"""

from typing import Dict, Any

# ЗАВЖДИ НАМАГАЙТЕСЬ ВИКЛИКАТИ ІНСТРУМЕНТ БЕЗ БУДЬ-ЯКОГО ДОДАТКОВОГО ТЕКСТУ АБО ПОЯСНЕНЬ.
# ВИКОРИСТОВУЙТЕ ТІЛЬКИ ДОСТУПНІ ФУНКЦІЇ:
# add_contact,search_contacts,show_contacts,edit_contact,delete_contact,view_contact_details,get_upcoming_birthdays,get_statistics,add_note,search_notes,show_notes,edit_note,delete_note,view_note_details,search_notes_by_tag,global_search


class FunctionDefinitions:
    """
    Клас, що містить системні промпти та визначення функцій для чат-асистента.

    Цей клас централізує всі налаштування для AI асистента:
    - Системний промпт з інструкціями та правилами
    - Повідомлення довідки
    - Визначення всіх доступних функцій
    """

    # Системний промпт - основні інструкції для AI асистента
    SYSTEM_PROMPT = """You are a helpful CLI assistant that manages contacts and notes.
    !!! ON RESPONSE TOOLS RESULT ALWAYS PROVIDE ERROR MESSAGE IF ANY ERROR OCCURRED.
    
    Be friendly and use emojis in your responses! 😊 Your output will be displayed in a terminal using Rich library, 
    so you can use Rich color markup that will be rendered properly:
    
    📌 AVAILABLE COLORS (Rich format):
    - [green] - for success messages, confirmations, positive results
    - [red] - for error messages, failures, critical warnings  
    - [blue] - for informational messages, general info
    - [yellow] - for warnings, cautions, important notes
    - [magenta] - for highlights, special emphasis, headers
    - [cyan] - for titles, section headers, names
    - [white] - for normal text, default content
    - [bold] - for emphasis, [italic] - for subtle text
    - [/color] - to close color tags (auto-closes at end of message)
    
    🎨 COLOR USAGE EXAMPLES:
    - "[green]✅ Contact added successfully![/green]"
    - "[red]❌ Error: Contact not found[/red]"
    - "[blue]ℹ️ Found 5 contacts matching your search[/blue]"
    - "[yellow]⚠️ Warning: Phone number format invalid[/yellow]"
    - "[magenta]🎯 Upcoming birthdays:[/magenta]"
    - "[cyan]📞 Contact Details:[/cyan]"
    - "[bold green]Success![/bold green]" - bold green
    - "[bold red]Error![/bold red]" - bold red
    
    ⚡ IMPORTANT RULES:
    - Use Rich markup format: [color]text[/color]
    - Colors auto-close at message end, but explicit closing is better
    - Combine colors with relevant emojis for better UX
    - Use [bold] for emphasis: [bold green], [bold red]
    - Keep color usage consistent throughout responses
    
    Use Rich color markup instead of ANSI escape sequences or custom markers."""

    # Повідомлення довідки з інструкціями для користувача
    HELP_MESSAGE = """
🤖 **CLI Assistant with AI Help**

**📞 Contact Commands:**
• "add contact" / "create new contact"
• "search contact ..." / "find contact"
• "show all contacts" / "list contacts"
• "delete contact" / "remove contact"
• "edit contact" / "modify contact" / "change contact"
• "edit ... phone to ...-...-.." (natural language editing)

**📝 Note Commands:**
• "add note" / "create note"
• "search note meeting" / "find note"
• "show all notes" / "list notes" 
• "delete note" / "remove note"
• "edit note" / "modify note"

**🔍 Search & Analysis:**
• "search everything about project"
• "show upcoming birthdays"
• "show stats" / "statistics"

**💬 Natural Language Examples:**
• "Add a contact for ..."
• "Find notes about the meeting"
• "Show me contacts with upcoming birthdays"
• "Edit ... phone number to ...."
• "Change contact information"

**🔧 Other Commands:**
• "help" - Show this help
• "exit" / "quit" - End conversation

**🧠 AI Features:**
- Advanced function calling capabilities
- Natural language understanding and generation
- Smart entity extraction and intent recognition
- Context-aware responses

**💡 Tips:**
- Use names and specific details in your commands
- I can understand variations of the same command
- Commands are case-insensitive
- Feel free to chat naturally - I'll understand!
        """

    # Словник всіх доступних функцій з їх описами та параметрами
    # Цей словник використовується для:
    # 1. Інформування AI про доступні функції
    # 2. Валідації параметрів викликів функцій
    # 3. Автоматичної генерації документації
    AVAILABLE_FUNCTIONS: Dict[str, Dict[str, Any]] = {
        # Функція для додавання нового контакту
        "add_contact": {
            "name": "add_contact",
            "description": "Add a new contact to the contact list. Name is required, phones can be multiple",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": 'The name of the contact (required) "^[a-zA-Z\\s\\-\']{1,100}$"',
                    },
                    "phones": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of phone numbers (10 digits each)",
                    },
                    "birthday": {
                        "type": "string",
                        "description": "The birthday in DD.MM.YYYY format",
                    },
                },
                "required": ["name"],  # Тільки ім'я є обов'язковим
            },
        },
        # Функція для пошуку контактів
        "search_contacts": {
            "name": "search_contacts",
            "description": "Search for contacts by name or phone number",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (name or phone)",
                    }
                },
                "required": ["query"],  # Запит для пошуку обов'язковий
            },
        },
        "add_note": {
            "name": "add_note",
            "description": "Add a new note with optional tags. If Title or Tags is not provided, it will be generated",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the note"},
                    "content": {
                        "type": "string",
                        "description": "The content of the note",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tags for the note",
                    },
                },
                "required": ["title", "content"],
            },
        },
        "search_notes": {
            "name": "search_notes",
            "description": "Search for notes by title, content, or tags",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
            },
        },
        "show_contacts": {
            "name": "show_contacts",
            "description": "Display all contacts in a table format",
            "parameters": {"type": "object", "properties": {}},
        },
        "show_notes": {
            "name": "show_notes",
            "description": "Display all notes in a table format",
            "parameters": {"type": "object", "properties": {}},
        },
        "get_upcoming_birthdays": {
            "name": "get_upcoming_birthdays",
            "description": "Get contacts with upcoming birthdays",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days ahead to check (default: 7)",
                    }
                },
            },
        },
        "get_statistics": {
            "name": "get_statistics",
            "description": "Get statistics about contacts and notes",
            "parameters": {"type": "object", "properties": {}},
        },
        "edit_contact": {
            "name": "edit_contact",
            "description": "Edit an existing contact (add/remove/change phone, birthday)",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the contact to edit (required)",
                    },
                    "action": {
                        "type": "string",
                        "enum": [
                            "add_phone",
                            "remove_phone",
                            "change_phone",
                            "add_birthday",
                        ],
                        "description": "The action to perform",
                    },
                    "phone": {
                        "type": "string",
                        "description": "Phone number for phone operations (10 digits)",
                    },
                    "new_phone": {
                        "type": "string",
                        "description": "New phone number for change operation (10 digits)",
                    },
                    "birthday": {
                        "type": "string",
                        "description": "Birthday in DD.MM.YYYY format",
                    },
                },
                "required": ["name", "action"],
            },
        },
        "delete_contact": {
            "name": "delete_contact",
            "description": "Delete a contact from the contact list",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the contact to delete",
                    }
                },
                "required": ["name"],
            },
        },
        "edit_note": {
            "name": "edit_note",
            "description": "Edit an existing note (title, content, tags)",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "The ID of the note to edit",
                    },
                    "action": {
                        "type": "string",
                        "enum": ["edit_title", "edit_content", "add_tag", "remove_tag"],
                        "description": "The action to perform",
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the note",
                    },
                    "content": {
                        "type": "string",
                        "description": "New content for the note",
                    },
                    "tag": {"type": "string", "description": "Tag to add or remove"},
                },
                "required": ["note_id", "action"],
            },
        },
        "delete_note": {
            "name": "delete_note",
            "description": "Delete a note from the notes list",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "The ID of the note to delete",
                    }
                },
                "required": ["note_id"],
            },
        },
        "view_contact_details": {
            "name": "view_contact_details",
            "description": "View detailed information about a specific contact",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the contact to view",
                    }
                },
                "required": ["name"],
            },
        },
        "view_note_details": {
            "name": "view_note_details",
            "description": "View detailed information about a specific note",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "The ID of the note to view",
                    }
                },
                "required": ["note_id"],
            },
        },
        "search_notes_by_tag": {
            "name": "search_notes_by_tag",
            "description": "Search for notes by specific tag",
            "parameters": {
                "type": "object",
                "properties": {
                    "tag": {"type": "string", "description": "The tag to search for"}
                },
                "required": ["tag"],
            },
        },
        "global_search": {
            "name": "global_search",
            "description": "Search across both contacts and notes simultaneously",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to apply to both contacts and notes",
                    }
                },
                "required": ["query"],
            },
        },
    }
