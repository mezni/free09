# build-phase10: Quickstart

## Prerequisites
- All build phases complete (build-phase1 through build-phase9)
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
# Install build phase 10 dependencies
uv sync
```

### 3. Configure Build Pipeline Optimization Stages
```bash
# Configure pipeline optimization stages in existing build system
# Ensure phase gate compliance validation is configured with 20s timeout (NFR-071)

# Ensure phase traceability and reporting framework is configured

# Ensure external deployment system integration is configured

# Ensure compliance and audit report generation is configured

# Ensure performance metrics framework is configured (NFR-074, <5% overhead)
```

### 3. Install Dependencies
```bash
uv sync --frozen
```

### 4. Run Pipeline Optimization Stages
```bash
# Test pipeline optimization stages
# List available stages
curl -s http://localhost:8000/api/v1/build-stages

# Create a new optimization stage
curl -s -X POST http://localhost:8000/api/v1/build-stages \
  -d '{"stage_name": "optimize", "stage_type": "performance"}'

# Get stage status with optimization score
curl -s http://localhost:8000/api/v1/build-stages/{stage_id}
```

### 5. Phase Gate Compliance Validation
```bash
# Test phase gate compliance validation
# List available gates
curl -s http://localhost:8000/api/v1/build-gates

# Create a new compliance gate (20s timeout per NFR-071)
curl -s -X POST http://localhost:8000/api/v1/build-gates \
  -d '{"gate_name": "compliance-gate", "gate_criteria": {"max_duration": 20}, "gate_timeout": 20}'

# Validate a stage against gates
curl -s http://localhost:8000/api/v1/build-gates/{gate_id}/validate/{stage_id}
```

### 6. External Deployment System Integration
```bash
# Test external deployment system integration
# List available systems
curl -s http://localhost:8000/api/v1/external-deployment-systems

# Create a new system integration
curl -s -X POST http://localhost:8000/api/v1/external-deployment-systems \
  -d '{"system_name": "jenkins", "api_endpoint": "https://jenkins.example.com", "auth_method": "OAuth2.0"}'

# Get system status
curl -s http://localhost:8000/api/v1/external-deployment-systems/{integration_id}
```

### 7. Compliance and Audit Reporting
```bash
# Test compliance and audit reporting
# Generate a compliance report
curl -s -X POST http://localhost:8000/api/v1/compliance-reports \
  -d '{"report_type": "build-audit", "period_start": "2024-01-01", "period_end": "2024-12-31"}'

# Get compliance report with audit trail
curl -s http://localhost:8000/api/v1/compliance-reports/{report_id}
```

### 8. Performance Metrics
```bash
# Test performance metrics
# Get performance metrics
curl -s "http://localhost:8000/api/v1/performance-metrics?stage_id={stage_id}&metric_type=duration"

# Record a performance metric
curl -s -X POST http://localhost:8000/api/v1/performance-metrics \
  -d '{"stage_id": "{stage_id}", "metric_type": "duration", "metric_value": 45.2}'

# Get optimization score trend
curl -s "http://localhost:8000/api/v1/performance-metrics?metric_type=optimization_score"
```

### 9. Version Tracking
```bash
# Test version metadata tracking
# Create a version
curl -s -X POST http://localhost:8000/api/v1/build-versions \
  -d '{"version_string": "10.0.0", "base_version": null, "stage_id": "stage_id", "is_release": true}'

# Get version details
curl -s http://localhost:8000/api/v1/build-versions/{version_id}

# Attempt to modify metadata on released version (should be blocked per NFR-073)
curl -s -X PATCH http://localhost:8000/api/v1/build-versions/{version_id} \
  -d '{"metadata": {"attempted": "modification"}}'
```

### 10. Verification
```bash
# Final verification
# Run all verification checks
# Ensure all build-phase10 features are operational
```
