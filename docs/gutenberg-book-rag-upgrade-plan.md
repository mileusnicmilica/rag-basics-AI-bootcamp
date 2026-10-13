# Optional upgrade plan: Project Gutenberg book corpus

**Status:** Implemented and jointly reviewed by Milica and Nemanja. Nemanja confirmed their review and approval in chat on 13 October 2026.

## Goal and current baseline

Add *The Brain and the Voice in Speech and Song* by F. W. Mott (Project Gutenberg eBook 13111) as a third corpus choice in the existing Streamlit demo. Preserve the two small teaching corpora and the current CLI behavior. Make the book searchable with traceable citations and add a selectable Gemini answer mode alongside the existing extractive mode. The first release remains local; Gemini mode calls Google's API only for a submitted question with retrieved context and a configured API key.

The current code holds short texts in `src/corpus.py`, splits by character count in `src/chunking.py`, ranks chunks by exact word overlap in `src/retrieval.py`, selects a source sentence or refuses in `src/rag.py`, and exposes profiles in `app.py` and `src/cli.py`. The book is much longer, so blindly treating it as one document with the current 140-character chunks and document-wide support check would make retrieval and citations weak.

## Source and format decision

**Recommended input: Gutenberg's UTF-8 plain text** at https://www.gutenberg.org/cache/epub/13111/pg13111.txt, linked from the [eBook page](https://www.gutenberg.org/ebooks/13111). It is directly readable by Python, has no HTML tags to strip, and includes section headings and figure descriptions. Keep the original download intact for provenance; index only the book text between Gutenberg's START and END markers. Exclude its license, table of contents, and repetitive front matter from search results, while keeping the full original file and a visible link to Gutenberg's terms.

The HTML edition is useful later if we decide to show original illustrations or need its document structure. EPUB and PDF add parsing work without helping the first text-only search. Plain text contains descriptions and references to figures, but not the diagrams themselves; the app must not claim to answer questions requiring visual inspection of a figure.

Gutenberg marks this eBook **public domain in the USA** and says users outside the USA should check local law. Before publishing the raw book or transformed excerpts with the public repository or a hosted app, both reviewers will check the applicable rights and Gutenberg terms. The proposed default is to keep the downloaded book in a git-ignored local `data/` directory and offer an explicit **Download book** action in the app. The source link, attribution, and license link remain visible in the app. This is a distribution decision, not a claim that local use or any later publication has already been cleared.

## Scope and implementation sequence

### 1. Acquire and prepare the source

- Add one download/validation helper for the official UTF-8 text. The app offers a one-time download button when the book is absent; a network failure leaves the two built-in profiles usable and gives a clear retry message.
- Save the unchanged raw file locally, together with source URL, retrieval date, and SHA-256 checksum. Do not fetch on every question. Use a small checked-in test fixture so automated tests never depend on Gutenberg being online.
- Parse only text between the Gutenberg markers. Separate real book sections using verified headings rather than assuming every all-caps line is a heading. Skip the table of contents and license. Preserve the section name and source URL in the derived data.
- Verify section boundaries and a sample of extracted passages manually against the original text. In particular, check figure captions, footnotes, and headings that might be mistaken for body text.

### 2. Build the book index and citations

- Extend the corpus profile list with a readable `mott-13111` choice. Represent sections as separate source documents, with stable section IDs. Preserve current `default` and `training-rag` data and outputs.
- For the book, chunk on paragraph or sentence boundaries with modest overlap so a claim is not cut mid-sentence. Compare at least two chunk sizes on the same book questions and record the results before choosing defaults. Keep the existing character-chunking path available for the homework examples.
- Give each book chunk a stable ID plus section title and source link. Display these in Streamlit with its score and full retrieved text. The answer must cite an actual displayed chunk; do not present a page number because the plain-text edition has no stable pages.
- Cache parsed sections and chunks by source checksum and chunk settings so Streamlit reruns do not rebuild the book index unnecessarily. Measure cold and repeated-question time on the local machine.

### 3. Check answer and retrieval quality

- Run the current lexical retriever as a baseline. With a book corpus, require answer support in the cited passage or a tightly adjacent passage; matching terms spread across distant sections of the same book must not count as support.
- Build a small, human-checked evaluation set from actual passages: at least six answerable and four unanswerable or near-miss questions. Record expected section/chunk evidence, retrieval rank, answer or refusal, and whether the cited text supports the answer. Do not invent expected facts from memory.
- Use those results to decide whether the initial book release needs stronger lexical ranking (for example BM25) or better query normalization. Make one measured change at a time and compare it with the baseline. Embeddings and a vector database remain possible later stages, each requiring a separate decision on dependency, cost, privacy, and evaluation.

### 4. Add Gemini grounded-answer mode

- Use Google's maintained `google-genai` Python SDK and a stable Flash model (`gemini-3.1-flash-lite` initially). Keep the model identifier in one place so it can be changed after compatibility and cost review.
- Read `GEMINI_API_KEY` from the local process environment. Never put a key in source, tests, screenshots, or Git. The app shows setup guidance if Gemini is selected without a key; extractive mode remains usable.
- Send the question and only the top retrieved passages to Gemini, each labeled with its chunk ID and section. Instruct the model to use only those passages, treat them as untrusted data, refuse unsupported claims, and return structured answer/citation data. Do not send the entire book or chat history.
- Validate the response locally: cited IDs must occur in the retrieved set, and evidence quotes must match the cited passage. A missing or malformed response, API failure, or unsupported answer must not become an uncited factual claim. Show a clear error for an API failure and a refusal for insufficient evidence.
- Citation-ID and exact-quote checks do not guarantee every model paraphrase is entailed; reviewers inspect the displayed source passages and evaluation examples.
- Clearly label which mode produced each answer. Gemini calls may consume quota or incur charges under the user's Google account; document this and do not call the API on page load, during download, or in automated tests.

