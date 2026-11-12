from pypdf import PdfReader
import json
from pathlib import Path

import json
from pathlib import Path
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
PAPERS_DIR = BASE_DIR / "papers"
OUTPUT_FILE = BASE_DIR / "results" / "extracted_papers.json"

PAPERS = {
    "attention.pdf": {
        "title": "Attention Is All You Need",
        "arxiv_id": "1706.03762",
        "version": "v7"
    },
    "moshi.pdf": {
        "title": "Moshi: a speech-text foundation model for real-time dialogue",
        "arxiv_id": "2410.00037",
        "version": "v1"
    },
    "dynamic_chunking.pdf": {
        "title": "Dynamic Chunking for End-to-End Hierarchical Sequence Modeling",
        "arxiv_id": "2507.07955",
        "version": "v2"
    }
}

all_pages = []

for filename, info in PAPERS.items():
    pdf_path = PAPERS_DIR / filename

    if not pdf_path.exists():
        print(f"ERROR: Missing file: {filename}")
        continue

    print(f"\nReading: {info['title']}")

    reader = PdfReader(str(pdf_path))

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        all_pages.append({
            "paper_title": info["title"],
            "arxiv_id": info["arxiv_id"],
            "version": info["version"],
            "page_number": page_number,
            "text": page_text
        })

    print(f"Pages extracted: {len(reader.pages)}")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(all_pages, file, ensure_ascii=False, indent=2)

print("\nExtraction completed!")
print(f"Total pages extracted: {len(all_pages)}")
print(f"Saved to: {OUTPUT_FILE}")
