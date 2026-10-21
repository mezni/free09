# build-phase10: Advanced API Contract

## Build Stages

### List Build Stages
```
GET /api/v1/build-stages
```
- **Parameters**: `stage_type` (optional), `status` (optional), `optimization_score_min` (optional), `page` (optional), `page_size` (optional)
- **Response**: Paged list of BuildStage objects

### Get Build Stage
```
GET /api/v1/build-stages/{stage_id}
```
- **Response**: BuildStage object

### Create Build Stage
```
POST /api/v1/build-stages
```
- **Request**: { stage_name, stage_type, optimization_score_min?, metadata? }
- **Response**: Created BuildStage object

### Update Build Stage
```
PATCH /api/v1/build-stages/{stage_id}
```
- **Request**: { status, end_timestamp, optimization_score, metadata? }
- **Response**: Updated BuildStage object

### Delete Build Stage
```
DELETE /api/v1/build-stages/{stage_id}
```

## Build Gates

### List Build Gates
```
GET /api/v1/build-gates
```
- **Parameters**: `gate_name` (optional), `is_active` (optional), `gate_timeout_max` (optional)
- **Response**: List of BuildGate objects

### Get Build Gate
```
GET /api/v1/build-gates/{gate_id}
```
- **Response**: BuildGate object

### Create Build Gate
```
POST /api/v1/build-gates
```
- **Request**: { gate_name, gate_criteria, gate_timeout, is_active }
- **Response**: Created BuildGate object

### Update Build Gate
```
PATCH /api/v1/build-gates/{gate_id}
```
- **Request**: { gate_criteria, gate_timeout, is_active }
- **Response**: Updated BuildGate object

### Delete Build Gate
```
DELETE /api/v1/build-gates/{gate_id}
```

## Build Versions

### List Build Versions
```
GET /api/v1/build-versions
```
- **Parameters**: `is_release` (optional), `stage_id` (optional), `optimization_score_min` (optional), `page` (optional), `page_size` (optional)
- **Response**: Paged list of BuildVersion objects

### Get Build Version
```
GET /api/v1/build-versions/{version_id}
```
- **Response**: BuildVersion object

### Create Build Version
```
POST /api/v1/build-versions
```
- **Request**: { version_string, base_version, stage_id, is_release, optimization_score, metadata? }
- **Response**: Created BuildVersion object

### Update Build Version
```
PATCH /api/v1/build-versions/{version_id}
```
- **Request**: { optimization_score, metadata? }
- **Constraint**: metadata must not modify immutable fields per NFR-073

### Delete Build Version
```
DELETE /api/v1/build-versions/{version_id}
```

## External Deployment Systems

### List External Deployment Systems
```
GET /api/v1/external-deployment-systems
```
- **Parameters**: `system_name` (optional), `auth_method` (optional), `status` (optional)
- **Response**: List of ExternalDeploymentSystem objects

### Get External Deployment System
```
GET /api/v1/external-deployment-systems/{integration_id}
```
- **Response**: ExternalDeploymentSystem object

### Create External Deployment System
```
POST /api/v1/external-deployment-systems
```
- **Request**: { system_name, api_endpoint, auth_method, metadata? }
- **Response**: Created ExternalDeploymentSystem object

### Update External Deployment System
```
PATCH /api/v1/external-deployment-systems/{integration_id}
```
- **Request**: { status, metadata? }

### Delete External Deployment System
```
DELETE /api/v1/external-deployment-systems/{integration_id}
```

## Performance Metrics

### Get Performance Metrics
```
GET /api/v1/performance-metrics
```
- **Parameters**: `stage_id` (optional), `start_time` (optional), `end_time` (optional), `metric_type` (optional, e.g., "duration", "optimization_score", "throughput")
- **Response**: Performance metrics data

### Record Performance Metrics
```
POST /api/v1/performance-metrics
```
- **Request**: { stage_id, metric_type, metric_value, metadata? }
- **Response**: Recorded performance metric

## Version Lifecycle

### Version Lifecycle Endpoints
- **Create**: POST /api/v1/build-versions
- **Read**: GET /api/v1/build-versions/{version_id}
- **Update**: PATCH /api/v1/build-versions/{version_id}
- **Delete**: DELETE /api/v1/build-versions/{version_id}

### Version States
- **Draft**: is_release=false, no release_timestamp
- **Released**: is_release=true, release_timestamp set, metadata immutable per NFR-073
- **Optimized**: optimization_score improved from prior version
- **Archived**: version removed from active pipeline but retained for audit
