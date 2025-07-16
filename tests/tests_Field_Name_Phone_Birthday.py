import pytest

from cli_assistant.base_field_classes import Field, Name, Phone, Birthday
from cli_assistant.class_birthday_managment import BirthdayManagementMixin
from cli_assistant.class_record_main import Record
# Checkiing that field take string and return it as string
def test_field_accepts_string():
    f = Field("test")
    assert f.value == "test"
    assert str(f) == "test"
# Checking that field raises TypeError for non-string input
def test_field_rejects_non_string():
    with pytest.raises(TypeError):
        Field(123)
# Checking that Name field accepts valid names
def test_name_valid():
    n = Name("John Doe")
    assert n.value == "John Doe"
# Checking that name is stripped of leading and trailing spaces
def test_name_strip_and_length():
    n = Name("  Anna-Marie O'Neil  ")
    assert n.value == "Anna-Marie O'Neil"
# Checking that Name field raises ValueError for empty names
def test_name_empty():
    with pytest.raises(ValueError):
        Name("   ")
# Checking that Name field raises ValueError for names that are too long
def test_name_too_long():
    with pytest.raises(ValueError):
        Name("A" * 101)
# Checking that Name field raises ValueError for names with invalid characters
def test_name_invalid_chars():
    with pytest.raises(ValueError):
        Name("John123")
# Checking that name accepts boundary lengths
def test_name_boundary_length():
    Name("A")  # min length
    Name("A" * 100)  # max length
# Checking that phone validates correctly
def test_phone_valid():
    p = Phone("123-456-7890")
    assert p.value == "1234567890"
# Checking that phone raises ValueError for invalid formats
def test_phone_invalid_length():
    with pytest.raises(ValueError):
        Phone("123456789")  # 9 digits
#checking that valid birthday will be added
def test_add_birthday_valid():
    obj = BirthdayManagementMixin()
    obj.add_birthday("01.01.2000")
    assert obj.birthday.value == "2000-01-01"
# Checking that if added birthday with wrong format raises ValueError for invalid formats
def test_add_birthday_invalid_format():
    obj = BirthdayManagementMixin()
    with pytest.raises(ValueError):
        obj.add_birthday("2000-01-01")  # Wrong format
# Testing if we can remove birthday
def test_remove_birthday():
    obj = BirthdayManagementMixin()
    obj.add_birthday("01.01.2000")
    obj.remove_birthday()
    assert obj.birthday is None
# Testing if days to birthday returns None when no birthday is set
def test_days_to_birthday_none():
    obj = BirthdayManagementMixin()
    assert obj.days_to_birthday() is None
# Testing day to birthday shows correct number of days
def test_days_to_birthday_valid():
    obj = BirthdayManagementMixin()
    obj.add_birthday("01.01.2000")
    days = obj.days_to_birthday()
    assert isinstance(days, int)
    assert days >= 0
# Testing if working days to birthday on leap year
def test_days_to_birthday_leap_year():
    obj = BirthdayManagementMixin()
    obj.add_birthday("29.02.2000")
    days = obj.days_to_birthday()
    assert isinstance(days, int)
# Testing if days to birthday returns correct value when birthday is today
def test_days_to_birthday_today():
    obj = BirthdayManagementMixin()
    obj.add_birthday("01.01.2000")
    # Should always return days until next birthday, even if birthday this year has passed
    days = obj.days_to_birthday()
    assert days >= 0
    
# Record creation with valid name
def test_record_init_valid_name():
    r = Record("John Doe")
    assert r.name.value == "John Doe"
    assert r.phones == []
    assert r.birthday is None
    assert r.email is None

# Record creation with empty name should fail
def test_record_init_empty_name():
    with pytest.raises(ValueError):
        Record("   ")

# Add valid phone to record
def test_add_phone_valid():
    r = Record("John Doe")
    r.add_phone("123-456-7890")
    assert r.phones[0].value == "1234567890"

# Adding duplicate phone should fail
def test_add_phone_duplicate():
    r = Record("John Doe")
    r.add_phone("123-456-7890")
    with pytest.raises(ValueError):
        r.add_phone("1234567890")  # Same normalized

# Remove existing phone from record
def test_remove_phone_exists():
    r = Record("John Doe")
    r.add_phone("123-456-7890")
    r.remove_phone("1234567890")
    assert r.phones == []

# Removing non-existent phone should fail
def test_remove_phone_not_exists():
    r = Record("John Doe")
    r.add_phone("123-456-7890")
    with pytest.raises(ValueError):
        r.remove_phone("0987654321")

# Edit existing phone to new valid phone
def test_edit_phone_valid():
    r = Record("John Doe")
    r.add_phone("123-456-7890")
    r.edit_phone("1234567890", "0987654321")
    assert r.phones[0].value == "0987654321"

# Editing non-existent phone should fail
def test_edit_phone_old_not_found():
    r = Record("John Doe")
    r.add_phone("123-456-7890")
    with pytest.raises(ValueError):
        r.edit_phone("1112223333", "0987654321")

# Editing phone to duplicate should fail
def test_edit_phone_new_duplicate():
    r = Record("John Doe")
    r.add_phone("123-456-7890")
    r.add_phone("0987654321")
    with pytest.raises(ValueError):
        r.edit_phone("1234567890", "0987654321")

# Find existing phone in record
def test_find_phone_exists():
    r = Record("John Doe")
    r.add_phone("123-456-7890")
    found = r.find_phone("1234567890")
    assert found is not None
    assert found.value == "1234567890"

# Finding non-existent phone should return None
def test_find_phone_not_exists():
    r = Record("John Doe")
    r.add_phone("123-456-7890")
    found = r.find_phone("0987654321")
    assert found is None