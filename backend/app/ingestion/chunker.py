"""
backend/app/ingestion/chunker.py

Chunking strategy differs by doc_type — this is the actual design
decision this file exists to make, not a detail.
"""
import re
from app.models.chunk import Chunk


def chunk_postmortem(text: str, max_words: int = 120) -> list[str]:
    """
    Narrative prose — split on paragraph boundaries first, then
    merge small paragraphs up to max_words so we don't end up with
    tiny, context-less fragments.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if len((current + " " + p).split()) > max_words and current:
            chunks.append(current.strip())
            current = p
        else:
            current = (current + " " + p).strip()
    if current:
        chunks.append(current)
    return chunks or [text]


def chunk_runbook(text: str) -> list[str]:
    """
    Runbooks are numbered steps — each numbered item is naturally
    self-contained, so chunk on the numbering itself rather than
    word count.
    """
    parts = re.split(r"\n(?=\d+\.\s)", text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts or [text]


def chunk_document(doc_type: str, text: str) -> list[str]:
    if doc_type == "runbook":
        return chunk_runbook(text)
    # postmortem, slack_thread, github_issue all default to paragraph-based chunking for now
    return chunk_postmortem(text)


def build_chunks(incident: dict) -> list[Chunk]:
    """Takes one incident dict (from all_incidents.json) and returns its Chunk objects."""
    pieces = chunk_document(incident["doc_type"], incident["doc_text"])
    return [
        Chunk(
            chunk_id=f"{incident['incident_id']}-c{i}",
            incident_id=incident["incident_id"],
            service=incident["service"],
            severity=incident["severity"],
            root_cause=incident["root_cause"],
            doc_type=incident["doc_type"],
            text=piece,
        )
        for i, piece in enumerate(pieces)
    ]
