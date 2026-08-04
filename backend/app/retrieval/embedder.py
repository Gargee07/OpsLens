"""backend/app/retrieval/embedder.py"""
import torch
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5",
    model_kwargs={"torch_dtype": torch.float16},
)


def embed_texts(texts: list[str]) -> list[list[float]]:
    return _model.encode(texts, normalize_embeddings=True).tolist()


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]