"""backend/app/models/chunk.py"""
from pydantic import BaseModel


class Chunk(BaseModel):
    chunk_id: str                # e.g. "INC-0001-c0"
    incident_id: str              # links back to the source Incident
    service: str
    severity: str
    root_cause: str               # kept for your own eval later — never shown to the retriever's ranking logic
    doc_type: str                 # postmortem | runbook | slack_thread | github_issue
    text: str                     # the actual chunk content that gets embedded
