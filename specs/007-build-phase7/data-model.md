# build-phase7: Data Model

## Finalization Entities

### ProjectStatus
- `project_id`: UUID (primary key)
- `version`: string (e.g., "1.0.0")
- `status`: string (Proposed, Implemented, Deprecated)
- `last_updated`: datetime (auto-now)
- `updated_by`: string (who last updated the status)

### ConstitutionArticle
- `article_id`: UUID (primary key)
- `article_number`: integer (1–11)
- `title`: string (e.g., "Specification First")
- `status`: string (Proposed, Implemented, Deprecated)
- `ratification_date`: date
- `updated_by`: string
- `approval_record`: text (signatures and dates)

### TraceMapping
- `mapping_id`: UUID (primary key)
- `mapping_number`: integer (1–220)
- `source`: string (e.g., "FR-001", "BR-010", "AC-001", "SC-001")
- `target`: string (e.g., "spec.md", "tasks.md", "constitution.md")
- `status`: string (Mapped, Partial, NotMapped)
- `mapped_date`: datetime
- `mapped_by`: string

### HandoffDocumentation
- `document_id`: UUID (primary key)
- `title`: string (e.g., "SPEC-001 Completion Report")
- `content`: text (full documentation content)
- `version`: string (e.g., "1.0.0")
- `created`: datetime (auto-now)
- `updated`: datetime (auto-now-on-update)
- `distributed_to`: string (who received the documentation)
- `distribution_date`: datetime

### VerificationResult
- `verification_id`: UUID (primary key)
- `phase`: integer (1–6)
- `status`: string (Pass, Fail, Inconclusive)
- `checked_at`: datetime (auto-now)
- `checked_by`: string
- `details`: text (verification details)
- `screenshot_url`: string (optional, path to verification screenshot)

## Relationships
- **ProjectStatus → ConstitutionArticle**: One-to-Many (one project status with multiple constitution articles)
- **ProjectStatus → TraceMapping**: One-to-Many (one project status with multiple trace mappings)
- **ProjectStatus → HandoffDocumentation**: One-to-Many (one project status with multiple hand-off documentation)
- **ProjectStatus → VerificationResult**: One-to-Many (one project status with multiple verification results)
- **TraceMapping → Source**: Many-to-One (multiple trace mappings can target the same source)
- **TraceMapping → Target**: Many-to-One (multiple trace mappings can target the same target)

## Indexes
- `UNIQUE` on `ProjectStatus.project_id`
- `UNIQUE` on `ConstitutionArticle.article_id`
- `UNIQUE` on `TraceMapping.mapping_id`
- `UNIQUE` on `HandoffDocumentation.document_id`
- `UNIQUE` on `VerificationResult.verification_id`
- Index on `ConstitutionArticle.status`
- Index on `TraceMapping.source`
- Index on `TraceMapping.target`
- Index on `HandoffDocumentation.version`
- Index on `VerificationResult.phase`

## JSON Schemas

```json
{
  "ProjectStatus": {
    "type": "object",
    "required": ["project_id", "version", "status", "last_updated"],
    "properties": {
      "project_id": {"type": "string", "format": "uuid"},
      "version": {"type": "string"},
      "status": {"type": "string", "enum": ["Proposed", "Implemented", "Deprecated"]},
      "last_updated": {"type": "string", "format": "date-time"},
      "updated_by": {"type": "string"}
    }
  },
  "ConstitutionArticle": {
    "type": "object",
    "required": ["article_id", "article_number", "title", "status", "ratification_date"],
    "properties": {
      "article_id": {"type": "string", "format": "uuid"},
      "article_number": {"type": "integer"},
      "title": {"type": "string"},
      "status": {"type": "string", "enum": ["Proposed", "Implemented", "Deprecated"]},
      "ratification_date": {"type": "string", "format": "date"},
      "updated_by": {"type": "string"},
      "approval_record": {"type": "string"}
    }
  },
  "TraceMapping": {
    "type": "object",
    "required": ["mapping_number", "source", "target", "status"],
    "properties": {
      "mapping_id": {"type": "string", "format": "uuid"},
      "mapping_number": {"type": "integer"},
      "source": {"type": "string"},
      "target": {"type": "string"},
      "status": {"type": "string", "enum": ["Mapped", "Partial", "NotMapped"]},
      "mapped_date": {"type": "string", "format": "date-time"},
      "mapped_by": {"type": "string"}
    }
  },
  "HandoffDocumentation": {
    "type": "object",
    "required": ["title", "content", "version", "created"],
    "properties": {
      "document_id": {"type": "string", "format": "uuid"},
      "title": {"type": "string"},
      "content": {"type": "text"},
      "version": {"type": "string"},
      "created": {"type": "string", "format": "date-time"},
      "updated": {"type": "string", "format": "date-time"},
      "distributed_to": {"type": "string"},
      "distribution_date": {"type": "string", "format": "date-time"}
    }
  },
  "VerificationResult": {
    "type": "object",
    "required": ["verification_id", "phase", "status", "checked_at"],
    "properties": {
      "verification_id": {"type": "string", "format": "uuid"},
      "phase": {"type": "integer", "minimum": 1, "maximum": 6},
      "status": {"type": "string", "enum": ["Pass", "Fail", "Inconclusive"]},
      "checked_at": {"type": "string", "format": "date-time"},
      "checked_by": {"type": "string"},
      "details": {"type": "text"},
      "screenshot_url": {"type": "string"}
    }
  }
}
```
