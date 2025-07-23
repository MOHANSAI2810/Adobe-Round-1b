import fitz  # PyMuPDF
import os
import re
import json
from sentence_transformers import SentenceTransformer, util
from datetime import datetime


def could_be_heading(text):
    if not text.strip() or len(text.strip()) < 3:
        return False
    if len(text.split()) > 12:
        return False
    if text.isupper() and len(text.strip()) > 3:
        return True
    if re.match(r'^(\d+(\.\d+)*\.?|[A-Z]\.|[IVX]+\.)\s+\S+', text):
        return True
    if re.match(r'^(CHAPTER|SECTION|ARTICLE|PART|APPENDIX|TABLE OF CONTENTS)\b', text.strip(), re.I):
        return True
    if len(text.split()) >= 2 and all(word[0].isupper() for word in text.split() if word[0].isalpha()):
        return True
    return False


def is_heading(text):
    # Same heuristic for subsection extraction stops
    return could_be_heading(text)


def extract_headings_from_pdfs(pdf_folder):
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    output = {}

    for pdf_file in pdf_files:
        doc = fitz.open(os.path.join(pdf_folder, pdf_file))
        headings = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("blocks")
            for block in blocks:
                text = block[4].strip()
                if could_be_heading(text):
                    headings.append({
                        "page": page_num + 1,
                        "heading": text
                    })
        output[pdf_file] = headings
    return output


def extract_subsection_text(pdf_path, heading_text, page_number):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number - 1)

    blocks = page.get_text("blocks")
    blocks = sorted(blocks, key=lambda b: b[1])  # Sort by vertical position

    heading_block_idx = None
    for i, block in enumerate(blocks):
        block_text = block[4].strip()
        if block_text == heading_text:
            heading_block_idx = i
            break

    if heading_block_idx is None:
        # Heading not found exactly; return empty subsection
        return ""

    subsection_texts = []
    for j in range(heading_block_idx + 1, len(blocks)):
        block_text = blocks[j][4].strip()
        if is_heading(block_text):
            break
        subsection_texts.append(block_text)

    # Join paragraphs, remove all \n, normalize spaces
    cleaned = " ".join(subsection_texts).replace('\n', ' ').strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


def semantic_search_headings(all_headings, query, top_k=5, threshold=0.3):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    heading_texts = [h[2] for h in all_headings]
    heading_embs = model.encode(heading_texts, convert_to_tensor=True, show_progress_bar=False)
    query_emb = model.encode(query, convert_to_tensor=True)
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
    return ranked_results


def main(pdf_folder, persona, job_to_be_done):
    # Step 1: Extract headings from all PDFs
    headings_data = extract_headings_from_pdfs(pdf_folder)

    # Flatten for semantic search
    all_headings = []
    for pdf, entries in headings_data.items():
        for h in entries:
            all_headings.append((pdf, h['page'], h['heading']))

    # Step 2: Semantic search to get matched headings using job_to_be_done as query
    matched_headings = semantic_search_headings(all_headings, job_to_be_done)

    # Step 3: Extract subsections under matched headings
    for entry in matched_headings:
        pdf_file = entry["pdf_file"]
        heading = entry["heading"]
        page_num = entry["page_number"]
        pdf_path = os.path.join(pdf_folder, pdf_file)
        subsection = extract_subsection_text(pdf_path, heading, page_num)
        entry["subsection_text"] = subsection

    # Step 4: Construct output JSON per requested format

    # Metadata
    documents_list = sorted(list({entry["pdf_file"] for entry in matched_headings}))
    metadata = {
        "input_documents": sorted(os.listdir(pdf_folder)),
        "persona": persona,
        "job_to_be_done": job_to_be_done,
        "processing_timestamp": datetime.utcnow().isoformat()
    }

    # extracted_sections
    extracted_sections = []
    for entry in matched_headings:
        extracted_sections.append({
            "document": entry["pdf_file"],
            "section_title": entry["heading"],
            "importance_rank": entry["importance_rank"],
            "page_number": entry["page_number"]
        })

    # subsection_analysis
    subsection_analysis = []
    for entry in matched_headings:
        subsection_analysis.append({
            "document": entry["pdf_file"],
            "refined_text": entry["subsection_text"],
            "page_number": entry["page_number"]
        })

    final_output = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    # Save output
    output_path = "final_output.json"
    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(final_output, f_out, ensure_ascii=False, indent=4)

    print(f"Process complete. Output saved to '{output_path}'.")


if __name__ == "__main__":
    # Example dynamic inputs - replace with your logic / UI input as needed
    pdf_folder = "pdfs"  # folder containing your PDFs
    persona = "HR professional"
    job_to_be_done = "Create and manage fillable forms for onboarding and compliance."
    
    main(pdf_folder, persona, job_to_be_done)
