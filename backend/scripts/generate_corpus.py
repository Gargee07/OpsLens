"""
Step 6-9 of Day 1: generate the synthetic incident corpus.
Run from repo root: `uv run python scripts/generate_corpus.py`
Requires GROQ_API_KEY in your environment (.env file + python-dotenv, or exported).
"""
import json
import os
import random
from datetime import datetime, timedelta

from groq import Groq
from pydantic import ValidationError

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root (OpsLens/) regardless of where the script is run from
_repo_root = Path(__file__).resolve().parent.parent.parent  # OpsLens/
load_dotenv(_repo_root / ".env")

_backend_root = Path(__file__).resolve().parent.parent  # OpsLens/backend/
sys.path.insert(0, str(_backend_root / "data"))  # adds backend/data/ so `from schema import Incident` works
# pyrefly: ignore [missing-import]
from schema import Incident

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"   # check Groq's current model list before running — names change

SYNTHETIC_DIR = "data/synthetic"
os.makedirs(SYNTHETIC_DIR, exist_ok=True)

with open("data/incident_families.json") as f:
    PLAN = json.load(f)


def call_llm(prompt: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,   # higher temperature = more wording diversity across variants
    )
    return resp.choices[0].message.content


def generate_postmortem(root_cause: str, description: str, service: str, symptom: str) -> dict:
    prompt = f"""You are writing an internal engineering postmortem. Return ONLY valid JSON, no markdown fences.

Context:
- Root cause category: {root_cause} ({description})
- Affected service: {service}
- How the on-call engineer first described the symptom: "{symptom}"

Write a realistic postmortem as if this really happened. Vary the specific numbers,
timeline, and narrative voice each time — do not reuse boilerplate phrasing.

Return JSON with exactly these keys:
{{
  "doc_text": "<full postmortem body, 200-400 words, include a timeline and root cause analysis>",
  "resolution_steps": ["<step 1>", "<step 2>", "..."]
}}"""
    raw = call_llm(prompt)
    return json.loads(raw)


def generate_runbook(root_cause: str, description: str, service: str) -> str:
    prompt = f"""Write a concise internal runbook (150-250 words) for on-call engineers
responding to a "{root_cause}" issue ({description}) affecting {service}.
Format as numbered diagnostic steps followed by numbered remediation steps.
Return plain text only, no JSON, no markdown fences."""
    return call_llm(prompt)


def build_incident(counter: list, root_cause: str, description: str,
                    service: str, symptom: str, severity: str,
                    is_distractor: bool = False, is_novel: bool = False) -> Incident:
    counter[0] += 1
    incident_id = f"INC-{counter[0]:04d}"
    pm = generate_postmortem(root_cause, description, service, symptom)
    timestamp = datetime.now() - timedelta(days=random.randint(1, 180))

    incident = Incident(
        incident_id=incident_id,
        service=service,
        severity=severity,
        symptom_description=symptom,
        root_cause=root_cause,
        resolution_steps=pm["resolution_steps"],
        timestamp=timestamp,
        deploy_version=f"v1.{random.randint(1,9)}.{random.randint(0,9)}",
        doc_type="postmortem",
        doc_text=pm["doc_text"],
        is_distractor=is_distractor,
        is_novel=is_novel,
    )
    return incident


def main():
    counter = [0]
    all_incidents: list[Incident] = []

    # --- families ---
    for family in PLAN["families"]:
        for symptom in family["symptom_phrasings"]:
            service = random.choice(family["candidate_services"])
            severity = random.choice(["SEV2", "SEV3"])
            incident = build_incident(
                counter, family["root_cause"], family["description"],
                service, symptom, severity,
            )
            all_incidents.append(incident)

        # one runbook per family (not tied to a single incident, added as its own doc)
        runbook_text = generate_runbook(
            family["root_cause"], family["description"], family["candidate_services"][0]
        )
        counter[0] += 1
        all_incidents.append(Incident(
            incident_id=f"INC-{counter[0]:04d}",
            service=family["candidate_services"][0],
            severity="SEV3",
            symptom_description=f"[runbook] {family['root_cause']}",
            root_cause=family["root_cause"],
            resolution_steps=[],
            timestamp=datetime.now(),
            doc_type="runbook",
            doc_text=runbook_text,
        ))

    # --- distractors ---
    for d in PLAN["distractors"]:
        incident = build_incident(
            counter, d["root_cause"], d["note"], d["candidate_services"][0],
            d["symptom_phrasing"], "SEV3", is_distractor=True,
        )
        all_incidents.append(incident)

    # --- novel incident (no family, for guardrail testing) ---
    n = PLAN["novel_incident"]
    incident = build_incident(
        counter, n["root_cause"], n["note"], n["candidate_services"][0],
        n["symptom_phrasing"], "SEV2", is_novel=True,
    )
    all_incidents.append(incident)

    # --- write out, one JSON file per incident + one combined file ---
    combined = []
    for inc in all_incidents:
        path = os.path.join(SYNTHETIC_DIR, f"{inc.incident_id}.json")
        with open(path, "w") as f:
            f.write(inc.model_dump_json(indent=2))
        combined.append(json.loads(inc.model_dump_json()))

    with open(os.path.join(SYNTHETIC_DIR, "all_incidents.json"), "w") as f:
        json.dump(combined, f, indent=2)

    print(f"[done] generated {len(all_incidents)} incidents into {SYNTHETIC_DIR}")


if __name__ == "__main__":
    main()
