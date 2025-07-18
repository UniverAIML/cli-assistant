#!/usr/bin/env python3
"""
Тестовий набір для системи управління адресною книгою

Комплексні тести, що покривають всі класи та функціональність включаючи:
- Валідацію полів
- Валідацію імен
- Валідацію номерів телефонів
- Управління записами
- Операції з адресною книгою
- Обробку помилок
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from database.contact_models import (
    Field,
    Name,
    Phone,
    Record,
    AddressBook,
    ContactData,
    Birthday,
)
from database.data_manager import DataManager
from datetime import date, timedelta
import tempfile
import os


class TestField:
    """Test cases for Field base class."""

    @pytest.mark.unit
    def test_field_creation(self):
        """Test basic field creation."""
        field = Field("test_value")
        assert field.value == "test_value"
        assert str(field) == "test_value"

    @pytest.mark.unit
    def test_field_str_representation(self):
        """Test string representation of field."""
        field = Field("123")
        assert str(field) == "123"


class TestName:
    """Test cases for Name class."""

    @pytest.mark.unit
    def test_name_creation_valid(self):
        """Test valid name creation."""
        name = Name("John Doe")
        assert name.value == "John Doe"
        assert str(name) == "John Doe"

    @pytest.mark.unit
    def test_name_creation_with_spaces(self):
        """Test name creation with leading/trailing spaces."""
        name = Name("  John Doe  ")
        assert name.value == "John Doe"

    @pytest.mark.unit
    def test_name_creation_empty_string(self):
        """Test name creation with empty string."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Name("")

    @pytest.mark.unit
    def test_name_creation_only_spaces(self):
        """Test name creation with only spaces."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Name("   ")

    @pytest.mark.unit
    def test_name_creation_none(self):
        """Test name creation with None."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Name(None)  # type: ignore


class TestPhone:
    """Test cases for Phone class."""

    @pytest.mark.unit
    def test_phone_creation_valid(self):
        """Test valid phone creation."""
        phone = Phone("1234567890")
        assert phone.value == "1234567890"
        assert str(phone) == "1234567890"

    @pytest.mark.unit
    def test_phone_creation_with_formatting(self):
        """Test phone creation with formatting characters."""
        phone = Phone("(123) 456-7890")
        assert phone.value == "(123) 456-7890"

    @pytest.mark.unit
    def test_phone_validation_exactly_10_digits(self):
        """Test phone validation with exactly 10 digits."""
        valid_phones = [
            "1234567890",
            "(123) 456-7890",
            "123-456-7890",
            "123.456.7890",
            " 123 456 7890 ",
        ]

        for phone_str in valid_phones:
            phone = Phone(phone_str)
            assert phone.value == phone_str

    @pytest.mark.unit
    def test_phone_validation_less_than_10_digits(self):
        """Test phone validation with less than 10 digits."""
        invalid_phones = ["123456789", "12345", "123-456-789", "(123) 456-789"]

        for phone_str in invalid_phones:
            with pytest.raises(
                ValueError, match="Phone number must contain exactly 10 digits"
            ):
                Phone(phone_str)

    @pytest.mark.unit
    def test_phone_validation_more_than_10_digits(self):
        """Test phone validation with more than 10 digits."""
        invalid_phones = ["12345678901", "123-456-78901", "(123) 456-78901"]

        for phone_str in invalid_phones:
            with pytest.raises(
                ValueError, match="Phone number must contain exactly 10 digits"
            ):
                Phone(phone_str)

    @pytest.mark.unit
    def test_phone_validation_no_digits(self):
        """Test phone validation with no digits."""
        invalid_phones = ["abcdefghij", "abc-def-ghij", "(abc) def-ghij"]

        for phone_str in invalid_phones:
            with pytest.raises(
                ValueError, match="Phone number must contain exactly 10 digits"
            ):
                Phone(phone_str)

    @pytest.mark.unit
    def test_phone_validation_empty_string(self):
        """Test phone validation with empty string."""
        with pytest.raises(
            ValueError, match="Phone number must contain exactly 10 digits"
        ):
            Phone("")


