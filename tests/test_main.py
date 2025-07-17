"""Tests for the main module."""

import pytest

from cli_assistant.main import main


def test_main_no_args(capsys):
    """Test main function with no arguments."""
    main([])
    captured = capsys.readouterr()
    assert "CLI Assistant v0.1.0" in captured.out
    assert "Usage:" in captured.out


def test_main_with_args(capsys):
    """Test main function with arguments."""
    main(["test", "arg"])
    captured = capsys.readouterr()
    assert "CLI Assistant v0.1.0" in captured.out
    assert "Received arguments: ['test', 'arg']" in captured.out
