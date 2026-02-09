"""PDF extraction and text processing utilities."""

import logging
from pathlib import Path
from typing import Optional

from pypdf import PdfReader

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Handles PDF text extraction and validation."""

    def __init__(self, max_pages: Optional[int] = None):
        """
        Initialize PDFExtractor.

        Args:
            max_pages: Maximum pages to extract (None for all pages)
        """
        self.max_pages = max_pages

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text content

        Raises:
            ValueError: If PDF is empty or unreadable
            FileNotFoundError: If file doesn't exist
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)

            if num_pages == 0:
                raise ValueError(f"PDF has no pages: {pdf_path}")

            pages_to_extract = (
                min(self.max_pages, num_pages) if self.max_pages else num_pages
            )

            text_content = []
            for i in range(pages_to_extract):
                page = reader.pages[i]
                text = page.extract_text()
                if text.strip():
                    text_content.append(text)

            if not text_content:
                raise ValueError(f"No readable text found in PDF: {pdf_path}")

            return "\n".join(text_content)

        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            raise

    def extract_metadata(self, pdf_path: Path) -> dict:
        """
        Extract metadata from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with metadata
        """
        try:
            reader = PdfReader(pdf_path)
            metadata = reader.metadata or {}
            return {
                "title": metadata.get("/Title", "Unknown"),
                "author": metadata.get("/Author", "Unknown"),
                "num_pages": len(reader.pages),
                "file_size": pdf_path.stat().st_size,
            }
        except Exception as e:
            logger.warning(f"Could not extract metadata from {pdf_path}: {e}")
            return {"error": str(e)}