### 5. Streamlit, CLI, documentation, and tests

- Add the book to the Streamlit corpus selector and add an answer-mode selector. If the book is missing, show the Gutenberg title/source and a **Download book** button; after download, permit questions without restarting the app. When another profile is selected, keep the existing chat behavior. Label each history entry with its selected profile, settings, and answer mode.
- Keep the CLI usable for both existing profiles. If the book profile is selected without the local file, show a useful setup message. Document the download and launch workflow in `README.md` without changing the original Week 6 evidence as though it had used the book.
- Add focused tests for parsing and section IDs, chunk boundaries and metadata, supported and unsupported book questions, source/citation alignment, missing-file behavior, Streamlit profile switching, missing API key, and mocked Gemini responses including invalid citations and API errors. Run the entire current test suite. Do not rely on a live network call or API key in CI.
- Show a short note in the app that the book was published in 1910 and may contain outdated scientific or medical ideas; answers report what this historical source says and are not current medical guidance.

## Proposed ownership and review

Ownership below assigns coordination and first-pass verification, not a claim about who personally writes each line. AI-assisted edits must be recorded accurately if used. Both people inspect the final source, tests, user interface, example answers, and documentation before acceptance.

| Work package | Proposed lead | Other person's review |
| --- | --- | --- |
| Source format, Gutenberg provenance/terms, download workflow, text cleaning, section-boundary examples | Milica | Nemanja checks source integrity, exclusions, metadata, and distribution decision |
| Book chunking, retrieval baseline, answer-support rule, stable citations, performance | Nemanja | Milica checks retrieved passages against the original book and reviews false matches/refusals |
| Gemini integration, key handling, grounded prompt, response validation and mocked tests | Nemanja | Milica reviews the exact passages sent to Gemini, answer/refusal examples, UI labeling, and key instructions |
| Streamlit selector, missing-book experience, historical-source notice, README and demo flow | Milica | Nemanja checks that UI results match the underlying RAG return values |
| Automated tests, evaluation questions and comparison table | Nemanja coordinates tests; Milica coordinates source-grounded examples | Both independently rerun and review every result |
| Final repository review and release decision | Both | Each records their own approval; neither approval is inferred from the other's report |

The demo lead can be agreed during review; the prior Week 6 role assignment does not automatically decide this extension.

## Acceptance criteria and approval gates

1. Existing profiles, CLI examples, and tests still work. The new book profile can be selected in Streamlit and loaded through its explicit download flow.
2. Book search returns readable passages with stable section/chunk IDs and source attribution. Neither Gutenberg license text nor the table of contents appears as an answer source.
3. At least six supported and four unsupported/near-miss evaluation cases are recorded and jointly checked against the source. Every accepted answer has a citation in the displayed retrieval set; unsupported cases do not fabricate citations.
4. The evaluated chunk settings and retrieval behavior are documented, including observed failures and any measured improvement. The app does not rebuild or redownload the unchanged book per question.
5. Rights and attribution decisions are recorded before distributing book text or hosting the app. The historical-source notice is visible.
6. Gemini mode sends only retrieved passages, produces validated citations or refusal, never runs without a key, and shows API errors without fabricated answers. Tests cover the Gemini contract without making paid or credentialed calls.
7. Both reviewers inspect all changed code, tests, documentation, and demonstration outputs and explicitly approve the completed extension.

### Approval and implementation status

- [x] Milica approves this plan. Date / evidence: 13 October 2026; joint approval reported by Nemanja in chat.
- [x] Nemanja requested implementation with Gemini on 13 October 2026 (recorded from this chat).

Implementation was authorized by Nemanja, and joint plan approval was later reported by Nemanja. This approval record reflects that report; it is not a direct message from Milica in this chat.

Implementation snapshot (13 October 2026): the local Gutenberg plain-text source is downloaded to the ignored `data/` directory and parses into 14 section documents. Book chunks use a 900-character target with 150-character overlap at paragraph/sentence boundaries. Streamlit has book download and selection controls, extractive and Gemini modes, a missing-key state, and a historical-source notice. Gemini uses the pinned `google-genai` SDK with `gemini-3.1-flash-lite`, sends only retrieved passages, and validates citation IDs and exact quotes. The full automated test suite reports `44 passed`. The app was smoke-tested locally at `http://localhost:8501`. No API key was configured in the implementation environment, so that run did not make a live Gemini request; Gemini behavior is covered by mocked responses. The pair later confirmed joint review and approval in chat on 13 October 2026; this record does not claim that the automated tests included a live API call.

### Final acceptance after implementation

- [x] Milica reviewed the final implementation and approves it. Date / evidence: 13 October 2026; joint review and approval reported by Nemanja in chat.
- [x] Nemanja reviewed the final implementation and approves it. Date / evidence: 13 October 2026; confirmed by Nemanja in chat.

## Sources

- [Project Gutenberg eBook 13111: metadata and download formats](https://www.gutenberg.org/ebooks/13111)
- [Official UTF-8 plain text, including provenance and license](https://www.gutenberg.org/cache/epub/13111/pg13111.txt)
- [Gemini API getting started and API-key setup](https://ai.google.dev/gemini-api/docs/get-started)
- [Stable Gemini 3.1 Flash-Lite model](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite)
