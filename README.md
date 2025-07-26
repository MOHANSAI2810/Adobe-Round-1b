# PDF Heading Extraction and Semantic Search

A Python application that extracts headings from PDF documents and performs semantic search to find relevant sections based on user queries. This tool is particularly useful for analyzing large documents and finding specific content quickly.

## Features

- **PDF Heading Extraction**: Automatically identifies and extracts headings from PDF documents using font size analysis and text pattern recognition
- **Semantic Search**: Uses sentence transformers to find semantically similar headings based on user queries
- **Subsection Extraction**: Extracts the content under matched headings for further analysis
- **Structured Output**: Generates JSON output with metadata, extracted sections, and subsection analysis
- **Batch Processing**: Processes multiple PDF files simultaneously

## Prerequisites

- Python 3.7 or higher
- Required Python packages (see Installation section)

## Installation

### Option 1: Local Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install PyMuPDF sentence-transformers
```

### Option 2: Docker Installation (Recommended)

1. Clone or download this repository
2. Build the Docker image:

```bash
docker build -t pdf-heading-extractor .
```

3. Run the application using Docker:

**For Linux/Mac:**
```bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-heading-extractor
```

**For Windows PowerShell:**
```powershell
docker run -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output pdf-heading-extractor
```

**For Windows Command Prompt:**
```cmd
docker run -v %cd%/input:/app/input -v %cd%/output:/app/output pdf-heading-extractor
```

**Note**: The `-v` flags mount your local `input` and `output` directories to the container, allowing you to place PDFs in `input/` and retrieve results from `output/`.

### Required Dependencies

- `PyMuPDF==1.23.8`: For PDF processing and text extraction
- `sentence-transformers==2.2.2`: For semantic similarity calculations
- `torch==2.0.1`: PyTorch backend for sentence transformers
- `unicodedata`: For text normalization (built-in)
- `logging`: For application logging (built-in)
- `json`: For JSON processing (built-in)
- `re`: For regular expressions (built-in)
- `os`: For file system operations (built-in)
- `datetime`: For timestamp generation (built-in)

## Project Structure

```
project/
├── main.py                 # Main application script
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
├── temp.py               # Temporary/utility script
├── input/                 # Input folder for PDFs and input.json
│   ├── input.json         # Configuration file
│   └── *.pdf              # PDF documents to process
├── output/                # Output folder
│   └── output.json        # Generated results
└── README.md              # This file
```

## Usage

### 1. Prepare Input Files

Create the required directory structure and place your files:

```bash
mkdir -p input output
```

### 2. Add PDF Documents

Place your PDF files in the `input/` directory.

### 3. Create Input Configuration

Create `input/input.json` with the following structure:

```json
{
  "persona": {
    "role": "Your role or persona description"
  },
  "job_to_be_done": {
    "task": "Your search query or task description"
  },
  "documents": [
    {
      "filename": "document1.pdf"
    },
    {
      "filename": "document2.pdf"
    }
  ]
}
```

### 4. Run the Application

#### Local Installation:
```bash
python main.py
```

#### Docker Installation:

**For Linux/Mac:**
```bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-heading-extractor
```

**For Windows PowerShell:**
```powershell
docker run -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output pdf-heading-extractor
```

**For Windows Command Prompt:**
```cmd
docker run -v %cd%/input:/app/input -v %cd%/output:/app/output pdf-heading-extractor
```

### 5. View Results

The application will generate `output/output.json` containing:

- **Metadata**: Input documents, persona, job description, and timestamp
- **Extracted Sections**: Matched headings with importance ranking
- **Subsection Analysis**: Extracted content under matched headings

## How It Works

### 1. Heading Extraction
The application analyzes PDF documents to identify headings using:
- Font size analysis (relative to page average)
- Text pattern recognition (chapter numbers, title case, etc.)
- Unicode normalization and text cleaning

### 2. Semantic Search
Uses the `all-MiniLM-L6-v2` sentence transformer model to:
- Encode headings and user queries into embeddings
- Calculate cosine similarity scores
- Rank results by relevance

### 3. Content Extraction
For matched headings, extracts the subsection content until the next heading is encountered.

## Configuration

### Input JSON Format

```json
{
  "persona": {
    "role": "string - Description of the user's role or context"
  },
  "job_to_be_done": {
    "task": "string - The search query or task to find relevant content for"
  },
  "documents": [
    {
      "filename": "string - PDF filename (with or without .pdf extension)"
    }
  ]
}
```

### Semantic Search Parameters

You can modify these parameters in the `semantic_headings` function:

- `top_k`: Maximum number of results to return (default: 5)
- `threshold`: Minimum similarity score (default: 0.3)

## Output Format

The generated `output/output.json` contains:

```json
{
  "metadata": {
    "input_documents": ["list of processed PDF filenames"],
    "persona": "user role description",
    "job_to_be_done": "search query",
    "processing_timestamp": "ISO timestamp"
  },
  "extracted_sections": [
    {
      "document": "pdf filename",
      "section_title": "heading text",
      "importance_rank": 1,
      "page_number": 5
    }
  ],
  "subsection_analysis": [
    {
      "document": "pdf filename",
      "refined_text": "extracted content under heading",
      "page_number": 5
    }
  ]
}
```

## Error Handling

The application includes comprehensive error handling for:
- Missing input files
- Invalid PDF files
- File path issues
- JSON parsing errors

All errors are logged with appropriate warning messages.

## Performance Considerations

- The sentence transformer model is loaded once globally for efficiency
- Large PDF files may take longer to process
- Memory usage scales with the number and size of PDF documents
- Docker containers may have slower initial startup due to model downloading
- Consider using Docker volumes for persistent model storage across runs

## Troubleshooting

### Common Issues

1. **File not found errors**: Ensure PDF files are in the `input/` directory
2. **Missing dependencies**: Install all required packages using pip
3. **Permission errors**: Ensure write permissions for the `output/` directory
4. **Docker volume mount issues**: Ensure the `input` and `output` directories exist and have proper permissions

### Docker-Specific Issues

1. **Build failures**: Ensure Docker is running and you have sufficient disk space
2. **Volume mount problems**: 
   - On Windows, use `${PWD}` instead of `$(pwd)` in PowerShell
   - Ensure the `input` and `output` directories exist before running the container
3. **Permission denied**: Run Docker commands with appropriate permissions
4. **Model download issues**: The first run may take longer as it downloads the sentence transformer model

### Debug Mode

To enable debug logging, modify the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is provided as-is for educational and research purposes.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## Version History

- Initial version with PDF heading extraction and semantic search capabilities 