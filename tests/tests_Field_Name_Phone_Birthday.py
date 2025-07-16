import pytest

from cli_assistant.base_field_classes import Field, Name, Phone, Birthday
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