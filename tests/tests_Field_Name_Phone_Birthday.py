import pytest

from cli_assistant.base_field_classes import Field, Name, Phone, Birthday

def test_field_accepts_string():
    f = Field("test")
    assert f.value == "test"
    assert str(f) == "test"

def test_field_rejects_non_string():
    with pytest.raises(TypeError):
        Field(123)

def test_name_valid():
    n = Name("John Doe")
    assert n.value == "John Doe"

def test_name_strip_and_length():
    n = Name("  Anna-Marie O'Neil  ")
    assert n.value == "Anna-Marie O'Neil"

def test_name_empty():
    with pytest.raises(ValueError):
        Name("   ")

def test_name_too_long():
    with pytest.raises(ValueError):
        Name("A" * 101)

def test_name_invalid_chars():
    with pytest.raises(ValueError):
        Name("John123")

def test_name_boundary_length():
    Name("A")  # min length
    Name("A" * 100)  # max length

def test_phone_valid():
    p = Phone("123-456-7890")
    assert p.value == "1234567890"

def test_phone_invalid_length():
    with pytest.raises(ValueError):
        Phone("123456789")  # 9 digits