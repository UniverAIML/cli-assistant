#!/usr/bin/env python3
"""
Example demonstrating the new JSON serialization capabilities.
This script shows how to use the new JSON-based DataManager instead of pickle.
"""

import json
from src.database.data_manager import DataManager
from src.database.contact_models import AddressBook, Record
from src.database.note_models import NotesManager, Note


def main():
    """Demonstrate JSON serialization features."""
    print("=== JSON Serialization Demo ===")

    # Create DataManager with JSON files
    dm = DataManager(
        contacts_filename="demo_contacts.json", notes_filename="demo_notes.json"
    )

    # Create sample data
    address_book = AddressBook()

    # Add some contacts
    john = Record("John Doe")
    john.add_phone("1234567890")
    john.add_phone("0987654321")
    john.add_birthday("15.06.1990")
    address_book.add_record(john)

    jane = Record("Jane Smith")
    jane.add_phone("5555555555")
    jane.add_birthday("23.12.1985")
    address_book.add_record(jane)

    # Create notes manager
    notes_manager = NotesManager()

    # Add some notes
    note1_id = notes_manager.create_note(
        "Meeting Notes",
        "Discuss project requirements and timeline",
        ["work", "meeting", "project"],
    )

    note2_id = notes_manager.create_note(
        "Shopping List", "Milk, Bread, Eggs, Cheese", ["personal", "shopping"]
    )

    note3_id = notes_manager.create_note(
        "Book Recommendations",
        "1. Clean Code by Robert Martin\n2. Design Patterns by Gang of Four",
        ["books", "learning", "programming"],
    )

    print(
        f"Created {len(address_book.data)} contacts and {len(notes_manager.data)} notes"
    )

    # Save data using JSON serialization
    print("\n=== Saving Data ===")
    success = dm.save_data(address_book, notes_manager)
    print(f"Save successful: {success}")

    # Show JSON structure
    print("\n=== JSON Structure for Contacts ===")
    contacts_json = address_book.to_json()
    print(contacts_json)

    print("\n=== JSON Structure for Notes ===")
    notes_json = notes_manager.to_json()
    print(notes_json)

    # Load data back
    print("\n=== Loading Data ===")
    loaded_address_book, loaded_notes_manager = dm.load_data()

    print(
        f"Loaded {len(loaded_address_book.data)} contacts and {len(loaded_notes_manager.data)} notes"
    )

    # Verify data integrity
    print("\n=== Data Integrity Check ===")

    # Check contacts
    for name, original_record in address_book.data.items():
        loaded_record = loaded_address_book.find(name)
        if loaded_record:
            print(f"✓ Contact '{name}' loaded successfully")
            print(f"  Phones: {[p.value for p in loaded_record.phones]}")
            if loaded_record.birthday:
                print(f"  Birthday: {loaded_record.birthday.value}")
        else:
            print(f"✗ Contact '{name}' not found in loaded data")

    # Check notes
    for note_id, original_note in notes_manager.data.items():
        loaded_note = loaded_notes_manager.find_note(note_id)
        if loaded_note:
            print(f"✓ Note '{loaded_note.title}' loaded successfully")
            print(f"  Tags: {loaded_note.tags}")
        else:
            print(f"✗ Note '{note_id}' not found in loaded data")

    # Test search functionality
    print("\n=== Search Functionality ===")

    # Search notes by tag
    work_notes = loaded_notes_manager.get_notes_by_tag("work")
    print(f"Notes tagged with 'work': {len(work_notes)}")
    for note_id, note in work_notes.items():
        print(f"  - {note.title}")

    # Search notes by content
    shopping_notes = loaded_notes_manager.search_notes("shopping")
    print(f"Notes containing 'shopping': {len(shopping_notes)}")
    for note_id, note in shopping_notes.items():
        print(f"  - {note.title}")

    # Get upcoming birthdays
    print("\n=== Upcoming Birthdays ===")
    upcoming = loaded_address_book.get_upcoming_birthdays()
    if upcoming:
        for birthday_info in upcoming:
            print(
                f"  - {birthday_info['name']}: {birthday_info['congratulation_date']}"
            )
    else:
        print("  No upcoming birthdays in the next 7 days")

    # Clean up demo files
    print("\n=== Cleanup ===")
    dm.delete_contacts_file()
    dm.delete_notes_file()
    print("Demo files cleaned up")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
