# build-phase9: Data Model

## Build Pipeline Stages

### BuildStage
- `stage_id`: UUID (primary key)
- `stage_name`: string (e.g., "compile", "test", "package", "scan")
- `stage_type`: string (e.g., "compile", "test", "package", "scan", "deploy")
- `status`: string (e.g., "pending", "running", "completed", "failed")
- `start_timestamp`: datetime (auto-now)
- `end_timestamp`: datetime (optional)
- `duration`: float (computed: end - start)
- `metadata`: JSONB (arbitrary key-value pairs)

### BuildGate
- `gate_id`: UUID (primary key)
- `gate_name`: string (e.g., "quality-gate", "compliance-gate", "security-gate")
- `gate_criteria`: JSONB (validation rules and thresholds)
- `gate_timeout`: integer (seconds, NFR-061)
- `is_active`: boolean (whether gate is active)
- `created_at`: datetime (auto-now)
- `updated_at`: datetime (auto-now)

### BuildVersion
- `version_id`: UUID (primary key)
- `version_string`: string (e.g., "1.0.0", "9.0.0-alpha")
- `base_version`: UUID (references prior version)
- `stage_id`: UUID (references the build stage where version was created)
- `is_release`: boolean (whether this is a released version)
- `release_timestamp`: datetime (optional)
- `metadata`: JSONB (immutable version metadata, NFR-064)
- `created_at`: datetime (auto-now)

### ExternalBuildSystem
- `integration_id`: UUID (primary key)
- `system_name`: string (e.g., "jenkins", "gitlab-ci", "azure-devops")
- `api_endpoint`: string (system endpoint URL)
- `auth_method`: string (e.g., "OAuth2.0", "API Key", "Bearer Token")
- `status`: string (e.g., "active", "inactive", "pending")
- `last_contact`: datetime (when system last communicated)
- `metadata`: JSONB (system-specific configuration details)

## Relationships
- **BuildStage → BuildVersion**: One-to-Many (a stage can produce multiple version iterations; a version originates from one stage)
- **BuildGate → BuildStage**: Many-to-Many (a gate can evaluate multiple stages; a stage can be evaluated by multiple gates)
- **BuildVersion → BuildStage**: Many-to-One (a version is created in one stage; multiple versions can come from the same stage)
- **ExternalBuildSystem → BuildStage**: Many-to-Many (external systems can trigger/stages; a stage can interact with multiple systems)

## Indexes
- `UNIQUE` on `BuildStage.stage_id`
- `UNIQUE` on `BuildGate.gate_id`
- `UNIQUE` on `BuildVersion.version_id`
- `UNIQUE` on `ExternalBuildSystem.integration_id`
- Index on `BuildStage.stage_type`
- Index on `BuildStage.status`
- Index on `BuildGate.gate_name`
- Index on `BuildVersion.is_release`
- Index on `BuildVersion.stage_id`
- Index on `ExternalBuildSystem.status`
- Index on `ExternalBuildSystem.auth_method`

## JSON Schemas (for API integration)

```json
{
  "BuildStage": {
    "type": "object",
    "required": ["stage_name", "stage_type", "status"],
    "properties": {
      "stage_id": {"type": "string", "format": "uuid"},
      "stage_name": {"type": "string"},
      "stage_type": {"type": "string"},
      "status": {"type": "string"},
      "start_timestamp": {"type": "string", "format": "date-time"},
      "end_timestamp": {"type": "string", "format": "date-time"},
      "duration": {"type": "float"},
      "metadata": {"type": "object"}
    }
  },
  "BuildGate": {
    "type": "object",
    "required": ["gate_name", "gate_criteria", "gate_timeout"],
    "properties": {
      "gate_id": {"type": "string", "format": "uuid"},
      "gate_name": {"type": "string"},
      "gate_criteria": {"type": "object"},
      "gate_timeout": {"type": "integer"},
      "is_active": {"type": "boolean"},
      "created_at": {"type": "string", "format": "date-time"},
      "updated_at": {"type": "string", "format": "date-time"}
    }
  },
  "BuildVersion": {
    "type": "object",
    "required": ["version_string", "base_version", "stage_id", "is_release"],
    "properties": {
      "version_id": {"type": "string", "format": "uuid"},
      "version_string": {"type": "string"},
      "base_version": {"type": "string", "format": "uuid"},
      "stage_id": {"type": "string", "format": "uuid"},
      "is_release": {"type": "boolean"},
      "release_timestamp": {"type": "string", "format": "date-time"},
      "metadata": {"type": "object"}
    }
  },
  "ExternalBuildSystem": {
    "type": "object",
    "required": ["system_name", "api_endpoint", "auth_method", "status"],
    "properties": {
      "integration_id": {"type": "string", "format": "uuid"},
      "system_name": {"type": "string"},
      "api_endpoint": {"type": "string"},
      "auth_method": {"type": "string"},
      "status": {"type": "string"},
      "last_contact": {"type": "string", "format": "date-time"},
      "metadata": {"type": "object"}
    }
  }
}
```
