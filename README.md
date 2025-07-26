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

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install PyMuPDF sentence-transformers
```

### Required Dependencies

- `PyMuPDF` (fitz): For PDF processing and text extraction
- `sentence-transformers`: For semantic similarity calculations
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
├── app/
│   ├── input/             # Input folder for PDFs and input.json
│   │   ├── input.json     # Configuration file
│   │   └── *.pdf          # PDF documents to process
│   └── output/            # Output folder
│       └── output.json    # Generated results
└── README.md              # This file
```

## Usage

### 1. Prepare Input Files

Create the required directory structure and place your files:

```bash
mkdir -p app/input app/output
```

### 2. Add PDF Documents

Place your PDF files in the `app/input/` directory.

### 3. Create Input Configuration

Create `app/input/input.json` with the following structure:

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

```bash
python main.py
```

### 5. View Results

The application will generate `app/output/output.json` containing:

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

The generated `output.json` contains:

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

## Troubleshooting

### Common Issues

1. **File not found errors**: Ensure PDF files are in the `app/input/` directory
2. **Missing dependencies**: Install all required packages using pip
3. **Permission errors**: Ensure write permissions for the `app/output/` directory

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