"""
backend/app/guardrails/confidence.py

Without this gate, the LLM will generate a plausible-sounding answer
even from weak or irrelevant retrieved context — this file exists
specifically to stop that. This is the guardrail your novel incident
(third_party_ssl_cert_expiry) is designed to trigger.
"""
import math

CONFIDENCE_THRESHOLD = 0.65   # tune this after testing against your novel incident


def _sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def check_confidence(reranked: list[dict], threshold: float = CONFIDENCE_THRESHOLD) -> dict:
    """
    Returns a decision dict:
      {"confident": True,  "results": [...]}                       -> safe to generate an answer
      {"confident": False, "closest_partials": [...]}               -> guardrail triggered
    """
    if not reranked:
        return {"confident": False, "closest_partials": []}

    top_score = reranked[0]["rerank_score"]
    confidence = _sigmoid(top_score)

    if confidence >= threshold:
        return {"confident": True, "results": reranked, "confidence": confidence}

    return {
        "confident": False,
        "closest_partials": reranked[:3],   # show what it almost matched, transparently
        "confidence": confidence,
    }
