"""Main orchestration script for PDF processing workflow."""

import json
import logging
import os
from pathlib import Path

from src.config import Config
from src.file_organizer import FileOrganizer
from src.llm_pipeline import PDFAnalysisPipeline
from src.pdf_extractor import PDFExtractor

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PDFProcessorOrchestrator:
    """Orchestrates the entire PDF processing workflow."""

    def __init__(self):
        """Initialize the orchestrator with all components."""
        Config.create_directories()
        self.extractor = PDFExtractor(max_pages=Config.MAX_PAGES_PER_PDF)
        self.pipeline = PDFAnalysisPipeline(
            model_name=Config.LLM_MODEL,
            base_url=Config.LLM_BASE_URL,
            temperature=Config.LLM_TEMPERATURE,
        )
        self.organizer = FileOrganizer(Config.PDF_OUTPUT_DIR)
        self.results = {}

    def process_pdf(self, pdf_path: Path) -> dict:
        """
        Process a single PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with analysis results
        """
        # Before processing a PDF file, check report.json to see if it was already processed
        report_path = Config.PDF_OUTPUT_DIR / "report.json"
        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                report_data = json.load(f)
                skip_these = [
                    item["file"] for item in report_data.get("processing_details", [])
                ]

                if pdf_path.name in skip_these:
                    logger.info(f"Skipping already processed file: {pdf_path.name}")
                    return {
                        "file": pdf_path.name,
                        "status": "skipped",
                    }

        # Process the PDF
        try:
            logger.info(f"Processing: {pdf_path.name}")
            text = self.extractor.extract_text(pdf_path)
            metadata = self.extractor.extract_metadata(pdf_path)

            # Analyze with LLM
            analysis = self.pipeline.generate_topic_and_summary(text)
            entities = self.pipeline.extract_key_entities(text)

            result = {
                "file": pdf_path.name,
                "status": "success",
                "metadata": metadata,
                "analysis": {
                    "topic": analysis.get("topic"),
                    "summary": analysis.get("summary"),
                    "entities": entities,
                },
            }

            logger.info(f"✓ {pdf_path.name} -> Topic: {analysis.get('topic')}")
            return result

        except Exception as e:
            logger.error(f"✗ Failed to process {pdf_path.name}: {e}")
            return {
                "file": pdf_path.name,
                "status": "error",
                "error": str(e),
            }

    def process_batch(self, pdf_dir: Path) -> dict:
        """
        Process all PDF files in a directory.

        Args:
            pdf_dir: Directory containing PDF files

        Returns:
            Dictionary with all results and organization info
        """
        pdf_files = list(pdf_dir.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return {"processed": 0, "failed": 0, "results": {}}

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        processed_count = 0
        failed_count = 0

        for pdf_path in pdf_files:
            result = self.process_pdf(pdf_path)
            if result is not None:
                self.results[pdf_path] = result

                if result["status"] == "success":
                    processed_count += 1
                elif result["status"] == "error":
                    failed_count += 1

        logger.info(
            f"Batch complete: {processed_count} processed, {failed_count} failed"
        )

        return {
            "processed": processed_count,
            "failed": failed_count,
            "total": len(pdf_files),
            "results": self.results,
        }

    def organize_files(self) -> dict:
        """
        Organize processed PDF files by topic.

        Returns:
            Dictionary with organization results
        """
        # Prepare file mappings for organization
        file_mappings = {}
        for pdf_path, result in self.results.items():
            if result["status"] == "success":
                file_mappings[pdf_path] = result["analysis"]

        if not file_mappings:
            logger.warning("No successfully processed files to organize")
            return {}

        organized = self.organizer.organize_by_topic(file_mappings)

        # Generate index if enabled
        if Config.GENERATE_INDEX:
            report_path = Config.PDF_OUTPUT_DIR / "index.json"
            self.organizer.generate_index(file_mappings, report_path)

        logger.info(f"Files organized into {len(organized)} topic categories")
        return organized

    def run(self, pdf_dir: Path = None) -> None:  # type: ignore
        """
        Run the complete PDF processing workflow.

        Args:
            pdf_dir: Directory containing PDFs (defaults to Config.PDF_INPUT_DIR)
        """
        pdf_dir = pdf_dir or Config.PDF_INPUT_DIR

        logger.info("=" * 60)
        logger.info("PDF Processing Workflow Started")
        logger.info("=" * 60)

        # Process all PDFs
        batch_results = self.process_batch(pdf_dir)

        # Organize by topic
        organized = self.organize_files()

        # Generate summary report
        self._generate_report(batch_results, organized)

    def _generate_report(self, batch_results: dict, organized: dict) -> None:
        """Generate and save a summary report."""
        report = {
            "summary": {
                "total_files": batch_results.get("total", 0),
                "processed": batch_results.get("processed", 0),
                "failed": batch_results.get("failed", 0),
                "topics_identified": len(organized),
            },
            "topics": {},
            "processing_details": [],
        }

        # Add topic details
        for topic, files in organized.items():
            report["topics"][topic] = {
                "file_count": len(files),
                "files": [f.name for f in files],
            }

        # Add processing details
        for pdf_path, result in self.results.items():
            if result["status"] == "success":
                report["processing_details"].append(
                    {
                        "file": pdf_path.name,
                        "topic": result["analysis"]["topic"],
                        "summary": result["analysis"]["summary"],
                    }
                )

        # Save report
        report_path = Config.PDF_OUTPUT_DIR / "report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to {report_path}")
        logger.info("=" * 60)
        logger.info(
            f"Processing complete: {report['summary']['processed']}/{report['summary']['total_files']} successful"
        )
        logger.info("=" * 60)


def main():
    """Entry point for the application."""
    orchestrator = PDFProcessorOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
