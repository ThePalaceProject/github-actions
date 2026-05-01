"""Mock Jira REST API server for testing the jira-release-sync action.

Records every request to a JSON log file so the test workflow can assert that
the action made the expected calls with the expected payloads.

Implements just enough of the Jira API surface used by action.yml:
  POST /rest/api/3/version                          create version
  GET  /rest/api/3/project/{key}/versions           list versions (returns the one we created)
  POST /rest/api/3/version/{id}/relatedwork         link related work
  PUT  /rest/api/3/issue/{key}                      update issue (fixVersions)
"""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Lock

LOG_LOCK = Lock()
LOG_PATH: Path
CREATED_VERSION_ID = "10001"
FAIL_ON: set[tuple[str, str]] = set()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # quiet default access log
        sys.stderr.write("mock_jira: " + (format % args) + "\n")

    def _read_body(self) -> dict | None:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"_raw": raw.decode("utf-8", "replace")}

    def _record(self, method: str, body: dict | None) -> None:
        entry = {"method": method, "path": self.path, "body": body}
        with LOG_LOCK, LOG_PATH.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def _send_json(self, status: int, payload: object) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _maybe_fail(self, method: str) -> bool:
        if (method, self.path) in FAIL_ON:
            self._send_json(500, {"error": "injected failure"})
            return True
        return False

    def do_GET(self) -> None:
        if self.path == "/__ready__":
            self._send_json(200, {"ok": True})
            return
        self._record("GET", None)
        if self._maybe_fail("GET"):
            return
        if "/rest/api/3/project/" in self.path and self.path.endswith("/versions"):
            self._send_json(200, [{"id": CREATED_VERSION_ID, "name": _last_created_name()}])
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        body = self._read_body()
        self._record("POST", body)
        if self._maybe_fail("POST"):
            return
        if self.path == "/rest/api/3/version":
            _set_last_created_name((body or {}).get("name", ""))
            self._send_json(201, {"id": CREATED_VERSION_ID, "name": (body or {}).get("name")})
            return
        if self.path.startswith("/rest/api/3/version/") and self.path.endswith("/relatedwork"):
            self._send_json(201, {"id": "rw-1"})
            return
        self._send_json(404, {"error": "not found"})

    def do_PUT(self) -> None:
        body = self._read_body()
        self._record("PUT", body)
        if self._maybe_fail("PUT"):
            return
        if self.path.startswith("/rest/api/3/issue/"):
            self.send_response(204)
            self.end_headers()
            return
        self._send_json(404, {"error": "not found"})


_LAST_CREATED_NAME = {"value": ""}


def _set_last_created_name(name: str) -> None:
    _LAST_CREATED_NAME["value"] = name


def _last_created_name() -> str:
    return _LAST_CREATED_NAME["value"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument(
        "--fail-on",
        action="append",
        default=[],
        metavar="METHOD:PATH",
        help="Return 500 for matching requests, e.g. 'POST:/rest/api/3/version'.",
    )
    args = parser.parse_args()

    global LOG_PATH
    LOG_PATH = args.log
    LOG_PATH.write_text("")

    for spec in args.fail_on:
        method, _, path = spec.partition(":")
        if not method or not path:
            sys.stderr.write(f"mock_jira: invalid --fail-on spec: {spec!r}\n")
            sys.exit(2)
        FAIL_ON.add((method, path))

    server = HTTPServer(("127.0.0.1", args.port), Handler)
    sys.stderr.write(f"mock_jira: listening on 127.0.0.1:{args.port}, log={LOG_PATH}\n")
    server.serve_forever()


if __name__ == "__main__":
    main()
