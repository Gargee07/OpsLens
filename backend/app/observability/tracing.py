"""
backend/app/observability/tracing.py

Two options, both included:

1. Langfuse (recommended, matches your project brief) — requires
   LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST in .env.
   Sign up free at cloud.langfuse.com, host = https://cloud.langfuse.com.

   NOTE: Langfuse's Python SDK moved to a new OpenTelemetry-based
   v3/v4 API in early 2026 (`from langfuse import observe, get_client`).
   If the import below fails on your installed version, check
   Langfuse's current Python SDK docs — this library changes fast,
   and the exact method names below may need a small adjustment.

2. local_trace_log() — a zero-dependency fallback. If Langfuse setup
   costs you more than ~30 min of friction, use this instead so you're
   not blocked. It still gives you real per-stage latency data, just
   without Langfuse's dashboard UI.
"""

"""backend/app/observability/tracing.py"""
import json
import os
from datetime import datetime

LOCAL_TRACE_PATH = "data/synthetic/trace_log.jsonl"


def log_stage(stage: str, query: str, latency_ms: float):
    """Writes one real, already-measured latency value to the local trace log."""
    record = {
        "stage": stage,
        "query": query,
        "latency_ms": latency_ms,
        "timestamp": datetime.now().isoformat(),
    }
    os.makedirs(os.path.dirname(LOCAL_TRACE_PATH), exist_ok=True)
    with open(LOCAL_TRACE_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")


def get_langfuse_client():
    try:
        from langfuse import get_client
        return get_client()
    except Exception as e:
        print(f"[observability] Langfuse not available, falling back to local logging: {e}")
        return None
# import json
# import os
# import time
# from contextlib import contextmanager
# from datetime import datetime

# LOCAL_TRACE_PATH = "data/synthetic/trace_log.jsonl"


# @contextmanager
# def local_trace_log(stage: str, query: str = ""):
#     """Zero-dependency fallback: logs stage name + latency to a local JSONL file."""
#     start = time.time()
#     record = {"stage": stage, "query": query, "timestamp": datetime.now().isoformat()}
#     try:
#         yield record
#     finally:
#         record["latency_ms"] = round((time.time() - start) * 1000, 1)
#         os.makedirs(os.path.dirname(LOCAL_TRACE_PATH), exist_ok=True)
#         with open(LOCAL_TRACE_PATH, "a") as f:
#             f.write(json.dumps(record) + "\n")


# def get_langfuse_client():
#     """Returns the Langfuse client, or None if not configured (fails gracefully)."""
#     try:
#         from langfuse import get_client
#         return get_client()
#     except Exception as e:
#         print(f"[observability] Langfuse not available, falling back to local logging: {e}")
#         return None
