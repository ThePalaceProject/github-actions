"""Assert the mock-jira request log matches expectations for a test case.

Reads a JSONL log produced by mock_jira.py and a JSON expectations file, then
exits non-zero with a diff-style message if they don't match. We compare a
normalized projection of each request (method, path, selected body fields) so
that incidental fields like description text don't make the test brittle.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def project(entry: dict) -> dict:
    """Extract just the fields we care about asserting on."""
    method = entry["method"]
    path = entry["path"]
    body = entry.get("body") or {}
    out: dict = {"method": method, "path": path}

    if method == "POST" and path == "/rest/api/3/version":
        out["name"] = body.get("name")
        out["project"] = body.get("project")
        out["released"] = body.get("released")
    elif method == "POST" and path.endswith("/relatedwork"):
        out["title"] = body.get("title")
        out["url"] = body.get("url")
        out["category"] = body.get("category")
    elif method == "PUT" and path.startswith("/rest/api/3/issue/"):
        out["fixVersions"] = body.get("update", {}).get("fixVersions")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    args = parser.parse_args()

    actual = [project(e) for e in load_jsonl(args.log)]
    expected = json.loads(args.expected.read_text())

    if actual == expected:
        print(f"OK: {len(actual)} requests matched expectations")
        return 0

    print("MISMATCH between actual and expected requests", file=sys.stderr)
    print("--- expected ---", file=sys.stderr)
    print(json.dumps(expected, indent=2), file=sys.stderr)
    print("--- actual ---", file=sys.stderr)
    print(json.dumps(actual, indent=2), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
