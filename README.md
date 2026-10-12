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

## Corpus profiles

- `default`: compact baseline corpus for Week 6 fundamentals.
- `training-rag`: profile mirroring examples with focus on citations, references, and LLM-as-a-judge framing.

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
entailment; the small built-in corpus and exact English word matching limit what
it can answer.

The CLI prints the retrieval trace, answer, refusal status, and references. The
same retrieval results are used for the trace and answer, so a cited ID can be
checked against the displayed chunks.

## Submission evidence

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

## Recommended evidence template (`evidence.md`)

Use this exact structure for easy review:

1. **Outcome 1: Chunking impact**
  - Config A:
  - Config B:
  - Retrieval difference summary:
2. **Outcome 2: Top-k retrieval**
  - Query:
  - Top-k output:
  - Why ranking is correct:
3. **Outcome 3: Citation quality**
  - Supported query:
  - Answer with citations:
  - Retrieved chunk IDs:
4. **Outcome 4: Refusal behavior**
  - Unsupported query:
  - Retrieved context:
  - Refusal output:
5. **Outcome 5: Final evidence pair**
  - Supported case command + output
  - Unsupported case command + output

Use `docs/homework-checklist.md` as submission guidance.
