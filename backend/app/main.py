"""
backend/app/main.py

Run: uv run uvicorn app.main:app --reload
Docs auto-generated at http://localhost:8000/docs
"""
import json
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.pipeline import run_query
from app.writeback.resolver import resolve_and_learn

app = FastAPI(title="OpsLens API")

# allow the Next.js frontend (different origin) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your actual Vercel URL before real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    symptom_description: str
    service_filter: str | None = None


class ResolveRequest(BaseModel):
    query: str
    resolution_notes: str
    service: str = "unknown"
    severity: str = "SEV3"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/query")
def query(req: QueryRequest):
    return run_query(req.symptom_description, service_filter=req.service_filter)


@app.post("/api/incidents/resolve")
def resolve(req: ResolveRequest, background_tasks: BackgroundTasks):
    # runs AFTER the response is sent — the engineer isn't stuck waiting for
    # the LLM to draft a postmortem and rebuild indexes
    background_tasks.add_task(
        resolve_and_learn, req.query, req.resolution_notes, req.service, req.severity
    )
    return {"status": "queued", "message": "Resolution is being processed and will be searchable shortly."}


@app.get("/api/incidents")
def list_incidents():
    with open("data/synthetic/all_incidents.json") as f:
        incidents = json.load(f)
    # trim the payload — full doc_text isn't needed for a list view
    return [
        {
            "incident_id": i["incident_id"],
            "service": i["service"],
            "severity": i["severity"],
            "root_cause": i["root_cause"],
            "symptom_description": i["symptom_description"],
            "timestamp": i["timestamp"],
        }
        for i in incidents
    ]


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    with open("data/synthetic/all_incidents.json") as f:
        incidents = json.load(f)
    for i in incidents:
        if i["incident_id"] == incident_id:
            related = [x for x in incidents if x["root_cause"] == i["root_cause"] and x["incident_id"] != incident_id]
            return {**i, "related_incidents": [r["incident_id"] for r in related][:5]}
    return {"error": "not found"}, 404
