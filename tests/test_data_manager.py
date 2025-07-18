#!/usr/bin/env python3
"""
DataManager tests - main test suite entry point.

This file imports all DataManager test modules to provide a single entry point
for running all DataManager-related tests.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import all test modules with relative imports
from .test_data_manager_basic import TestDataManagerBasic
from .test_data_manager_contacts import TestDataManagerContacts
from .test_data_manager_error_handling import TestDataManagerErrorHandling
from .test_data_manager_file_ops import TestDataManagerFileOps
from .test_data_manager_notes import TestDataManagerNotes

# Re-export test classes for pytest discovery
__all__ = [
    "TestDataManagerBasic",
    "TestDataManagerContacts",
    "TestDataManagerNotes",
    "TestDataManagerFileOps",
    "TestDataManagerErrorHandling",
]
