"""
backend/scripts/view_traces.py
Run from backend/: uv run python scripts/view_traces.py

Works whether or not Langfuse is configured — reads the local
JSONL trace log and prints average latency per pipeline stage.
"""
import json
from collections import defaultdict

TRACE_PATH = "data/synthetic/trace_log.jsonl"


def main():
    stage_latencies = defaultdict(list)

    with open(TRACE_PATH) as f:
        for line in f:
            record = json.loads(line)
            stage_latencies[record["stage"]].append(record["latency_ms"])

    print(f"{'Stage':<20} {'Count':<8} {'Avg (ms)':<10} {'Max (ms)':<10}")
    print("-" * 50)
    for stage, latencies in stage_latencies.items():
        avg = sum(latencies) / len(latencies)
        print(f"{stage:<20} {len(latencies):<8} {avg:<10.1f} {max(latencies):<10.1f}")


if __name__ == "__main__":
    main()
