# build-phase10: Quickstart

## Prerequisites
- All prior phases complete (build-phase1 through build-phase9)
- Access to the repository
- `uv sync`

## 1. Verify the repository state

```bash
make verify
```

`make verify` runs the required fast and slow checks. Phase‑10 contract tests are not yet part of the required set, so they can be run optionally:

```bash
uv run pytest tests/contract/test_phase10_*.py -q 2>/dev/null || echo "No phase‑10 contract tests yet."
```

## 2. Review the build‑plan extension

```bash
# List the user stories and functional requirements
cat specs/010-build-phase10/spec.md | head -65
```

## 3. Optional: add a placeholder implementation

If you wish to begin work on a user story, create a feature branch and add the minimal scaffolding (empty FastAPI route, a new service directory, etc.). The phase stays **Proposed** until acceptance evidence exists; the quick‑start only documents the path to that evidence.

## 4. Hand‑off and finalisation

When the work is finished, follow the same finalisation procedure used for phases 1‑7:

1. Set the spec status to **Implemented** after `make verify` passes.
2. Update the traceability matrix (`docs/traceability-matrix.md`) with the new TM 298‑TM 315 rows.
3. Record the finalisation in `docs/HANDOFF.md`.
4. Tag the release and push to `origin/main`.

