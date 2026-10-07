#!/usr/bin/env python3
"""Run Chimera AEC agents: python3 analyze.py request.json  (stdlib only)."""
import json, os, sys, urllib.error, urllib.request

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: analyze.py request.json", file=sys.stderr); return 2
    key = os.environ.get("AEC_API_KEY")
    if not key:
        print("AEC_API_KEY is not set — create one in Chimera AEC under Settings → API keys", file=sys.stderr); return 2
    url = os.environ.get("AEC_API_URL", "http://localhost:3100").rstrip("/") + "/api/v1/analyze"
    with open(sys.argv[1], "rb") as f:
        body = f.read()
    req = urllib.request.Request(url, data=body, method="POST", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            print(json.dumps(json.load(r), indent=2)); return 0
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr); return 1

if __name__ == "__main__":
    sys.exit(main())
