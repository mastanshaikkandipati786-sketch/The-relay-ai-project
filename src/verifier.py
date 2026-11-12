
import re


def verify_answer(answer, passages, expected_paper=None):
    """
    Checks whether an answer has supporting retrieved passages
    and whether it mentions the expected research paper.
    """

    if not answer or not answer.strip():
        return {
            "supported": False,
            "correct_paper": False,
            "result": "Empty answer"
        }

    if not passages:
        return {
            "supported": False,
            "correct_paper": False,
            "result": "No research passages retrieved"
        }

    answer_lower = answer.lower()

    # Check whether the expected paper was retrieved.
    retrieved_papers = {
        str(item.get("arxiv_id", ""))
        for item in passages
    }

    correct_paper = (
        expected_paper is None
        or expected_paper in retrieved_papers
    )

    # Check whether the answer contains words found
    # in the retrieved research passages.
    passage_text = " ".join(
        item.get("text", "").lower()
        for item in passages
    )

    answer_words = set(
        re.findall(r"\b[a-zA-Z]{4,}\b", answer_lower)
    )

    passage_words = set(
        re.findall(r"\b[a-zA-Z]{4,}\b", passage_text)
    )

    common_words = answer_words.intersection(passage_words)

    support_ratio = (
        len(common_words) / len(answer_words)
        if answer_words else 0
    )

    supported = support_ratio >= 0.20

    return {
        "supported": supported,
        "correct_paper": correct_paper,
        "support_ratio": round(support_ratio, 3),
        "result": (
            "Checks passed"
            if supported and correct_paper
            else "Manual review needed"
        )
    }
