# Implementation Plan: build-phase6

**Branch**: `main` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-build-phase6/spec.md`

## Summary

Add the monitoring and observability layer to the telco platform: centralized
log aggregation, Prometheus metrics with Grafana dashboards, alert rules with
team-based routing, OpenTelemetry tracing propagation across service
boundaries, service mesh traffic monitoring with Istio, incident runbooks and
performance anomaly detection.

The technical approach is recorded in [research.md](research.md), the entities
in [data-model.md](data-model.md) and the onboarding contract in
[quickstart.md](quickstart.md).

## Technical Context

**Language/Version**: Python 3.13 (pinned by `.python-version`)

**Primary Dependencies**: Prometheus, Grafana, Loki, Alertmanager, Istio and
the OpenTelemetry collector. The Python side uses the `opentelemetry-sdk` and
`opentelemetry-exporter-otlp` packages, which are not yet declared as
dependencies.

**Storage**: Log, metric and tracing data is held by the observability stack
itself rather than in the application database. The entities in
`data-model.md` describe the records the phase exposes for querying, not new
application tables.

**Testing**: `pytest` through the nox `fast_checks` session, with the
`log`, `metric`, `alert`, `trace`, `mesh` and `runbook` markers; these markers
are not yet registered in `tests/conftest.py`

**Target Platform**: Linux server

**Project Type**: Observability platform extension

**Performance Goals**: Log search under 2 seconds (SC-02); metrics collection
under 1% service latency overhead (NFR-031); tracing propagation under 5ms
(NFR-033); alert notification within 1 minute (SC-03); incident response under
5 minutes (NFR-034)

**Constraints**:
- BR-012 is not violated: the implementation-language and persistence baseline
  is unchanged
- No database schema changes, business logic redesign, infrastructure
  provisioning or cloud provider migration (Boundaries)
- Every critical service must have a dashboard (NFR-035)

**Scale/Scope**: Requirements FR-050 to FR-056 across user stories US1 to US6,
reserving test mappings TM125–TM145 across tasks T162–T223

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Art. I — Specification First
- **Pass**: `spec.md` defines FR-050 to FR-056, NFR-030 to NFR-035, SC-01 to
  SC-07, seven acceptance criteria and five assumptions. The phase status
  stays **Proposed** until every acceptance criterion passes

### Art. II — Domain Ownership and Service Boundaries
- **Pass**: The phase observes the existing services; it does not move
  ownership of any domain's data. The observability stack reads the services'
  telemetry rather than their tables

### Art. III — Security and Privacy by Design
- **Pass**: Log entries carry a request ID and a trace ID for correlation and
  no credentials; the secret scan gate covers the new configuration

### Art. V — Data Modeling and Database Evolution
- **Pass**: No migration is introduced. The phase adds no table and no column

### Art. VII — Testing and Verifiability
- **Pass**: SC-01 to SC-07 are measurable; each requirement reserves three
  test mappings within TM125–TM145

### Art. VIII — Observability and Operability
- **Pass**: The phase *is* the observability work: metrics, traces, logs,
  alerts and runbooks are the deliverables, and each has a measurable
  threshold

### Art. X — Maintainability and Delivery
- **Pass**: The stack is configured, not hand-built; each component is an
  upstream project with a documented configuration surface

**Constitution Check: ALL GATES PASS**

## Project Structure

### Documentation (this feature)

```text
specs/006-build-phase6/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── middleware/
│   ├── logging.py       # Structured log emission for Loki (US1)
│   └── metrics.py       # Prometheus metrics exposition (US2)
├── services/
│   └── anomaly_detection.py  # Performance anomaly detection (FR-056)
├── api/endpoints/
│   └── observability.py      # Alert and runbook endpoints (US3, US6)
deploy/
├── prometheus/           # Scrape configuration and alert rules
├── grafana/              # Dashboards, one per critical service
├── alertmanager/         # Routing rules and notification channels
├── istio/                # Service mesh telemetry configuration
└── loki/                 # Log aggregation configuration
```

The phase 5 tracing package at `services/common/opentelemetry/` is extended
rather than replaced, so the tracing work spans both the shared library and
the service pipelines.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | The phase adds no service, no runtime network endpoint and no database object; it configures the observability stack around the services that already exist, so every constitution gate passes without a justified exception |
