"""
backend/scripts/test_retrieval.py
Run from backend/: uv run python scripts/test_retrieval.py

This is your eyeball-check for Day 2: does hybrid search actually
group same-root-cause incidents together despite different wording?
"""
import sys
sys.path.append(".")
from app.retrieval.hybrid import hybrid_search

TEST_QUERIES = [
    "checkout-service p99 latency spiking, seems to correlate with inventory-service",
    "auth-service login failures spiking right after deploy",
    "legitimate payment requests getting 429 errors",
    # this last one should trigger low-confidence results across the board — it's your novel incident
    "auth-service SSL handshake failures with an external identity provider, first time this has happened",
]

if __name__ == "__main__":
    for q in TEST_QUERIES:
        print(f"\n{'='*80}\nQUERY: {q}\n{'='*80}")
        results = hybrid_search(q, top_k=5)
        for r in results:
            print(f"  [{r['fused_score']:.4f}] {r['chunk_id']} | root_cause={r['root_cause']} | {r['text'][:80]}...")
