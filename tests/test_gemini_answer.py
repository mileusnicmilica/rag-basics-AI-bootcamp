import json
from types import SimpleNamespace

import pytest

from src.chunking import Chunk
from src.gemini_answer import generate_grounded_answer


def _client_mock(monkeypatch, response_payload, captured=None):
    class Models:
        def generate_content(self, **kwargs):
            if captured is not None:
                captured.update(kwargs)
            return SimpleNamespace(text=json.dumps(response_payload))

    class Client:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.models = Models()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr("src.gemini_answer.genai.Client", Client)


def test_gemini_uses_only_retrieved_passages_and_validates_quote(monkeypatch) -> None:
    chunk = Chunk("source-1", "doc-1", "Section 1", "Musical sounds have loudness, pitch, and quality.")
    captured = {}
    _client_mock(
        monkeypatch,
        {
            "answer": "The qualities are loudness, pitch, and quality.",
            "refused": False,
            "citations": [{"chunk_id": "source-1", "quote": "loudness, pitch, and quality"}],
        },
        captured,
    )

    result = generate_grounded_answer(
        "What are the qualities of musical sounds?", [chunk], api_key="test-key"
    )

    assert result.refused is False
    assert result.citations == ["source-1"]
    assert "[source-1]" in result.answer
    request = json.loads(captured["contents"])
    assert request["question"] == "What are the qualities of musical sounds?"
    assert [passage["chunk_id"] for passage in request["passages"]] == ["source-1"]
    assert captured["config"].response_mime_type == "application/json"
    assert captured["config"].max_output_tokens == 512


def test_gemini_refuses_invalid_or_unretrieved_citations(monkeypatch) -> None:
    chunk = Chunk("source-1", "doc-1", "Section 1", "Musical sounds have loudness, pitch, and quality.")
    _client_mock(
        monkeypatch,
        {
            "answer": "An unsupported answer.",
            "refused": False,
            "citations": [{"chunk_id": "not-retrieved", "quote": "made up evidence"}],
        },
    )

    result = generate_grounded_answer("What are musical qualities?", [chunk], api_key="test-key")

    assert result.refused is True
    assert result.citations == []


def test_gemini_refusal_is_returned_without_citations(monkeypatch) -> None:
    chunk = Chunk("source-1", "doc-1", "Section 1", "Musical sounds have loudness and pitch.")
    _client_mock(monkeypatch, {"answer": "", "refused": True, "citations": []})

    result = generate_grounded_answer("What won the world cup?", [chunk], api_key="test-key")

    assert result.refused is True
    assert result.citations == []


def test_gemini_is_not_called_when_retrieval_has_no_evidence(monkeypatch) -> None:
    def unexpected_call(**kwargs):
        pytest.fail("Gemini should not be called without matching passages")

    monkeypatch.setattr("src.gemini_answer.genai.Client", unexpected_call)
    chunk = Chunk("source-1", "doc-1", "Section 1", "Musical sounds have loudness and pitch.")

    result = generate_grounded_answer("Who won the world cup in 1958?", [chunk], api_key="test-key")

    assert result.refused is True
    assert result.citations == []


def test_gemini_is_not_called_for_a_weak_partial_match(monkeypatch) -> None:
    def unexpected_call(**kwargs):
        pytest.fail("Gemini should not be called for a weak partial match")

    monkeypatch.setattr("src.gemini_answer.genai.Client", unexpected_call)
    chunk = Chunk("source-1", "doc-1", "Section 1", "The world is round.")

    result = generate_grounded_answer(
        "Who won the world cup in 1958?", [chunk], api_key="test-key"
    )

    assert result.refused is True
    assert result.retrieved[0].score == 0.25


def test_gemini_requires_an_api_key() -> None:
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        generate_grounded_answer("question", [], api_key="")
