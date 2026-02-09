"""Unit tests for LLM pipeline."""

import json
import pytest
from unittest.mock import Mock, patch

from src.llm_pipeline import PDFAnalysisPipeline


@pytest.fixture
@patch("src.llm_pipeline.Ollama")
def pipeline(mock_ollama):
    """Create a PDFAnalysisPipeline instance."""
    mock_ollama.return_value = Mock()
    return PDFAnalysisPipeline(model_name="mistral")


def test_parse_response_json(pipeline):
    """Test JSON response parsing."""
    response = '{"topic": "AI", "summary": "About artificial intelligence"}'
    result = pipeline._parse_response(response)
    assert result["topic"] == "AI"
    assert result["summary"] == "About artificial intelligence"


def test_parse_response_fallback(pipeline):
    """Test fallback response parsing."""
    response = "Some random text without JSON"
    result = pipeline._parse_response(response)
    assert result["topic"] == "Uncategorized"
    assert len(result["summary"]) > 0


@patch("src.llm_pipeline.Ollama")
def test_generate_topic_and_summary(mock_ollama):
    """Test topic and summary generation."""
    mock_llm = Mock()
    mock_llm.invoke.return_value = '{"topic": "Finance", "summary": "Financial report"}'
    mock_ollama.return_value = mock_llm

    pipeline = PDFAnalysisPipeline()
    result = pipeline.generate_topic_and_summary("Test PDF content")

    assert result["topic"] == "Finance"
    assert "summary" in result


@patch("src.llm_pipeline.Ollama")
def test_extract_key_entities(mock_ollama):
    """Test key entity extraction."""
    mock_llm = Mock()
    mock_llm.invoke.return_value = '["Entity1", "Entity2", "Entity3"]'
    mock_ollama.return_value = mock_llm

    pipeline = PDFAnalysisPipeline()
    result = pipeline.extract_key_entities("Test content")

    assert len(result) == 3
    assert "Entity1" in result
