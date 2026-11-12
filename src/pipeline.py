
import os
import time
from dotenv import load_dotenv
from groq import Groq
from retrieval import retrieve
from verifier import verify_answer

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Groq API key not found. Check your .env file.")

client = Groq(api_key=api_key)


def answer_question(question):
    print("\nSearching research papers...")

    passages = retrieve(question, top_k=3)

    if not passages:
        print("No relevant passages found.")
        return

    context = ""

    for item in passages:
        context += (
            f"\nPaper: {item['paper_title']}\n"
            f"arXiv: {item['arxiv_id']} {item['version']}\n"
            f"PDF page: {item['page_number']}\n"
            f"Text: {item['text']}\n"
        )

    print("Retrieved", len(passages), "passages.")
    print("Sending passages to Groq...")

    start = time.perf_counter()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer using only the supplied research passages. "
                    "Use simple English and no more than 150 words. "
                    "Explain important steps clearly. "
                    "Cite the paper title, arXiv version, and PDF page. "
                    "If the passages do not support an answer, say so."
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

    end = time.perf_counter()

    answer = response.choices[0].message.content

    print("\nANSWER:")

    if answer and answer.strip():
        print(answer)
    else:
        print("The model returned an empty answer.")

    # Run the preliminary answer verifier.
    verification = verify_answer(answer, passages)

    print("\nVERIFICATION:")
    print("Passage word overlap:", verification.get("support_ratio", 0))
    print("Retrieved paper check:", verification["correct_paper"])
    print("Result:", verification["result"])

    print("\nREQUEST DETAILS:")
    print("Latency:", round((end - start) * 1000, 2), "ms")
    print("Input tokens:", response.usage.prompt_tokens)
    print("Output tokens:", response.usage.completion_tokens)
    print("Total tokens:", response.usage.total_tokens)


if __name__ == "__main__":
    question = input("Ask a question about the research papers: ")
    answer_question(question)
