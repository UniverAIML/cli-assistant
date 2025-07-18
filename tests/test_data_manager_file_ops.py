#!/usr/bin/env python3
"""
DataManager file operations tests - file management functionality.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database.data_manager import DataManager
from database.contact_models import AddressBook, Record
from database.note_models import NotesManager


class TestDataManagerFileOps:
    """Test DataManager file operations."""

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
    def test_file_existence_checks(self):
        """Test file existence checking methods."""
        # Initially no files should exist
        assert not self.dm.contacts_file_exists()
        assert not self.dm.notes_file_exists()
        assert not self.dm.file_exists()

        # Create and save contacts
        book = AddressBook()
        self.dm.save_contacts(book)

        assert self.dm.contacts_file_exists()
        assert not self.dm.notes_file_exists()
        assert self.dm.file_exists()  # Should return True if any file exists

        # Create and save notes
        notes_manager = NotesManager()
        self.dm.save_notes(notes_manager)

        assert self.dm.contacts_file_exists()
        assert self.dm.notes_file_exists()
        assert self.dm.file_exists()

    @pytest.mark.unit
    def test_file_size_methods(self):
        """Test file size calculation methods."""
        # Initially files don't exist, so size should be 0
        assert self.dm.get_contacts_file_size() == 0
        assert self.dm.get_notes_file_size() == 0

        # Create and save some data
        book = AddressBook()
        record = Record("Test")
        book.add_record(record)
        self.dm.save_contacts(book)

        notes_manager = NotesManager()
        notes_manager.create_note("Test", "Content")
        self.dm.save_notes(notes_manager)

        # Files should now have some size
        assert self.dm.get_contacts_file_size() > 0
        assert self.dm.get_notes_file_size() > 0

    @pytest.mark.unit
    def test_file_deletion(self):
        """Test file deletion methods."""
        # Create files first
        book = AddressBook()
        notes_manager = NotesManager()
        self.dm.save_data(book, notes_manager)

        assert self.dm.contacts_file_exists()
        assert self.dm.notes_file_exists()

        # Test deleting contacts file
        result = self.dm.delete_contacts_file()
        assert result is True
        assert not self.dm.contacts_file_exists()
        assert self.dm.notes_file_exists()

        # Test deleting notes file
        result = self.dm.delete_notes_file()
        assert result is True
        assert not self.dm.notes_file_exists()

        # Test deleting non-existent files
        assert self.dm.delete_contacts_file() is False
        assert self.dm.delete_notes_file() is False

    @pytest.mark.unit
    def test_file_size_empty_files(self):
        """Test file sizes with empty data structures."""
        # Save empty structures
        empty_book = AddressBook()
        empty_notes = NotesManager()

        self.dm.save_data(empty_book, empty_notes)

        # Even empty files should have some size (pickle overhead)
        assert self.dm.get_contacts_file_size() > 0
        assert self.dm.get_notes_file_size() > 0

    @pytest.mark.unit
    def test_file_operations_sequence(self):
        """Test sequence of file operations."""
        # Start with no files
        assert not self.dm.file_exists()

        # Create contacts file only
        book = AddressBook()
        record = Record("Test User")
        book.add_record(record)
        self.dm.save_contacts(book)

        assert self.dm.contacts_file_exists()
        assert not self.dm.notes_file_exists()
        assert self.dm.file_exists()

        # Add notes file
        notes_manager = NotesManager()
        notes_manager.create_note("Test Note", "Content")
        self.dm.save_notes(notes_manager)

        assert self.dm.contacts_file_exists()
        assert self.dm.notes_file_exists()
        assert self.dm.file_exists()

        # Delete contacts, keep notes
        self.dm.delete_contacts_file()
        assert not self.dm.contacts_file_exists()
        assert self.dm.notes_file_exists()
        assert self.dm.file_exists()  # Still True because notes exist

        # Delete notes too
        self.dm.delete_notes_file()
        assert not self.dm.contacts_file_exists()
        assert not self.dm.notes_file_exists()
        assert not self.dm.file_exists()  # Now False
