# build-phase11: Quickstart

## Prerequisites
- All build phases complete (build-phase1 through build-phase10)
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
# Install build phase 11 dependencies
uv sync
```

### 3. Configure Build Pipeline Reporting Stages
```bash
# Configure pipeline reporting stages in existing build system
# Ensure phase gate statistical analysis is configured with 15s timeout (NFR-081)

# Ensure phase dashboard and visualization framework is configured

# Ensure external monitoring system integration is configured

# Ensure compliance and statistical process control report generation is configured

# Ensure trend analysis framework is configured (NFR-084, <3% overhead)
```

### 3. Install Dependencies
```bash
uv sync --frozen
```

### 4. Run Pipeline Reporting Stages
```bash
# Test pipeline reporting stages
# List available stages
curl -s http://localhost:8000/api/v1/build-stages

# Create a new reporting stage
curl -s -X POST http://localhost:8000/api/v1/build-stages \
  -d '{"stage_name": "report", "stage_type": "statistical"}'

# Get stage status with report data
curl -s http://localhost:8000/api/v1/build-stages/{stage_id}
```

### 5. Phase Gate Statistical Analysis
```bash
# Test phase gate statistical analysis
# List available gates
curl -s http://localhost:8000/api/v1/build-gates

# Create a new statistical gate (15s timeout per NFR-081)
curl -s -X POST http://localhost:8000/api/v1/build-gates \
  -d '{"gate_name": "statistical-gate", "gate_criteria": {"max_duration": 15}, "gate_timeout": 15}'

# Validate a stage against gates
curl -s http://localhost:8000/api/v1/build-gates/{gate_id}/validate/{stage_id}
```

### 6. External Monitoring System Integration
```bash
# Test external monitoring system integration
# List available systems
curl -s http://localhost:8000/api/v1/external-monitoring-systems

# Create a new system integration
curl -s -X POST http://localhost:8000/api/v1/external-monitoring-systems \
  -d '{"system_name": "prometheus", "api_endpoint": "https://prometheus.example.com", "auth_method": "OAuth2.0"}'

# Get system status
curl -s http://localhost:8000/api/v1/external-monitoring-systems/{integration_id}
```

### 7. Compliance and Statistical Process Control Reporting
```bash
# Test compliance and statistical process control reporting
# Generate a compliance report
curl -s -X POST http://localhost:8000/api/v1/compliance-reports \
  -d '{"report_type": "build-spc", "period_start": "2024-01-01", "period_end": "2024-12-31"}'

# Get compliance report with statistical charts
curl -s http://localhost:8000/api/v1/compliance-reports/{report_id}
```

### 8. Trend Analysis
```bash
# Test trend analysis
# Get trend analysis data
curl -s "http://localhost:8000/api/v1/performance-metrics?stage_id={stage_id}&metric_type=report_data"

# Record a trend metric
curl -s -X POST http://localhost:8000/api/v1/performance-metrics \
  -d '{"stage_id": "{stage_id}", "metric_type": "report_data", "metric_value": 0.85}'

# Get trend analysis overview
curl -s "http://localhost:8000/api/v1/performance-metrics?metric_type=report_data"
```

### 9. Version Tracking
```bash
# Test version metadata tracking
# Create a version
curl -s -X POST http://localhost:8000/api/v1/build-versions \
  -d '{"version_string": "11.0.0", "base_version": null, "stage_id": "stage_id", "is_release": true}'

# Get version details
curl -s http://localhost:8000/api/v1/build-versions/{version_id}

# Attempt to modify metadata on released version (should be blocked per phase 11 conventions)
curl -s -X PATCH http://localhost:8000/api/v1/build-versions/{version_id} \
  -d '{"metadata": {"attempted": "modification"}}'
```

### 10. Verification
```bash
# Final verification
# Run all verification checks
# Ensure all build-phase11 features are operational
```
