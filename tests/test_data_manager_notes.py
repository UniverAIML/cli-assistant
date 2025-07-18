#!/usr/bin/env python3
"""
DataManager notes tests - notes-specific functionality.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cli_assistant.database.data_manager import DataManager
from cli_assistant.database.note_models import NotesManager


class TestDataManagerNotes:
    """Test DataManager notes functionality."""

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
    def test_save_and_load_notes(self):
        """Test saving and loading notes."""
        # Create test data
        notes_manager = NotesManager()
        id1 = notes_manager.create_note(
            "Meeting Notes", "Discussed project timeline", ["work", "meeting"]
        )
        id2 = notes_manager.create_note(
            "Shopping List", "Milk, Bread, Eggs", ["shopping"]
        )

        # Test saving notes
        result = self.dm.save_notes(notes_manager)
        assert result is True
        assert self.dm.notes_file_exists()

        # Test loading notes
        loaded_manager = self.dm.load_notes()
        assert len(loaded_manager.data) == 2

        # Verify note details
        note1 = loaded_manager.find_note(id1)
        assert note1 is not None
        assert note1.title == "Meeting Notes"
        assert note1.content == "Discussed project timeline"
        assert "work" in note1.tags
        assert "meeting" in note1.tags

    @pytest.mark.unit
    def test_save_notes_with_tags(self):
        """Test saving notes with multiple tags."""
        notes_manager = NotesManager()
        note_id = notes_manager.create_note(
            "Tagged Note",
            "This note has many tags",
            ["tag1", "tag2", "tag3", "important"],
        )

        # Save and reload
        self.dm.save_notes(notes_manager)
        loaded_manager = self.dm.load_notes()

        loaded_note = loaded_manager.find_note(note_id)
        assert loaded_note is not None
        assert len(loaded_note.tags) == 4
        assert "tag1" in loaded_note.tags
        assert "important" in loaded_note.tags

    @pytest.mark.unit
    def test_save_notes_without_tags(self):
        """Test saving notes without tags."""
        notes_manager = NotesManager()
        note_id = notes_manager.create_note("Simple Note", "Just content, no tags")

        # Save and reload
        self.dm.save_notes(notes_manager)
        loaded_manager = self.dm.load_notes()

        loaded_note = loaded_manager.find_note(note_id)
        assert loaded_note is not None
        assert loaded_note.title == "Simple Note"
        assert loaded_note.content == "Just content, no tags"
        assert len(loaded_note.tags) == 0

    @pytest.mark.unit
    def test_save_notes_with_timestamps(self):
        """Test that timestamps are preserved during save/load."""
        notes_manager = NotesManager()
        note_id = notes_manager.create_note("Time Note", "Content")

        # Get original timestamps
        original_note = notes_manager.find_note(note_id)
        assert original_note is not None
        original_created = original_note.created_at

        # Update the note to set updated_at
        original_note.update_content("Updated content")
        original_updated = original_note.updated_at

        # Save and reload
        self.dm.save_notes(notes_manager)
        loaded_manager = self.dm.load_notes()

        loaded_note = loaded_manager.find_note(note_id)
        assert loaded_note is not None
        assert loaded_note.created_at == original_created
        assert loaded_note.updated_at == original_updated
        assert loaded_note.content == "Updated content"
