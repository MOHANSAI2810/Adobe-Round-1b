from fpdf import FPDF
title = "Document Structural Outline Extraction"
submitted_by = "Submitted by: Code_Crackers"

# Headings to bold
side_headings = [
    "Problem Statement (Round 1A)",
    "Round 1A Requirements (Key Points)",
    "Solution Overview",
    "Key Features",
    "System Architecture & Processing Pipeline",
    "Sample Output JSON Format",
    "Core Algorithmic Techniques",
    "Technologies & Dependencies",
    "How to Build & Run",
    "Strengths & Innovations",
    "Limitations & Next Steps",
    "References",
    "Appendix: Full Solution Code",
    "Submission Checklist",
]

# Full content as provided (excluding title and submission)
content = """
Problem Statement (Round 1A)
In the Round 1A phase of the "Connecting the Dots" challenge, participants are asked to build an intelligent pipeline that can process a given PDF and extract its complete structural outline: title, and all major and minor headings (H1, H2, H3…) with levels and page numbers. The solution should be fast, robust across different PDF types, completely offline, and not rely exclusively on font size for heading recognition.

Round 1A Requirements (Key Points)
Input: A PDF (<50 pages).

Output: JSON capturing:

Title

Each heading: level (H1/H2/H3...), text, page.

Constraints:

Run offline; model (if used) ≤200MB; ≤10s per PDF.

No API/web calls; no hardcoding; supports diverse PDF structures.

Must generalize: works on academic, business, textbooks, etc.

Solution Overview
This solution combines PyMuPDF and pdfplumber to robustly interpret the structure of PDFs, leveraging hybrid heuristics across font, pattern, and layout for best-in-class heading extraction.

Key Features
Hybrid Approach: Uses both font statistics (relative, not absolute), positional cues, and regular expression patterns to detect headings.

Multi-Format: Handles both text-based and scanned/image-heavy PDFs.

Level Assignment: Dynamically assigns heading levels based on font size and style in context.

No Over-Reliance on Font Size: Heading detection cross-validates using regex and position, not only size.

Title Detection: Selects a probable title from the top of the first page.

Batch Processing: Processes all PDFs in a directory automatically, producing a corresponding JSON per file.

System Architecture & Processing Pipeline
Page Classification:
Each page is scanned to determine if it is primarily text or image-based. Text-heavy pages are parsed with PyMuPDF; image-heavy pages (e.g., scanned documents) use pdfplumber to recover headings.

Text Span Extraction:
For each text-containing page, all text elements are extracted, recording their content, font, style, bounding box, and relative positions.

Font Analysis:
Analyzes font sizes across the page to estimate "body" size (main text) and detect which sizes are used for headings.

Heading Candidate Selection:
Each text element is tested against heading and "non-heading" regexes, size/style heuristics, and its position on the page (title likely at top/center, headings left/top aligned).

Heading Level Assignment:
Based on its font size relative to detected body size, each heading is assigned a structural level: H1–H6.

Deduplication & Pruning:
Headings are de-duplicated, merged (scanned/image extraction), and sorted.

Title Extraction:
The probable document title is inferred from prominent, central, bold/large text at the top of the first page.

Output Generation:
For every input PDF, produces a {filename}.json in the required format.

Sample Output JSON Format
json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "h1", "text": "Introduction", "page": 1 },
    { "level": "h2", "text": "What is AI?", "page": 2 },
    { "level": "h3", "text": "History of AI", "page": 3 }
  ]
}
Core Algorithmic Techniques
Smart Heuristics: Beyond just font size—headings must pass checks for briefness, lack of sentence punctuation, capitalization/patterns, and positioning.

Pattern Recognition: Regexes for numbered (1., 1.1.), ALL CAPS, "CHAPTER"/"SECTION", and roman numerals.

PDF Images & OCR: pdfplumber is used for scanned-image PDFs, extracting the largest text as likely heading candidates.

Technologies & Dependencies
Language: Python 3.8+

PDF Parsing: PyMuPDF (fitz), pdfplumber

Others: re, json, dataclasses, pathlib

How to Build & Run
Build the Docker Image
text
docker build --platform linux/amd64 -t mysolution-round1a:latest .
Run the Solution
text
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolution-round1a:latest
Place all PDF files into /input. Each PDF will produce a {filename}.json in /output.

Strengths & Innovations
Not Font-size Only: Cross-corroborates headings via position, style, and structure.

Robust to Layout: Successfully extracts structure from academic, report, and textbook PDFs—even with mixed fonts and layouts.

Image-Aware: Recovers headings as much as possible from image/scan pages.

Fast: Batch processes all files in a directory, ~1–3 seconds per normal-length PDF.

Limitations & Next Steps
Imperfect for Unstructured/Weird PDFs: Some artistic or non-standard PDFs may still challenge clean heading detection.

Image-Heavy OCR: True OCR is outside scope (per constraints)—future versions might integrate offline Tesseract OCR for full image-based extraction.

References
PyMuPDF documentation

pdfplumber documentation

Appendix: Full Solution Code
(Included in main repo. Key modules shown below for reference.)

Submission Checklist
All dependencies dockerized and run offline

No font-size-only logic

README explains approach and how to run
"""

# Create the PDF
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", 'B', size=14)
pdf.multi_cell(0, 10, title, align="C")
pdf.ln(5)
pdf.set_font("Arial", size=12)
pdf.cell(0, 10, submitted_by, ln=True)
pdf.ln(10)

# Add the main content
pdf.set_font("Arial", size=11)
for line in content.split("\n"):
    line = line.strip()
    if not line:
        continue
    if line in side_headings:
        pdf.set_font("Arial", 'B', size=11)
    else:
        pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, line)

# Save the file
output_path = "/mnt/data/Connecting_the_Dots_Challenge_Round1A_Final.pdf"
pdf.output(output_path)
output_path