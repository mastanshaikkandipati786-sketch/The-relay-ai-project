
import json
import re
import math
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "results" / "extracted_papers.json"

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "what", "why", "how", "does", "do", "did",
    "and", "or", "to", "of", "in", "on", "for",
    "with", "by", "from", "it", "this", "that",
    "be", "can", "could", "would", "should",
    "using", "use", "used", "their", "its"
}


def tokenize(text):
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return [word for word in words if word not in STOPWORDS]


def retrieve(question, top_k=3):
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        pages = json.load(file)

    query_words = tokenize(question)

    if not query_words:
        return []

    documents = [
        tokenize(page.get("text", ""))
        for page in pages
    ]

    total_documents = len(documents)

    if total_documents == 0:
        return []

    document_lengths = [len(doc) for doc in documents]
    average_length = sum(document_lengths) / total_documents

    document_frequency = Counter()

    for doc in documents:
        for word in set(doc):
            document_frequency[word] += 1

    k1 = 1.5
    b = 0.75

    results = []

    for index, page in enumerate(pages):
        words = documents[index]
        word_counts = Counter(words)
        doc_length = document_lengths[index]

        score = 0.0

        for word in query_words:
            frequency = word_counts[word]

            if frequency == 0:
                continue

            df = document_frequency[word]

            idf = math.log(
                1 + (total_documents - df + 0.5) / (df + 0.5)
            )

            denominator = frequency + k1 * (
                1 - b + b * doc_length / max(average_length, 1)
            )

            score += idf * (
                frequency * (k1 + 1) / denominator
            )

        # Give extra importance to matching words in the paper title.
        title_words = tokenize(page.get("paper_title", ""))

        title_matches = set(query_words) & set(title_words)
        score += len(title_matches) * 2.0

        # Give a small bonus when the exact question phrase appears.
        original_text = page.get("text", "").lower()
        clean_question = question.lower().strip()

        if clean_question and clean_question in original_text:
            score += 3.0

        if score > 0:
            results.append({
                "score": round(score, 3),
                "paper_title": page["paper_title"],
                "arxiv_id": page["arxiv_id"],
                "version": page["version"],
                "page_number": page["page_number"],
                "text": page["text"][:1200]
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]


if __name__ == "__main__":
    question = "How does scaled dot-product attention work using queries keys and values?"

    matches = retrieve(question, top_k=3)

    print("Question:", question)
    print("\nTop relevant pages:")

    for result in matches:
        print("\n------------------------------")
        print("Paper:", result["paper_title"])
        print("arXiv:", result["arxiv_id"], result["version"])
        print("Page:", result["page_number"])
        print("Score:", result["score"])
        print("Text:", result["text"][:400])
