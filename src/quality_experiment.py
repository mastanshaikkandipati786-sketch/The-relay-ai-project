import os
import sys
import csv
import time
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from retrieval import retrieve

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "tests"))

from test_questions import QUESTIONS

load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Groq API key not found in .env")

client = Groq(api_key=api_key, timeout=60.0, max_retries=0)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT, "results")

CSV_FILE = os.path.join(RESULTS_DIR, "results.csv")
ANSWERS_FILE = os.path.join(RESULTS_DIR, "quality_answers.txt")

os.makedirs(RESULTS_DIR, exist_ok=True)

with open(ANSWERS_FILE, "w", encoding="utf-8") as answer_file:

    for number, item in enumerate(QUESTIONS, start=1):

        question = item["question"]

        print(f"\n{'=' * 60}")
        print(f"Question {number}/16: {question}")

        passages = retrieve(question, top_k=3)

        context = ""

        for passage in passages:
            context += (
                f"\nPaper: {passage['paper_title']}\n"
                f"arXiv: {passage['arxiv_id']} "
                f"{passage['version']}\n"
                f"PDF page: {passage['page_number']}\n"
                f"Text: {passage['text']}\n"
            )

        start_time = time.perf_counter()
        timestamp = datetime.now().astimezone().isoformat()

        status = "ok"
        answer = ""
        tokens_in = ""
        tokens_out = ""

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Answer using only the supplied research "
                            "passages. Use simple English. Keep the "
                            "answer under 150 words. Cite paper title, "
                            "arXiv version, and PDF page. If the "
                            "passages do not support the answer, "
                            "clearly say that the papers do not "
                            "provide enough information."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Question: {question}\n\n"
                            f"Research passages:\n{context}"
                        )
                    }
                ],
                max_completion_tokens=1000,
                reasoning_effort="low"
            )

            answer = response.choices[0].message.content or ""
            tokens_in = response.usage.prompt_tokens
            tokens_out = response.usage.completion_tokens

            if not answer.strip():
                answer = "[Empty answer]"

        except Exception as error:
            status = "error"
            answer = f"REQUEST ERROR: {type(error).__name__}: {error}"

        total_ms = round(
            (time.perf_counter() - start_time) * 1000, 2
        )

        print("\nANSWER:")
        print(answer)
        print("\nStatus:", status)
        print("Latency:", total_ms, "ms")
        print("Input tokens:", tokens_in)
        print("Output tokens:", tokens_out)

        answer_file.write(
            f"\nQUESTION {number}: {question}\n"
            f"EXPECTED PAPER: {item['expected_paper']}\n"
            f"ANSWERABLE: {item['answerable']}\n"
            f"RETRIEVED PASSAGES:\n{context}\n"
            f"ANSWER:\n{answer}\n"
            f"STATUS: {status}\n"
            f"{'-' * 60}\n"
        )
        answer_file.flush()

        with open(CSV_FILE, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)

            writer.writerow([
                f"quality-{number:02d}",
                "answer_quality",
                "real",
                timestamp,
                "",
                total_ms,
                status,
                0,
                tokens_in,
                tokens_out,
                "BM25_top3",
                ""
            ])

print("\nQUALITY EXPERIMENT FINISHED.")
print("Answers saved to:", ANSWERS_FILE)
print("Raw measurements saved to:", CSV_FILE)
