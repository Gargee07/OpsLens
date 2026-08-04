"""backend/app/reranking/reranker.py"""
import torch
from sentence_transformers import CrossEncoder

_model = CrossEncoder(
    "BAAI/bge-reranker-base",
    max_length=256,
    model_kwargs={"torch_dtype": torch.float16},
)


def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    if not candidates:
        return []
    pairs = [(query, c["text"]) for c in candidates]
    scores = _model.predict(pairs)
    for c, score in zip(candidates, scores):
        c["rerank_score"] = float(score)
    return sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)[:top_k]