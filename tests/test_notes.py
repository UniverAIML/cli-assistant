#!/usr/bin/env python3
"""
Test Suite for Notes Management System

Comprehensive tests covering all notes functionality including:
- Note creation and validation
- Note content management
- Tags management
- Notes manager operations
- Search functionality
"""

import pytest
from datetime import datetime
from typing import Dict
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cli_assistant.database.note_models import Note, NotesManager, NoteData


class TestNote:
    """Test cases for Note class."""

    @pytest.mark.unit
    def test_note_creation_basic(self):
        """Test basic note creation."""
        note = Note("Test Title", "Test content", ["tag1", "tag2"])
        assert note.title == "Test Title"
        assert note.content == "Test content"
        assert note.tags == ["tag1", "tag2"]
        assert note.created_at is not None
        assert note.updated_at is None

    @pytest.mark.unit
    def test_note_creation_minimal(self):
        """Test note creation with minimal parameters."""
        note = Note("Title Only")
        assert note.title == "Title Only"
        assert note.content == ""
        assert note.tags == []
        assert note.created_at is not None

    @pytest.mark.unit
    def test_note_creation_empty_title_error(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Note title cannot be empty"):
            Note("")

        with pytest.raises(ValueError, match="Note title cannot be empty"):
            Note("   ")

    @pytest.mark.unit
    def test_note_update_content(self):
        """Test updating note content."""
        note = Note("Test", "Original content")
        original_created = note.created_at

        note.update_content("Updated content")

        assert note.content == "Updated content"
        assert note.updated_at is not None
        assert note.created_at == original_created

    @pytest.mark.unit
    def test_note_update_title(self):
        """Test updating note title."""
        note = Note("Original Title", "Content")

        note.update_title("New Title")

        assert note.title == "New Title"
        assert note.updated_at is not None

    @pytest.mark.unit
    def test_note_update_title_empty_error(self):
        """Test that empty title update raises ValueError."""
        note = Note("Original", "Content")

        with pytest.raises(ValueError, match="Note title cannot be empty"):
            note.update_title("")

    @pytest.mark.unit
    def test_note_add_tag(self):
        """Test adding tags to note."""
        note = Note("Test", "Content")

        note.add_tag("new_tag")
        assert "new_tag" in note.tags
        assert note.updated_at is not None

        # Test adding duplicate tag (case insensitive)
        note.add_tag("NEW_TAG")
        assert note.tags.count("new_tag") == 1  # Should not add duplicate

    @pytest.mark.unit
    def test_note_remove_tag(self):
        """Test removing tags from note."""
        note = Note("Test", "Content", ["tag1", "tag2", "tag3"])

        note.remove_tag("tag2")
        assert "tag2" not in note.tags
        assert len(note.tags) == 2
        assert note.updated_at is not None

    @pytest.mark.unit
    def test_note_has_tag(self):
        """Test checking if note has specific tag."""
        note = Note("Test", "Content", ["Python", "Programming"])

        assert note.has_tag("python")  # Case insensitive
        assert note.has_tag("Programming")
        assert not note.has_tag("JavaScript")

    @pytest.mark.unit
    def test_note_search_in_content(self):
        """Test searching within note content."""
        note = Note(
            "Python Tutorial",
            "This is a guide for Python programming",
            ["python", "tutorial"],
        )

        assert note.search_in_content("python")  # In title and tags
        assert note.search_in_content("guide")  # In content
        assert note.search_in_content("tutorial")  # In tags
        assert not note.search_in_content("javascript")

    @pytest.mark.unit
    def test_note_to_typed_dict(self):
        """Test converting note to TypedDict."""
        note = Note("Test", "Content", ["tag1"])
        note.update_content("Updated")  # To set updated_at

        data = note.to_typed_dict()

        assert isinstance(data, dict)
        assert data["title"] == "Test"
        assert data["content"] == "Updated"
        assert data["tags"] == ["tag1"]
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.unit
    def test_note_from_typed_dict(self):
        """Test creating note from TypedDict."""
        data: NoteData = {
            "title": "Test Note",
            "content": "Test content",
            "tags": ["test", "sample"],
            "created_at": "2024-01-01 12:00:00",
            "updated_at": "2024-01-02 13:00:00",
        }

        note = Note.from_typed_dict(data)

        assert note.title == "Test Note"
        assert note.content == "Test content"
        assert note.tags == ["test", "sample"]
        assert note.created_at == "2024-01-01 12:00:00"
        assert note.updated_at == "2024-01-02 13:00:00"


class TestNotesManager:
    """Test cases for NotesManager class."""

    @pytest.mark.unit
    def test_notes_manager_creation(self):
        """Test creating empty notes manager."""
        manager = NotesManager()
        assert len(manager.data) == 0
        assert manager._next_id == 1

    @pytest.mark.unit
    def test_add_note(self):
        """Test adding note to manager."""
        manager = NotesManager()
        note = Note("Test Note", "Content")

        note_id = manager.add_note(note)

        assert note_id.startswith("note_")
        assert note_id in manager.data
        assert manager.data[note_id] == note

    @pytest.mark.unit
    def test_create_note(self):
        """Test creating note through manager."""
        manager = NotesManager()

        note_id = manager.create_note("Test Title", "Test content", ["tag1", "tag2"])

        assert note_id in manager.data
        note = manager.data[note_id]
        assert note.title == "Test Title"
        assert note.content == "Test content"
        assert note.tags == ["tag1", "tag2"]

    @pytest.mark.unit
    def test_find_note(self):
        """Test finding note by ID."""
        manager = NotesManager()
        note_id = manager.create_note("Test", "Content")

        found_note = manager.find_note(note_id)
        assert found_note is not None
        assert found_note.title == "Test"

        # Test finding non-existent note
        assert manager.find_note("nonexistent") is None

    @pytest.mark.unit
    def test_delete_note(self):
        """Test deleting note."""
        manager = NotesManager()
        note_id = manager.create_note("Test", "Content")

        assert manager.delete_note(note_id) is True
        assert note_id not in manager.data

        # Test deleting non-existent note
        assert manager.delete_note("nonexistent") is False

    @pytest.mark.unit
    def test_search_notes(self):
        """Test searching notes."""
        manager = NotesManager()
        id1 = manager.create_note(
            "Python Tutorial", "Learn Python programming", ["python", "programming"]
        )
        id2 = manager.create_note(
            "JavaScript Guide", "Web development with JS", ["javascript", "web"]
        )
        id3 = manager.create_note(
            "Programming Tips", "General programming advice", ["programming", "tips"]
        )

        # Search by title
        results = manager.search_notes("python")
        assert len(results) == 1  # Only "Python Tutorial" contains "python"
        assert id1 in results

        # Search by content
        results = manager.search_notes("web")
        assert len(results) == 1
        assert id2 in results

        # Search by tag
        results = manager.search_notes("javascript")
        assert len(results) == 1
        assert id2 in results

    @pytest.mark.unit
    def test_get_notes_by_tag(self):
        """Test getting notes by specific tag."""
        manager = NotesManager()
        id1 = manager.create_note("Note 1", "Content", ["python", "tutorial"])
        id2 = manager.create_note("Note 2", "Content", ["javascript", "tutorial"])
        id3 = manager.create_note("Note 3", "Content", ["python", "advanced"])

        # Get notes with "python" tag
        python_notes = manager.get_notes_by_tag("python")
        assert len(python_notes) == 2
        assert id1 in python_notes
        assert id3 in python_notes

        # Get notes with "tutorial" tag
        tutorial_notes = manager.get_notes_by_tag("tutorial")
        assert len(tutorial_notes) == 2
        assert id1 in tutorial_notes
        assert id2 in tutorial_notes

    @pytest.mark.unit
    def test_get_all_tags(self):
        """Test getting all unique tags."""
        manager = NotesManager()
        manager.create_note("Note 1", "Content", ["Python", "Tutorial"])
        manager.create_note(
            "Note 2", "Content", ["javascript", "TUTORIAL"]
        )  # Case variation
        manager.create_note("Note 3", "Content", ["Python", "Advanced"])

        all_tags = manager.get_all_tags()

        # Should be lowercase and unique
        expected_tags = ["advanced", "javascript", "python", "tutorial"]
        assert sorted(all_tags) == expected_tags

    @pytest.mark.unit
    def test_get_recent_notes(self):
        """Test getting recent notes."""
        import time

        manager = NotesManager()

        # Create notes with some updates
        id1 = manager.create_note("Old Note", "Content")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        id2 = manager.create_note("New Note", "Content")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        id3 = manager.create_note("Updated Note", "Content")

        # Update one note to change its timestamp
        time.sleep(0.01)  # Small delay to ensure different timestamp
        note3 = manager.find_note(id3)
        assert note3 is not None
        note3.update_content("Updated content")

        recent = manager.get_recent_notes(2)
        assert len(recent) == 2

        # The updated note should be first (most recent)
        recent_ids = list(recent.keys())
        assert id3 in recent_ids  # Updated note should be included

    @pytest.mark.unit
    def test_to_typed_dict(self):
        """Test converting manager to typed dict."""
        manager = NotesManager()
        id1 = manager.create_note("Note 1", "Content 1", ["tag1"])
        id2 = manager.create_note("Note 2", "Content 2", ["tag2"])

        data = manager.to_typed_dict()

        assert isinstance(data, dict)
        assert len(data) == 2
        assert id1 in data
        assert id2 in data
        assert data[id1]["title"] == "Note 1"
        assert data[id2]["title"] == "Note 2"

    @pytest.mark.unit
    def test_from_typed_dict(self):
        """Test loading manager from typed dict."""
        manager = NotesManager()

        # Create test data
        test_data: Dict[str, NoteData] = {
            "note_0001": {
                "title": "Test Note 1",
                "content": "Content 1",
                "tags": ["tag1"],
                "created_at": "2024-01-01 12:00:00",
                "updated_at": None,
            },
            "note_0002": {
                "title": "Test Note 2",
                "content": "Content 2",
                "tags": ["tag2"],
                "created_at": "2024-01-02 12:00:00",
                "updated_at": "2024-01-02 13:00:00",
            },
        }

        manager.from_typed_dict(test_data)

        assert len(manager.data) == 2
        assert "note_0001" in manager.data
        assert "note_0002" in manager.data
        assert manager.data["note_0001"].title == "Test Note 1"
        assert manager.data["note_0002"].title == "Test Note 2"
        assert manager._next_id == 3  # Should be set to max + 1


class TestNotesIntegration:
    """Integration tests for notes system."""

    @pytest.mark.integration
    def test_complete_workflow(self):
        """Test complete notes workflow."""
        manager = NotesManager()

        # Create notes
        id1 = manager.create_note(
            "Python Basics", "Introduction to Python", ["python", "basics"]
        )
        id2 = manager.create_note(
            "Advanced Python", "Advanced concepts", ["python", "advanced"]
        )

        # Search and verify
        python_notes = manager.search_notes("python")
        assert len(python_notes) == 2

        # Update a note
        note1 = manager.find_note(id1)
        assert note1 is not None
        note1.update_content("Updated introduction to Python programming")
        note1.add_tag("programming")

        # Search by new tag
        programming_notes = manager.get_notes_by_tag("programming")
        assert len(programming_notes) == 1
        assert id1 in programming_notes

        # Get all tags
        all_tags = manager.get_all_tags()
        assert "programming" in all_tags
        assert len(all_tags) >= 3  # basics, python, advanced, programming

        # Delete a note
        assert manager.delete_note(id2) is True
        assert len(manager.data) == 1

        # Verify search after deletion
        python_notes = manager.search_notes("python")
        assert len(python_notes) == 1
        assert id1 in python_notes


if __name__ == "__main__":
    pytest.main([__file__])
