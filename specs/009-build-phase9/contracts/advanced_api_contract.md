# build-phase9: Advanced API Contract

## Build Stages

### List Build Stages
```
GET /api/v1/build-stages
```
- **Parameters**: `stage_type` (optional), `status` (optional), `page` (optional), `page_size` (optional)
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
- **Request**: { stage_name, stage_type, metadata? }
- **Response**: Created BuildStage object

### Update Build Stage
```
PATCH /api/v1/build-stages/{stage_id}
```
- **Request**: { status, end_timestamp, metadata? }
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
- **Parameters**: `gate_name` (optional), `is_active` (optional)
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
- **Parameters**: `is_release` (optional), `stage_id` (optional), `base_version` (optional), `page` (optional), `page_size` (optional)
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
- **Request**: { version_string, base_version, stage_id, is_release, metadata? }
- **Response**: Created BuildVersion object

### Update Build Version
```
PATCH /api/v1/build-versions/{version_id}
```
- **Request**: { metadata? }
- **Constraint**: metadata must not modify immutable fields per NFR-064

### Delete Build Version
```
DELETE /api/v1/build-versions/{version_id}
```

## External Build Systems

### List External Build Systems
```
GET /api/v1/external-build-systems
```
- **Parameters**: `status` (optional), `auth_method` (optional)
- **Response**: List of ExternalBuildSystem objects

### Get External Build System
```
GET /api/v1/external-build-systems/{integration_id}
```
- **Response**: ExternalBuildSystem object

### Create External Build System
```
POST /api/v1/external-build-systems
```
- **Request**: { system_name, api_endpoint, auth_method, metadata? }
- **Response**: Created ExternalBuildSystem object

### Update External Build System
```
PATCH /api/v1/external-build-systems/{integration_id}
```
- **Request**: { status, metadata? }

### Delete External Build System
```
DELETE /api/v1/external-build-systems/{integration_id}
```

## Version Lifecycle

### Version Lifecycle Endpoints
- **Create**: POST /api/v1/build-versions
- **Read**: GET /api/v1/build-versions/{version_id}
- **Update**: PATCH /api/v1/build-versions/{version_id}
- **Delete**: DELETE /api/v1/build-versions/{version_id}

### Version States
- **Draft**: is_release=false, no release_timestamp
- **Released**: is_release=true, release_timestamp set, metadata immutable
- **Archived**: version removed from active pipeline but retained for audit

## Versioning
- **API version**: /api/v1/ (current)
- **Version compatibility**: Maintained for minor version updates
- **Immutability**: Build version metadata (NFR-064) must not be modifiable after release
