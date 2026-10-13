"""Passage chunks for the larger Gutenberg book corpus."""

import re

from .chunking import Chunk
from .corpus import Document


def split_book_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    units = []
    for paragraph in re.split(r"\n\s*\n", text):
        cleaned = " ".join(paragraph.split())
        if not cleaned:
            continue
        if len(cleaned) <= chunk_size:
            units.append(cleaned)
        else:
            units.extend(
                sentence.strip()
                for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z"(])', cleaned)
                if sentence.strip()
            )

    chunks: list[str] = []
    current: list[str] = []
    for unit in units:
        if current and len(" ".join(current + [unit])) > chunk_size:
            chunks.append(" ".join(current))
            carried: list[str] = []
            for previous in reversed(current):
                candidate = [previous] + carried
                if len(" ".join(candidate)) > overlap:
                    break
                carried = candidate
            current = carried if len(" ".join(carried + [unit])) <= chunk_size else []
        current.append(unit)
    if current:
        chunks.append(" ".join(current))
    return chunks


def build_book_chunks(
    documents: list[Document], chunk_size: int = 900, overlap: int = 150
) -> list[Chunk]:
    chunks = []
    for document in documents:
        for index, text in enumerate(split_book_text(document.text, chunk_size, overlap)):
            chunks.append(
                Chunk(
                    chunk_id=f"{document.doc_id}-chunk-{index}",
                    doc_id=document.doc_id,
                    title=document.title,
                    text=text,
                    source_url=document.source_url,
                )
            )
    return chunks
