#!/usr/bin/env python3
"""Run the phase-5 performance benchmark and compare it with the baseline."""

import argparse
import json
import os
import sys

os.environ.setdefault("TELECO_DB_URL", "sqlite://")

from src.main import app  # noqa: E402
from src.observability.benchmark import (  # noqa: E402
    compare_to_baseline,
    run_benchmark,
)


def main() -> int:
    """Run the benchmark, print the report and return the comparison result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=50)
    args = parser.parse_args()

    result = run_benchmark(app, iterations=args.iterations)
    comparison = compare_to_baseline(result)
    print(json.dumps({"result": result, "comparison": comparison}, indent=2))
    return 0 if comparison["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
