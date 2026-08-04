"""backend/app/retrieval/vector_store.py"""
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

COLLECTION = "incident_chunks"
EMBED_DIM = 384   


# _client = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))
_client = QdrantClient(
    url=os.environ.get("QDRANT_URL", "http://localhost:6333"),
    api_key=os.environ.get("QDRANT_API_KEY"),
)



def init_collection():
    if not _client.collection_exists(COLLECTION):
        _client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )


def upsert_chunks(chunks: list, vectors: list[list[float]]):
    points = [
        PointStruct(
            id=i,
            vector=vec,
            payload={
                "chunk_id": c.chunk_id,
                "incident_id": c.incident_id,
                "service": c.service,
                "severity": c.severity,
                "root_cause": c.root_cause,   # kept in payload for YOUR eval checks only
                "doc_type": c.doc_type,
                "text": c.text,
            },
        )
        for i, (c, vec) in enumerate(zip(chunks, vectors))
    ]
    _client.upsert(collection_name=COLLECTION, points=points)


def dense_search(query_vector: list[float], top_k: int = 20,
                  service_filter: str | None = None) -> list[dict]:
    query_filter = None
    if service_filter:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        query_filter = Filter(must=[FieldCondition(key="service", match=MatchValue(value=service_filter))])

    results = _client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=top_k,
        query_filter=query_filter,
    ).points
    return [{"chunk_id": r.payload["chunk_id"], "score": r.score, **r.payload} for r in results]
