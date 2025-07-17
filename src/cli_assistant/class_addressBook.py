from collections import UserDict
from typing import Dict, List, Optional, Any
from datetime import date, timedelta
from cli_assistant.class_record_main import Record

def normalize_name(name: str) -> str:
    return name.strip().lower()

class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        key = normalize_name(record.name.value)
        if key in self.data:
            raise ValueError("Contact with this name already exists")
        self.data[key] = record

    def find(self, name: str) -> Optional[Record]:
        key = normalize_name(name)
        return self.data.get(key)

    def delete(self, name: str) -> bool:
        key = normalize_name(name)
        if key in self.data:
            del self.data[key]
            return True
        return False

    def get_all_records(self) -> List[Record]:
        return sorted(self.data.values(), key=lambda r: r.name.value.lower())

    def search_by_name(self, query: str) -> List[Record]:
        query_norm = normalize_name(query)
        results = []
        for key, record in self.data.items():
            if query_norm in key:
                results.append(record)
        # Fuzzy search: sort by similarity (simple ratio)
        results.sort(key=lambda r: self._similarity(query_norm, normalize_name(r.name.value)), reverse=True)
        return results

    def _similarity(self, a: str, b: str) -> float:
        # Simple similarity: ratio of matching chars
        matches = sum(1 for x, y in zip(a, b) if x == y)
        return matches / max(len(a), len(b), 1)

    def search_by_phone(self, phone: str) -> Optional[Record]:
        normalized_phone = ''.join(filter(str.isdigit, phone))
        for record in self.data.values():
            for p in record.phones:
                if p.value == normalized_phone:
                    return record
        return None

    def search_contacts(self, query: str) -> List[Record]:
        name_results = set(self.search_by_name(query))
        phone_result = self.search_by_phone(query)
        results = list(name_results)
        if phone_result and phone_result not in results:
            results.append(phone_result)
        # Sort by relevance (name similarity first)
        results.sort(key=lambda r: self._similarity(normalize_name(query), normalize_name(r.name.value)), reverse=True)
        return results

    def get_upcoming_birthdays(self, days: int = 7) -> List[Dict[str, Any]]:
        today = date.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                days_until = record.birthday.days_to_next_birthday()
                next_bday = today + timedelta(days=days_until)
                if 0 <= days_until <= days:
                    # Move to Monday if birthday falls on weekend
                    weekday = next_bday.weekday()
                    if weekday >= 5:
                        next_bday += timedelta(days=(7 - weekday))
                    upcoming.append({
                        "name": record.name.value,
                        "birthday": str(next_bday),
                        "days_until": (next_bday - today).days
                    })
        upcoming.sort(key=lambda x: x["days_until"])
        return upcoming

    def get_birthdays_in_period(self, start_date: date, end_date: date) -> List[Record]:
        results = []
        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.date.replace(year=start_date.year)
                if start_date <= bday <= end_date:
                    results.append(record)
        results.sort(key=lambda r: r.birthday.date)
        return results

    def get_page(self, page_num: int, page_size: int = 10) -> List[Record]:
        all_records = self.get_all_records()
        start = (page_num - 1) * page_size
        end = start + page_size
        return all_records[start:end]

    def get_total_pages(self, page_size: int = 10) -> int:
        total = len(self.data)
        return (total + page_size - 1) // page_size

    def get_stats(self) -> Dict[str, int]:
        total = len(self.data)
        with_phones = sum(1 for r in self.data.values() if r.phones)
        with_birthdays = sum(1 for r in self.data.values() if r.birthday)
        return {
            "total_contacts": total,
            "with_phones": with_phones,
            "with_birthdays": with_birthdays
        }

    def get_phone_stats(self) -> Dict[str, int]:
        stats = {}
        for r in self.data.values():
            for p in r.phones:
                stats[p.value] = stats.get(p.value, 0) + 1
        return stats

    def to_dict(self) -> Dict[str, dict]:
        return {k: v.to_dict() for k, v in self.data.items()}

    def from_dict(self, data: Dict[str, dict]) -> None:
        self.clear()
        for k, v in data.items():
            record = Record.from_dict(v)
            self.add_record(record)

    def clear(self) -> None:
        self.data.clear()