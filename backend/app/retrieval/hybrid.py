"""backend/app/retrieval/hybrid.py"""
from app.retrieval.embedder import embed_query
from app.retrieval.vector_store import dense_search
from app.retrieval.bm25_index import bm25_search

RRF_K = 60   # standard default constant, rarely needs tuning


def reciprocal_rank_fusion(*ranked_lists: list[dict], top_k: int = 10) -> list[dict]:
    scores: dict[str, float] = {}
    payloads: dict[str, dict] = {}
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0) + 1 / (RRF_K + rank + 1)
            payloads[cid] = item
    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{"chunk_id": cid, "fused_score": score, **payloads[cid]} for cid, score in fused]


def hybrid_search(query: str, top_k: int = 10, service_filter: str | None = None) -> list[dict]:
    query_vector = embed_query(query)
    dense_results = dense_search(query_vector, top_k=20, service_filter=service_filter)
    sparse_results = bm25_search(query, top_k=20)
    return reciprocal_rank_fusion(dense_results, sparse_results, top_k=top_k)
