# backend/scripts/debug_reranker_latency.py — updated
import time
import sys
sys.path.append(".")
from app.reranking.reranker import _model
from app.retrieval.hybrid import hybrid_search

# pull real candidates for one real query, same as the pipeline actually does
candidates = hybrid_search("checkout-service p99 latency spiking, seems to correlate with inventory-service", top_k=10)
pairs = [("checkout-service p99 latency spiking", c["text"]) for c in candidates]

print(f"Avg text length: {sum(len(c['text'].split()) for c in candidates) / len(candidates):.0f} words")

for i in range(5):
    start = time.time()
    _model.predict(pairs)
    print(f"Call {i+1}: {(time.time() - start)*1000:.1f}ms")