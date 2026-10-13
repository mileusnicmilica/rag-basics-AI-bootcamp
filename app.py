"""Local Streamlit interface for extractive and optional Gemini RAG."""

import hashlib
import os

import httpx
import streamlit as st
from google.genai import errors as gemini_errors

from src import book_source
from src.book_chunking import build_book_chunks
from src.chunking import build_chunks
from src.corpus import list_corpus_profiles, load_corpus
from src.gemini_answer import MODEL_ID, generate_grounded_answer
from src.rag import build_grounded_answer


@st.cache_data(show_spinner=False)
def prepare_chunks(profile: str, chunk_size: int, overlap: int, book_checksum: str):
    documents = load_corpus(profile)
    if profile == book_source.PROFILE:
        return build_book_chunks(documents, chunk_size=chunk_size, overlap=overlap)
    return build_chunks(documents, chunk_size=chunk_size, overlap=overlap)


st.set_page_config(page_title="RAG demo", page_icon="📚")
st.title("RAG demo")
st.caption(
    "Postavite pitanje nad izabranim engleskim korpusom. Izaberite odgovor iz izvora "
    "ili Gemini odgovor zasnovan na pronađenim odlomcima."
)

with st.sidebar:
    st.header("Podešavanja")
    profile = st.selectbox(
        "Profil korpusa",
        list_corpus_profiles(),
        format_func=lambda item: "Mott — Gutenberg 13111" if item == book_source.PROFILE else item,
        key="profile",
    )
    if st.session_state.get("previous_profile") != profile:
        st.session_state["chunk_size"] = 900 if profile == book_source.PROFILE else 140
        st.session_state["overlap"] = 150 if profile == book_source.PROFILE else 30
        st.session_state["top_k"] = 4 if profile == book_source.PROFILE else 2
        st.session_state["previous_profile"] = profile
    chunk_size = st.number_input("Veličina segmenta", min_value=1, step=10, key="chunk_size")
    overlap = st.number_input("Preklop", min_value=0, step=5, key="overlap")
    top_k = st.number_input("Broj rezultata (top-k)", min_value=1, step=1, key="top_k")
    answer_mode = st.selectbox("Način odgovaranja", ["Extractive", "Gemini"], key="answer_mode")
    invalid_settings = overlap >= chunk_size
    if invalid_settings:
        st.error("Preklop mora biti manji od veličine segmenta.")
    book_available = book_source.book_is_available()
    if profile == book_source.PROFILE and not book_available:
        st.info(
            f"{book_source.BOOK_TITLE} još nije preuzeta. "
            f"[Otvori stranicu Project Gutenberg]({book_source.BOOK_URL})."
        )
        if st.button("Preuzmi knjigu", key="download_book"):
            try:
                book_source.download_book()
            except (OSError, ValueError, UnicodeError) as exc:
                st.error(f"Preuzimanje nije uspelo: {exc}")
            else:
                st.rerun()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if answer_mode == "Gemini" and not gemini_key:
        st.info("Za Gemini odgovor podesite GEMINI_API_KEY pre pokretanja aplikacije.")
    elif answer_mode == "Gemini":
        st.caption(f"Model: {MODEL_ID}")
    clear_history = st.button("Obriši istoriju", key="clear_history")

if profile == book_source.PROFILE:
    st.info(
        "Ovo je istorijska knjiga iz 1910. godine. Može sadržati zastarele naučne "
        "i medicinske tvrdnje; odgovori nisu savremeni medicinski savet. "
        f"[Izvor]({book_source.BOOK_URL}) · "
        "[Uslovi korišćenja](https://www.gutenberg.org/policy/license.html)"
    )
if answer_mode == "Gemini":
    st.caption(
        "Gemini režim šalje pitanje i pronađene odlomke Google Gemini API-ju. "
        "Poziv se izvršava tek kada pošaljete pitanje i može koristiti kvotu vašeg API naloga."
    )

if "history" not in st.session_state:
    st.session_state.history = []
if clear_history:
    st.session_state.history = []

st.caption("Svako pitanje se obrađuje nezavisno; prethodna pitanja nisu kontekst za novi odgovor.")
input_disabled = (
    invalid_settings
    or (profile == book_source.PROFILE and not book_available)
    or (answer_mode == "Gemini" and not gemini_key)
)
prompt = st.chat_input("Unesite pitanje", disabled=input_disabled)
if prompt and prompt.strip() and not input_disabled:
    question = prompt.strip()
    checksum = (
        hashlib.sha256(book_source.BOOK_PATH.read_bytes()).hexdigest()
        if profile == book_source.PROFILE
        else ""
    )
    chunks = prepare_chunks(profile, chunk_size, overlap, checksum)
    try:
        with st.spinner("Pretražujem korpus..."):
            result = (
                generate_grounded_answer(question, chunks, top_k=top_k, api_key=gemini_key)
                if answer_mode == "Gemini"
                else build_grounded_answer(
                    question,
                    chunks,
                    top_k=top_k,
                    support_scope="chunk" if profile == book_source.PROFILE else "document",
                )
            )
    except (ValueError, gemini_errors.APIError, httpx.HTTPError, OSError) as exc:
        st.error(f"Odgovor nije dostupan: {exc}")
    else:
        st.session_state.history.append(
            {
                "question": question,
                "profile": profile,
                "chunk_size": chunk_size,
                "overlap": overlap,
                "top_k": top_k,
                "answer_mode": answer_mode,
                "model_id": MODEL_ID if answer_mode == "Gemini" else None,
                "result": result,
            }
        )

for entry in st.session_state.history:
    with st.chat_message("user"):
        st.write(entry["question"])

    with st.chat_message("assistant"):
        result = entry["result"]
        st.write(result.answer)
        st.write(f"Status: {'Odbijeno' if result.refused else 'Odgovoreno'}")
        st.write("Reference: " + (", ".join(result.citations) if result.citations else "Nema"))
        st.caption(
            f"Profil: {entry['profile']} · Veličina segmenta: {entry['chunk_size']} · "
            f"Preklop: {entry['overlap']} · Top-k: {entry['top_k']} · "
            f"Odgovor: {entry['answer_mode']}"
        )
        with st.expander(f"Pronađeni segmenti ({len(result.retrieved)})"):
            if not result.retrieved:
                st.info("Pretraga nije pronašla nijedan segment.")
            for index, item in enumerate(result.retrieved, start=1):
                st.write(
                    f"{index}. {item.chunk.title} [{item.chunk.chunk_id}] "
                    f"— ocena: {item.score:.3f}"
                )
                st.write(item.chunk.text)
                if item.chunk.source_url:
                    st.markdown(f"[Izvor]({item.chunk.source_url})")
