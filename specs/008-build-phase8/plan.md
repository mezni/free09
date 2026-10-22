# Implementation Plan: build-phase8

**Branch**: `main` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-build-phase8/spec.md`

## Summary

Extend the telco platform with six capabilities on top of the existing
service set: advanced analytics endpoints, AI model metrics with anomaly
detection, an admin surface with role-based access, an external partner
integration framework, monthly compliance reporting, and a feature flag
framework with instant rollback.

The technical approach is recorded in [research.md](research.md) and the data
model in [data-model.md](data-model.md); the API surface is fixed by
[contracts/advanced_api_contract.md](contracts/advanced_api_contract.md).

## Technical Context

**Language/Version**: Python 3.13 (consistent with `.python-version`)

**Primary Dependencies**: Existing telco platform services (auth-service, crm-service, billing-service, inventory-service), OpenTelemetry, Pandas, Scikit-learn, FastAPI

**Storage**: PostgreSQL (per ADR-0001 centralized PostgreSQL), with separate schemas per service per Art. II

**Testing**: pytest (per noxfile.py configuration), with governance test files TM001–TM220

**Target Platform**: Linux server (existing infrastructure)

**Project Type**: web-service (telco platform extension)

**Performance Goals**: AI anomaly detection >85% precision; Admin UI <200ms response; Analytics endpoints valid responses for all query types

**Constraints**: 
- AI-powered features must have explainable decision boundaries (NFR-050)
- Admin UI must respond in under 200ms (NFR-051)
- External partner integrations must use OAuth2.0 (NFR-052)
- Compliance reporting must be generated monthly (NFR-053)
- Feature flags must have instant rollback capability (NFR-054)

**Scale/Scope**: Builds on existing telco platform with 220 prior test mappings (TM001–TM220); extends to TM260–TM277 for phase 8 features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Art. I — Specification First
- **Pass**: Spec approved and complete (build-phase8/spec.md); all FRs, NFRs, success criteria, assumptions, and edge cases documented

### Art. II — Domain Ownership and Service Boundaries
- **Pass**: New analytics endpoints extend existing API gateway; partner integration framework uses documented APIs per Art. VI; admin UI enhancements use existing role-based access framework; AI/ML features built on existing OpenTelemetry telemetry data; compliance reports generated from existing data models and logging; feature flags build on existing infrastructure
- **Constraint**: No new service ownership — all features extend existing services (auth-service, crm-service, billing-service, inventory-service)

### Art. III — Security and Privacy by Design
- **Pass**: AI-powered features require explainable decision boundaries (NFR-050); external partner integrations use OAuth2.0 (NFR-052); compliance reporting covers SOC2, GDPR (NFR-053); feature flags have instant rollback (NFR-054); edge cases addressed for missing metadata, model staleness, partner API changes, data gaps, rollback conflicts

### Art. VI — API and Integration Contracts
- **Pass**: Advanced API endpoints documented in contracts/advanced_api_contract.md; partner integration framework with standardized authentication, routing, and monitoring; compliance report endpoint with generate/read operations; feature flag lifecycle endpoints (CRUD + toggle)

### Art. VII — Testing and Verifiability
- **Pass**: All success criteria are measurable and technology-agnostic (SC-01 through SC-05); edge cases explicitly identified (5 cases); acceptance criteria defined for all 6 FRs; traceability from TM260–TM277

### Art. VIII — Observability and Operability
- **Pass**: AI anomaly detection requires model training and validation pipeline; feature flags require instant rollback tracking; compliance reports require monthly generation verification; admin UI performance monitoring; analytics endpoints require telemetry integration

**Constitution Check: ALL GATES PASS** ✅ — Re-check after Phase 1 design identical

## Project Structure

### Documentation (this feature)

```text
specs/008-build-phase8/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── advanced_api_contract.md
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── main.py                       # FastAPI application and router wiring
├── database.py                   # Engine, session factory and schema creation
├── security.py                   # Bearer authentication dependency
├── api/
│   └── endpoints/
│       └── analytics.py          # Advanced analytics endpoints (US1)
├── router/
│   └── analytics.py              # Analytics router (US1)
├── models/
│   ├── analytics_event.py        # AnalyticsEvent entity (US1)
│   └── feature_flag.py           # FeatureFlag entity (US5)
├── middleware/                   # Request middleware (US3)
└── services/                     # Domain services (US2)

tests/
├── contract/                     # API surface contracts
├── integration/                  # Cross-component flows
└── unit/                         # Isolated units
```

The remaining user stories are not yet implemented; their intended locations
follow the same layout:

| Story | Intended location |
|---|---|
| US2 — AI model metrics and anomaly detection | `src/models/ai_model_metrics.py`, `src/services/anomaly_detection.py`, `src/api/endpoints/ai_metrics.py` |
| US3 — Admin surface with role-based access | `src/models/admin_role.py`, `src/middleware/admin.py`, `src/api/endpoints/admin.py` |
| US4 — Partner integrations | `src/models/partner_integration.py`, `src/api/endpoints/partner.py` |
| US5 — Compliance reporting | `src/models/compliance_report.py`, `src/api/endpoints/compliance.py`, `src/api/endpoints/feature_flags.py` |

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | The phase introduces no new service, no new runtime network endpoint and no new database object, so every constitution gate passes without a justified exception |
