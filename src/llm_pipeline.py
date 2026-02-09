"""LangChain pipeline for PDF analysis with local LLM."""

import json
import logging
from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama

logger = logging.getLogger(__name__)


class PDFAnalysisPipeline:
    """LangChain pipeline for analyzing PDF content with local LLM."""

    def __init__(
        self,
        model_name: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.3,
    ):
        """
        Initialize the PDF analysis pipeline.

        Args:
            model_name: Name of the local LLM model (default: llama3.2)
            base_url: Base URL for Ollama server
            temperature: Temperature for LLM generation (0-1)
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the local LLM connection."""
        try:
            llm = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature,
            )
            logger.info(f"Connected to local LLM: {self.model_name}")
            return llm
        except Exception as e:
            logger.error(f"Failed to connect to Ollama at {self.base_url}: {e}")
            raise

    def generate_topic_and_summary(self, text: str, max_length: int = 200) -> dict:
        """
        Generate topic and summary for PDF text.

        Args:
            text: Extracted PDF text
            max_length: Maximum length for summary

        Returns:
            Dictionary with 'topic' and 'summary' keys
        """
        # Truncate text if too long for prompt
        truncated_text = text[: min(len(text), 8000)]

        prompt_template = PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze the following document text and provide:
1. A single-word or 2-3 word topic category
2. A brief summary in {max_length} words

Format your response as JSON with keys "topic" and "summary".

Text:
{text}

JSON Response:
            """,
        )

        try:
            prompt = prompt_template.format(text=truncated_text, max_length=max_length)
            response = self.llm.invoke(prompt)
            result = self._parse_response(response)
            logger.info(f"Generated topic: {result.get('topic')}")
            return result
        except Exception as e:
            logger.error(f"Failed to generate topic/summary: {e}")
            return {
                "topic": "Uncategorized",
                "summary": "Failed to process",
                "error": str(e),
            }

    def _parse_response(self, response: str) -> dict:
        """
        Parse LLM response to extract topic and summary.

        Args:
            response: Raw response from LLM

        Returns:
            Parsed dictionary with topic and summary
        """
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)
                return {
                    "topic": str(parsed.get("topic", "Uncategorized")).strip(),
                    "summary": str(parsed.get("summary", ""))[:200].strip(),
                }
        except json.JSONDecodeError:
            pass

        # Fallback: parse free-form response
        lines = response.strip().split("\n")
        return {
            "topic": "Uncategorized",
            "summary": " ".join(lines)[:200],
        }

    def extract_key_entities(self, text: str) -> list:
        """
        Extract key entities/concepts from text.

        Args:
            text: Extracted PDF text

        Returns:
            List of key entities
        """
        truncated_text = text[: min(len(text), 8000)]

        prompt = f"""Extract 3-5 key concepts or entities from this text. 
Return as a JSON array of strings.

Text: {truncated_text}

JSON Array:"""

        try:
            response = self.llm.invoke(prompt)
            # Try to parse JSON array
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            return []
        except Exception as e:
            logger.warning(f"Failed to extract entities: {e}")
            return []
