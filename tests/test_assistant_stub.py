"""
Test file for AssistantStub class.
Demonstrates how all the stubbed methods work.
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from cli_assistant.assistant_stub import AssistantStub


def test_assistant_stub():
    """Test all methods in AssistantStub class."""
    print("=== Testing AssistantStub Class ===\n")
    
    # Initialize the stub
    assistant = AssistantStub()
    
    print("--- Testing Core Functionality ---")
    assistant.save_data()
    assistant.validate_phone("1234567890")
    assistant.validate_email("test@example.com")
    
    print("--- Testing Display Methods ---")
    assistant.display_welcome()
    assistant.display_contacts_table([{"name": "John"}, {"name": "Jane"}])
    assistant.display_notes_table({"1": {"title": "Note 1"}, "2": {"title": "Note 2"}})
    
    print("--- Testing Data Retrieval ---")
    assistant.get_upcoming_birthdays(14)
    assistant.search_contacts("John")
    assistant.search_notes("meeting")
    
    print("--- Testing Contact Management ---")
    assistant.add_contact()
    assistant.view_contact_details()
    assistant.edit_contact()
    assistant.delete_contact()
    
    print("--- Testing Note Management ---")
    assistant.add_note()
    assistant.view_note_details()
    assistant.edit_note()
    assistant.delete_note()
    
    print("--- Testing Menu Methods ---")
    assistant.contacts_menu()
    assistant.notes_menu()
    assistant.ai_assistant_menu()
    assistant.global_search()
    
    print("--- Testing Utility Methods ---")
    assistant.load_data()
    assistant.export_data("json")
    assistant.import_data("/path/to/file.json")
    assistant.backup_data()
    assistant.restore_data("/path/to/backup.json")
    
    print("--- Testing Settings ---")
    settings = assistant.get_settings()
    assistant.update_settings({"theme": "dark", "language": "en"})
    assistant.reset_settings()
    
    print("--- Testing Statistics ---")
    stats = assistant.get_statistics()
    print(f"Stats returned: {stats}")
    assistant.generate_report("detailed")
    
    print("--- Testing Advanced Search ---")
    assistant.advanced_contact_search({"age_range": [25, 35], "city": "New York"})
    assistant.advanced_note_search({"tags": ["work"], "date_range": ["2024-01-01", "2024-12-31"]})
    
    print("--- Testing Batch Operations ---")
    contacts_data = [
        {"name": "Contact1", "phone": "1111111111"},
        {"name": "Contact2", "phone": "2222222222"}
    ]
    notes_data = [
        {"title": "Note1", "content": "Content1"},
        {"title": "Note2", "content": "Content2"}
    ]
    assistant.batch_add_contacts(contacts_data)
    assistant.batch_add_notes(notes_data)
    assistant.batch_delete_items("contacts", ["id1", "id2", "id3"])
    
    print("--- Testing AI/NLP Features ---")
    nlp_result = assistant.parse_natural_language_command("Add contact John with phone 555-1234")
    print(f"NLP result: {nlp_result}")
    
    entities = assistant.extract_entities("Contact John Smith at john@example.com, phone 555-1234")
    print(f"Extracted entities: {entities}")
    
    sentiment = assistant.analyze_sentiment("I love this application!")
    print(f"Sentiment analysis: {sentiment}")
    
    categories = assistant.auto_categorize_note("Meeting with client about project deadlines")
    print(f"Auto categories: {categories}")
    
    tags = assistant.suggest_tags("Important meeting tomorrow at 3pm with the development team")
    print(f"Suggested tags: {tags}")
    
    print("--- Testing Voice Features (Future) ---")
    audio_data = b"fake_audio_data"
    text = assistant.speech_to_text(audio_data)
    print(f"Speech to text result: {text}")
    
    audio = assistant.text_to_speech("Hello, this is a test message")
    print(f"Text to speech generated {len(audio)} bytes of audio data")
    
    print("--- Testing Integration Features ---")
    assistant.sync_with_cloud()
    assistant.export_to_calendar("John Smith")
    assistant.send_notification("Task completed successfully!", "success")
    
    print("--- Running Main Application ---")
    assistant.run()
    
    print("\n=== All AssistantStub methods tested successfully! ===")


if __name__ == "__main__":
    test_assistant_stub()
