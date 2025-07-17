from datetime import date, timedelta

import pytest

from address_book.class_addressBook import AddressBook, normalize_name
from address_book.class_record_main import Record


# Test: Create a record with phones and find by name (case-insensitive)
def make_record(name, phones=None, birthday=None):
    r = Record(name)
    if phones:
        for p in phones:
            r.add_phone(p)
    if birthday:
        r.birthday = birthday
    return r


# Test: Add record and find by normalized name
def test_add_record_and_find():
    ab = AddressBook()
    rec = make_record("Alice", ["1234567890"])
    ab.add_record(rec)
    assert ab.find("alice") == rec
    assert ab.find("ALICE") == rec


# Test: Prevent adding duplicate records (case-insensitive)
def test_add_duplicate_record():
    ab = AddressBook()
    rec = make_record("Bob")
    ab.add_record(rec)
    with pytest.raises(ValueError):
        ab.add_record(make_record("bob"))


# Test: Delete record and check removal
def test_delete_record():
    ab = AddressBook()
    rec = make_record("Charlie")
    ab.add_record(rec)
    assert ab.delete("charlie") is True
    assert ab.find("charlie") is None
    assert ab.delete("charlie") is False


# Test: Get all records sorted by name
def test_get_all_records_sorted():
    ab = AddressBook()
    ab.add_record(make_record("Zed"))
    ab.add_record(make_record("Ann"))
    ab.add_record(make_record("Mike"))
    names = [r.name.value for r in ab.get_all_records()]
    assert names == ["Ann", "Mike", "Zed"]


# Test: Search records by name substring
def test_search_by_name():
    ab = AddressBook()
    ab.add_record(make_record("Anna"))
    ab.add_record(make_record("Annette"))
    ab.add_record(make_record("Bob"))
    results = ab.search_by_name("ann")
    assert len(results) == 2
    assert all("ann" in r.name.value.lower() for r in results)


# Test: Search record by phone number
def test_search_by_phone():
    ab = AddressBook()
    ab.add_record(make_record("Tom", ["1234567890"]))
    ab.add_record(make_record("Jerry", ["2222222222"]))
    result = ab.search_by_phone("1234567890")
    assert result is not None
    assert result.name.value == "Tom"
    assert ab.search_by_phone("3333333333") is None


# Test: Search contacts by name or phone substring
def test_search_contacts():
    ab = AddressBook()
    ab.add_record(make_record("Sam", ["5555555555"]))
    ab.add_record(make_record("Samuel", ["6666666666"]))
    ab.add_record(make_record("Pam", ["5555555555"]))
    results = ab.search_contacts("sam")
    assert any(r.name.value == "Sam" for r in results)
    assert any(r.name.value == "Samuel" for r in results)
    results_phone = ab.search_contacts("5555555555")
    # Accept if at least one record with the phone is found
    assert any(r.name.value in ["Sam", "Pam"] for r in results_phone)


# Test: Get upcoming birthdays within a period
def test_get_upcoming_birthdays(monkeypatch):
    ab = AddressBook()
    today = date.today()
    # Birthday today
    rec1 = make_record(
        "Today",
        birthday=type(
            "B", (), {"date": today, "days_to_next_birthday": lambda self: 0}
        )(),
    )
    # Birthday in 3 days
    rec2 = make_record(
        "Soon",
        birthday=type(
            "B",
            (),
            {
                "date": today + timedelta(days=3),
                "days_to_next_birthday": lambda self: 3,
            },
        )(),
    )
    ab.add_record(rec1)
    ab.add_record(rec2)
    upcoming = ab.get_upcoming_birthdays(days=7)
    names = [x["name"] for x in upcoming]
    assert "Today" in names and "Soon" in names


# Test: Get birthdays in a specific date period
def test_get_birthdays_in_period():
    ab = AddressBook()
    start = date(2025, 1, 1)
    end = date(2025, 1, 31)
    rec = make_record("Jan", birthday=type("B", (), {"date": date(2025, 1, 10)})())
    ab.add_record(rec)
    results = ab.get_birthdays_in_period(start, end)
    assert rec in results


# Test: Get statistics for contacts and phones
def test_stats_and_phone_stats():
    ab = AddressBook()
    ab.add_record(make_record("Anna", ["1111111111"]))
    ab.add_record(make_record("Bob", ["2222222222", "3333333333"]))
    ab.add_record(make_record("Carol"))
    stats = ab.get_stats()
    assert stats["total_contacts"] == 3
    assert stats["with_phones"] == 2
    assert stats["with_birthdays"] == 0
    phone_stats = ab.get_phone_stats()
    assert phone_stats["1111111111"] == 1
    assert phone_stats["2222222222"] == 1
    assert phone_stats["3333333333"] == 1


# Test: Export and import address book data
def test_to_dict_and_from_dict():
    ab = AddressBook()
    ab.add_record(make_record("Anna", ["1111111111"]))
    ab.add_record(make_record("Bob", ["2222222222"]))
    data = ab.to_dict()
    ab2 = AddressBook()
    ab2.from_dict(data)
    anna_record = ab2.find("Anna")
    assert anna_record is not None
    assert anna_record.name.value == "Anna"
    bob_record = ab2.find("Bob")
    assert bob_record is not None
    assert bob_record.phones[0].value == "2222222222"


# Test: Clear all records in address book
def test_clear():
    ab = AddressBook()
    ab.add_record(make_record("A"))
    ab.clear()
    assert len(ab.data) == 0
