# Success Criteria Contract

**Purpose**: Define and verify success criteria for the build phase 1 feature.

**Success Criteria**:
- SC-001: Fresh clone to verified state ≤ 30 minutes
- SC-005: Full required-check set ≤ 5 minutes on CI; fast lane ≤ 2 minutes
- SC-004: Local check run ≤ 3 minutes excluding cold dependency resolution
- SC-002: Constitution Article I.1 gate must pass before user story work begins
- SC-003: Constitution ratified and specification approved

**Verification Methods**:
- timed fresh clone from repository
- run nox fast-checks and measure duration
- measure local check run duration
- check constitution gate status in .specify/memory/constitution.md
- check approval status in specification

**Metrics Collection**:
- Use make timing targets
- Record durations in logs
- Compare against SC thresholds
