# Week 6 RAG Homework Starter

This starter app helps students practice Week 6 concepts from the RAG lecture:

- corpus preparation
- chunking with overlap
- simple retrieval
- answer generation with citations
- refusal behavior when evidence is missing

## Learning goals

By the end of this homework, a student pair should be able to:

1. Explain how chunking strategy affects retrieval quality.
2. Implement a retrieval pipeline that returns top-k relevant chunks.
3. Return answers with explicit citations to source chunks.
4. Refuse unsupported questions instead of hallucinating.
5. Show evidence for one supported and one unsupported question.

## Project structure

```text
rag-week-6-homework-starter/
  src/
    corpus.py
    chunking.py
    retrieval.py
    rag.py
    cli.py
  tests/
    test_chunking.py
    test_corpus.py
    test_retrieval.py
    test_rag.py
    test_cli.py
  docs/
    homework-checklist.md
    plan-rada.md
    pair-report.md
  scripts/
    run_tests.sh
  evidence.md
  requirements.txt
```

## Setup

Use a new virtual environment for your operating system. The starter may contain an
old `.venv` created on another computer; it is not portable.

Windows PowerShell:

```powershell
python -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-win\Scripts\python.exe -m pytest -q
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

## Run tests

```bash
./scripts/run_tests.sh
```

On Windows, use `.\.venv-win\Scripts\python.exe -m pytest -q`.

## Run demo CLI

```bash
python -m src.cli --question "What is retrieval augmented generation?"
python -m src.cli --question "Who won the world cup in 1958?"
python -m src.cli --corpus-profile training-rag --question "Why are citations important in RAG?"
```

## Run the local web app

Install the dependencies as shown in Setup, then start Streamlit from the project root:

```powershell
.\.venv-win\Scripts\python.exe -m streamlit run app.py --server.address localhost
```

On macOS/Linux, use `python -m streamlit run app.py --server.address localhost`
from the activated virtual environment. Open the local address printed by
Streamlit in your browser. You only need the terminal to start or stop the server;
enter questions in the browser.

The sidebar lets you choose the corpus profile, chunk size, overlap, answer mode,
and number of retrieved chunks (`top-k`). The app shows the answer or refusal,
references, and expandable retrieved chunks with their scores and source IDs.
Each question is independent, and the displayed history lasts only for the
current browser session. Use **Obriši istoriju** to clear it.

Available corpora are `default`, `training-rag`, and the optional
`Mott — Gutenberg 13111` book profile. The built-in corpus is defined in
`src/corpus.py`.

Choose **Mott — Gutenberg 13111** to use the book corpus. On first use, select
**Preuzmi knjigu**; the UTF-8 source and its download metadata are saved under
`data/`, which is excluded from Git. This profile uses paragraph and sentence
chunks. The book was published in 1910 and may contain outdated science; its
answers are not current medical guidance.

Choose **Gemini** (`gemini-3.1-flash-lite`) to generate an answer from retrieved
passages. After you submit a question, the question and passages are sent to
Google, and usage may count against your API quota. The app checks that each
Gemini citation points to a retrieved chunk and that its exact
evidence quote appears in that chunk. If citation validation fails, the app
refuses the answer. This checks citation identity and quote presence; it cannot
prove every paraphrase is fully entailed, so review the displayed passages.

Set a Gemini API key in the terminal before starting the app. Create a key in
[Google AI Studio](https://aistudio.google.com/app/apikey), then in PowerShell:

```powershell
$env:GEMINI_API_KEY = "your-api-key"
.\.venv-win\Scripts\python.exe -m streamlit run app.py --server.address localhost
```

On macOS/Linux, use `export GEMINI_API_KEY="your-api-key"` before the Streamlit
command. Never commit the key to Git. Without a key, **Extractive** mode remains
available and Gemini mode is disabled.

## Corpus profiles

- `default`: compact baseline corpus for Week 6 fundamentals.
- `training-rag`: profile mirroring examples with focus on citations, references, and LLM-as-a-judge framing.
- `mott-13111`: optional Project Gutenberg book corpus; download it from Streamlit before using it in the CLI.

## How this starter decides what to answer

`src/chunking.py` splits each document into character-length chunks with overlap and
keeps a source document ID and a chunk ID. Character boundaries can cut a word or
sentence. The comparison in `evidence.md` shows why chunk size matters.

`src/retrieval.py` removes common English question words, then scores each chunk by
the fraction of **distinct informative query terms** it contains. For example, a
chunk matching three of four terms scores `0.750`. Results with zero score are
discarded; remaining results are sorted by descending score. Ties keep their
original corpus order, and `top_k` limits the number returned.

`src/rag.py` checks whether chunks from the same retrieved document cover enough
query terms (at least 60%, and at least two terms for a multi-term question). It
quotes a complete sentence from a retrieved chunk and cites that chunk ID. For a
"why" question, a matching causal sentence is preferred. When this check cannot
find a complete supported sentence, the system refuses and gives no references.
This is a conservative lexical demonstration, not a general guarantee of factual
entailment; exact English word matching limits what it can answer, and the
`default` profile is intentionally small.

For the Mott book profile, paragraph/sentence chunks are checked independently
so matches from distant passages cannot combine to satisfy the support check.
Gemini mode receives only the top retrieved chunks and validates the cited IDs
and exact evidence quotes before displaying an answer.

The CLI prints the retrieval trace, answer, refusal status, and references. The
same retrieval results are used for the trace and answer, so a cited ID can be
checked against the displayed chunks.

## Submission evidence

The Mott corpus retrieval comparison and 20-question manual test set are
recorded in `docs/book-evaluation.md`. The implementation scope
and joint approval record are in `docs/gutenberg-book-rag-upgrade-plan.md`.

- `evidence.md` contains the five required outcomes, commands, outputs, and a test snapshot.
- `docs/homework-checklist.md` tracks completed requirements.
- `docs/pair-report.md` separates proposed responsibilities, recorded contributions,
  and the reported review of the final bundle. The demo lead is recorded there.

## Homework tasks for students

1. **Outcome 1 (chunking impact):** tune chunking parameters in `src/chunking.py` and compare retrieval quality for the same query.
2. **Outcome 2 (top-k retrieval):** verify `src/retrieval.py` returns correctly ordered top-k relevant chunks.
3. **Outcome 3 (citations):** ensure `src/rag.py` returns grounded answers with explicit citations to chunk IDs.
4. **Outcome 4 (refusal):** ensure unsupported questions trigger refusal instead of hallucinated answers.
5. **Outcome 5 (evidence):** document one supported and one unsupported query with full retrieval and output evidence.

## Evidence summary

The complete commands and outputs are in [`evidence.md`](evidence.md). The
recorded examples cover all five outcomes:

1. **Chunking impact:** `chunk_size=140, overlap=30` splits the traceability
   sentence; `chunk_size=220, overlap=40` keeps it together and supports an
   answer to “How does metadata help source traceability?”
2. **Top-k retrieval:** the query “How do citations and references improve
   trust?” is shown with `top_k=2` and `top_k=3`, including scores and ranking.
3. **Citation quality:** “Why are citations important in RAG?” is answered with
   the retrieved source `tr-doc-1-chunk-1`.
4. **Refusal:** “Who won the world cup in 1958?” is refused because the default
   corpus has no supporting result.
5. **Final evidence pair:** `evidence.md` includes reproducible CLI commands
   and outputs for a supported and an unsupported question.

Use `docs/homework-checklist.md` as submission guidance.
