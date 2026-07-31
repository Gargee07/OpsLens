"""
backend/app/reranking/reranker.py

Re-ranking is a SECOND, more accurate pass over the candidate set that
hybrid_search already narrowed down. Unlike embedding similarity (which
compares two pre-computed vectors), a cross-encoder looks at the query
and each candidate TOGETHER and outputs one relevance score — slower,
but much better at telling "genuinely relevant" apart from "superficially
similar" (exactly what your distractor incidents are designed to test).
"""
from sentence_transformers import CrossEncoder

_model = CrossEncoder("BAAI/bge-reranker-base")


def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """
    candidates: output of hybrid_search() — each dict has at least a 'text' key.
    Returns candidates re-sorted by rerank_score, trimmed to top_k.
    """
    if not candidates:
        return []

    pairs = [(query, c["text"]) for c in candidates]
    scores = _model.predict(pairs)   # raw cross-encoder logits — higher = more relevant

    for c, score in zip(candidates, scores):
        c["rerank_score"] = float(score)

    return sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)[:top_k]
