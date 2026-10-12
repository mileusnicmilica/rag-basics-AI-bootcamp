# Week 6 RAG homework evidence

Environment used for these runs: Windows PowerShell, Python 3.11.7, `pytest==8.3.3`.
Run commands from the project root after installing `requirements.txt`. The examples
use the bundled corpus only; no external source or model is involved.

## 1. Outcome 1: Chunking impact

**Question used for both configurations:** `How does metadata help source traceability?`
Both runs use the `default` corpus and `top_k=2`. The CLI passes these
parameters to `src.chunking.build_chunks`.

**Config A:** `chunk_size=140`, `overlap=30`

```powershell
.\.venv-win\Scripts\python.exe -m src.cli --question "How does metadata help source traceability?" --chunk-size 140 --overlap 30 --top-k 2
```

```text
Retrieved chunks:
- [doc-2-chunk-0] score=0.500 title=Chunking and Metadata
  Chunking splits documents into smaller parts. Good chunk size and overlap improve retrieval quality. Metadata helps filtering and source tra
- [doc-2-chunk-1] score=0.500 title=Chunking and Metadata
  helps filtering and source traceability.

Answer:
I do not have enough grounded evidence in the provided corpus to answer that question.
Refused: True
References:
None
```

**Config B:** `chunk_size=220`, `overlap=40`

```powershell
.\.venv-win\Scripts\python.exe -m src.cli --question "How does metadata help source traceability?" --chunk-size 220 --overlap 40 --top-k 2
```

```text
Retrieved chunks:
- [doc-2-chunk-0] score=0.750 title=Chunking and Metadata
  Chunking splits documents into smaller parts. Good chunk size and overlap improve retrieval quality. Metadata helps filtering and source traceability.

Answer:
Based on the provided corpus: Metadata helps filtering and source traceability. [doc-2-chunk-0]
Refused: False
References:
- [doc-2-chunk-0]
```

**Retrieval difference summary:** With A, the word `traceability` and its sentence
are split across two character chunks. Each chunk matches only two of the four
distinct informative query terms (`metadata`, `help`, `source`, `traceability`),
so each scores `0.500`. The remaining standalone sentence fragment starts in
lowercase and is not presented as an answer. With B, one chunk contains the full
sentence and matches three terms (`metadata`, `source`, `traceability`), scoring
`0.750`; the system can cite a complete answer. `help` does not match `helps`
because this starter uses exact tokens rather than stemming. This is an observed
gain for this question, not a claim that larger chunks always rank better.

## 2. Outcome 2: Top-k retrieval

**Query:** `How do citations and references improve trust?` on `training-rag`.
The distinct informative terms are `citations`, `references`, `improve`, and
`trust`. The score is matched terms divided by four; common question words are
ignored. Chunks with no matches are excluded. Ties retain corpus order.

**Top-k output, `top_k=2`:**

```powershell
.\.venv-win\Scripts\python.exe -m src.cli --corpus-profile training-rag --question "How do citations and references improve trust?" --top-k 2
```

```text
- [tr-doc-1-chunk-0] score=0.750 title=RAG with Citations
  RAG with citations should retrieve relevant documents with source metadata and include references in the answer. Citations improve transpare
- [tr-doc-1-chunk-1] score=0.750 title=RAG with Citations
  r. Citations improve transparency and trust because users can verify evidence.
```

**Top-k output, `top_k=3`:**

```powershell
.\.venv-win\Scripts\python.exe -m src.cli --corpus-profile training-rag --question "How do citations and references improve trust?" --top-k 3
```

```text
- [tr-doc-1-chunk-0] score=0.750 title=RAG with Citations
  RAG with citations should retrieve relevant documents with source metadata and include references in the answer. Citations improve transpare
- [tr-doc-1-chunk-1] score=0.750 title=RAG with Citations
  r. Citations improve transparency and trust because users can verify evidence.
- [tr-doc-2-chunk-0] score=0.250 title=Structured Citation Output
  A cited answer can include answer text and list of source titles. A common format is an answer body followed by a References section.
```

**Why the ranking is correct:** Each of the first two chunks matches three of
the four terms. The third matches only `references`, so it scores `0.250`.
`top_k=2` returns the first two; `top_k=3` adds the third without changing
the ordering. The first two tie and retain their source order.

## 3. Outcome 3: Citation quality

**Supported query:** `Why are citations important in RAG?` on `training-rag`.

**Retrieved chunk IDs and scores:** `tr-doc-1-chunk-0` (`0.667`) and
`tr-doc-1-chunk-1` (`0.333`). The latter contains the complete causal sentence
used in the answer, even though the first chunk ranks higher.

**Answer with citations:**

```text
Based on the provided corpus: Citations improve transparency and trust because users can verify evidence. [tr-doc-1-chunk-1]

References:
- [tr-doc-1-chunk-1]
```

The cited ID is in the displayed retrieval set. The answer body and separate
reference list are both visible in the CLI output in Outcome 5.

## 4. Outcome 4: Refusal behavior

**Unsupported query:** `Who won the world cup in 1958?` on `default`.

**Retrieved context:** None. After common question words are ignored, the
remaining terms (`won`, `world`, `cup`, `1958`) do not occur in the corpus.

**Refusal output:**

```text
I do not have enough grounded evidence in the provided corpus to answer that question.
Refused: True
References:
None
```

No retrieved passage supports a winner or even covers the event. The system
therefore makes no factual claim and cites no chunk. A regression test also
checks a question with a single misleading topic match (`capital of RAG`).

## 5. Outcome 5: Final evidence pair

### Supported case command + output

```powershell
.\.venv-win\Scripts\python.exe -m src.cli --corpus-profile training-rag --question "Why are citations important in RAG?"
```

```text
Question:
Why are citations important in RAG?

Corpus profile: training-rag
Chunk size: 140
Overlap: 30
Top-k: 2

Retrieved chunks:
- [tr-doc-1-chunk-0] score=0.667 title=RAG with Citations
  RAG with citations should retrieve relevant documents with source metadata and include references in the answer. Citations improve transpare
- [tr-doc-1-chunk-1] score=0.333 title=RAG with Citations
  r. Citations improve transparency and trust because users can verify evidence.

Answer:
Based on the provided corpus: Citations improve transparency and trust because users can verify evidence. [tr-doc-1-chunk-1]

Refused: False
References:
- [tr-doc-1-chunk-1]
```

### Unsupported case command + output

```powershell
.\.venv-win\Scripts\python.exe -m src.cli --question "Who won the world cup in 1958?"
```

```text
Question:
Who won the world cup in 1958?

Corpus profile: default
Chunk size: 140
Overlap: 30
Top-k: 2

Retrieved chunks:
None

Answer:
I do not have enough grounded evidence in the provided corpus to answer that question.

Refused: True
References:
None
```

### Test output snapshot

```powershell
.\.venv-win\Scripts\python.exe -m pytest -q
```

```text
.....................                                                    [100%]
21 passed in 0.17s
```

The CLI examples and test snapshot above were run by the AI assistant during
implementation. The pair's independent review is tracked in `docs/pair-report.md`.
