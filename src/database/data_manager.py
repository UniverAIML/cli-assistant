"""
Data management module for AddressBook and NotesManager persistence.

This module provides functionality for saving and loading AddressBook and NotesManager data
using pickle serialization protocol.
"""

import pickle
from pathlib import Path
from .contact_models import AddressBook
from .note_models import NotesManager
from typing import Dict, Any, Tuple, Optional


class DataManager:
    """
    Manages persistence of AddressBook and NotesManager data using pickle serialization.

    This class handles saving and loading of AddressBook and NotesManager instances to/from disk,
    providing a clean separation of concerns between data storage and business logic.
    """

    def __init__(
        self,
        contacts_filename: str = "addressbook.pkl",
        notes_filename: Optional[str] = None,
    ) -> None:
        """
        Initialize DataManager with specified filenames.

        Args:
            contacts_filename (str): Name of the file to store contacts. Defaults to "addressbook.pkl"
            notes_filename (Optional[str]): Name of the file to store notes. If None, generates based on contacts filename
        """
        self.contacts_filename = contacts_filename

        # Handle legacy single-file format
        if notes_filename is None:
            if contacts_filename.endswith(".pkl"):
                self.notes_filename = contacts_filename.replace(".pkl", "_notes.pkl")
            else:
                self.notes_filename = contacts_filename + "_notes.pkl"
        else:
            self.notes_filename = notes_filename

        self.contacts_filepath = Path(self.contacts_filename)
        self.notes_filepath = Path(self.notes_filename)

    def save_contacts(self, address_book: AddressBook) -> bool:
        """
        Save AddressBook data to file using pickle serialization.

        Args:
            address_book (AddressBook): The AddressBook instance to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            with open(self.contacts_filepath, "wb") as file:
                pickle.dump(address_book, file)
            return True
        except (IOError, pickle.PickleError) as e:
            print(f"Error saving contacts: {e}")
            return False

    def save_notes(self, notes_manager: NotesManager) -> bool:
        """
        Save NotesManager data to file using pickle serialization.

        Args:
            notes_manager (NotesManager): The NotesManager instance to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            with open(self.notes_filepath, "wb") as file:
                pickle.dump(notes_manager, file)
            return True
        except (IOError, pickle.PickleError) as e:
            print(f"Error saving notes: {e}")
            return False

    def save_data(
        self, address_book: AddressBook, notes_manager: Optional[NotesManager] = None
    ) -> bool:
        """
        Save both AddressBook and NotesManager data.

        Args:
            address_book (AddressBook): The AddressBook instance to save
            notes_manager (Optional[NotesManager]): The NotesManager instance to save

        Returns:
            bool: True if all saves were successful, False otherwise
        """
        contacts_saved = self.save_contacts(address_book)
        notes_saved = True

        if notes_manager is not None:
            notes_saved = self.save_notes(notes_manager)

        return contacts_saved and notes_saved

    def load_contacts(self) -> AddressBook:
        """
        Load AddressBook data from file using pickle deserialization.

        Returns:
            AddressBook: Loaded AddressBook instance, or new empty one if file not found
        """
        try:
            if self.contacts_filepath.exists():
                with open(self.contacts_filepath, "rb") as file:
                    address_book = pickle.load(file)
                    if isinstance(address_book, AddressBook):
                        return address_book
                    else:
                        print(
                            "Warning: Invalid contacts data format in file. Creating new AddressBook."
                        )
                        return AddressBook()
            else:
                # File doesn't exist, return new AddressBook
                return AddressBook()
        except (IOError, pickle.PickleError, EOFError) as e:
            print(f"Error loading contacts: {e}. Creating new AddressBook.")
            return AddressBook()

    def load_notes(self) -> NotesManager:
        """
        Load NotesManager data from file using pickle deserialization.

        Returns:
            NotesManager: Loaded NotesManager instance, or new empty one if file not found
        """
        try:
            if self.notes_filepath.exists():
                with open(self.notes_filepath, "rb") as file:
                    notes_manager = pickle.load(file)
                    if isinstance(notes_manager, NotesManager):
                        return notes_manager
                    else:
                        print(
                            "Warning: Invalid notes data format in file. Creating new NotesManager."
                        )
                        return NotesManager()
            else:
                # File doesn't exist, return new NotesManager
                return NotesManager()
        except (IOError, pickle.PickleError, EOFError) as e:
            print(f"Error loading notes: {e}. Creating new NotesManager.")
            return NotesManager()

    def load_data(self) -> Tuple[AddressBook, NotesManager]:
        """
        Load both AddressBook and NotesManager data from files.

        Returns:
            Tuple[AddressBook, NotesManager]: Loaded instances or new empty ones if files not found
        """
        address_book = self.load_contacts()
        notes_manager = self.load_notes()
        return address_book, notes_manager

    def contacts_file_exists(self) -> bool:
        """
        Check if the contacts data file exists.

        Returns:
            bool: True if file exists, False otherwise
        """
        return self.contacts_filepath.exists()

    def notes_file_exists(self) -> bool:
        """
        Check if the notes data file exists.

        Returns:
            bool: True if file exists, False otherwise
        """
        return self.notes_filepath.exists()

    def file_exists(self) -> bool:
        """
        Check if any data files exist.

        Returns:
            bool: True if any file exists, False otherwise
        """
        return self.contacts_file_exists() or self.notes_file_exists()

    def get_contacts_file_size(self) -> int:
        """
        Get size of the contacts data file in bytes.

        Returns:
            int: File size in bytes, or 0 if file doesn't exist
        """
        try:
            return (
                self.contacts_filepath.stat().st_size
                if self.contacts_filepath.exists()
                else 0
            )
        except OSError:
            return 0

    def get_notes_file_size(self) -> int:
        """
        Get size of the notes data file in bytes.

        Returns:
            int: File size in bytes, or 0 if file doesn't exist
        """
        try:
            return (
                self.notes_filepath.stat().st_size
                if self.notes_filepath.exists()
                else 0
            )
        except OSError:
            return 0

    def delete_contacts_file(self) -> bool:
        """
        Delete the contacts data file.

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if self.contacts_filepath.exists():
                self.contacts_filepath.unlink()
                return True
            return False
        except OSError as e:
            print(f"Error deleting contacts file: {e}")
            return False

    def delete_notes_file(self) -> bool:
        """
        Delete the notes data file.

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if self.notes_filepath.exists():
                self.notes_filepath.unlink()
                return True
            return False
        except OSError as e:
            print(f"Error deleting notes file: {e}")
            return False
