import sys

from src.cli import main


def test_cli_shows_the_same_retrieved_chunk_as_answer_citation(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["rag-cli", "--question", "What is retrieval augmented generation?"])
    main()
    output = capsys.readouterr().out
    assert "Retrieved chunks:" in output
    assert "score=1.000" in output
    assert "Based on the provided corpus:" in output
    assert "References:\n- [doc-1-chunk-0]" in output
    assert output.count("[doc-1-chunk-0]") == 3
