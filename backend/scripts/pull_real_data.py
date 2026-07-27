"""
Step 5 of Day 1: pull real public data into data/raw/.
Run from the repo root: `uv run python scripts/pull_real_data.py`
"""
import os
import subprocess
import requests

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)


def pull_danluu_postmortems():
    """Clone the danluu/post-mortems repo for style/tone reference."""
    target = os.path.join(RAW_DIR, "post-mortems")
    if not os.path.exists(target):
        subprocess.run(
            ["git", "clone", "--depth", "1",
             "https://github.com/danluu/post-mortems.git", target],
            check=True,
        )
    print(f"[done] danluu postmortems cloned to {target}")


def pull_loghub_sample(system: str = "HDFS"):
    """
    Download a small public sample log file from the logpai/loghub repo.
    2k-line samples are hosted directly in the repo for several systems
    (HDFS, OpenStack, Spark, etc.) — no signup required for these samples.
    """
    url = f"https://raw.githubusercontent.com/logpai/loghub/master/{system}/{system}_2k.log"
    out_path = os.path.join(RAW_DIR, f"{system}_2k.log")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(resp.content)
    print(f"[done] {system} sample log saved to {out_path}")


def pull_github_issues(repo: str, n: int = 20):
    """
    Pull the most recent closed issues (with comments) from a real
    open-source repo, for conversational-style diagnosis data.
    Set GITHUB_TOKEN in your environment to avoid low unauthenticated
    rate limits.
    """
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    resp = requests.get(
        f"https://api.github.com/repos/{repo}/issues",
        params={"state": "closed", "per_page": n},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    issues = resp.json()

    out_path = os.path.join(RAW_DIR, "github_issues.json")
    import json
    with open(out_path, "w") as f:
        json.dump(issues, f, indent=2)
    print(f"[done] {len(issues)} issues from {repo} saved to {out_path}")


if __name__ == "__main__":
    pull_danluu_postmortems()
    pull_loghub_sample("HDFS")          # swap for "OpenStack", "Spark", etc. if preferred
    pull_github_issues("fastapi/fastapi", n=20)   # pick any mid-size repo you like
