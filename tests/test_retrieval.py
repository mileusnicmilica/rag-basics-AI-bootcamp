from src.chunking import Chunk
import pytest

from src.retrieval import lexical_score, retrieve_top_k


def test_retrieve_top_k_orders_by_score_desc() -> None:
    chunks = [
        Chunk(chunk_id="a", doc_id="1", title="A", text="rag retrieval citations evidence"),
        Chunk(chunk_id="b", doc_id="1", title="B", text="weather forecast rain tomorrow"),
    ]
    results = retrieve_top_k("rag citations", chunks, k=2)
    assert results
    assert results[0].chunk.chunk_id == "a"


def test_retrieve_top_k_returns_empty_for_unrelated_query() -> None:
    chunks = [
        Chunk(chunk_id="a", doc_id="1", title="A", text="vector database retrieval"),
    ]
    results = retrieve_top_k("basketball playoffs", chunks, k=2)
    assert results == []


def test_common_question_words_do_not_create_false_matches() -> None:
    chunk = Chunk(chunk_id="a", doc_id="1", title="A", text="The model is in the corpus.")
    assert lexical_score("Who was in the world cup in 1958?", chunk.text) == 0
    assert retrieve_top_k("Who was in the world cup in 1958?", [chunk]) == []


def test_score_counts_distinct_query_terms_and_ranks_by_coverage() -> None:
    assert lexical_score("rag citations", "rag rag rag") == 0.5
    assert lexical_score("rag citations", "rag citations") == 1.0


def test_top_k_preserves_corpus_order_on_ties_and_limits_result_count() -> None:
    chunks = [
        Chunk(chunk_id="first", doc_id="1", title="A", text="rag"),
        Chunk(chunk_id="second", doc_id="2", title="B", text="rag"),
        Chunk(chunk_id="third", doc_id="3", title="C", text="rag citations"),
    ]
    assert [result.chunk.chunk_id for result in retrieve_top_k("rag citations", chunks, k=2)] == [
        "third", "first"
    ]
    assert [result.chunk.chunk_id for result in retrieve_top_k("rag citations", chunks, k=3)] == [
        "third", "first", "second"
    ]


def test_retrieval_rejects_invalid_limits() -> None:
    with pytest.raises(ValueError):
        retrieve_top_k("rag", [], k=0)
    with pytest.raises(ValueError):
        retrieve_top_k("rag", [], min_score=-0.1)
