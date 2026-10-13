"""End-to-end checks of the Streamlit interface over the existing RAG logic."""

from pathlib import Path
import json
from types import SimpleNamespace

from streamlit.testing.v1 import AppTest

from src.book_source import BOOK_TITLE, PROFILE


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_supported_question_uses_selected_profile_and_shows_cited_chunk() -> None:
    app = AppTest.from_file(APP_PATH).run()
    app.selectbox(key="profile").set_value("training-rag").run()
    app.chat_input[0].set_value("Why are citations important in RAG?").run()

    assert not app.exception
    assert len(app.chat_message) == 2
    assert app.session_state.history[0]["profile"] == "training-rag"
    assert any("Citations improve transparency and trust" in item.value for item in app.markdown)
    assert any(
        "tr-doc-1-chunk-1" in item.value and "ocena:" in item.value
        for item in app.markdown
    )


def test_unsupported_question_shows_refusal_without_references() -> None:
    app = AppTest.from_file(APP_PATH).run()
    app.chat_input[0].set_value("Who won the world cup in 1958?").run()

    assert not app.exception
    assert len(app.chat_message) == 2
    assert any("Odbijeno" in item.value for item in app.markdown)
    assert any("Reference: Nema" in item.value for item in app.markdown)
    assert any("Pretraga nije pronašla nijedan segment." in item.value for item in app.info)


def test_invalid_overlap_prevents_question_from_running() -> None:
    app = AppTest.from_file(APP_PATH).run()
    app.number_input(key="overlap").set_value(140).run()

    assert not app.exception
    assert any("Preklop mora biti manji" in item.value for item in app.error)
    assert app.chat_input[0].disabled
    assert app.session_state.history == []


def test_history_keeps_original_settings_and_can_be_cleared() -> None:
    app = AppTest.from_file(APP_PATH).run()
    app.chat_input[0].set_value("What is retrieval augmented generation?").run()
    app.selectbox(key="profile").set_value("training-rag").run()
    app.chat_input[0].set_value("Why are citations important in RAG?").run()

    assert not app.exception
    assert len(app.chat_message) == 4
    assert [entry["profile"] for entry in app.session_state.history] == ["default", "training-rag"]
    assert any("Profil: default" in item.value for item in app.caption)

    app.button(key="clear_history").click().run()
    assert app.session_state.history == []
    assert not app.chat_message


def test_gemini_mode_without_key_disables_question_input(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    app = AppTest.from_file(APP_PATH).run()
    app.selectbox(key="answer_mode").set_value("Gemini").run()

    assert not app.exception
    assert app.chat_input[0].disabled
    assert any("GEMINI_API_KEY" in item.value for item in app.info)


def test_missing_book_profile_shows_download_action(tmp_path, monkeypatch) -> None:
    from src import book_source

    monkeypatch.setattr(book_source, "BOOK_PATH", tmp_path / "missing.txt")
    app = AppTest.from_file(APP_PATH).run()
    app.selectbox(key="profile").set_value(PROFILE).run()

    assert not app.exception
    assert app.button(key="download_book").label == "Preuzmi knjigu"
    assert app.chat_input[0].disabled
    assert any(BOOK_TITLE in item.value for item in app.info)


def test_download_button_makes_book_available_without_app_restart(tmp_path, monkeypatch) -> None:
    from src import book_source

    sample = """*** START OF THE PROJECT GUTENBERG EBOOK TEST ***
THE BRAIN AND THE VOICE IN SPEECH AND SONG

THE BRAIN AND THE VOICE IN SPEECH AND SONG

An introduction.

THEORIES ON THE ORIGIN OF SPEECH

Speech begins with a verified passage.
*** END OF THE PROJECT GUTENBERG EBOOK TEST ***
"""
    path = tmp_path / "book.txt"
    monkeypatch.setattr(book_source, "BOOK_PATH", path)

    def fake_download():
        path.write_text(sample, encoding="utf-8")
        return path

    monkeypatch.setattr(book_source, "download_book", fake_download)
    app = AppTest.from_file(APP_PATH).run()
    app.selectbox(key="profile").set_value(PROFILE).run()
    app.button(key="download_book").click().run()

    assert not app.exception
    assert path.is_file()
    assert not app.chat_input[0].disabled


def test_book_profile_uses_section_chunks_and_shows_historical_notice(tmp_path, monkeypatch) -> None:
    from src import book_source

    sample = """*** START OF THE PROJECT GUTENBERG EBOOK TEST ***
THE BRAIN AND THE VOICE IN SPEECH AND SONG
CONTENTS
THEORIES ON THE ORIGIN OF SPEECH

THE BRAIN AND THE VOICE IN SPEECH AND SONG

The book begins with an introduction about the voice.

THEORIES ON THE ORIGIN OF SPEECH

All musical sounds can be distinguished by three qualities: Loudness, pitch, and quality.
*** END OF THE PROJECT GUTENBERG EBOOK TEST ***
"""
    monkeypatch.setattr(book_source, "BOOK_PATH", tmp_path / "book.txt")
    book_source.BOOK_PATH.write_text(sample, encoding="utf-8")
    app = AppTest.from_file(APP_PATH).run()
    app.selectbox(key="profile").set_value(PROFILE).run()
    app.chat_input[0].set_value("What are the three qualities of musical sounds?").run()

    assert not app.exception
    assert app.session_state.history[0]["profile"] == PROFILE
    assert "pg13111-section-01-chunk-0" in app.session_state.history[0]["result"].citations
    assert any("istorijska knjiga iz 1910" in item.value for item in app.info)


def test_gemini_app_mode_calls_model_only_after_question_submit(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    calls = []

    class Models:
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                text=json.dumps(
                    {
                        "answer": "Retrieval augmented generation combines retrieval with text generation.",
                        "refused": False,
                        "citations": [
                            {
                                "chunk_id": "doc-1-chunk-0",
                                "quote": "Retrieval augmented generation combines retrieval with text generation.",
                            }
                        ],
                    }
                )
            )

    class Client:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.models = Models()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr("src.gemini_answer.genai.Client", Client)
    app = AppTest.from_file(APP_PATH).run()
    assert calls == []
    app.selectbox(key="answer_mode").set_value("Gemini").run()
    assert calls == []
    app.chat_input[0].set_value("What is retrieval augmented generation?").run()

    assert not app.exception
    assert len(calls) == 1
    assert calls[0]["model"] == "gemini-3.1-flash-lite"
    assert app.session_state.history[0]["answer_mode"] == "Gemini"
    assert app.session_state.history[0]["result"].citations == ["doc-1-chunk-0"]
