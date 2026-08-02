"""
backend/scripts/build_index.py
Run from backend/: uv run python scripts/build_index.py
"""
import json
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append(".")

from app.ingestion.chunker import build_chunks
from app.retrieval.embedder import embed_texts
from app.retrieval.vector_store import init_collection, upsert_chunks
from app.retrieval.bm25_index import build_bm25_index


def main():
    with open("data/synthetic/all_incidents.json") as f:
        incidents = json.load(f)

    all_chunks = []
    for incident in incidents:
        all_chunks.extend(build_chunks(incident))
    print(f"[chunking] {len(incidents)} incidents -> {len(all_chunks)} chunks")

    print("[embedding] encoding all chunks locally...")
    vectors = embed_texts([c.text for c in all_chunks])

    print("[vector store] writing to Qdrant...")
    init_collection()
    upsert_chunks(all_chunks, vectors)

    print("[bm25] building sparse index...")
    build_bm25_index(all_chunks)

    print(f"[done] indexed {len(all_chunks)} chunks into both Qdrant and BM25")


if __name__ == "__main__":
    main()
