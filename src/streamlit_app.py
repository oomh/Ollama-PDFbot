"""Streamlit frontend for PDF processing application."""

import json
import logging
import threading
from pathlib import Path
from typing import Optional

import streamlit as st
from streamlit.logger import get_logger

from src.config import Config
from src.main import PDFProcessorOrchestrator

# Configure logger for Streamlit
logger = get_logger(__name__)


class StreamlitLogHandler(logging.Handler):
    """Custom logging handler to capture logs for Streamlit display."""

    def __init__(self, log_container):
        """Initialize the handler with a Streamlit container."""
        super().__init__()
        self.log_container = log_container
        self.logs = []

    def emit(self, record):
        """Emit a log record to both the list and Streamlit container."""
        try:
            msg = self.format(record)
            self.logs.append(msg)
            # Keep only last 100 logs to avoid performance issues
            if len(self.logs) > 100:
                self.logs = self.logs[-100:]
        except Exception:
            self.handleError(record)

    def get_logs(self) -> list:
        """Get all captured logs."""
        return self.logs


def setup_logging_handler() -> StreamlitLogHandler:
    """Setup a custom logging handler for Streamlit display."""
    log_container = st.container()
    handler = StreamlitLogHandler(log_container)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    return handler


def validate_ollama_connection(base_url: str) -> bool:
    """Check if Ollama is running and accessible."""
    try:
        import requests

        response = requests.get(f"{base_url}/api/tags", timeout=2)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ollama connection failed: {e}")
        return False


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="PDF Organizer",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("PDF Organizer with Local LLM")
    st.markdown(
        "Automatically categorize and organize your PDFs using your Ollama local LLM "
    )

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")

        # Folder selection
        st.subheader("Folder Selection")
        st.caption(f"Current working directory: {Config.APP_DIR}")
        input_folder = st.text_input(
            "Input Folder (PDFs to process)",
            value=str(Config.PDF_INPUT_DIR),
            help="Path to folder containing PDF files",
        )
        output_folder = st.text_input(
            "Output Folder (organized PDFs)",
            value=str(Config.PDF_OUTPUT_DIR),
            help="Path to save organized PDFs and reports",
        )

        # LLM Configuration
        st.subheader("LLM Configuration")
        llm_model = st.selectbox(
            "LLM Model",
            ["llama3.2", "mistral", "neural-chat", "dolphin-mixtral"],
            index=0,
            help="Select the local LLM model to use",
            accept_new_options=True
        )
        llm_base_url = st.text_input(
            "Ollama Base URL",
            value=Config.LLM_BASE_URL,
            help="URL where Ollama server is running",
        )
        llm_temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=Config.LLM_TEMPERATURE,
            step=0.1,
            help="Lower = more focused, Higher = more creative",
        )

        # Processing Configuration
        st.subheader("Processing Settings")
        max_pages = st.number_input(
            "Max Pages per PDF",
            min_value=1,
            value=Config.MAX_PAGES_PER_PDF,
            help="Limit pages processed per document",
        )
        batch_size = st.number_input(
            "Batch Size",
            min_value=1,
            value=Config.BATCH_SIZE,
            help="Number of PDFs to process",
        )

        # Connection check
        st.subheader("Connection Status")
        if st.button("Check Ollama Connection", key="check_ollama"):
            if validate_ollama_connection(llm_base_url):
                st.success("Connected to Ollama!")
            else:
                st.error("Cannot connect to Ollama. Make sure it's running.")
                
        # End of Sidebar Logic


    # Main content area
    st.subheader("Processing Status")

    info_col1, info_col2 = st.columns([1, 1])

    with info_col1:
        # Check if folders exist
        input_path = Path(input_folder)
        output_path = Path(output_folder)

        # Display folder info
        with info_col1:
            st.info(f"Input: {input_folder}")
            if input_path.exists():
                pdf_count = len(list(input_path.glob("*.pdf")))
                st.caption(f"Found {pdf_count} PDF files")
            else:
                st.warning("Input folder does not exist")

        with info_col2:
            st.info(f"Output: {output_folder}")
            if output_path.exists():
                st.caption(f"Output folder ready")
            else:
                st.caption("Output folder will be created")

    second_section = st.columns([1])
    with second_section[0]:
        st.subheader("Action")
        process_button = st.button(
            "Start Processing",
            use_container_width=True,
            type="primary",
            key="process_button",
        )

    # Processing section
    if process_button:
        # Validate inputs
        if not input_path.exists():
            st.error("❌ Input folder does not exist")
            return

        pdf_files = list(input_path.glob("*.pdf"))
        if not pdf_files:
            st.error("❌ No PDF files found in input folder")
            return

        if not validate_ollama_connection(llm_base_url):
            st.error(
                f"❌ Cannot connect to Ollama at {llm_base_url}. Please start Ollama and try again."
            )
            return

        # Create output folder if needed
        output_path.mkdir(parents=True, exist_ok=True)

        # Progress tracking
        st.divider()
        st.subheader("📈 Processing Progress")

        # Create containers for progress display
        progress_bar = st.progress(0)
        status_text = st.empty()
        logs_expander = st.expander("📋 Processing Logs", expanded=True)

        with logs_expander:
            logs_container = st.container()

        # Setup logging handler
        handler = StreamlitLogHandler(logs_container)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        try:
            # Process PDFs
            orchestrator = PDFProcessorOrchestrator()

            # Override config with user input
            Config.PDF_INPUT_DIR = input_path
            Config.PDF_OUTPUT_DIR = output_path
            Config.LLM_MODEL = llm_model
            Config.LLM_BASE_URL = llm_base_url
            Config.LLM_TEMPERATURE = llm_temperature
            Config.MAX_PAGES_PER_PDF = max_pages

            # Reinitialize with new config
            orchestrator = PDFProcessorOrchestrator()

            total_pdfs = len(pdf_files)
            processed = 0
            failed = 0

            # Process each PDF
            for idx, pdf_path in enumerate(pdf_files):
                # Update progress
                progress = (idx) / total_pdfs
                progress_bar.progress(progress)
                status_text.info(
                    f"Processing {idx + 1}/{total_pdfs}: {pdf_path.name}"
                )

                result = orchestrator.process_pdf(pdf_path)
                if result["status"] == "success":
                    processed += 1
                elif result["status"] == "error":
                    failed += 1

                # Display logs
                with logs_container:
                        for log_msg in handler.get_logs()[-10:]:  # Show last 10 logs
                            st.text(log_msg)

            # Organize files
            status_text.info("Organizing files by topic...")
            organized = orchestrator.organize_files()

            # Final progress
            progress_bar.progress(1.0)

            # Success summary
            st.divider()
            st.success("✅ Processing Complete!")

            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            with summary_col1:
                st.metric("Total PDFs", total_pdfs)
            with summary_col2:
                st.metric("Successfully Processed", processed)
            with summary_col3:
                st.metric("Failed", failed)
            with summary_col4:
                st.metric("Topics Identified", len(organized))

            # Display results
            st.subheader("📑 Results by Topic")
            for topic, files in organized.items():
                with st.expander(f"📌 {topic} ({len(files)} files)"):
                    for file_path in files:
                        st.caption(f"✓ {file_path.name}")

            # Display report if available
            report_path = output_path / "report.json"
            if report_path.exists():
                st.subheader("📊 Full Report")
                with open(report_path) as f:
                    report = json.load(f)

                # Summary stats
                report_col1, report_col2, report_col3 = st.columns(3)
                with report_col1:
                    st.metric(
                        "Success Rate",
                        f"{(report['summary']['processed'] / report['summary']['total_files'] * 100):.1f}%"
                        if report["summary"]["total_files"] > 0
                        else "N/A",
                    )
                with report_col2:
                    st.metric("Topics Created", report["summary"]["topics_identified"])
                with report_col3:
                    st.metric("Total Files", report["summary"]["total_files"])

                # Detailed processing info
                if report["processing_details"]:
                    st.subheader("📝 Processing Details")
                    for item in report["processing_details"]:
                        with st.expander(f"{item['file']} → {item['topic']}"):
                            st.markdown(f"**Topic:** {item['topic']}")
                            st.markdown(f"**Summary:** {item['summary']}")

        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            logger.exception("Processing error")
        finally:
            # Clean up handler
            root_logger.removeHandler(handler)

    # Footer
    st.divider()
    st.caption(
        "🚀 PDF Organizer - Powered by LangChain + Local LLM (Ollama) | "
        "Organize your PDFs intelligently"
    )


if __name__ == "__main__":
    main()
