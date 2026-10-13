"""End-to-end checks of the Streamlit interface over the existing RAG logic."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


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
