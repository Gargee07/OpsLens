"""
Step 10 of Day 1: verify the generated corpus before moving on.
Run from repo root: `uv run python scripts/sanity_check.py`
"""
import json
from collections import Counter

import sys
sys.path.append("data")
from schema import Incident


def main():
    with open("data/synthetic/all_incidents.json") as f:
        raw = json.load(f)

    incidents = []
    errors = 0
    for item in raw:
        try:
            incidents.append(Incident(**item))
        except Exception as e:
            errors += 1
            print(f"[SCHEMA ERROR] {item.get('incident_id', '?')}: {e}")

    print(f"\nTotal incidents: {len(incidents)}  |  Schema errors: {errors}\n")

    by_family = Counter(i.root_cause for i in incidents if not i.is_distractor and not i.is_novel)
    print("Incidents per family (want 4-6+ each, plus 1 runbook each):")
    for root_cause, count in by_family.items():
        print(f"  {root_cause}: {count}")

    distractors = [i for i in incidents if i.is_distractor]
    novel = [i for i in incidents if i.is_novel]
    print(f"\nDistractors: {len(distractors)} (expect {len(distractors)})")
    print(f"Novel (no-family) incidents: {len(novel)} (expect 1)")

    print("\n--- Spot-check 3 random postmortems for wording diversity ---")
    postmortems = [i for i in incidents if i.doc_type == "postmortem"]
    import random
    for i in random.sample(postmortems, min(3, len(postmortems))):
        print(f"\n[{i.incident_id}] {i.root_cause} | {i.service}")
        print(i.doc_text[:200] + "...")


if __name__ == "__main__":
    main()
