"""backend/app/retrieval/bm25_index.py"""
import pickle
from rank_bm25 import BM25Okapi

INDEX_PATH = "data/synthetic/bm25_index.pkl"


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


def build_bm25_index(chunks: list):
    corpus = [_tokenize(c.text) for c in chunks]
    bm25 = BM25Okapi(corpus)
    # store the chunk metadata alongside the index so search can return full payloads
    payloads = [c.model_dump() for c in chunks]
    with open(INDEX_PATH, "wb") as f:
        pickle.dump({"bm25": bm25, "payloads": payloads}, f)


def bm25_search(query: str, top_k: int = 20) -> list[dict]:
    with open(INDEX_PATH, "rb") as f:
        data = pickle.load(f)
    scores = data["bm25"].get_scores(_tokenize(query))
    ranked = sorted(zip(scores, data["payloads"]), key=lambda x: x[0], reverse=True)[:top_k]
    return [{"chunk_id": p["chunk_id"], "score": s, **p} for s, p in ranked]
