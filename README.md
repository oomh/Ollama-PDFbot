# PDF Organizer with Local AI

Tired of manually organizing my PDFs, I made this tool to help me organize my ever growing document library made mostly of PDF files. It uses an Ollama LLM running on my computer to automatically categorize and organize my documents. Add all your PDFs to  Data/{your_directory}, point the app to that directory in the Streamlit sidebar and it'll intelligently sort them into topic-based folders with detailed summaries.

No cloud services needed—everything runs locally on my machine. You need a local Ollama LLM installed, link to instructions is available.

## What Can It Do?

- **AI categorization**: Automatically assigns topics using a local LLM 
- **Smart summaries**: Generates concise summaries for each document
- **Auto-organize**: Sorts PDFs into folders by topic automatically
- **Entity extraction**: Identifies key concepts and entities in documents
- **Detailed reports**: Creates JSON reports with processing results
- **Batch processing**: Handle multiple PDFs at once with progress tracking

## How It Works

PDF Files
   > Extract text and metadata
   > Analyze with local AI (Ollama)
   > Generate topic and summary
   > Extract key entities
   > Organize into topic folders
   > Generate reports
   > Output: Organized PDFs with summaries and index

## Prerequisites

Before you get started, you'll need:

- **Python 3.13+** (check with `python --version`)
- **Ollama** - A tool to run AI models locally on your computer
- **uv** - A fast Python package manager (optional but recommended)

### Install Ollama (Important!)

Ollama is the local AI engine that powers this tool. Without it, the app won't work.

1. **Download and install Ollama** from: <https://ollama.com.>
2. **Start Ollama** - After installation, run Ollama (it should run in the background)
3. **Download a model** - Open a terminal and run:

   ```bash
   ollama pull llama3.2 
   (# Or any other model you would like, consider your PC specifications, smaller models require less juice)
   ```

This downloads a lightweight AI model (~5GB). If you prefer a faster model, try:

```bash
ollama pull mistral
```

You can check if Ollama is running by visiting `http://localhost:11434` in your browser.

## Installation & Setup

Clone or download this project to your computer:

```bash
cd /path/to/filebot
```

### Step 2: Install Dependencies