class TestRecord:
    """Test cases for Record class."""

    @pytest.mark.unit
    def test_record_creation(self):
        """Test basic record creation."""
        record = Record("John")
        assert record.name.value == "John"
        assert len(record.phones) == 0

    @pytest.mark.unit
    def test_add_phone_valid(self):
        """Test adding valid phone to record."""
        record = Record("John")
        record.add_phone("1234567890")

        assert len(record.phones) == 1
        assert record.phones[0].value == "1234567890"

    @pytest.mark.unit
    def test_add_phone_multiple(self):
        """Test adding multiple phones to record."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")

        assert len(record.phones) == 2
        assert record.phones[0].value == "1234567890"
        assert record.phones[1].value == "5555555555"

    @pytest.mark.unit
    def test_add_phone_duplicate(self):
        """Test adding duplicate phone to record."""
        record = Record("John")
        record.add_phone("1234567890")

        with pytest.raises(
            ValueError, match="Phone 1234567890 already exists for John"
        ):
            record.add_phone("1234567890")

    @pytest.mark.unit
    def test_add_phone_invalid(self):
        """Test adding invalid phone to record."""
        record = Record("John")

        with pytest.raises(
            ValueError, match="Phone number must contain exactly 10 digits"
        ):
            record.add_phone("123456789")

    @pytest.mark.unit
    def test_remove_phone_existing(self):
        """Test removing existing phone from record."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")

        record.remove_phone("1234567890")
        assert len(record.phones) == 1
        assert record.phones[0].value == "5555555555"

    @pytest.mark.unit
    def test_remove_phone_non_existing(self):
        """Test removing non-existing phone from record."""
        record = Record("John")
        record.add_phone("1234567890")

        with pytest.raises(ValueError, match="Phone 9999999999 not found for John"):
            record.remove_phone("9999999999")

    @pytest.mark.unit
    def test_edit_phone_existing(self):
        """Test editing existing phone in record."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")

        record.edit_phone("1234567890", "1112223333")

        assert len(record.phones) == 2
        found_phone = record.find_phone("1112223333")
        assert found_phone is not None
        assert found_phone.value == "1112223333"

    @pytest.mark.unit
    def test_edit_phone_non_existing(self):
        """Test editing non-existing phone in record."""
        record = Record("John")
        record.add_phone("1234567890")

        with pytest.raises(ValueError, match="Phone 9999999999 not found for John"):
            record.edit_phone("9999999999", "1112223333")

    @pytest.mark.unit
    def test_edit_phone_to_existing(self):
        """Test editing phone to already existing phone."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")

        with pytest.raises(
            ValueError, match="Phone 5555555555 already exists for John"
        ):
            record.edit_phone("1234567890", "5555555555")

    @pytest.mark.unit
    def test_edit_phone_invalid_new_phone(self):
        """Test editing to invalid phone number."""
        record = Record("John")
        record.add_phone("1234567890")

        with pytest.raises(
            ValueError, match="Phone number must contain exactly 10 digits"
        ):
            record.edit_phone("1234567890", "123456789")

    @pytest.mark.unit
    def test_find_phone_existing(self):
        """Test finding existing phone in record."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")

        found_phone = record.find_phone("1234567890")
        assert found_phone is not None
        assert found_phone.value == "1234567890"

    @pytest.mark.unit
    def test_find_phone_non_existing(self):
        """Test finding non-existing phone in record."""
        record = Record("John")
        record.add_phone("1234567890")

        found_phone = record.find_phone("9999999999")
        assert found_phone is None

    @pytest.mark.unit
    def test_find_phone_with_formatting(self):
        """Test finding phone with different formatting."""
        record = Record("John")
        record.add_phone("(123) 456-7890")

        found_phone = record.find_phone("1234567890")
        assert found_phone is not None
        assert found_phone.value == "(123) 456-7890"

    @pytest.mark.unit
    def test_str_representation_no_phones(self):
        """Test string representation with no phones."""
        record = Record("John")
        expected = "Contact name: John, phones: "
        assert str(record) == expected

    @pytest.mark.unit
    def test_str_representation_with_phones(self):
        """Test string representation with phones."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")

        expected = "Contact name: John, phones: 1234567890; 5555555555"
        assert str(record) == expected


