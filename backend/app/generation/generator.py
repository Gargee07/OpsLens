"""
backend/app/generation/generator.py

The final step: synthesize an answer FROM the retrieved, re-ranked,
guardrail-approved chunks — grounded and cited, not freely generated.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import re

# Load .env from repo root (OpsLens/) if key not already in environment
_repo_root = Path(__file__).resolve().parent.parent.parent.parent  # OpsLens/
load_dotenv(_repo_root / ".env", override=False)

_api_key = os.environ.get("GROQ_API_KEY")
if not _api_key:
    raise EnvironmentError(
        "GROQ_API_KEY is not set. Add it to OpsLens/.env or export it before running."
    )
client = Groq(api_key=_api_key)
MODEL = "llama-3.3-70b-versatile"   # check Groq's current model list before running


def generate_answer(query: str, results: list[dict]) -> dict:
    """
    results: the confident, re-ranked chunk list from the guardrail.
    Builds a grounded prompt — the model is instructed to answer ONLY
    from the provided context and cite which incident(s) it drew from.
    """
    context = "\n\n".join(
        f"[Source: {r['incident_id']}, root_cause={r['root_cause']}]\n{r['text']}"
        for r in results
    )

    prompt = f"""You are an incident response assistant. Answer the engineer's
question using ONLY the context below. Cite the specific incident ID(s) you
drew from. If the context doesn't fully answer the question, say so honestly
rather than filling gaps with assumptions.

Context:
{context}

Engineer's question: {query}

Answer:"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,   # low — this step should be grounded, not creative
    )

    answer_text = resp.choices[0].message.content
    cited_ids = re.findall(r"INC-\d{4}", answer_text)
    actual_sources = [r["incident_id"] for r in results if r["incident_id"] in cited_ids]

    return {
        "answer": answer_text,
        "sources": actual_sources or [r["incident_id"] for r in results],  # fallback if regex finds nothing
    }


def no_confident_match_response(closest_partials: list[dict]) -> dict:
    """The guardrail's alternative path — transparent about uncertainty, not a hallucinated fix."""
    return {
        "answer": (
            "No confident match found in past incidents for this symptom. "
            "This may be a novel issue. Closest partial matches are listed below "
            "for reference, but none are a strong enough match to recommend a fix from."
        ),
        "sources": [],
        "closest_partials": [
            {"incident_id": p["incident_id"], "root_cause": p["root_cause"], "snippet": p["text"][:150]}
            for p in closest_partials
        ],
    }
