"""Local Streamlit interface for the existing RAG demonstration."""

import streamlit as st

from src.chunking import build_chunks
from src.corpus import list_corpus_profiles, load_corpus
from src.rag import build_grounded_answer


st.set_page_config(page_title="RAG demo", page_icon="📚")
st.title("RAG demo")
st.caption(
    "Pitajte mali ugrađeni engleski korpus. Pretraga je leksička, a odgovor je "
    "izdvojena rečenica iz izvora; ova aplikacija ne poziva LLM."
)

with st.sidebar:
    st.header("Podešavanja")
    profile = st.selectbox("Profil korpusa", list_corpus_profiles(), key="profile")
    chunk_size = st.number_input("Veličina segmenta", min_value=1, value=140, step=10, key="chunk_size")
    overlap = st.number_input("Preklop", min_value=0, value=30, step=5, key="overlap")
    top_k = st.number_input("Broj rezultata (top-k)", min_value=1, value=2, step=1, key="top_k")
    invalid_settings = overlap >= chunk_size
    if invalid_settings:
        st.error("Preklop mora biti manji od veličine segmenta.")
    clear_history = st.button("Obriši istoriju", key="clear_history")

if "history" not in st.session_state:
    st.session_state.history = []
if clear_history:
    st.session_state.history = []

st.caption("Svako pitanje se obrađuje nezavisno; prethodna pitanja nisu kontekst za novi odgovor.")
prompt = st.chat_input("Unesite pitanje na engleskom", disabled=invalid_settings)
if prompt and prompt.strip() and not invalid_settings:
    question = prompt.strip()
    documents = load_corpus(profile)
    chunks = build_chunks(documents, chunk_size=chunk_size, overlap=overlap)
    result = build_grounded_answer(question, chunks, top_k=top_k)
    st.session_state.history.append(
        {
            "question": question,
            "profile": profile,
            "chunk_size": chunk_size,
            "overlap": overlap,
            "top_k": top_k,
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
            f"Preklop: {entry['overlap']} · Top-k: {entry['top_k']}"
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