class TestAddressBook:
    """Test cases for AddressBook class."""

    @pytest.mark.unit
    def test_address_book_creation(self):
        """Test basic address book creation."""
        book = AddressBook()
        assert len(book.data) == 0

    @pytest.mark.unit
    def test_add_record(self):
        """Test adding record to address book."""
        book = AddressBook()
        record = Record("John")
        book.add_record(record)

        assert len(book.data) == 1
        assert "John" in book.data
        assert book.data["John"] == record

    @pytest.mark.unit
    def test_add_multiple_records(self):
        """Test adding multiple records to address book."""
        book = AddressBook()
        john_record = Record("John")
        jane_record = Record("Jane")

        book.add_record(john_record)
        book.add_record(jane_record)

        assert len(book.data) == 2
        assert "John" in book.data
        assert "Jane" in book.data

    @pytest.mark.unit
    def test_add_record_duplicate_name(self):
        """Test adding record with duplicate name overwrites."""
        book = AddressBook()

        john_record1 = Record("John")
        john_record1.add_phone("1234567890")

        john_record2 = Record("John")
        john_record2.add_phone("5555555555")

        book.add_record(john_record1)
        book.add_record(john_record2)  # This should overwrite the first

        assert len(book.data) == 1
        found_record = book.find("John")
        assert found_record is not None
        assert found_record == john_record2
        assert len(found_record.phones) == 1
        assert found_record.phones[0].value == "5555555555"

    @pytest.mark.unit
    def test_find_existing_record(self):
        """Test finding existing record in address book."""
        book = AddressBook()
        record = Record("John")
        book.add_record(record)

        found_record = book.find("John")
        assert found_record is not None
        assert found_record == record

    @pytest.mark.unit
    def test_find_non_existing_record(self):
        """Test finding non-existing record in address book."""
        book = AddressBook()

        found_record = book.find("NonExisting")
        assert found_record is None

    @pytest.mark.unit
    def test_delete_existing_record(self):
        """Test deleting existing record from address book."""
        book = AddressBook()
        record = Record("John")
        book.add_record(record)

        assert "John" in book.data
        book.delete("John")
        assert "John" not in book.data
        assert len(book.data) == 0

    @pytest.mark.unit
    def test_delete_non_existing_record(self):
        """Test deleting non-existing record from address book."""
        book = AddressBook()

        with pytest.raises(ValueError, match="Contact NonExisting not found"):
            book.delete("NonExisting")

    @pytest.mark.unit
    def test_get_all_records(self):
        """Test getting all records from address book."""
        book = AddressBook()
        john_record = Record("John")
        jane_record = Record("Jane")

        book.add_record(john_record)
        book.add_record(jane_record)

        all_records = book.get_all_records()
        assert len(all_records) == 2
        assert "John" in all_records
        assert "Jane" in all_records
        assert all_records["John"] == john_record
        assert all_records["Jane"] == jane_record

    @pytest.mark.unit
    def test_get_all_records_empty(self):
        """Test getting all records from empty address book."""
        book = AddressBook()
        all_records = book.get_all_records()
        assert len(all_records) == 0
        assert all_records == {}


class TestIntegration:
    """Integration tests for the complete Address Book system."""

    @pytest.mark.integration
    def test_full_workflow(self):
        """Test complete workflow as described in requirements."""
        # Create new address book
        book = AddressBook()

        # Create record for John
        john_record = Record("John")
        john_record.add_phone("1234567890")
        john_record.add_phone("5555555555")

        # Add John's record to address book
        book.add_record(john_record)

        # Create and add new record for Jane
        jane_record = Record("Jane")
        jane_record.add_phone("9876543210")
        book.add_record(jane_record)

        # Verify records are in the book
        assert len(book.data) == 2
        assert book.find("John") is not None
        assert book.find("Jane") is not None

        # Find and edit phone for John
        john = book.find("John")
        assert john is not None
        john.edit_phone("1234567890", "1112223333")

        # Verify the change
        updated_phone = john.find_phone("1112223333")
        assert updated_phone is not None
        assert updated_phone.value == "1112223333"

        # Verify old phone is gone
        old_phone = john.find_phone("1234567890")
        assert old_phone is None

        # Search for specific phone in John's record
        found_phone = john.find_phone("5555555555")
        assert found_phone is not None
        assert found_phone.value == "5555555555"

        # Delete Jane's record
        book.delete("Jane")
        assert len(book.data) == 1
        assert book.find("Jane") is None
        assert book.find("John") is not None


