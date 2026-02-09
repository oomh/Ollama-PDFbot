"""Configuration and environment management."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # PDF Processing
    PDF_INPUT_DIR = Path(os.getenv("PDF_INPUT_DIR", "data/sample_pdfs"))
    PDF_OUTPUT_DIR = Path(os.getenv("PDF_OUTPUT_DIR", "data/output"))
    MAX_PAGES_PER_PDF = int(os.getenv("MAX_PAGES_PER_PDF", "50"))
    
    # load the current working directory of the app
    APP_DIR = Path.cwd()

    # LLM Configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # Application Settings
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    GENERATE_INDEX = os.getenv("GENERATE_INDEX", "true").lower() == "true"

    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.PDF_INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
