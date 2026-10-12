from dataclasses import dataclass
import re

from .chunking import Chunk
from .retrieval import RetrievalResult, informative_tokens, lexical_score, retrieve_top_k, tokenize


REFUSAL_MESSAGE = "I do not have enough grounded evidence in the provided corpus to answer that question."


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    citations: list[str]
    refused: bool
    retrieved: list[RetrievalResult]


def _supported_by(question: str, chunk_text: str) -> bool:
    """Require most query terms, and at least two for a multi-term question."""
    terms = informative_tokens(question)
    if not terms:
        return False
    matched = terms.intersection(tokenize(chunk_text))
    minimum_matches = 1 if len(terms) == 1 else 2
    return len(matched) >= minimum_matches and len(matched) / len(terms) >= 0.6


def _sentence_score(question: str, sentence: str) -> float:
    score = lexical_score(question, sentence)
    asks_why = question.strip().lower().startswith("why")
    has_causal_word = re.search(r"\b(because|improves?|helps?|reduces?)\b", sentence, re.I)
    if score > 0 and asks_why and has_causal_word:
        score += 0.4
    return score


def _best_complete_sentence(question: str, chunk_text: str) -> tuple[str, float] | None:
    sentences = re.split(r"(?<=[.!?])\s+", chunk_text)
    complete = []
    for sentence in sentences:
        candidate = sentence.strip()
        if candidate and candidate[0].isupper() and candidate.endswith((".", "!", "?")):
            complete.append(candidate)
    if not complete:
        return None

    best = max(complete, key=lambda sentence: _sentence_score(question, sentence))
    score = _sentence_score(question, best)
    return (best, score) if score > 0 else None


def build_grounded_answer(question: str, chunks: list[Chunk], top_k: int = 2) -> RagAnswer:
    results = retrieve_top_k(question, chunks, k=top_k)
    # Combine only chunks from the same source document when checking support.
    for item in results:
        same_document = [result for result in results if result.chunk.doc_id == item.chunk.doc_id]
        combined_text = " ".join(result.chunk.text for result in same_document)
        if not _supported_by(question, combined_text):
            continue

        candidates = []
        for result in same_document:
            best = _best_complete_sentence(question, result.chunk.text)
            if best is not None:
                sentence, score = best
                candidates.append((sentence, score, result.chunk.chunk_id))
        if candidates:
            sentence, _, citation = max(candidates, key=lambda candidate: candidate[1])
            return RagAnswer(
                answer=f"Based on the provided corpus: {sentence} [{citation}]",
                citations=[citation],
                refused=False,
                retrieved=results,
            )

    return RagAnswer(answer=REFUSAL_MESSAGE, citations=[], refused=True, retrieved=results)
