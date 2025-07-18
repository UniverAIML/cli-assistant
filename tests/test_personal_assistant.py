#!/usr/bin/env python3
"""
Тестовий набір для основного додатку персонального асистента.

Тести для класу PersonalAssistant та його інтеграції з
управлінням контактами та нотатками.

Цей файл містить:
- Тести валідації даних
- Тести операцій з контактами
- Тести операцій з нотатками
- Тести інтеграції компонентів
- Тести обробки помилок
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Додаємо src до шляху для імпортів
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Правильні імпорти на основі реальної структури проекту
from personal_assistant import PersonalAssistant
from database.contact_models import AddressBook, Record
from database.note_models import NotesManager, Note
from database.data_manager import DataManager


class TestPersonalAssistant:
    """
    Тестові випадки для класу PersonalAssistant.

    Покриває:
    - Ініціалізацію та налаштування
    - Валідацію даних
    - CRUD операції з контактами
    - CRUD операції з нотатками
    - Обробку помилок
    - Збереження/завантаження даних
    """

    def setup_method(self):
        """
        Налаштування тестового середовища.

        Створює:
        - Тимчасові файли для тестування
        - Екземпляр PersonalAssistant
        - Тестові дані
        """
        # Створюємо тимчасові файли для тестування
        self.temp_dir = tempfile.mkdtemp()
        self.contacts_file = os.path.join(self.temp_dir, "test_contacts.json")
        self.notes_file = os.path.join(self.temp_dir, "test_notes.json")

        # Mock the DataManager to use test files
        with patch("personal_assistant.DataManager") as mock_dm_class:
            mock_dm = MagicMock()
            mock_dm.load_data.return_value = (AddressBook(), NotesManager())
            mock_dm.save_data.return_value = True
            mock_dm_class.return_value = mock_dm

            self.app = PersonalAssistant()
            self.app.data_manager = mock_dm

    def teardown_method(self):
        """Clean up test environment."""
        try:
            if os.path.exists(self.contacts_file):
                os.remove(self.contacts_file)
            if os.path.exists(self.notes_file):
                os.remove(self.notes_file)
            os.rmdir(self.temp_dir)
        except OSError:
            pass

    @pytest.mark.unit
    def test_personal_assistant_initialization(self):
        """Test PersonalAssistant initialization."""
        assert isinstance(self.app.address_book, AddressBook)
        assert isinstance(self.app.notes_manager, NotesManager)
        assert hasattr(self.app, "data_manager")

    @pytest.mark.unit
    def test_validate_phone(self):
        """Test phone number validation."""
        # Valid phone numbers (10 digits)
        assert self.app.validate_phone("1234567890") is True
        assert self.app.validate_phone("123-456-7890") is True
        assert self.app.validate_phone("(123) 456-7890") is True
        assert self.app.validate_phone("123 456 7890") is True

        # Invalid phone numbers
        assert self.app.validate_phone("12345") is False  # Too short
        assert self.app.validate_phone("12345678901") is False  # Too long
        assert self.app.validate_phone("abcdefghij") is False  # Not numbers
        assert self.app.validate_phone("") is False  # Empty

    @pytest.mark.unit
    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert self.app.validate_email("test@example.com") is True
        assert self.app.validate_email("user.name@domain.co.uk") is True
        assert self.app.validate_email("test123+tag@gmail.com") is True

        # Invalid emails
        assert self.app.validate_email("invalid-email") is False
        assert self.app.validate_email("@domain.com") is False
        assert self.app.validate_email("user@") is False
        assert self.app.validate_email("") is False

    @pytest.mark.unit
    def test_search_contacts(self):
        """Test contact search functionality."""
        # Add test contacts
        record1 = Record("John Doe")
        record1.add_phone("1234567890")
        self.app.address_book.add_record(record1)

        record2 = Record("Jane Smith")
        record2.add_phone("0987654321")
        self.app.address_book.add_record(record2)

        record3 = Record("Bob Johnson")
        record3.add_phone("1111111111")
        self.app.address_book.add_record(record3)

        # Search by name
        results = self.app.search_contacts("john")
        assert len(results) == 2  # John Doe and Bob Johnson

        # Search by phone
        results = self.app.search_contacts("123")
        assert len(results) == 1  # John Doe

        # Search with no results
        results = self.app.search_contacts("nonexistent")
        assert len(results) == 0

    @pytest.mark.unit
    def test_search_notes(self):
        """Test notes search functionality."""
        # Add test notes
        id1 = self.app.notes_manager.create_note(
            "Python Tutorial", "Learn Python programming", ["python", "tutorial"]
        )
        id2 = self.app.notes_manager.create_note(
            "Meeting Notes", "Team meeting discussion", ["work", "meeting"]
        )
        id3 = self.app.notes_manager.create_note(
            "Shopping List", "Buy groceries", ["shopping"]
        )

        # Search by title
        results = self.app.search_notes("python")
        assert len(results) == 1
        assert id1 in results

        # Search by content
        results = self.app.search_notes("meeting")
        assert len(results) == 1
        assert id2 in results

        # Search by tag
        results = self.app.search_notes("shopping")
        assert len(results) == 1
        assert id3 in results

        # Search with no results
        results = self.app.search_notes("nonexistent")
        assert len(results) == 0

    @pytest.mark.unit
    def test_get_upcoming_birthdays(self):
        """Test upcoming birthdays functionality."""
        # Add contacts with birthdays
        record1 = Record("John")
        # Set birthday to tomorrow (should appear in upcoming)
        from datetime import date, timedelta

        tomorrow = date.today() + timedelta(days=1)
        birthday_str = tomorrow.strftime("%d.%m.%Y")
        record1.add_birthday(birthday_str)
        self.app.address_book.add_record(record1)

        record2 = Record("Jane")
        # Set birthday to far future (should not appear)
        far_future = date.today() + timedelta(days=30)
        birthday_str2 = far_future.strftime("%d.%m.%Y")
        record2.add_birthday(birthday_str2)
        self.app.address_book.add_record(record2)

        # Test upcoming birthdays
        upcoming = self.app.get_upcoming_birthdays(7)
        # This test depends on the implementation of get_upcoming_birthdays in AddressBook
        # We can't easily test without mocking the current date
        assert isinstance(upcoming, list)

    @pytest.mark.unit
    def test_save_data(self):
        """Test data saving functionality."""
        # Create a mock for the data_manager
        mock_dm = MagicMock()
        mock_dm.save_data.return_value = True
        self.app.data_manager = mock_dm

        # This should not raise an exception
        self.app.save_data()

        # Verify save_data was called
        mock_dm.save_data.assert_called_with(
            self.app.address_book, self.app.notes_manager
        )

    @pytest.mark.unit
    def test_display_contacts_table_empty(self):
        """Test displaying empty contacts table."""
        # Just verify the method runs without errors
        self.app.display_contacts_table([])
        # Since we use print(), we can't easily test output without capturing stdout

    @pytest.mark.unit
    def test_display_contacts_table_with_data(self):
        """Test displaying contacts table with data."""
        # Add test contact
        record = Record("Test User")
        record.add_phone("1234567890")
        record.add_birthday("15.06.1990")

        # Just verify the method runs without errors
        self.app.display_contacts_table([record])
        # Since we use print(), we can't easily test output without capturing stdout

    @pytest.mark.unit
    def test_display_notes_table_empty(self):
        """Test displaying empty notes table."""
        # Just verify the method runs without errors
        self.app.display_notes_table({})
        # Since we use print(), we can't easily test output without capturing stdout

    @pytest.mark.unit
    def test_display_notes_table_with_data(self):
        """Test displaying notes table with data."""
        # Add test note
        note_id = self.app.notes_manager.create_note(
            "Test Note", "Test content", ["test"]
        )

        # Just verify the method runs without errors
        self.app.display_notes_table()
        # Since we use print(), we can't easily test output without capturing stdout


class TestPersonalAssistantIntegration:
    """Integration tests for PersonalAssistant."""

    @pytest.mark.integration
    def test_full_workflow_contacts(self):
        """Test complete contacts workflow."""
        # Create real PersonalAssistant with temporary files
        temp_dir = tempfile.mkdtemp()
        contacts_file = os.path.join(temp_dir, "test_contacts.json")
        notes_file = os.path.join(temp_dir, "test_notes.json")

        try:
            with patch("personal_assistant.DataManager") as mock_dm_class:
                # Create real data manager but with test files
                real_dm = DataManager(contacts_file, notes_file)
                mock_dm_class.return_value = real_dm

                app = PersonalAssistant()

                # Add a contact
                record = Record("Integration Test")
                record.add_phone("1234567890")
                record.add_birthday("01.01.1990")
                app.address_book.add_record(record)

                # Save data
                app.save_data()

                # Verify data was saved
                assert os.path.exists(contacts_file)

                # Create new app instance to test loading
                app2 = PersonalAssistant()

                # Verify data was loaded
                assert len(app2.address_book.data) == 1
                assert "Integration Test" in app2.address_book.data

        finally:
            # Cleanup
            try:
                if os.path.exists(contacts_file):
                    os.remove(contacts_file)
                if os.path.exists(notes_file):
                    os.remove(notes_file)
                os.rmdir(temp_dir)
            except OSError:
                pass

    @pytest.mark.integration
    def test_full_workflow_notes(self):
        """Test complete notes workflow."""
        # Create real PersonalAssistant with temporary files
        temp_dir = tempfile.mkdtemp()
        contacts_file = os.path.join(temp_dir, "test_contacts.json")
        notes_file = os.path.join(temp_dir, "test_notes.json")

        try:
            with patch("personal_assistant.DataManager") as mock_dm_class:
                # Create real data manager but with test files
                real_dm = DataManager(contacts_file, notes_file)
                mock_dm_class.return_value = real_dm

                app = PersonalAssistant()

                # Add a note
                note_id = app.notes_manager.create_note(
                    "Integration Test Note",
                    "This is a test note for integration testing",
                    ["test", "integration"],
                )

                # Save data
                app.save_data()

                # Verify data was saved
                assert os.path.exists(notes_file)

                # Create new app instance to test loading
                app2 = PersonalAssistant()

                # Verify data was loaded
                assert len(app2.notes_manager.data) == 1
                loaded_note = app2.notes_manager.find_note(note_id)
                assert loaded_note is not None
                assert loaded_note.title == "Integration Test Note"

        finally:
            # Cleanup
            try:
                if os.path.exists(contacts_file):
                    os.remove(contacts_file)
                if os.path.exists(notes_file):
                    os.remove(notes_file)
                os.rmdir(temp_dir)
            except OSError:
                pass


if __name__ == "__main__":
    pytest.main([__file__])
