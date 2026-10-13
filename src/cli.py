import argparse

from . import book_source
from .book_chunking import build_book_chunks
from .chunking import build_chunks
from .corpus import list_corpus_profiles, load_corpus
from .rag import build_grounded_answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Week 6 RAG homework starter")
    parser.add_argument("--question", required=True, help="Question to ask over the local corpus")
    parser.add_argument("--chunk-size", type=int, default=None, help="Chunk size (characters for built-in corpora)")
    parser.add_argument("--overlap", type=int, default=None, help="Chunk overlap")
    parser.add_argument("--top-k", type=int, default=None, help="Number of retrieved chunks")
    parser.add_argument(
        "--corpus-profile",
        default="default",
        choices=list_corpus_profiles(),
        help="Corpus profile: default or training-rag",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    is_book = args.corpus_profile == book_source.PROFILE
    chunk_size = args.chunk_size if args.chunk_size is not None else (900 if is_book else 140)
    overlap = args.overlap if args.overlap is not None else (150 if is_book else 30)
    top_k = args.top_k if args.top_k is not None else (4 if is_book else 2)
    try:
        corpus = load_corpus(args.corpus_profile)
    except FileNotFoundError as exc:
        raise SystemExit(f"Error: {exc}") from exc
    chunks = (
        build_book_chunks(corpus, chunk_size=chunk_size, overlap=overlap)
        if is_book
        else build_chunks(corpus, chunk_size=chunk_size, overlap=overlap)
    )
    result = build_grounded_answer(
        args.question,
        chunks,
        top_k=top_k,
        support_scope="chunk" if is_book else "document",
    )

    print("Question:")
    print(args.question)
    print("\nCorpus profile:", args.corpus_profile)
    print("Chunk size:", chunk_size)
    print("Overlap:", overlap)
    print("Top-k:", top_k)
    print("\nRetrieved chunks:")
    if result.retrieved:
        for item in result.retrieved:
            print(f"- [{item.chunk.chunk_id}] score={item.score:.3f} title={item.chunk.title}")
            print(f"  {item.chunk.text}")
    else:
        print("None")
    print("\nAnswer:")
    print(result.answer)
    print("\nRefused:", result.refused)
    print("References:")
    if result.citations:
        for citation in result.citations:
            print(f"- [{citation}]")
    else:
        print("None")


if __name__ == "__main__":
    main()