I recommend using `uv` (it's much faster than pip):

```bash
uv sync
```

If you want to run the tests

```bash
uv sync --extra dev
```

### Step 3: Create a Configuration File

Create a `.env` file in the project directory:

```bash
cp .env.example .env  # If an example exists, or create from scratch
```

Edit `.env` with your settings:

```env
# PDF Processing
PDF_INPUT_DIR=data/sample_pdfs
PDF_OUTPUT_DIR=data/output
MAX_PAGES_PER_PDF=50

# LLM Configuration
LLM_MODEL=llama3.2
LLM_BASE_URL=http://localhost:11434
LLM_TEMPERATURE=0.3

# Application Settings
BATCH_SIZE=5
LOG_LEVEL=INFO
GENERATE_INDEX=true
```

## Using the App

The easiest way to use this tool is through the interactive Streamlit web interface. It gives you a visual dashboard with real-time progress tracking, folder selection, and detailed results.

**To start the web app:**

```bash
uv run streamlit run src/streamlit_app.py
```

Then open your browser to **`http://localhost:8501`**

**The web interface includes:**

- Folder browser to select input and output directories
- Real-time settings adjustment (model, temperature, page limits)
- Connection checker to verify Ollama is running
- Live progress bar showing processing status
- Expandable logs to see what the app is doing
- Results dashboard with metrics
- Topic-based results with file listings
- Detailed JSON reports with summaries

### Alternative: Command Line (Advanced)

If you prefer the command line:

1. **Put your PDFs** in the input folder:

   ```bash
   cp your_pdfs/*.pdf data/{your_directory_here}/
   ```

2. **Run the processor**:

   ```bash
   uv run python -m src.main
   ```

3. **Check the results**:

   ```bash
   ls data/output/
   cat data/output/report.json
   ```

### Understanding the Output

After processing, you'll find organized files in `data/output/`:

```txt
data/output/
├── Machine_Learning/
│   ├── paper1.pdf
│   └── paper2.pdf
├── Healthcare/
│   ├── study.pdf
│   └── research.pdf
├── index.json      (List of all files with summaries)
└── report.json     (Summary statistics and details)
```

Each topic folder contains PDFs automatically sorted by the AI. The JSON files contain metadata for searching and referencing.

## Testing

```bash
uv run pytest tests/ -v
```

With coverage report:

```bash
uv run pytest tests/ --cov=src --cov-report=html
```

## Key Components

Under the hood, here's what each part does:

### PDF Extractor (`src/pdf_extractor.py`)

- Reads text from PDFs safely
- Extracts document metadata (title, author, etc.)
- Handles corrupted or image-based PDFs gracefully

### AI Pipeline (`src/llm_pipeline.py`)

- Connects to your local Ollama instance
- Generates topics and summaries using AI
- Extracts key concepts from documents
- All processing happens on your computer

### File Organizer (`src/file_organizer.py`)

- Sorts PDFs into topic folders automatically
- Creates clean, searchable folder structures
- Generates index files for quick reference

### Main Orchestrator (`src/main.py`)

- Coordinates the entire workflow
- Processes multiple PDFs in sequence
- Generates final reports with statistics

### Process Fewer Pages

To save memory and time, limit pages processed per PDF:

```env
MAX_PAGES_PER_PDF=10
```

### Adjust AI Creativity

The `temperature` setting controls how creative the AI is:

```env
LLM_TEMPERATURE=0.1  # Very strict and consistent
LLM_TEMPERATURE=0.5  # Balanced (default)
LLM_TEMPERATURE=0.9  # Creative and varied
```

## Troubleshooting

**Problem**: The app can't find Ollama

**Solution**:

1. Make sure Ollama is running (check your system tray or start it again)
2. Verify the URL in your `.env` matches where Ollama is running
3. Try opening `http://localhost:11434` in your browser

### "ModuleNotFoundError" or "No module named..."

**Problem**: Missing dependencies

**Solution**:

```bash
# Reinstall dependencies
uv sync
```

### Processing is Very Slow

**Problem**: Taking too long to process PDFs

**Solution**:

- Use a faster model: `LLM_MODEL=mistral`
- Reduce pages processed: `MAX_PAGES_PER_PDF=10`
- Lower temperature for faster inference: `LLM_TEMPERATURE=0.1`

### "Out of Memory" Error

**Problem**: Your computer ran out of RAM

**Solution**:

- Use a smaller model like `mistral` or `neural-chat`
- Reduce `MAX_PAGES_PER_PDF` to 5 or 10
- Process fewer PDFs at a time

## Getting Help

1. **Check the logs** - The app prints detailed error messages
2. **Read the troubleshooting section above**
3. **Check if Ollama is running** - Most issues are related to Ollama not being available
4. **Review the test files** for usage examples (in the `tests/` folder)
5. **Visit the Ollama documentation**: <https://ollama.com/library>

### Common Questions

**Q: Why do I need Ollama?**
A: Ollama runs AI models locally so you don't need internet or external services.

**Q: Is my data private?**
A: Yes! Everything runs on your computer. No data is sent anywhere.

**Q: Can I use this on a Mac or Windows?**
A: Yes! Ollama works on Windows, Mac, and Linux.

**Q: How much storage do I need?**
A: Models are 2-20GB depending on which one you choose. You'll also need space for processed PDFs.

## License

MIT License - Feel free to use and modify this project

## Contributing

Found a bug or have a feature idea? We'd love your help!

1. Create an issue describing the problem
2. Fork the project
3. Make your changes
4. Add tests for new features
5. Submit a pull request
