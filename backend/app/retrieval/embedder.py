"""backend/app/retrieval/embedder.py"""
from sentence_transformers import SentenceTransformer

# bge-base is a strong general-purpose retrieval model and runs fine on CPU
# for a corpus this size. Swap for a different MTEB-leaderboard model later
# if you want to compare retrieval quality.
_model = SentenceTransformer("BAAI/bge-base-en-v1.5")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embeds a list of strings. Use this for both indexing and queries."""
    return _model.encode(texts, normalize_embeddings=True).tolist()


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
