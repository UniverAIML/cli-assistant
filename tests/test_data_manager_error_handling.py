#!/usr/bin/env python3
"""
DataManager error handling tests - error conditions and corrupted data.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cli_assistant.database.data_manager import DataManager
from cli_assistant.database.contact_models import AddressBook
from cli_assistant.database.note_models import NotesManager


class TestDataManagerErrorHandling:
    """Test DataManager error handling."""

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
    def test_error_handling_corrupted_files(self):
        """Test handling of corrupted files."""
        # Create corrupted contacts file
        with open(self.contacts_file, "w") as f:
            f.write("This is not valid pickle data")

        # Should return new empty AddressBook instead of crashing
        loaded_book = self.dm.load_contacts()
        assert isinstance(loaded_book, AddressBook)
        assert len(loaded_book.data) == 0

        # Create corrupted notes file
        with open(self.notes_file, "w") as f:
            f.write("This is also not valid pickle data")

        # Should return new empty NotesManager instead of crashing
        loaded_notes = self.dm.load_notes()
        assert isinstance(loaded_notes, NotesManager)
        assert len(loaded_notes.data) == 0

    @pytest.mark.unit
    def test_error_handling_corrupted_combined_load(self):
        """Test handling corrupted files when loading both together."""
        # Create corrupted files
        with open(self.contacts_file, "w") as f:
            f.write("Corrupted contacts")
        with open(self.notes_file, "w") as f:
            f.write("Corrupted notes")

        # Should return new empty instances
        loaded_book, loaded_notes = self.dm.load_data()
        assert isinstance(loaded_book, AddressBook)
        assert isinstance(loaded_notes, NotesManager)
        assert len(loaded_book.data) == 0
        assert len(loaded_notes.data) == 0

    @pytest.mark.unit
    def test_error_handling_binary_corrupted_files(self):
        """Test handling files with binary garbage."""
        # Create files with binary garbage
        with open(self.contacts_file, "wb") as f:
            f.write(b"\x00\x01\x02\x03\x04\x05\xff\xfe\xfd")

        with open(self.notes_file, "wb") as f:
            f.write(b"\xff\xfe\xfd\xfc\xfb\xfa\x00\x01\x02")

        # Should handle gracefully
        loaded_book = self.dm.load_contacts()
        loaded_notes = self.dm.load_notes()

        assert isinstance(loaded_book, AddressBook)
        assert isinstance(loaded_notes, NotesManager)
        assert len(loaded_book.data) == 0
        assert len(loaded_notes.data) == 0

    @pytest.mark.unit
    def test_error_handling_permission_denied(self):
        """Test handling permission denied errors."""
        # This test might not work on all systems, so we'll skip implementation
        # for now as it requires special file permission setup
        pass

    @pytest.mark.unit
    def test_error_handling_empty_files(self):
        """Test handling completely empty files."""
        # Create empty files
        open(self.contacts_file, "w").close()
        open(self.notes_file, "w").close()

        # Should handle gracefully
        loaded_book = self.dm.load_contacts()
        loaded_notes = self.dm.load_notes()

        assert isinstance(loaded_book, AddressBook)
        assert isinstance(loaded_notes, NotesManager)
        assert len(loaded_book.data) == 0
        assert len(loaded_notes.data) == 0

    @pytest.mark.unit
    def test_error_handling_partial_pickle_data(self):
        """Test handling files with partial/truncated pickle data."""
        # Create a valid pickle file first
        book = AddressBook()
        self.dm.save_contacts(book)

        # Now truncate it to make it invalid
        with open(self.contacts_file, "r+b") as f:
            f.truncate(10)  # Keep only first 10 bytes

        # Should handle gracefully
        loaded_book = self.dm.load_contacts()
        assert isinstance(loaded_book, AddressBook)
        assert len(loaded_book.data) == 0

    @pytest.mark.unit
    def test_error_handling_load_nonexistent_specific_files(self):
        """Test loading from specific non-existent files."""
        # Test loading contacts when file doesn't exist
        loaded_book = self.dm.load_contacts()
        assert isinstance(loaded_book, AddressBook)
        assert len(loaded_book.data) == 0

        # Test loading notes when file doesn't exist
        loaded_notes = self.dm.load_notes()
        assert isinstance(loaded_notes, NotesManager)
        assert len(loaded_notes.data) == 0
