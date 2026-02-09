"""Unit tests for PDF extraction module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.pdf_extractor import PDFExtractor


@pytest.fixture
def extractor():
    """Create a PDFExtractor instance."""
    return PDFExtractor(max_pages=10)


def test_extractor_init():
    """Test PDFExtractor initialization."""
    extractor = PDFExtractor(max_pages=5)
    assert extractor.max_pages == 5


def test_extract_text_file_not_found(extractor):
    """Test extraction with non-existent file."""
    with pytest.raises(FileNotFoundError):
        extractor.extract_text(Path("nonexistent.pdf"))


@patch("src.pdf_extractor.PdfReader")
def test_extract_text_success(mock_reader, extractor):
    """Test successful text extraction."""
    # Mock PDF with pages
    mock_page = Mock()
    mock_page.extract_text.return_value = "Sample text"
    mock_reader_instance = Mock()
    mock_reader_instance.pages = [mock_page]
    mock_reader.return_value = mock_reader_instance

    # Create a mock file
    with patch("src.pdf_extractor.Path.exists", return_value=True):
        result = extractor.extract_text(Path("test.pdf"))
        assert "Sample text" in result


@patch("src.pdf_extractor.PdfReader")
def test_extract_metadata(mock_reader, extractor):
    """Test metadata extraction."""
    mock_metadata = {"/Title": "Test Doc", "/Author": "Test Author"}
    mock_reader_instance = Mock()
    mock_reader_instance.metadata = mock_metadata
    mock_reader_instance.pages = [Mock(), Mock()]
    mock_reader.return_value = mock_reader_instance

    with patch.object(Path, "stat") as mock_stat:
        mock_stat.return_value.st_size = 1024
        with patch("src.pdf_extractor.Path.exists", return_value=True):
            result = extractor.extract_metadata(Path("test.pdf"))
            assert result["title"] == "Test Doc"
            assert result["author"] == "Test Author"
            assert result["num_pages"] == 2
