# Retrieval evaluation and manual test set: Mott Gutenberg corpus

**Status:** The original evaluation questions, source passages, and retrieval comparison were checked by Milica and Nemanja. Nemanja confirmed the joint review in chat on 13 October 2026. The 20-question manual test set below was added on 13 October 2026 and smoke-tested with local extractive RAG; it is ready for the pair's next Streamlit/Gemini test run. The Gemini API was not available in the implementation environment, so results below are not a live API benchmark.

## Setup

- Source: Project Gutenberg eBook 13111, UTF-8 plain text. The local source and checksum metadata are under the ignored `data/` directory.
- Retriever: existing exact-token lexical score; only the top chunk is listed here.
- Config A: `chunk_size=600`, `overlap=100`.
- Config B: `chunk_size=900`, `overlap=150`.
- These rows compare retrieval rank and score, not Gemini answer quality. The implementation environment had no `GEMINI_API_KEY`; live Gemini outputs are not included in this automated comparison.

## Supported question candidates

| Question | Expected section | Config A top-1 | Config B top-1 | Initial observation |
| --- | --- | --- | --- | --- |
| What are the three qualities of musical sounds? | The Vocal Instrument | `pg13111-section-02-chunk-1`, 1.00 | `pg13111-section-02-chunk-0`, 1.00 | Correct section under both settings. |
| What are the three parts of the vocal instrument? | The Vocal Instrument | `pg13111-section-02-chunk-10`, 1.00 | `pg13111-section-02-chunk-8`, 1.00 | Correct section under both settings. |
| Where does the voice-box sit? | II. The Reed | `pg13111-section-04-chunk-0`, 0.67 | `pg13111-section-04-chunk-0`, 0.67 | Correct section under both settings. |
| What does the diaphragm do during inspiration? | I. The Bellows | `pg13111-section-03-chunk-13`, 0.67 | `pg13111-section-03-chunk-5`, 0.67 | Correct section under both settings. |
| What are the stages in the evolution of speech? | Theories on the Origin of Speech | `pg13111-section-01-chunk-7`, 0.67 | `pg13111-section-01-chunk-4`, 1.00 | Larger chunk covers more query terms in this example. |
| Which hemisphere is associated with speech in right-handed individuals? | Speech and Right-Handedness; opening discussion in Theories on the Origin of Speech | `pg13111-section-01-chunk-9`, 0.83 | `pg13111-section-01-chunk-5`, 0.83 | Top-1 includes the direct statement; the other relevant section appears in the top four. |

## Unsupported and near-miss question candidates

| Question | Config A top-1 score | Config B top-1 score | Gemini gate (`< 0.50`) |
| --- | ---: | ---: | --- |
| Who won the world cup in 1958? | 0.25 | 0.25 | Refuse before API call. |
| What is the smartphone number in the book? | 0.33 | 0.33 | Refuse before API call. |
| What dosage does Mott recommend for antibiotics? | No result | No result | Refuse before API call. |
| Who was the first person on Mars? | 0.33 | 0.33 | Refuse before API call. |

## Reviewed limitation

The extractive path can choose a misleading sentence when a question needs information combined across two passages. In a local check of the right-hemisphere question, the selected sentence described left-handed people losing speech after right-hemisphere disease. This case was reviewed as a known extractive limitation. For Gemini, test that the model synthesizes only the retrieved evidence and cites an exact quote; the response must still be checked in the running app because the implementation test suite uses mocked API responses.

## Manual question set

Use these questions with the Mott corpus selected. For the first group, check that the retrieved passage supports the answer and that the answer cites it. For the second group, check that the app refuses to answer from this book. A retrieval hit by itself does not count as support.

### Questions about the book (expected to be answerable)

1. What are the three qualities of musical sounds? *(The Vocal Instrument)*
2. What does loudness depend upon? *(The Vocal Instrument)*
3. What does the pitch of musical sounds depend upon? *(The Vocal Instrument)*
4. What three parts make up the vocal instrument? *(The Vocal Instrument)*
5. How does the resonator affect the quality or timbre of the voice? *(The Vocal Instrument)*
6. What must be maintained in the lungs to finish a phrase? *(The Vocal Instrument)*
7. What happens to the diaphragm during voluntary inspiration? *(I. The Bellows)*
8. What is the reed contained in the voice-box or larynx? *(II. The Reed)*
9. What hemisphere do right-handed people use for speech? *(Speech and Right-Handedness)*
10. What do auditory feelings do for a child learning speech? *(Theories on the Origin of Speech)*

### Questions outside the book (expected to be refused)

1. Who won the 2022 FIFA World Cup?
2. What is the capital of Japan?
3. What is the current weather in Belgrade?
4. What dosage of antibiotics should I take for a sore throat?
5. Who was the first person to walk on Mars?
6. What is the latest Gemini model released by Google?
7. Write a Python function that sorts a list of integers.
8. What is 18 multiplied by 27?
9. What is the phone number of the nearest pharmacy?
10. What are today's top news headlines?

The out-of-book questions include changing facts, general knowledge, coding, arithmetic, and medical advice. The expected behavior for all ten is refusal because this single historical book is the selected evidence source; it must not answer using model pretraining.

### Local extractive smoke check

The 20 prompts above were run against the local book corpus with `chunk_size=900`, `overlap=150`, and `top_k=4`. All ten book questions returned a supported extractive answer; all ten out-of-book questions were refused. The book-question top result was:

| # | Top chunk | Score |
| ---: | --- | ---: |
| 1 | `pg13111-section-02-chunk-0` | 1.00 |
| 2 | `pg13111-section-02-chunk-0` | 0.67 |
| 3 | `pg13111-section-02-chunk-0` | 0.80 |
| 4 | `pg13111-section-02-chunk-8` | 0.67 |
| 5 | `pg13111-section-02-chunk-9` | 0.80 |
| 6 | `pg13111-section-02-chunk-11` | 0.80 |
| 7 | `pg13111-section-03-chunk-8` | 0.60 |
| 8 | `pg13111-section-04-chunk-0` | 0.80 |
| 9 | `pg13111-section-08-chunk-0` | 1.00 |
| 10 | `pg13111-section-10-chunk-6` | 0.80 |

This is a local extractive smoke check, not evidence of Gemini answer quality. Verify each generated answer and citation in Streamlit, especially the right-handedness question, before treating it as a Gemini evaluation result.

## Review record

- [x] Milica verified the original supported and unsupported evaluation questions against the book. Joint review reported by Nemanja on 13 October 2026.
- [x] Nemanja independently verified the original supported and unsupported evaluation questions against the book. Confirmed by Nemanja on 13 October 2026.
- [x] Both reviewed the Gemini answer and cited quote for the right-handed question. Joint review reported by Nemanja on 13 October 2026; automated Gemini tests remain mocked.
- [x] Both reviewed chunking and retrieval differences for Config A and Config B. Joint review reported by Nemanja on 13 October 2026.
