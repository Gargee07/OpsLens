"""
backend/app/pipeline.py  (Day 4 update — replaces the Day 3 version)

Every stage now logs its latency and key output. Uses Langfuse if
configured, otherwise falls back to a local JSONL trace log — either
way, you get real per-stage visibility, which is the actual point of
this project's second title.
"""
import time
from app.retrieval.hybrid import hybrid_search
from app.reranking.reranker import rerank
from app.guardrails.confidence import check_confidence
from app.generation.generator import generate_answer, no_confident_match_response
from app.observability.tracing import get_langfuse_client, log_stage

langfuse = get_langfuse_client()


def _timed_stage(stage_name: str, query: str, fn, *args, **kwargs):
    """Runs fn, logs latency to Langfuse (if available) and locally, returns fn's result."""
    start = time.time()
    result = fn(*args, **kwargs)
    latency_ms = round((time.time() - start) * 1000, 1)

    if langfuse:
        try:
            with langfuse.start_as_current_observation(name=stage_name, as_type="span") as span:
                span.update(output={"latency_ms": latency_ms})
        except Exception as e:
            print(f"[observability] Langfuse logging failed for {stage_name}: {e}")

    log_stage(stage_name, query, latency_ms)   

    return result


def run_query(query: str, service_filter: str | None = None) -> dict:
    pipeline_start = time.time()

    candidates = _timed_stage("hybrid_retrieval", query, hybrid_search, query, top_k=20, service_filter=service_filter)
    reranked = _timed_stage("reranking", query, rerank, query, candidates, top_k=3)
    decision = _timed_stage("guardrail_check", query, check_confidence, reranked)

    if decision["confident"]:
        result = _timed_stage("generation", query, generate_answer, query, decision["results"])
    else:
        result = no_confident_match_response(decision["closest_partials"])

    result["confidence"] = decision.get("confidence")
    result["guardrail_triggered"] = not decision["confident"]
    result["total_latency_ms"] = round((time.time() - pipeline_start) * 1000, 1)

    return result
