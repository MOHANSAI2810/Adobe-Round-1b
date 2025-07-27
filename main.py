import fitz  # PyMuPDF
import os
import re
import json
import unicodedata
import logging
import sys
from sentence_transformers import SentenceTransformer, util
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load SentenceTransformer model once globally
MODEL = SentenceTransformer('all-MiniLM-L6-v2')


def normalize_text(text):
    """Normalize unicode, remove excessive whitespace."""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def could_be_heading(text):
    text = text.strip()
    if not text or len(text) < 3:
        return False
    if len(text.split()) > 12:
        return False
    # Uppercase heuristic
    if text.isupper() and len(text) > 3:
        return True
    # Common chapter/section patterns
    if re.match(r'^(\d+(\.\d+)*\.?|[A-Z]\.|[IVX]+\.)\s+\S+', text):
        return True
    if re.match(r'^(CHAPTER|SECTION|ARTICLE|PART|APPENDIX|TABLE OF CONTENTS)\b', text, re.I):
        return True
    # Title casing heuristic: all words start with uppercase letter (where applicable)
    words = text.split()
    if len(words) >= 2 and all(w[0].isupper() for w in words if w[0].isalpha()):
        return True
    return False


def is_heading(text):
    return could_be_heading(text)


def extract_headings(pdf_folder, pdf_files_list):
    """
    Extract headings only from the specified list of PDFs in pdf_files_list.
    """
    output = {}

    for pdf_file in pdf_files_list:
        if not pdf_file.lower().endswith('.pdf'):
            pdf_file += '.pdf'  # normalize extension if missing
        doc_path = os.path.join(pdf_folder, pdf_file)
        if not os.path.isfile(doc_path):
            logging.warning(f"File '{pdf_file}' not found in folder '{pdf_folder}', skipping.")
            continue

        logging.info(f"Extracting headings from: {pdf_file}")
        doc = fitz.open(doc_path)
        headings = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]

            # Compute average font size on page for thresholding (optional)
            font_sizes = []
            for block in blocks:
                if block['type'] == 0:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_sizes.append(span["size"])
            avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0

            for block in blocks:
                if block['type'] == 0:  # text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            font_size = span["size"]
                            text_norm = normalize_text(text)

                            # Heading heuristic: font size larger/equal than avg or fixed threshold + regex checks
                            if text and font_size >= max(11, avg_font_size) and could_be_heading(text_norm):
                                headings.append({
                                    "page": page_num ,
                                    "heading": text_norm,
                                    "font_size": font_size
                                })
                                logging.debug(f"Heading found: '{text_norm}' on page {page_num } (font size {font_size})")

        # Sort headings by page number and font size descending
        headings = sorted(headings, key=lambda x: (x["page"], -x["font_size"]))
        # Deduplicate headings on same page with same text
        unique_headings = []
        seen = set()
        for h in headings:
            key = (h["page"], h["heading"])
            if key not in seen:
                unique_headings.append(h)
                seen.add(key)

        output[pdf_file] = unique_headings

    return output


