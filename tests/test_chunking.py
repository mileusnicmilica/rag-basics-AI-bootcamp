import pytest

from src.chunking import build_chunks, split_text_with_overlap
from src.corpus import Document, load_default_corpus
from src.rag import build_grounded_answer


def test_split_text_with_overlap_returns_multiple_chunks() -> None:
    text = "abcdefghijklmnopqrstuvwxyz" * 4
    chunks = split_text_with_overlap(text, chunk_size=30, overlap=10)
    assert len(chunks) >= 3


def test_split_text_with_overlap_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        split_text_with_overlap("abc", chunk_size=10, overlap=10)


def test_split_text_with_overlap_preserves_requested_overlap() -> None:
    chunks = split_text_with_overlap("abcdefghijklmnop", chunk_size=8, overlap=3)
    assert chunks == ["abcdefgh", "fghijklm", "klmnop"]


def test_build_chunks_keeps_source_metadata_and_stable_ids() -> None:
    document = Document(doc_id="source-7", title="Source title", text="abcdefghijklmnop")
    chunks = build_chunks([document], chunk_size=8, overlap=3)
    assert [chunk.chunk_id for chunk in chunks] == [
        "source-7-chunk-0", "source-7-chunk-1", "source-7-chunk-2"
    ]
    assert all(chunk.doc_id == "source-7" and chunk.title == "Source title" for chunk in chunks)


def test_chunk_size_changes_whether_a_complete_answer_can_be_cited() -> None:
    question = "How does metadata help source traceability?"
    documents = load_default_corpus()
    small = build_grounded_answer(question, build_chunks(documents, chunk_size=140, overlap=30))
    large = build_grounded_answer(question, build_chunks(documents, chunk_size=220, overlap=40))
    assert small.refused is True
    assert [item.score for item in small.retrieved] == [0.5, 0.5]
    assert large.refused is False
    assert large.retrieved[0].score == 0.75
    assert "Metadata helps filtering and source traceability." in large.answer
