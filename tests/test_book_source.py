from pathlib import Path
import hashlib
import json
from io import BytesIO

import pytest

from src.book_chunking import build_book_chunks, split_book_text
from src.book_source import download_book, load_book_corpus, parse_book_text
from src.corpus import Document


def test_parser_keeps_body_sections_and_excludes_contents_index_and_license() -> None:
    text = """*** START OF THE PROJECT GUTENBERG EBOOK TEST ***
THE BRAIN AND THE VOICE IN SPEECH AND SONG
CONTENTS
THEORIES ON THE ORIGIN OF SPEECH

THE BRAIN AND THE VOICE IN SPEECH AND SONG

An introductory passage about the instrument.

THEORIES ON THE ORIGIN OF SPEECH

Speech begins with a verified passage.

INDEX
Index-only words about speech.
*** END OF THE PROJECT GUTENBERG EBOOK TEST ***
START OF FULL LICENSE
License-only words.
"""

    documents = parse_book_text(text)

    assert [document.doc_id for document in documents] == ["pg13111-section-00", "pg13111-section-01"]
    assert "introductory passage" in documents[0].text
    assert "verified passage" in documents[1].text
    assert all("Index-only" not in document.text for document in documents)
    assert all("License-only" not in document.text for document in documents)
    assert all(document.source_url for document in documents)


def test_parser_rejects_text_without_gutenberg_markers() -> None:
    with pytest.raises(ValueError, match="markers"):
        parse_book_text("Not a Gutenberg eBook")


def test_book_chunks_keep_sentence_boundaries_ids_and_source_metadata() -> None:
    document = Document(
        doc_id="book-section-1",
        title="Book — Section 1",
        text="First sentence is complete. Second sentence is also complete. Third sentence finishes it.",
        source_url="https://example.test/book",
    )

    chunks = build_book_chunks([document], chunk_size=72, overlap=40)

    assert len(chunks) == 2
    assert chunks[0].text == "First sentence is complete. Second sentence is also complete."
    assert chunks[1].text == "Second sentence is also complete. Third sentence finishes it."
    assert [chunk.chunk_id for chunk in chunks] == ["book-section-1-chunk-0", "book-section-1-chunk-1"]
    assert all(chunk.source_url == document.source_url for chunk in chunks)


def test_book_chunker_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError, match="overlap"):
        split_book_text("A sentence.", chunk_size=10, overlap=10)


def test_missing_book_file_has_actionable_message(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Download eBook"):
        load_book_corpus(tmp_path / "missing.txt")


def test_download_saves_original_text_and_provenance_metadata(tmp_path, monkeypatch) -> None:
    text = """*** START OF THE PROJECT GUTENBERG EBOOK TEST ***
THE BRAIN AND THE VOICE IN SPEECH AND SONG

THE BRAIN AND THE VOICE IN SPEECH AND SONG

An introduction.

THEORIES ON THE ORIGIN OF SPEECH

Speech passage.
*** END OF THE PROJECT GUTENBERG EBOOK TEST ***
"""
    raw = text.encode("utf-8")

    def fake_urlopen(request, timeout):
        assert timeout == 30
        return BytesIO(raw)

    monkeypatch.setattr("src.book_source.urlopen", fake_urlopen)
    destination = tmp_path / "pg13111.txt"
    result = download_book(destination)
    metadata = json.loads(destination.with_suffix(".json").read_text(encoding="utf-8"))

    assert result == destination
    assert destination.read_bytes() == raw
    assert metadata["sha256"] == hashlib.sha256(raw).hexdigest()
    assert metadata["source_url"].endswith("pg13111.txt")
    assert metadata["retrieved_at_utc"]
