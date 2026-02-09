"""Unit tests for file organization module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.file_organizer import FileOrganizer


@pytest.fixture
def organizer(tmp_path):
    """Create a FileOrganizer instance with temporary directory."""
    return FileOrganizer(tmp_path)


def test_sanitize_folder_name():
    """Test folder name sanitization."""
    assert FileOrganizer._sanitize_folder_name("Hello World") == "Hello_World"
    assert FileOrganizer._sanitize_folder_name("Tech/Science") == "Tech_Science"
    assert FileOrganizer._sanitize_folder_name("A" * 100) == "A" * 50


def test_organize_by_topic(organizer, tmp_path):
    """Test organization of files by topic."""
    # Create mock PDF file
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("mock pdf content")

    file_mappings = {pdf_file: {"topic": "Machine Learning", "summary": "Test"}}

    organized = organizer.organize_by_topic(file_mappings)

    assert "Machine Learning" in organized
    assert len(organized["Machine Learning"]) == 1
    assert organized["Machine Learning"][0].name == "test.pdf"


def test_generate_index(organizer, tmp_path):
    """Test index generation."""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("mock content")

    file_mappings = {
        pdf_file: {
            "topic": "AI",
            "summary": "About AI",
            "entities": ["AI", "ML"],
        }
    }

    index_path = tmp_path / "index.json"
    organizer.generate_index(file_mappings, index_path)

    assert index_path.exists()

    import json

    with open(index_path) as f:
        index = json.load(f)
    assert "test.pdf" in index
    assert index["test.pdf"]["topic"] == "AI"
