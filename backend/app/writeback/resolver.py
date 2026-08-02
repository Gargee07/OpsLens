"""
backend/app/writeback/resolver.py

This is the piece almost no tutorial RAG project has: when an engineer
resolves an incident, this drafts a postmortem, chunks it, embeds it,
and adds it to BOTH indexes (Qdrant + BM25) — so the next similar
query benefits from it immediately.

Runs as a FastAPI BackgroundTask (see main.py) so it never blocks the
response the engineer is waiting for.
"""
import json
import os
from datetime import datetime

from app.ingestion.chunker import build_chunks
from app.retrieval.embedder import embed_texts
from app.retrieval.vector_store import upsert_chunks
from app.retrieval.bm25_index import build_bm25_index
from app.generation.generator import client, MODEL

ALL_INCIDENTS_PATH = "data/synthetic/all_incidents.json"


def _draft_postmortem(query: str, resolution_notes: str) -> dict:
    """Uses the LLM to turn a raw resolution note into a structured postmortem."""
    prompt = f"""Write a concise internal postmortem (150-250 words) based on this
resolved incident. Return ONLY valid JSON, no markdown fences.

Original symptom reported: "{query}"
Engineer's resolution notes: "{resolution_notes}"

Return JSON with exactly these keys:
{{
  "doc_text": "<postmortem narrative, written from the notes above>",
  "root_cause": "<short snake_case label for the root cause>",
  "resolution_steps": ["<step 1>", "<step 2>", "..."]
}}"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return json.loads(resp.choices[0].message.content)


def _next_incident_id(incidents: list[dict]) -> str:
    max_num = max((int(i["incident_id"].split("-")[1]) for i in incidents), default=0)
    return f"INC-{max_num + 1:04d}"


def resolve_and_learn(query: str, resolution_notes: str, service: str = "unknown",
                       severity: str = "SEV3") -> dict:
    """
    The full write-back flow. This is intentionally the SAME shape as
    Day 1's ingestion (schema -> chunk -> embed -> index) — just
    triggered by a resolution event instead of a batch import.
    """
    with open(ALL_INCIDENTS_PATH) as f:
        incidents = json.load(f)

    draft = _draft_postmortem(query, resolution_notes)
    new_incident = {
        "incident_id": _next_incident_id(incidents),
        "service": service,
        "severity": severity,
        "symptom_description": query,
        "root_cause": draft["root_cause"],
        "resolution_steps": draft["resolution_steps"],
        "timestamp": datetime.now().isoformat(),
        "deploy_version": None,
        "related_incident_ids": [],
        "doc_type": "postmortem",
        "doc_text": draft["doc_text"],
        "is_distractor": False,
        "is_novel": False,
    }

    # 1. persist to the corpus file (source of truth)
    incidents.append(new_incident)
    with open(ALL_INCIDENTS_PATH, "w") as f:
        json.dump(incidents, f, indent=2)

    # 2. chunk + embed the new incident only (not the whole corpus again)
    chunks = build_chunks(new_incident)
    vectors = embed_texts([c.text for c in chunks])
    upsert_chunks(chunks, vectors)

    # 3. BM25 has no incremental update in rank_bm25 — rebuild from the full,
    #    now-updated corpus. Fine at this corpus size; a production system
    #    would use a search engine with real incremental indexing (e.g. Elasticsearch).
    all_chunks = []
    for incident in incidents:
        all_chunks.extend(build_chunks(incident))
    build_bm25_index(all_chunks)

    return {"incident_id": new_incident["incident_id"], "status": "indexed"}
