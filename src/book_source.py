"""Acquire and parse Project Gutenberg eBook 13111 for the optional corpus."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

from .corpus import Document


BOOK_TITLE = "The Brain and the Voice in Speech and Song"
BOOK_URL = "https://www.gutenberg.org/ebooks/13111"
BOOK_TEXT_URL = "https://www.gutenberg.org/cache/epub/13111/pg13111.txt"
BOOK_PATH = Path(__file__).resolve().parents[1] / "data" / "pg13111.txt"
PROFILE = "mott-13111"
MAX_DOWNLOAD_BYTES = 5_000_000

START_MARKER = re.compile(r"(?m)^\*\*\* START OF THE PROJECT GUTENBERG EBOOK .+ \*\*\*$")
END_MARKER = re.compile(r"(?m)^\*\*\* END OF THE PROJECT GUTENBERG EBOOK .+ \*\*\*$")
TITLE_LINE = re.compile(r"(?m)^THE BRAIN AND THE VOICE IN SPEECH AND SONG\s*$")

# These are body headings verified against the Gutenberg plain-text edition.
SECTION_HEADINGS = (
    ("Theories on the Origin of Speech", "THEORIES ON THE ORIGIN OF SPEECH"),
    ("The Vocal Instrument", "THE VOCAL INSTRUMENT"),
    ("I. The Bellows", "I. THE BELLOWS"),
    ("II. The Reed", "II. THE REED"),
    ("III. The Resonator and Articulator", "III. THE RESONATOR AND ARTICULATOR"),
    (
        "Pathological Degenerative Changes Producing Speech Defects and What They Teach",
        "PATHOLOGICAL DEGENERATIVE CHANGES PRODUCING SPEECH DEFECTS\nAND WHAT THEY TEACH",
    ),
    ("The Cerebral Mechanism of Speech and Song", "THE CEREBRAL MECHANISM OF SPEECH AND SONG"),
    ("Speech and Right-Handedness", "SPEECH AND RIGHT-HANDEDNESS"),
    ("Localisation of Speech Centres in the Brain", "LOCALISATION OF SPEECH CENTRES IN THE BRAIN"),
    (
        "The Primary Site of Revival of Words in Silent Thought",
        "THE PRIMARY SITE OF REVIVAL OF WORDS IN SILENT THOUGHT",
    ),
    (
        "Case of Deafness Arising from Destruction of the Auditory Centres",
        "CASE OF DEAFNESS ARISING FROM DESTRUCTION OF THE AUDITORY CENTRES IN THE\nBRAIN CAUSING LOSS OF SPEECH",
    ),
    (
        "The Primary Revival of Some Sensations in the Brain",
        "THE PRIMARY REVIVAL OF SOME SENSATIONS IN THE BRAIN",
    ),
    ("Psychic Mechanism of the Voice", "PSYCHIC MECHANISM OF THE VOICE"),
)


def book_is_available(path: Path | None = None) -> bool:
    path = path or BOOK_PATH
    return path.is_file()


def download_book(destination: Path | None = None) -> Path:
    """Download the official UTF-8 edition once and record its provenance."""
    destination = destination or BOOK_PATH
    request = Request(BOOK_TEXT_URL, headers={"User-Agent": "rag-basics-AI-bootcamp/1.0"})
    with urlopen(request, timeout=30) as response:
        raw = response.read(MAX_DOWNLOAD_BYTES + 1)
    if len(raw) > MAX_DOWNLOAD_BYTES:
        raise ValueError("The downloaded book exceeds the expected size limit.")
    text = raw.decode("utf-8-sig")
    parse_book_text(text)  # Reject a redirect or response that is not the requested book.

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".txt.tmp")
    temporary.write_bytes(raw)
    temporary.replace(destination)
    metadata = {
        "title": BOOK_TITLE,
        "source_url": BOOK_TEXT_URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    destination.with_suffix(".json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return destination


def parse_book_text(text: str) -> list[Document]:
    """Return one document per recognized body section, excluding PG wrapper."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    start = START_MARKER.search(text)
    end = END_MARKER.search(text)
    if not start or not end or end.start() <= start.end():
        raise ValueError("The Gutenberg book markers are missing or out of order.")
    body = text[start.end():end.start()]
    title_matches = list(TITLE_LINE.finditer(body))
    if len(title_matches) < 2:
        raise ValueError("The book title and body opening were not found.")
    body = body[title_matches[-1].end():]
    index_heading = re.search(r"(?m)^INDEX[ \t]*$", body)
    if index_heading:
        body = body[:index_heading.start()]

    headings = sorted(
        (
            (match.start(), match.end(), title)
            for title, raw_heading in SECTION_HEADINGS
            for match in re.finditer(r"(?m)^" + re.escape(raw_heading) + r"[ \t]*$", body)
        ),
        key=lambda item: item[0],
    )
    if not headings:
        raise ValueError("No expected book sections were found.")

    sections = [("Introduction", body[:headings[0][0]])]
    sections.extend(
        (title, body[end:headings[index + 1][0] if index + 1 < len(headings) else len(body)])
        for index, (_, end, title) in enumerate(headings)
    )
    documents = []
    for index, (title, section_text) in enumerate(sections):
        cleaned = re.sub(r"[ \t]+", " ", section_text).strip()
        if cleaned:
            documents.append(
                Document(
                    doc_id=f"pg13111-section-{index:02d}",
                    title=f"{BOOK_TITLE}: {title}",
                    text=cleaned,
                    source_url=BOOK_URL,
                )
            )
    return documents


def load_book_corpus(path: Path | None = None) -> list[Document]:
    path = path or BOOK_PATH
    if not path.is_file():
        raise FileNotFoundError("Book corpus is missing. Download eBook 13111 in the Streamlit app first.")
    return parse_book_text(path.read_text(encoding="utf-8-sig"))
