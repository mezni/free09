# Data Model: build-phase1

## Entities

### Constitution Principle
- **Name**: specification_principle
- **Fields**: id, principle_text, article_reference, status, approval_date
- **Relationships**: mapped_to_article (1:1 with docs/constitution.md Art. I-XI)
- **Validation rules**: principle_text required, article_reference must reference existing article, status must be one of [Proposed, Accepted, Deferred]
- **State transitions**: Proposed → Accepted → Deferred

### Constitution Article
- **Name**: specification_article
- **Fields**: article_number, title, principle_count, status, ratification_date
- **Relationships**: mapped_principle (1:1 with specification_principle), governance_record (1:1 .specify/memory/constitution.md)
- **Validation rules**: article_number required in format Art. I-XI, title required, status must be one of [Proposed, Accepted]
- **State transitions**: Proposed → Accepted

### Research Decision
- **Name**: research_decision
- **Fields**: decision_id, decision_text, rationale, alternatives_considered, status
- **Relationships**: related_articles (0:n with specification_article), generated_artifacts (0:n)
- **Validation rules**: decision_text required, rationale required, status must be one of [Accepted, Deferred]

### User Scenario
- **Name**: onboarding_scenario
- **Fields**: scenario_id, scenario_text, steps, status
- **Relationships**: tested_artifacts (0:n)
- **Validation rules**: scenario_text required, steps required, status must be one of [Pass, Fail]

## Relationships

### specification_principle --1:1--> specification_article
- Each principle maps to exactly one article

### specification_article --1:n--> research_decision
- Each article can have multiple research decisions

### research_decision --0:n--> onboarding_scenario
- Each research decision can be tested by multiple scenarios

## Validation Rules from Requirements
- BR-011: No application database objects created in Phase 0
- BR-012: Tooling does not change the Python FastAPI on PostgreSQL baseline
- Constitution Article I.1: Implementation only against approved specification
- All entities tracked in .specify/memory/constitution.md

## Notes
- No application database objects created (BR-011)
- Constitution governed by .specify/memory/constitution.md v1.0.0
- Clause references use numbered form from docs/constitution.md
