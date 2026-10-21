# build-phase10: Data Model

## Build Pipeline Stages

### BuildStage
- `stage_id`: UUID (primary key)
- `stage_name`: string (e.g., "compile", "test", "package", "scan", "optimize")
- `stage_type`: string (e.g., "compile", "test", "package", "scan", "optimize", "deploy")
- `status`: string (e.g., "pending", "running", "completed", "failed", "optimized")
- `start_timestamp`: datetime (auto-now)
- `end_timestamp`: datetime (optional)
- `duration`: float (computed: end - start)
- `optimization_score`: float (0.0–1.0, new for phase 10, NFR-074)
- `metadata`: JSONB (arbitrary key-value pairs)

### BuildGate
- `gate_id`: UUID (primary key)
- `gate_name`: string (e.g., "compliance-gate", "security-gate", "performance-gate")
- `gate_criteria`: JSONB (validation rules and thresholds)
- `gate_timeout`: integer (seconds, NFR-071, 20s for compliance)
- `is_active`: boolean (whether gate is active)
- `created_at`: datetime (auto-now)
- `updated_at`: datetime (auto-now)

### BuildVersion
- `version_id`: UUID (primary key)
- `version_string`: string (e.g., "1.0.0", "10.0.0-alpha")
- `base_version`: UUID (references prior version)
- `stage_id`: UUID (references the build stage where version was created)
- `is_release`: boolean (whether this is a released version)
- `release_timestamp`: datetime (optional)
- `optimization_score`: float (0.0–1.0, inherited from stage, NFR-074)
- `metadata`: JSONB (immutable version metadata, NFR-073)
- `created_at`: datetime (auto-now)

### ExternalDeploymentSystem
- `integration_id`: UUID (primary key)
- `system_name`: string (e.g., "jenkins", "gitlab-ci", "azure-devops", "circleci")
- `api_endpoint`: string (system endpoint URL)
- `auth_method`: string (e.g., "OAuth2.0", "API Key", "Bearer Token", "SSH Key")
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
- `UNIQUE` on `ExternalDeploymentSystem.integration_id`
- Index on `BuildStage.stage_type`
- Index on `BuildStage.status`
- Index on `BuildStage.optimization_score`
- Index on `BuildGate.gate_name`
- Index on `BuildGate.is_active`
- Index on `BuildVersion.is_release`
- Index on `BuildVersion.stage_id`
- Index on `BuildVersion.optimization_score`
- Index on `ExternalDeploymentSystem.status`
- Index on `ExternalDeploymentSystem.auth_method`

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
      "optimization_score": {"type": "float"},
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
      "optimization_score": {"type": "float"},
      "metadata": {"type": "object"}
    }
  },
  "ExternalDeploymentSystem": {
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