class TestTypedDict:
    """Test cases for TypedDict functionality."""

    @pytest.mark.unit
    def test_contact_data_structure(self):
        """Test ContactData TypedDict structure."""
        contact: ContactData = {
            "name": "John Doe",
            "phones": ["1234567890", "5555555555"],
            "birthday": None,
        }

        assert contact["name"] == "John Doe"
        assert len(contact["phones"]) == 2
        assert "1234567890" in contact["phones"]
        assert "5555555555" in contact["phones"]
        assert contact["birthday"] is None

    @pytest.mark.unit
    def test_record_to_typed_dict(self):
        """Test Record to_typed_dict method."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")

        typed_dict = record.to_typed_dict()

        assert typed_dict["name"] == "John"
        assert len(typed_dict["phones"]) == 2
        assert "1234567890" in typed_dict["phones"]
        assert "5555555555" in typed_dict["phones"]
        assert typed_dict["birthday"] is None

    @pytest.mark.unit
    def test_record_to_typed_dict_no_phones(self):
        """Test Record to_typed_dict with no phones."""
        record = Record("John")

        typed_dict = record.to_typed_dict()

        assert typed_dict["name"] == "John"
        assert typed_dict["phones"] == []
        assert typed_dict["birthday"] is None

    @pytest.mark.unit
    def test_address_book_to_typed_dict(self):
        """Test AddressBook to_typed_dict method."""
        book = AddressBook()

        john_record = Record("John")
        john_record.add_phone("1234567890")
        book.add_record(john_record)

        jane_record = Record("Jane")
        jane_record.add_phone("9876543210")
        jane_record.add_phone("5555555555")
        book.add_record(jane_record)

        typed_dict = book.to_typed_dict()

        assert len(typed_dict) == 2
        assert "John" in typed_dict
        assert "Jane" in typed_dict

        assert typed_dict["John"]["name"] == "John"
        assert typed_dict["John"]["phones"] == ["1234567890"]
        assert typed_dict["John"]["birthday"] is None

        assert typed_dict["Jane"]["name"] == "Jane"
        assert len(typed_dict["Jane"]["phones"]) == 2
        assert "9876543210" in typed_dict["Jane"]["phones"]
        assert "5555555555" in typed_dict["Jane"]["phones"]
        assert typed_dict["Jane"]["birthday"] is None

    @pytest.mark.unit
    def test_address_book_to_typed_dict_empty(self):
        """Test AddressBook to_typed_dict with empty book."""
        book = AddressBook()

        typed_dict = book.to_typed_dict()

        assert typed_dict == {}


class TestBirthday:
    """Test cases for Birthday class."""

    @pytest.mark.unit
    def test_birthday_creation(self):
        """Test valid birthday creation."""
        birthday = Birthday("01.01.1990")
        assert birthday.value == "01.01.1990"
        assert birthday.date == date(1990, 1, 1)

    @pytest.mark.unit
    def test_birthday_creation_invalid_format(self):
        """Test birthday creation with invalid format."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("01/01/1990")

    @pytest.mark.unit
    def test_birthday_creation_invalid_date(self):
        """Test birthday creation with invalid date."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("30.02.1990")

    @pytest.mark.unit
    def test_birthday_str_representation(self):
        """Test string representation of birthday."""
        birthday = Birthday("01.01.1990")
        assert str(birthday) == "01.01.1990"

    @pytest.mark.unit
    def test_birthday_creation_valid_format(self):
        """Test valid birthday creation with DD.MM.YYYY format."""
        birthday = Birthday("15.03.1990")
        assert birthday.value == "15.03.1990"
        assert str(birthday) == "15.03.1990"
        assert birthday.date == date(1990, 3, 15)

    @pytest.mark.unit
    def test_birthday_creation_current_year(self):
        """Test birthday creation with current year."""
        birthday = Birthday("01.01.2025")
        assert birthday.value == "01.01.2025"
        assert birthday.date == date(2025, 1, 1)

    @pytest.mark.unit
    def test_birthday_creation_leap_year(self):
        """Test birthday creation with leap year date."""
        birthday = Birthday("29.02.2020")
        assert birthday.value == "29.02.2020"
        assert birthday.date == date(2020, 2, 29)

    @pytest.mark.unit
    def test_birthday_creation_invalid_format_american(self):
        """Test birthday creation with American format (MM/DD/YYYY)."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("03/15/1990")

    @pytest.mark.unit
    def test_birthday_creation_invalid_format_iso(self):
        """Test birthday creation with ISO format (YYYY-MM-DD)."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("1990-03-15")

    @pytest.mark.unit
    def test_birthday_creation_invalid_format_no_dots(self):
        """Test birthday creation without dots."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("15031990")

    @pytest.mark.unit
    def test_birthday_creation_invalid_date_complex(self):
        """Test birthday creation with invalid date."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("32.13.2020")  # Invalid day and month

    @pytest.mark.unit
    def test_birthday_creation_invalid_month(self):
        """Test birthday creation with invalid month."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("15.13.2020")  # Month 13 doesn't exist

    @pytest.mark.unit
    def test_birthday_creation_invalid_day(self):
        """Test birthday creation with invalid day."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("32.03.2020")  # Day 32 doesn't exist

    @pytest.mark.unit
    def test_birthday_creation_invalid_leap_year(self):
        """Test birthday creation with invalid leap year date."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("29.02.2021")  # 2021 is not a leap year

    @pytest.mark.unit
    def test_birthday_creation_empty_string(self):
        """Test birthday creation with empty string."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("")

    @pytest.mark.unit
    def test_birthday_creation_partial_date(self):
        """Test birthday creation with partial date."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("15.03")

    @pytest.mark.unit
    def test_birthday_creation_extra_characters(self):
        """Test birthday creation with extra characters."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("15.03.1990 extra")


class TestRecordWithBirthday:
    """Test cases for Record class with birthday functionality."""

    @pytest.mark.unit
    def test_record_creation_with_birthday_none(self):
        """Test record creation has birthday as None initially."""
        record = Record("John")
        assert record.birthday is None

    @pytest.mark.unit
    def test_add_birthday_valid(self):
        """Test adding valid birthday to record."""
        record = Record("John")
        record.add_birthday("15.03.1990")

        assert record.birthday is not None
        assert record.birthday.value == "15.03.1990"
        assert record.birthday.date == date(1990, 3, 15)

    @pytest.mark.unit
    def test_add_birthday_replace_existing(self):
        """Test replacing existing birthday."""
        record = Record("John")
        record.add_birthday("15.03.1990")
        record.add_birthday("20.05.1985")

        assert record.birthday is not None
        assert record.birthday.value == "20.05.1985"
        assert record.birthday.date == date(1985, 5, 20)

    @pytest.mark.unit
    def test_add_birthday_invalid_format(self):
        """Test adding birthday with invalid format."""
        record = Record("John")

        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            record.add_birthday("1990-03-15")

    @pytest.mark.unit
    def test_str_representation_with_birthday(self):
        """Test string representation with birthday."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_birthday("15.03.1990")

        expected = "Contact name: John, phones: 1234567890, birthday: 15.03.1990"
        assert str(record) == expected

    @pytest.mark.unit
    def test_str_representation_without_birthday(self):
        """Test string representation without birthday."""
        record = Record("John")
        record.add_phone("1234567890")

        expected = "Contact name: John, phones: 1234567890"
        assert str(record) == expected

    @pytest.mark.unit
    def test_to_typed_dict_with_birthday(self):
        """Test to_typed_dict method with birthday."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_birthday("15.03.1990")

        typed_dict = record.to_typed_dict()

        assert typed_dict["name"] == "John"
        assert typed_dict["phones"] == ["1234567890"]
        assert typed_dict["birthday"] == "15.03.1990"

    @pytest.mark.unit
    def test_to_typed_dict_without_birthday(self):
        """Test to_typed_dict method without birthday."""
        record = Record("John")
        record.add_phone("1234567890")

        typed_dict = record.to_typed_dict()

        assert typed_dict["name"] == "John"
        assert typed_dict["phones"] == ["1234567890"]
        assert typed_dict["birthday"] is None


class TestAddressBookBirthdays:
    """Test cases for AddressBook birthday functionality."""

    @pytest.mark.unit
    def test_get_upcoming_birthdays_empty_book(self):
        """Test get_upcoming_birthdays with empty address book."""
        book = AddressBook()
        upcoming = book.get_upcoming_birthdays()
        assert upcoming == []

    @pytest.mark.unit
    def test_get_upcoming_birthdays_no_birthdays(self):
        """Test get_upcoming_birthdays with contacts but no birthdays."""
        book = AddressBook()

        john = Record("John")
        john.add_phone("1234567890")
        book.add_record(john)

        jane = Record("Jane")
        jane.add_phone("5555555555")
        book.add_record(jane)

        upcoming = book.get_upcoming_birthdays()
        assert upcoming == []

    @pytest.mark.unit
    def test_get_upcoming_birthdays_tomorrow(self):
        """Test get_upcoming_birthdays with birthday tomorrow."""
        book = AddressBook()

        john = Record("John")
        john.add_phone("1234567890")
        tomorrow = date.today() + timedelta(days=1)
        john.add_birthday(tomorrow.strftime("%d.%m.%Y"))
        book.add_record(john)

        upcoming = book.get_upcoming_birthdays()
        assert len(upcoming) == 1
        assert upcoming[0]["name"] == "John"

        # Якщо завтра вихідний, то дата привітання переноситься на понеділок
        expected_date = tomorrow
        if tomorrow.weekday() >= 5:  # Субота або неділя
            days_until_monday = 7 - tomorrow.weekday()
            expected_date = tomorrow + timedelta(days=days_until_monday)

        assert upcoming[0]["congratulation_date"] == expected_date.strftime("%Y.%m.%d")

    @pytest.mark.unit
    def test_get_upcoming_birthdays_today(self):
        """Test get_upcoming_birthdays with birthday today."""
        book = AddressBook()

        john = Record("John")
        john.add_phone("1234567890")
        today = date.today()
        john.add_birthday(today.strftime("%d.%m.%Y"))
        book.add_record(john)

        upcoming = book.get_upcoming_birthdays()
        assert len(upcoming) == 1
        assert upcoming[0]["name"] == "John"

        # Якщо сьогодні вихідний, то дата привітання переноситься на понеділок
        expected_date = today
        if today.weekday() >= 5:  # Субота або неділя
            days_until_monday = 7 - today.weekday()
            expected_date = today + timedelta(days=days_until_monday)

        assert upcoming[0]["congratulation_date"] == expected_date.strftime("%Y.%m.%d")

    @pytest.mark.unit
    def test_get_upcoming_birthdays_in_7_days(self):
        """Test get_upcoming_birthdays with birthday in exactly 7 days."""
        book = AddressBook()

        john = Record("John")
        john.add_phone("1234567890")
        in_7_days = date.today() + timedelta(days=7)
        john.add_birthday(in_7_days.strftime("%d.%m.%Y"))
        book.add_record(john)

        upcoming = book.get_upcoming_birthdays()
        assert len(upcoming) == 1
        assert upcoming[0]["name"] == "John"

        # Якщо день народження через 7 днів припадає на вихідний, переносимо на понеділок
        expected_date = in_7_days
        if in_7_days.weekday() >= 5:  # Субота або неділя
            days_until_monday = 7 - in_7_days.weekday()
            expected_date = in_7_days + timedelta(days=days_until_monday)

        assert upcoming[0]["congratulation_date"] == expected_date.strftime("%Y.%m.%d")

    @pytest.mark.unit
    def test_get_upcoming_birthdays_in_8_days(self):
        """Test get_upcoming_birthdays with birthday in 8 days (should not appear)."""
        book = AddressBook()

        john = Record("John")
        john.add_phone("1234567890")
        in_8_days = date.today() + timedelta(days=8)
        john.add_birthday(in_8_days.strftime("%d.%m.%Y"))
        book.add_record(john)

        upcoming = book.get_upcoming_birthdays()
        assert upcoming == []

    @pytest.mark.unit
    def test_get_upcoming_birthdays_weekend_saturday(self):
        """Test get_upcoming_birthdays with birthday on Saturday (moves to Monday)."""
        book = AddressBook()

        john = Record("John")
        john.add_phone("1234567890")

        # Find next Saturday
        today = date.today()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:  # Today is Saturday
            days_until_saturday = 7

        # Make sure it's within 7 days
        if days_until_saturday <= 7:
            saturday = today + timedelta(days=days_until_saturday)
            monday = saturday + timedelta(days=2)  # Monday after Saturday

            john.add_birthday(saturday.strftime("%d.%m.%Y"))
            book.add_record(john)

            upcoming = book.get_upcoming_birthdays()
            assert len(upcoming) == 1
            assert upcoming[0]["name"] == "John"
            assert upcoming[0]["congratulation_date"] == monday.strftime("%Y.%m.%d")

    @pytest.mark.unit
    def test_get_upcoming_birthdays_weekend_sunday(self):
        """Test get_upcoming_birthdays with birthday on Sunday (moves to Monday)."""
        book = AddressBook()

        john = Record("John")
        john.add_phone("1234567890")

        # Find next Sunday
        today = date.today()
        days_until_sunday = (6 - today.weekday()) % 7
        if days_until_sunday == 0:  # Today is Sunday
            days_until_sunday = 7

        # Make sure it's within 7 days
        if days_until_sunday <= 7:
            sunday = today + timedelta(days=days_until_sunday)
            monday = sunday + timedelta(days=1)  # Monday after Sunday

            john.add_birthday(sunday.strftime("%d.%m.%Y"))
            book.add_record(john)

            upcoming = book.get_upcoming_birthdays()
            assert len(upcoming) == 1
            assert upcoming[0]["name"] == "John"
            assert upcoming[0]["congratulation_date"] == monday.strftime("%Y.%m.%d")

    @pytest.mark.unit
    def test_get_upcoming_birthdays_multiple_contacts(self):
        """Test get_upcoming_birthdays with multiple contacts."""
        book = AddressBook()

        # John's birthday tomorrow
        john = Record("John")
        john.add_phone("1234567890")
        tomorrow = date.today() + timedelta(days=1)
        john.add_birthday(tomorrow.strftime("%d.%m.%Y"))
        book.add_record(john)

        # Jane's birthday in 3 days
        jane = Record("Jane")
        jane.add_phone("5555555555")
        in_3_days = date.today() + timedelta(days=3)
        jane.add_birthday(in_3_days.strftime("%d.%m.%Y"))
        book.add_record(jane)

        # Bob's birthday in 10 days (should not appear)
        bob = Record("Bob")
        bob.add_phone("9999999999")
        in_10_days = date.today() + timedelta(days=10)
        bob.add_birthday(in_10_days.strftime("%d.%m.%Y"))
        book.add_record(bob)

        upcoming = book.get_upcoming_birthdays()
        assert len(upcoming) == 2

        names = [contact["name"] for contact in upcoming]
        assert "John" in names
        assert "Jane" in names
        assert "Bob" not in names

    @pytest.mark.unit
    def test_get_upcoming_birthdays_past_birthday_this_year(self):
        """Test get_upcoming_birthdays with birthday that already passed this year."""
        book = AddressBook()

        john = Record("John")
        john.add_phone("1234567890")

        # Set birthday to January 1st (likely in the past for current date July 13, 2025)
        john.add_birthday("01.01.1990")
        book.add_record(john)

        upcoming = book.get_upcoming_birthdays()
        # Should be empty since January 1st 2025 has passed and January 1st 2026 is too far
        assert upcoming == []

    @pytest.mark.unit
    def test_get_upcoming_birthdays_next_year(self):
        """Test get_upcoming_birthdays considers next year for past birthdays."""
        book = AddressBook()

        john = Record("John")
        john.add_phone("1234567890")

        # Set birthday to a date that would be in next year's range
        # For example, if today is July 13, 2025, then July 15, 2026 should be checked
        birthday_next_week = date.today() + timedelta(days=3)
        birthday_str = (
            f"{birthday_next_week.day:02d}.{birthday_next_week.month:02d}.1990"
        )
        john.add_birthday(birthday_str)
        book.add_record(john)

        upcoming = book.get_upcoming_birthdays()
        assert len(upcoming) == 1
        assert upcoming[0]["name"] == "John"
