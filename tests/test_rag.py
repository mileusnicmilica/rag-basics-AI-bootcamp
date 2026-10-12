from src.chunking import Chunk, build_chunks
from src.corpus import load_default_corpus, load_training_rag_corpus
from src.rag import build_grounded_answer


def test_build_grounded_answer_returns_citations_for_supported_query() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=120, overlap=20)
    result = build_grounded_answer("What is retrieval augmented generation?", chunks, top_k=2)
    assert result.refused is False
    assert len(result.citations) >= 1
    assert all(citation in [item.chunk.chunk_id for item in result.retrieved] for citation in result.citations)
    assert f"[{result.citations[0]}]" in result.answer


def test_build_grounded_answer_refuses_unsupported_query() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=120, overlap=20)
    result = build_grounded_answer("Who was emperor of Mars?", chunks, top_k=2)
    assert result.refused is True
    assert result.citations == []


def test_world_cup_question_is_refused_without_false_citations() -> None:
    chunks = build_chunks(load_default_corpus())
    result = build_grounded_answer("Who won the world cup in 1958?", chunks)
    assert result.refused is True
    assert result.retrieved == []
    assert result.citations == []


def test_unsupported_fact_with_one_topic_match_is_refused() -> None:
    chunks = build_chunks(load_training_rag_corpus())
    result = build_grounded_answer("What is the capital of RAG?", chunks)
    assert result.refused is True
    assert result.citations == []


def test_why_question_uses_complete_causal_sentence_from_retrieved_chunk() -> None:
    chunks = build_chunks(load_training_rag_corpus())
    result = build_grounded_answer("Why are citations important in RAG?", chunks)
    assert result.refused is False
    assert "because users can verify evidence" in result.answer
    assert result.citations == ["tr-doc-1-chunk-1"]
    assert result.citations[0] in [item.chunk.chunk_id for item in result.retrieved]
    cited_chunk = next(item.chunk for item in result.retrieved if item.chunk.chunk_id == result.citations[0])
    assert "Citations improve transparency and trust because users can verify evidence." in cited_chunk.text


def test_sentence_fragment_is_not_presented_as_an_answer() -> None:
    chunk = Chunk(
        chunk_id="fragment", doc_id="source", title="Source",
        text="helps filtering and source traceability.",
    )
    result = build_grounded_answer("What helps source traceability?", [chunk])
    assert result.refused is True
    assert result.citations == []
