# build-phase9: Quickstart

## Prerequisites
- All build phases complete (build-phase1 through build-phase8)
- Docker and Docker Compose installed
- Access to existing build infrastructure
- `.python-version` or equivalent for build tooling

## Setup

### 1. Verify Prior Phases Complete
```bash
# Ensure all prior phases are operational
make check

# Verify existing infrastructure
make docker-up
```

### 2. Install Dependencies
```bash
# Install build phase 9 dependencies
uv sync
```

### 3. Configure Build Pipeline Stages
```bash
# Configure pipeline stages in existing build system
# Ensure phase gate validation is configured

# Ensure phase documentation framework is configured
# Ensure external build system integration is configured

# Ensure compliance report generation is configured

# Ensure version metadata framework is configured
```

### 3. Install Dependencies
```bash
uv sync --frozen
```

### 4. Run Build Pipeline Stages
```bash
# Test pipeline stages
# List available stages
curl -s http://localhost:8000/api/v1/build-stages

# Create a new stage
curl -s -X POST http://localhost:8000/api/v1/build-stages \
  -d '{"stage_name": "scan", "stage_type": "security"}'

# Get stage status
curl -s http://localhost:8000/api/v1/build-stages/{stage_id}
```

### 5. Phase Gate Validation
```bash
# Test phase gate validation
# List available gates
curl -s http://localhost:8000/api/v1/build-gates

# Create a new gate
curl -s -X POST http://localhost:8000/api/v1/build-gates \
  -d '{"gate_name": "quality-gate", "gate_criteria": {"max_duration": 30}, "gate_timeout": 30}'

# Validate a stage against gates
curl -s http://localhost:8000/api/v1/build-gates/{gate_id}/validate/{stage_id}
```

### 6. External Build System Integration
```bash
# Test external build system integration
# List available systems
curl -s http://localhost:8000/api/v1/external-build-systems

# Create a new system integration
curl -s -X POST http://localhost:8000/api/v1/external-build-systems \
  -d '{"system_name": "jenkins", "api_endpoint": "https://jenkins.example.com", "auth_method": "OAuth2.0"}'

# Get system status
curl -s http://localhost:8000/api/v1/external-build-systems/{integration_id}
```

### 7. Compliance Reporting
```bash
# Test compliance reporting
# Generate a compliance report
curl -s -X POST http://localhost:8000/api/v1/compliance-reports \
  -d '{"report_type": "build-compliance", "period_start": "2024-01-01", "period_end": "2024-12-31"}'

# Get compliance report
curl -s http://localhost:8000/api/v1/compliance-reports/{report_id}
```

### 8. Version Metadata Tracking
```bash
# Test version metadata tracking
# Create a version
curl -s -X POST http://localhost:8000/api/v1/build-versions \
  -d '{"version_string": "9.0.0", "base_version": null, "stage_id": "stage_id", "is_release": true}'

# Get version details
curl -s http://localhost:8000/api/v1/build-versions/{version_id}

# Attempt to modify metadata (should be blocked for released versions)
curl -s -X PATCH http://localhost:8000/api/v1/build-versions/{version_id} \
  -d '{"metadata": {"attempted": "modification"}}'
```

### 9. Verification
```bash
# Final verification
# Run all verification checks
# Ensure all build-phase9 features are operational
```
