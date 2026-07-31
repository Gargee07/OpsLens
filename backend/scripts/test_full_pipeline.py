"""
backend/scripts/test_full_pipeline.py
Run from backend/: uv run python scripts/test_full_pipeline.py
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root (OpsLens/) regardless of where the script is run from
_repo_root = Path(__file__).resolve().parent.parent.parent  # OpsLens/
load_dotenv(_repo_root / ".env")

sys.path.append(".")
from app.pipeline import run_query

TEST_QUERIES = [
    "checkout-service p99 latency spiking, seems to correlate with inventory-service",
    "auth-service login failures spiking right after deploy",
    # genuinely NOT in the corpus at all — the real guardrail test (see note from Day 2)
    "notification-service emails going to the wrong recipients after a template change",
]

if __name__ == "__main__":
    for q in TEST_QUERIES:
        print(f"\n{'='*80}\nQUERY: {q}\n{'='*80}")
        result = run_query(q)
        print(f"Guardrail triggered: {result['guardrail_triggered']}  |  confidence: {result['confidence']:.3f}")
        print(f"\nAnswer:\n{result['answer']}")
        if result.get("sources"):
            print(f"\nSources: {result['sources']}")
        if result.get("closest_partials"):
            print(f"\nClosest partials (not confident enough to cite):")
            for p in result["closest_partials"]:
                print(f"  - {p['incident_id']} ({p['root_cause']}): {p['snippet']}...")
