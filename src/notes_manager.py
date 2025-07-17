from collections import UserDict
from typing import List, Optional, Dict, Any, Set
from datetime import datetime, timedelta, date
from address_book.models import Note
import uuid
import json
import csv
import io

class NotesManager(UserDict):
    def __init__(self):
        super().__init__()
        self.tag_index: Dict[str, Set[str]] = {}
        self.date_index: List[tuple] = []
        self._cache = {}

    def add_note(self, title: str, content: str = "", tags: List[str] = None) -> str:
        note = Note(title, content, tags)
        self.data[note.id] = note
        self._update_indices(note)
        self._clear_cache()
        return note.id

    def find_note(self, note_id: str) -> Optional[Note]:
        return self.data.get(note_id)

    def update_note(self, note_id: str, title: str = None, content: str = None, tags: List[str] = None) -> bool:
        note = self.find_note(note_id)
        if not note:
            return False
        if title is not None:
            note.update_title(title)
        if content is not None:
            note.update_content(content)
        if tags is not None:
            note.tags = note._process_tags(tags)
        self._update_indices(note)
        self._clear_cache()
        return True

    def delete_note(self, note_id: str) -> bool:
        note = self.data.pop(note_id, None)
        if note:
            self._remove_from_indices(note)
            self._clear_cache()
            return True
        return False

    def get_all_notes(self) -> List[Note]:
        return sorted(self.data.values(), key=lambda n: n.created_at, reverse=True)

    def search_notes(self, query: str, search_fields: List[str] = ["title", "content", "tags"]) -> List[Note]:
        results = []
        for note in self.data.values():
            score = 0
            if "title" in search_fields and query.lower() in note.title.lower():
                score += 2
            if "content" in search_fields and query.lower() in note.content.lower():
                score += 1
            if "tags" in search_fields and any(query.lower() in tag for tag in note.tags):
                score += 1.5
            if score > 0:
                results.append((score, note))
        results.sort(reverse=True, key=lambda x: x[0])
        return [n for _, n in results]

    def search_by_tags(self, tags: List[str], match_all: bool = False) -> List[Note]:
        tags = [t.lower() for t in tags]
        notes = []
        for note in self.data.values():
            note_tags = set(note.tags)
            if match_all and all(t in note_tags for t in tags):
                notes.append(note)
            elif not match_all and any(t in note_tags for t in tags):
                notes.append(note)
        notes.sort(key=lambda n: len(set(n.tags) & set(tags)), reverse=True)
        return notes

    def search_by_date_range(self, start_date: date, end_date: date) -> List[Note]:
        notes = []
        for note in self.data.values():
            created = datetime.strptime(note.created_at, "%Y-%m-%d %H:%M:%S.%f").date()
            if start_date <= created <= end_date:
                notes.append(note)
        notes.sort(key=lambda n: n.created_at)
        return notes

    def get_recent_notes(self, days: int = 7) -> List[Note]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        notes = []
        for note in self.data.values():
            updated = note.updated_at or note.created_at
            dt = datetime.strptime(updated, "%Y-%m-%d %H:%M:%S.%f")
            if dt >= cutoff:
                notes.append(note)
        notes.sort(key=lambda n: n.updated_at or n.created_at, reverse=True)
        return notes

    def get_all_tags(self) -> List[str]:
        tags = set()
        for note in self.data.values():
            tags.update(note.tags)
        return sorted(tags)

    def get_tag_statistics(self) -> Dict[str, int]:
        stats = {}
        for note in self.data.values():
            for tag in note.tags:
                stats[tag] = stats.get(tag, 0) + 1
        return stats

    def rename_tag(self, old_tag: str, new_tag: str) -> int:
        count = 0
        for note in self.data.values():
            if note.has_tag(old_tag):
                note.remove_tag(old_tag)
                note.add_tag(new_tag)
                count += 1
        self._clear_cache()
        return count

    def delete_tag(self, tag: str) -> int:
        count = 0
        for note in self.data.values():
            if note.has_tag(tag):
                note.remove_tag(tag)
                count += 1
        self._clear_cache()
        return count

    def sort_notes(self, sort_by: str = "created", reverse: bool = True) -> List[Note]:
        key_map = {
            "created": lambda n: n.created_at,
            "updated": lambda n: n.updated_at or n.created_at,
            "title": lambda n: n.title.lower(),
            "tag_count": lambda n: len(n.tags)
        }
        key_func = key_map.get(sort_by, key_map["created"])
        return sorted(self.data.values(), key=key_func, reverse=reverse)

    def filter_notes(self, filters: Dict[str, Any]) -> List[Note]:
        notes = list(self.data.values())
        if "has_tags" in filters:
            tags = set(t.lower() for t in filters["has_tags"])
            notes = [n for n in notes if tags.issubset(set(n.tags))]
        if "created_after" in filters:
            after = filters["created_after"]
            notes = [n for n in notes if datetime.strptime(n.created_at, "%Y-%m-%d %H:%M:%S.%f").date() > after]
        if "created_before" in filters:
            before = filters["created_before"]
            notes = [n for n in notes if datetime.strptime(n.created_at, "%Y-%m-%d %H:%M:%S.%f").date() < before]
        if "content_min_length" in filters:
            min_len = filters["content_min_length"]
            notes = [n for n in notes if len(n.content) >= min_len]
        if "title_contains" in filters:
            substr = filters["title_contains"].lower()
            notes = [n for n in notes if substr in n.title.lower()]
        return notes

    def export_notes(self, format: str = "json") -> str:
        notes = [note.to_typed_dict() for note in self.data.values()]
        if format == "json":
            return json.dumps(notes, ensure_ascii=False, indent=2)
        elif format == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["id", "title", "content", "tags", "created_at", "updated_at"])
            writer.writeheader()
            for note in notes:
                note["tags"] = ",".join(note["tags"])
                writer.writerow(note)
            return output.getvalue()
        elif format == "markdown":
            md = ""
            for note in self.data.values():
                md += f"## {note.title}\n\n{note.content}\n\n**Tags:** {', '.join(note.tags)}\n\n---\n"
            return md
        else:
            raise ValueError("Unsupported export format")

    def import_notes(self, data: str, format: str = "json") -> int:
        count = 0
        if format == "json":
            notes = json.loads(data)
            for note_dict in notes:
                note = Note.from_typed_dict(note_dict)
                if note.id not in self.data:
                    self.data[note.id] = note
                    self._update_indices(note)
                    count += 1
        elif format == "csv":
            reader = csv.DictReader(io.StringIO(data))
            for row in reader:
                row["tags"] = row["tags"].split(",") if row["tags"] else []
                note = Note.from_typed_dict(row)
                if note.id not in self.data:
                    self.data[note.id] = note
                    self._update_indices(note)
                    count += 1
        else:
            raise ValueError("Unsupported import format")
        self._clear_cache()
        return count

    def get_statistics(self) -> Dict[str, Any]:
        total_notes = len(self.data)
        tag_stats = self.get_tag_statistics()
        total_tags = len(tag_stats)
        notes_per_tag = total_notes / total_tags if total_tags else 0
        most_used = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        notes_this_week = sum(1 for n in self.data.values() if datetime.strptime(n.created_at, "%Y-%m-%d %H:%M:%S.%f") > week_ago)
        notes_this_month = sum(1 for n in self.data.values() if datetime.strptime(n.created_at, "%Y-%m-%d %H:%M:%S.%f") > month_ago)
        content_lengths = [len(n.content) for n in self.data.values()]
        return {
            "total_notes": total_notes,
            "total_tags": total_tags,
            "avg_notes_per_tag": notes_per_tag,
            "most_used_tags": most_used,
            "notes_this_week": notes_this_week,
            "notes_this_month": notes_this_month,
            "content_length_avg": sum(content_lengths) / total_notes if total_notes else 0,
            "content_length_max": max(content_lengths) if content_lengths else 0,
            "content_length_min": min(content_lengths) if content_lengths else 0,
        }

    def get_activity_summary(self, days: int = 30) -> Dict[str, int]:
        summary = {}
        now = datetime.utcnow()
        for i in range(days):
            day = (now - timedelta(days=i)).date()
            created = sum(1 for n in self.data.values() if datetime.strptime(n.created_at, "%Y-%m-%d %H:%M:%S.%f").date() == day)
            updated = sum(1 for n in self.data.values() if n.updated_at and datetime.strptime(n.updated_at, "%Y-%m-%d %H:%M:%S.%f").date() == day)
            summary[str(day)] = {"created": created, "updated": updated}
        return summary

    # --- Indexing and Caching ---
    def _update_indices(self, note: Note):
        # Update tag index
        for tag in note.tags:
            self.tag_index.setdefault(tag, set()).add(note.id)
        # Update date index
        self.date_index.append((note.created_at, note.id))

    def _remove_from_indices(self, note: Note):
        for tag in note.tags:
            if tag in self.tag_index and note.id in self.tag_index[tag]:
                self.tag_index[tag].remove(note.id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
        self.date_index = [t for t in self.date_index if t[1] != note.id]

    def _clear_cache(self):
        self._cache.clear()