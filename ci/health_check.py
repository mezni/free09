"""Health check — verifies the local runtime stack answers health probes.

Exits 0 when the API is healthy, 2 when the probe cannot be executed, and 1
when the API answered but reported an unhealthy state.
"""

import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_URL = os.environ.get("HEALTHCHECK_URL", "http://localhost:8000/healthz")
DEFAULT_TIMEOUT = float(os.environ.get("HEALTHCHECK_TIMEOUT", "5"))


def probe(url: str, timeout: float) -> tuple[int, str]:
    """Return (status_code, body). status_code is 0 when the probe failed."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError):
        return 0, ""


def main() -> int:
    status, body = probe(DEFAULT_URL, DEFAULT_TIMEOUT)

    if status == 0:
        print(f"Health check COULD NOT RUN — {DEFAULT_URL} is unreachable")
        return 2

    if status >= 500:
        print(f"Health check FAILED — {DEFAULT_URL} returned {status}")
        print(body[:500])
        return 1

    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        payload = None

    if isinstance(payload, dict) and payload.get("status") in {"unhealthy", "fail"}:
        print(f"Health check FAILED — {DEFAULT_URL} reported an unhealthy status")
        print(body[:500])
        return 1

    print(f"Health check PASSED — {DEFAULT_URL} returned {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
