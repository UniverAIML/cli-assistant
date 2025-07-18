#!/usr/bin/env python3
"""
Basic DataManager tests - core functionality.
"""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cli_assistant.database.contact_models import AddressBook, Record
from cli_assistant.database.data_manager import DataManager
from cli_assistant.database.note_models import NotesManager


class TestDataManagerBasic:
    """Test basic DataManager functionality."""

    def setup_method(self):
        """Setup test environment with temporary files."""
        self.temp_dir = tempfile.mkdtemp()
        self.contacts_file = os.path.join(self.temp_dir, "test_contacts.pkl")
        self.notes_file = os.path.join(self.temp_dir, "test_notes.pkl")
        self.dm = DataManager(self.contacts_file, self.notes_file)

    def teardown_method(self):
        """Clean up test files."""
        try:
            if os.path.exists(self.contacts_file):
                os.remove(self.contacts_file)
            if os.path.exists(self.notes_file):
                os.remove(self.notes_file)
            os.rmdir(self.temp_dir)
        except OSError:
            pass

    @pytest.mark.unit
    def test_load_data_empty(self):
        """Test loading when no files exist."""
        address_book, notes_manager = self.dm.load_data()

        assert isinstance(address_book, AddressBook)
        assert isinstance(notes_manager, NotesManager)
        assert len(address_book.data) == 0
        assert len(notes_manager.data) == 0

    @pytest.mark.unit
    def test_save_and_load_both(self):
        """Test saving and loading both contacts and notes together."""
        # Create test data
        book = AddressBook()
        record = Record("Test User")
        record.add_phone("1111111111")
        book.add_record(record)

        notes_manager = NotesManager()
        note_id = notes_manager.create_note("Test Note", "Test content", ["test"])

        # Test saving both
        result = self.dm.save_data(book, notes_manager)
        assert result is True

        # Test loading both
        loaded_book, loaded_notes = self.dm.load_data()

        assert len(loaded_book.data) == 1
        assert "Test User" in loaded_book.data

        assert len(loaded_notes.data) == 1
        loaded_note = loaded_notes.find_note(note_id)
        assert loaded_note is not None
        assert loaded_note.title == "Test Note"
