"""
backend/app/pipeline.py

This is the function main.py (Day 4-5) will eventually call from the
API endpoint. Keeping it separate from the API layer now means Day 3
testing doesn't depend on FastAPI being wired up yet.
"""
from app.retrieval.hybrid import hybrid_search
from app.reranking.reranker import rerank
from app.guardrails.confidence import check_confidence
from app.generation.generator import generate_answer, no_confident_match_response


def run_query(query: str, service_filter: str | None = None) -> dict:
    candidates = hybrid_search(query, top_k=20, service_filter=service_filter)
    reranked = rerank(query, candidates, top_k=3)
    decision = check_confidence(reranked)

    if decision["confident"]:
        result = generate_answer(query, decision["results"])
        result["confidence"] = decision["confidence"]
        result["guardrail_triggered"] = False
        return result

    result = no_confident_match_response(decision["closest_partials"])
    result["confidence"] = decision["confidence"]
    result["guardrail_triggered"] = True
    return result
