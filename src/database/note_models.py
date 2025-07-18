"""
Notes management module for Personal Assistant.

This module provides functionality for managing notes with tags and timestamps.
"""

from collections import UserDict
from typing import List, Optional, Dict, TypedDict
from datetime import datetime
import re


class NoteData(TypedDict):
    """Typed representation of a note for static type checking and serialization."""

    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: Optional[str]


class Note:
    """Class for storing note information including title, content, tags and timestamps."""

    def __init__(self, title: str, content: str = "", tags: List[str] = None) -> None:
        if not title or not title.strip():
            raise ValueError("Note title cannot be empty")

        self.title = title.strip()
        self.content = content
        self.tags = tags or []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.updated_at: Optional[str] = None

    def update_content(self, content: str) -> None:
        """Update note content and set updated timestamp."""
        self.content = content
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def update_title(self, title: str) -> None:
        """Update note title and set updated timestamp."""
        if not title or not title.strip():
            raise ValueError("Note title cannot be empty")

        self.title = title.strip()
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def add_tag(self, tag: str) -> None:
        """Add a tag to the note."""
        tag = tag.strip().lower()
        if tag and tag not in [t.lower() for t in self.tags]:
            self.tags.append(tag)
            self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the note."""
        tag = tag.strip().lower()
        original_tags = self.tags[:]
        self.tags = [t for t in self.tags if t.lower() != tag]

        if len(self.tags) != len(original_tags):
            self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def has_tag(self, tag: str) -> bool:
        """Check if note has a specific tag."""
        tag = tag.strip().lower()
        return tag in [t.lower() for t in self.tags]

    def search_in_content(self, query: str) -> bool:
        """Search for query in note title, content, or tags."""
        query = query.lower()
        return (
            query in self.title.lower()
            or query in self.content.lower()
            or any(query in tag.lower() for tag in self.tags)
        )

    def __str__(self) -> str:
        tags_str = f", tags: {', '.join(self.tags)}" if self.tags else ""
        updated_str = f", updated: {self.updated_at}" if self.updated_at else ""
        return f"Note: {self.title}, created: {self.created_at}{updated_str}{tags_str}"

    def to_typed_dict(self) -> NoteData:
        """Return a TypedDict representation of the note."""
        return {
            "title": self.title,
            "content": self.content,
            "tags": self.tags[:],  # Create a copy
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_typed_dict(cls, data: NoteData) -> "Note":
        """Create a Note instance from TypedDict data."""
        note = cls.__new__(cls)  # Create instance without calling __init__
        note.title = data["title"]
        note.content = data["content"]
        note.tags = data["tags"][:]  # Create a copy
        note.created_at = data["created_at"]
        note.updated_at = data.get("updated_at")
        return note


class NotesManager(UserDict[str, Note]):
    """Class for storing and managing note records."""

    def __init__(self) -> None:
        super().__init__()
        self._next_id = 1

    def _generate_id(self) -> str:
        """Generate a unique ID for a note."""
        note_id = f"note_{self._next_id:04d}"
        self._next_id += 1
        # Ensure ID is unique
        while note_id in self.data:
            note_id = f"note_{self._next_id:04d}"
            self._next_id += 1
        return note_id

    def add_note(self, note: Note) -> str:
        """Add a note to the manager and return its ID."""
        note_id = self._generate_id()
        self.data[note_id] = note
        return note_id

    def create_note(self, title: str, content: str = "", tags: List[str] = None) -> str:
        """Create a new note and add it to the manager."""
        note = Note(title, content, tags)
        return self.add_note(note)

    def find_note(self, note_id: str) -> Optional[Note]:
        """Find a note by ID."""
        return self.data.get(note_id)

    def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID."""
        if note_id in self.data:
            del self.data[note_id]
            return True
        return False

    def search_notes(self, query: str) -> Dict[str, Note]:
        """Search for notes containing the query."""
        results = {}
        for note_id, note in self.data.items():
            if note.search_in_content(query):
                results[note_id] = note
        return results

    def get_notes_by_tag(self, tag: str) -> Dict[str, Note]:
        """Get all notes that have a specific tag."""
        results = {}
        for note_id, note in self.data.items():
            if note.has_tag(tag):
                results[note_id] = note
        return results

    def get_all_tags(self) -> List[str]:
        """Get all unique tags across all notes."""
        all_tags = set()
        for note in self.data.values():
            all_tags.update(tag.lower() for tag in note.tags)
        return sorted(list(all_tags))

    def get_recent_notes(self, limit: int = 10) -> Dict[str, Note]:
        """Get the most recently created or updated notes."""

        def get_latest_time(note: Note) -> str:
            return note.updated_at or note.created_at

        sorted_items = sorted(
            self.data.items(), key=lambda x: get_latest_time(x[1]), reverse=True
        )

        return dict(sorted_items[:limit])

    def to_typed_dict(self) -> Dict[str, NoteData]:
        """Return the entire notes manager as mapping id -> NoteData."""
        return {note_id: note.to_typed_dict() for note_id, note in self.data.items()}

    def from_typed_dict(self, data: Dict[str, NoteData]) -> None:
        """Load notes from typed dict data."""
        self.data.clear()
        max_id = 0

        for note_id, note_data in data.items():
            note = Note.from_typed_dict(note_data)
            self.data[note_id] = note

            # Extract numeric part of ID to maintain sequence
            if note_id.startswith("note_"):
                try:
                    id_num = int(note_id.split("_")[1])
                    max_id = max(max_id, id_num)
                except (IndexError, ValueError):
                    pass

        self._next_id = max_id + 1
