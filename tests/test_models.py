import unittest
from address_book.models import Note
from uuid import UUID
import re

class TestNote(unittest.TestCase):

    def test_valid_note_creation(self):
        note = Note("Test Title", "Sample content.", ["tag1", "tag-two"])
        self.assertEqual(note.title, "Test Title")
        self.assertEqual(note.content, "Sample content.")
        self.assertIn("tag1", note.tags)
        self.assertIsNotNone(note.created_at)
        self.assertTrue(UUID(note.id))

    def test_title_validation(self):
        with self.assertRaises(ValueError):
            Note("   ")
        with self.assertRaises(ValueError):
            Note("a" * 201)

    def test_content_validation(self):
        long_content = "a" * 10001
        with self.assertRaises(ValueError):
            Note("Title", long_content)
        with self.assertRaises(ValueError):
            Note("Title", "<script>alert('bad')</script>")

    def test_tag_validation(self):
        note = Note("Title", "", ["valid-tag", "VALID-TAG", "invalid tag", "bad*char"])
        self.assertIn("valid-tag", note.tags)
        self.assertNotIn("invalid tag", note.tags)
        self.assertNotIn("bad*char", note.tags)
        self.assertEqual(len(note.tags), 1)

    def test_update_content_and_title(self):
        note = Note("Title")
        note.update_content("New content")
        self.assertEqual(note.content, "New content")
        self.assertIsNotNone(note.updated_at)
        note.update_title("New Title")
        self.assertEqual(note.title, "New Title")

    def test_tag_addition_and_removal(self):
        note = Note("Title")
        self.assertTrue(note.add_tag("new-tag"))
        self.assertFalse(note.add_tag("new-tag"))
        self.assertTrue(note.remove_tag("new-tag"))
        self.assertFalse(note.remove_tag("nonexistent"))

    def test_has_tag(self):
        note = Note("Title", tags=["test"])
        self.assertTrue(note.has_tag("TEST"))
        self.assertFalse(note.has_tag("none"))

    def test_get_tags_sorted(self):
        note = Note("Title", tags=["z", "a", "m"])
        self.assertEqual(note.get_tags(), ["a", "m", "z"])

    def test_search_in_content(self):
        note = Note("Hello World", "This is content")
        self.assertTrue(note.search_in_content("hello"))
        self.assertTrue(note.search_in_content("content"))
        self.assertFalse(note.search_in_content("missing"))

    def test_matches_tags(self):
        note = Note("Title", tags=["science", "tech"])
        self.assertTrue(note.matches_tags(["TECH"]))
        self.assertFalse(note.matches_tags(["math"]))

    def test_get_search_score(self):
        note = Note("Hello", "This is content about hello world", ["greeting"])
        score = note.get_search_score("hello")
        self.assertGreater(score, 2.0)
        self.assertEqual(note.get_search_score("none"), 0.0)

    def test_to_from_typed_dict(self):
        original = Note("Test", "Body", ["tag"])
        data = original.to_typed_dict()
        copy = Note.from_typed_dict(data)
        self.assertEqual(copy.title, original.title)
        self.assertEqual(copy.content, original.content)
        self.assertEqual(copy.tags, original.tags)
        self.assertEqual(copy.created_at, original.created_at)
        self.assertEqual(copy.id, original.id)

    def test_str_representation(self):
        note = Note("Title", "Content" * 30, ["alpha", "beta"])
        rep = str(note)
        self.assertIn("Title", rep)
        self.assertIn("alpha", rep)
        self.assertIn("created_at", rep)

if __name__ == '__main__':
    unittest.main()
