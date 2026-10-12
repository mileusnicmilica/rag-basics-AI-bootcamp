from dataclasses import dataclass
import re

from .chunking import Chunk


TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")
STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
        "for", "from", "how", "i", "in", "is", "it", "of", "on", "or", "the",
        "this", "to", "was", "were", "what", "when", "where", "which", "who",
        "why", "with",
    }
)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def informative_tokens(text: str) -> set[str]:
    """Return distinct English query terms after common question words are removed."""
    return set(tokenize(text)) - STOPWORDS


@dataclass(frozen=True)
class RetrievalResult:
    chunk: Chunk
    score: float


def lexical_score(query: str, chunk_text: str) -> float:
    """Score a chunk by the fraction of distinct informative query terms it covers."""
    q_tokens = informative_tokens(query)
    c_tokens = tokenize(chunk_text)
    if not q_tokens or not c_tokens:
        return 0.0

    matched = q_tokens.intersection(c_tokens)
    return len(matched) / len(q_tokens)


def retrieve_top_k(query: str, chunks: list[Chunk], k: int = 3, min_score: float = 0.01) -> list[RetrievalResult]:
    if k <= 0:
        raise ValueError("k must be > 0")
    if min_score < 0:
        raise ValueError("min_score must be >= 0")

    scored = [
        RetrievalResult(chunk=chunk, score=lexical_score(query, chunk.text))
        for chunk in chunks
    ]
    filtered = [item for item in scored if item.score > 0 and item.score >= min_score]
    filtered.sort(key=lambda item: item.score, reverse=True)
    return filtered[:k]
