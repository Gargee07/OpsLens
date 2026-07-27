"""
Step 7 of Day 1: generate a small deploy event log so "latency spiked
after deploy X" queries have something real to correlate against.
Run from repo root: `uv run python scripts/generate_deploy_events.py`
"""
import json
import os
import random
from datetime import datetime, timedelta

import sys
sys.path.append("data")
from schema import DeployEvent

with open("data/services.json") as f:
    SERVICES = [s["name"] for s in json.load(f)["services"]]

COMMIT_MESSAGES = [
    "bump connection pool size",
    "add retry logic for downstream calls",
    "update rate limit config",
    "refactor auth token validation",
    "add feature flag for new checkout flow",
    "fix cache TTL configuration",
    "upgrade payment SDK version",
    "add structured logging",
]


def main():
    events = []
    for service in SERVICES:
        for _ in range(random.randint(3, 6)):
            events.append(DeployEvent(
                service=service,
                version=f"v1.{random.randint(1,9)}.{random.randint(0,9)}",
                timestamp=datetime.now() - timedelta(days=random.randint(1, 180)),
                commit_message=random.choice(COMMIT_MESSAGES),
            ))

    events.sort(key=lambda e: e.timestamp)
    out_path = "data/synthetic/deploy_events.json"
    os.makedirs("data/synthetic", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump([json.loads(e.model_dump_json()) for e in events], f, indent=2)
    print(f"[done] {len(events)} deploy events written to {out_path}")


if __name__ == "__main__":
    main()
