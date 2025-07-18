#!/usr/bin/env python3
"""
DataManager contacts tests - contact-specific functionality.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database.data_manager import DataManager
from database.contact_models import AddressBook, Record


class TestDataManagerContacts:
    """Test DataManager contact functionality."""

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
    def test_save_and_load_contacts(self):
        """Test saving and loading contacts."""
        # Create test data
        book = AddressBook()
        record1 = Record("John Doe")
        record1.add_phone("1234567890")
        record1.add_birthday("15.06.1990")
        book.add_record(record1)

        record2 = Record("Alice Smith")
        record2.add_phone("0987654321")
        book.add_record(record2)

        # Test saving contacts
        result = self.dm.save_contacts(book)
        assert result is True
        assert self.dm.contacts_file_exists()

        # Test loading contacts
        loaded_book = self.dm.load_contacts()
        assert len(loaded_book.data) == 2
        assert "John Doe" in loaded_book.data
        assert "Alice Smith" in loaded_book.data

        # Verify contact details
        john = loaded_book.find("John Doe")
        assert john is not None
        assert len(john.phones) == 1
        assert john.phones[0].value == "1234567890"
        assert john.birthday is not None
        assert john.birthday.value == "15.06.1990"

    @pytest.mark.unit
    def test_save_contacts_with_birthday(self):
        """Test saving contacts with birthday information."""
        book = AddressBook()
        record = Record("Birthday Person")
        record.add_phone("5555555555")
        record.add_birthday("01.01.1990")
        book.add_record(record)

        # Save and reload
        self.dm.save_contacts(book)
        loaded_book = self.dm.load_contacts()

        loaded_record = loaded_book.find("Birthday Person")
        assert loaded_record is not None
        assert loaded_record.birthday is not None
        assert loaded_record.birthday.value == "01.01.1990"

    @pytest.mark.unit
    def test_save_contacts_multiple_phones(self):
        """Test saving contacts with multiple phone numbers."""
        book = AddressBook()
        record = Record("Multi Phone")
        record.add_phone("1111111111")
        record.add_phone("2222222222")
        record.add_phone("3333333333")
        book.add_record(record)

        # Save and reload
        self.dm.save_contacts(book)
        loaded_book = self.dm.load_contacts()

        loaded_record = loaded_book.find("Multi Phone")
        assert loaded_record is not None
        assert len(loaded_record.phones) == 3
        phone_values = [phone.value for phone in loaded_record.phones]
        assert "1111111111" in phone_values
        assert "2222222222" in phone_values
        assert "3333333333" in phone_values