def clean_text(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_subsection(pdf_path, heading_text, page_number):
    logging.info(f"Extracting subsection under heading '{heading_text}' in {os.path.basename(pdf_path)} page {page_number}")
    doc = fitz.open(pdf_path)
    collected_text = []
    started = False

    for page_num in range(page_number - 1, len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: b[1])  # Sort vertically by y0

        if not started:
            heading_block_idx = None
            for i, block in enumerate(blocks):
                block_text = normalize_text(block[4].strip())
                if block_text == heading_text:
                    heading_block_idx = i
                    break
            if heading_block_idx is None:
                continue
            started = True
            start_idx = heading_block_idx + 1
        else:
            start_idx = 0

        for i in range(start_idx, len(blocks)):
            block_text = normalize_text(blocks[i][4].strip())
            if is_heading(block_text):
                # Assume next heading implies end of current subsection
                return clean_text(" ".join(collected_text))
            collected_text.append(block_text)

    return clean_text(" ".join(collected_text))  # End of doc reached


def semantic_headings(all_headings, query, top_k=5, threshold=0.3):
    logging.info(f"Performing semantic search for query: '{query}'")
    heading_texts = [h[2] for h in all_headings]
    heading_embs = MODEL.encode(heading_texts, convert_to_tensor=True, show_progress_bar=False)
    query_emb = MODEL.encode(query, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(query_emb, heading_embs)[0]

    topk = min(top_k, len(all_headings))
    matches = [(float(scores[idx]), all_headings[idx]) for idx in scores.argsort(descending=True)[:topk]]
    filtered = [entry for entry in matches if entry[0] > threshold]

    ranked_results = []
    for rank, (score, info) in enumerate(filtered, start=1):
        pdf_file, page_num, heading_text = info
        ranked_results.append({
            "pdf_file": pdf_file,
            "heading": heading_text,
            "page_number": page_num,
            "similarity_score": round(score, 4),
            "importance_rank": rank
        })

    logging.info(f"Semantic search found {len(ranked_results)} relevant headings above threshold.")
    return ranked_results


def main(pdf_folder, persona, job_to_be_done, input_documents):
    # Step 1: Extract headings from the specified PDFs
    pdf_filenames = [doc["filename"] for doc in input_documents]
    headings_data = extract_headings(pdf_folder, pdf_filenames)

    # Flatten for semantic search: list of tuples (pdf_file, page_num, heading_text)
    all_headings = []
    for pdf, entries in headings_data.items():
        for h in entries:
            all_headings.append((pdf, h['page'], h['heading']))

    if not all_headings:
        logging.warning("No headings extracted from specified PDF files.")
        return

    # Step 2: Semantic search to get matched headings using the "job_to_be_done" as query
    matched_headings = semantic_headings(all_headings, job_to_be_done)

    if not matched_headings:
        logging.info("No matched headings found above threshold for the given query.")
    else:
        # Step 3: Extract subsections under matched headings
        for entry in matched_headings:
            pdf_file = entry["pdf_file"]
            heading = entry["heading"]
            page_num = entry["page_number"]
            pdf_path = os.path.join(pdf_folder, pdf_file)
            subsection = extract_subsection(pdf_path, heading, page_num)
            entry["subsection_text"] = subsection

    # Step 4: Construct output JSON per requested format
    metadata = {
        "input_documents": pdf_filenames,
        "persona": persona,
        "job_to_be_done": job_to_be_done,
        "processing_timestamp": datetime.utcnow().isoformat() + "Z"
    }

    extracted_sections = []
    for entry in matched_headings:
        extracted_sections.append({
            "document": entry["pdf_file"],
            "section_title": entry["heading"],
            "importance_rank": entry["importance_rank"],
            "page_number": entry["page_number"]
        })

    subsection_analysis = []
    for entry in matched_headings:
        subsection_analysis.append({
            "document": entry["pdf_file"],
            "refined_text": entry.get("subsection_text", ""),
            "page_number": entry["page_number"]
        })

    final_output = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    output_path = "output/output.json"
    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(final_output, f_out, ensure_ascii=False, indent=4)

    logging.info(f"Process complete. Output saved to '{output_path}'.")


def load_input_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    # Automatically load the input.json file from the "input" folder
    input_json_path = os.path.join("input", "input.json")
    
    if not os.path.isfile(input_json_path):
        print(f"Input JSON file not found at path: {input_json_path}")
        sys.exit(1)
    
    input_data = load_input_json(input_json_path)

    # pdf_folder is same as input folder where PDFs are present
    pdf_folder = "input"

    persona = input_data.get("persona", {}).get("role", "Unknown Persona")
    job_to_be_done = input_data.get("job_to_be_done", {}).get("task", "")
    documents = input_data.get("documents", [])

    main(pdf_folder, persona, job_to_be_done, documents)
