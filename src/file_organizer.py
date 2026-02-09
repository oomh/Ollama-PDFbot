"""File organization and management utilities."""

import logging
import shutil
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class FileOrganizer:
    """Handles organization of processed PDF files into topic folders."""

    def __init__(self, base_output_dir: Path, create_subdirs: bool = True):
        """
        Initialize FileOrganizer.

        Args:
            base_output_dir: Base directory for organized files
            create_subdirs: Whether to create subdirectories for topics
        """
        self.base_output_dir = Path(base_output_dir)
        self.create_subdirs = create_subdirs
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    def organize_by_topic(
        self, file_mappings: Dict[Path, dict]
    ) -> Dict[str, List[Path]]:
        """
        Organize PDF files into topic-based folders.

        Args:
            file_mappings: Dictionary mapping file paths to analysis results
                            (must contain 'topic' key)

        Returns:
            Dictionary mapping topics to list of organized file paths
        """
        organized = {}

        for pdf_path, analysis_data in file_mappings.items():
            topic = analysis_data.get("topic", "Uncategorized")
            # Sanitize folder name
            folder_name = self._sanitize_folder_name(topic)

            if self.create_subdirs:
                topic_dir = self.base_output_dir / folder_name
                topic_dir.mkdir(parents=True, exist_ok=True)
                dest_path = topic_dir / pdf_path.name
            else:
                # Prefix filename with topic
                dest_path = self.base_output_dir / f"{folder_name}_{pdf_path.name}"

            try:
                shutil.copy2(pdf_path, dest_path)
                logger.info(f"Organized {pdf_path.name} -> {dest_path}")

                if topic not in organized:
                    organized[topic] = []
                organized[topic].append(dest_path)
            except Exception as e:
                logger.error(f"Failed to organize {pdf_path.name}: {e}")

        return organized

    def generate_index(
        self, file_mappings: Dict[Path, dict], output_file: Path
    ) -> None:
        """
        Generate an index file documenting all processed files.

        Args:
            file_mappings: Dictionary mapping file paths to analysis results
            output_file: Path to save the index
        """
        index = {}
        for pdf_path, analysis_data in file_mappings.items():
            index[pdf_path.name] = {
                "topic": analysis_data.get("topic"),
                "summary": analysis_data.get("summary"),
                "entities": analysis_data.get("entities", []),
            }

        try:
            import json

            with open(output_file, "w") as f:
                json.dump(index, f, indent=2)
            logger.info(f"Index saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to generate index: {e}")

    @staticmethod
    def _sanitize_folder_name(name: str) -> str:
        """
        Sanitize a string to be used as a folder name.

        Args:
            name: Input string

        Returns:
            Sanitized folder name
        """
        # Replace spaces with underscores
        name = name.replace(" ", "_")
        # Remove or replace invalid characters
        invalid_chars = '<>:"|?*/'
        for char in invalid_chars:
            name = name.replace(char, "_")
        # Limit length
        return name[:50] if name else "unknown"
