# build-phase8: Quickstart

## Prerequisites
- All build phases complete (build-phase1 through build-phase7)
- Docker and Docker Compose installed
- Python 3.13+ (via `.python-version`)
- `uv` package manager
- Access to existing telemetry and analytics pipeline

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
uv sync
```

### 3. Configure Advanced Analytics
```bash
# Configure analytics endpoints in existing API
# Ensure telemetry pipeline is capturing events

# Ensure AI/ML model training pipeline is operational
# Ensure admin UI role-based access is configured

# Ensure partner integration framework is configured
# Ensure compliance report generation is configured

# Ensure feature flag framework is configured
```

### 3. Install Dependencies
```bash
uv sync --frozen
```

### 4. Run Analytics Endpoints
```bash
# Test analytics endpoints
curl -s http://localhost:8000/api/v1/analytics/events

# Test AI model metrics
curl -s http://localhost:8000/api/v1/ai-model-metrics

# Test partner integrations
curl -s http://localhost:8000/api/v1/partner-integrations

# Test compliance reports
curl -s http://localhost:8000/api/v1/compliance-reports

# Test feature flags
curl -s http://localhost:8000/api/v1/feature-flags
```

### 5. AI Anomaly Detection
```bash
# Ensure AI/ML model training pipeline is operational
# Ensure anomaly detection is operational

# Test anomaly detection
# Use existing telemetry data to validate anomaly detection
```

### 6. Admin UI Enhancement
```bash
# Ensure admin UI role-based access is configured
# Ensure new roles and permissions are configured

# Test admin UI
# Navigate to admin UI and verify role-based access
```

### 7. Partner Integration
```bash
# Ensure partner integration framework is configured
# Ensure partner systems are registered

# Test partner integration
# Use partner API endpoints to verify integration
```

### 8. Compliance Reporting
```bash
# Ensure compliance report generation is configured
# Ensure monthly reports are generated

# Test compliance reporting
# Generate a compliance report and verify all required fields
```

### 9. Feature Flag Framework
```bash
# Ensure feature flag framework is configured
# Ensure instant rollback is operational

# Test feature flags
# Create, toggle, and rollback feature flags
```

### 10. Verification
```bash
# Final verification
# Run all verification checks
# Ensure all advanced features are operational
```

## SDK Usage (Phase 8 Features)

### Python - Analytics Events
```python
import requests

# Record an analytics event
event = {
    "event_type": "page_view",
    "service": "web-frontend",
    "endpoint": "/dashboard",
    "metadata": {"page_id": "abc123"}
}

response = requests.post(
    "http://localhost:8000/api/v1/analytics/events",
    json=event
)

# Get analytics events
response = requests.get(
    "http://localhost:8000/api/v1/analytics/events",
    params={"service": "web-frontend"}
)

# Get AI model metrics
response = requests.get(
    "http://localhost:8000/api/v1/ai-model-metrics",
    params={"model_id": "anomaly_detection_v1"}
)

# Get partner integrations
response = requests.get(
    "http://localhost:8000/api/v1/partner-integrations",
    params={"status": "active"}
)

# Get compliance reports
response = requests.get(
    "http://localhost:8000/api/v1/compliance-reports",
    params={"report_type": "SOC2",
             "period_start": "2024-01-01",
             "period_end": "2024-12-31"}
)

# Get feature flags
response = requests.get(
    "http://localhost:8000/api/v1/feature-flags",
    params={"is_active": True}
)

# Create a feature flag
response = requests.post(
    "http://localhost:8000/api/v1/feature-flags",
    json={"flag_name": "new_checkout_flow", "is_active": True, "rollout_percentage": 20}
)

# Toggle a feature flag
response = requests.patch(
    "http://localhost:8000/api/v1/feature-flags/flag_id",
    json={"is_active": False, "rollout_percentage": 0}
)
```

### Python - AI Model Metrics
```python
from sklearn.ensemble import IsolationForest
import numpy as np

# Train anomaly detection model
X = np.random.random((100, 5))
model = IsolationForest(contamination=0.1)
model.fit(X)

# Get model metrics
metrics = {
    "model_name": "anomaly_detection_v1",
    "accuracy": 0.95,
    "precision": 0.91,
    "recall": 0.89,
    "training_timestamp": "2024-01-15T10:00:00Z",
    "validity_until": "2025-01-15T10:00:00Z",
    "features_used": ["latency", "error_rate", "throughput"]
}
```

### Python - Partner Integration
```python
# Onboard a partner
partner = {
    "partner_name": "partner_abc",
    "api_endpoint": "https://api.partner.com",
    "auth_method": "OAuth2.0",
    "metadata": {"scope": "read_write"}
}

response = requests.post(
    "http://localhost:8000/api/v1/partner-integrations",
    json=partner
)

# Update partner status
response = requests.patch(
    "http://localhost:8000/api/v1/partner-integrations/integration_id",
    json={"status": "active", "metadata": {"last_contact": "2024-01-15T10:00:00Z"}}
)
```

### Python - Compliance Report
```python
# Generate a compliance report
report = {
    "report_type": "SOC2",
    "period_start": "2024-01-01",
    "period_end": "2024-12-31"
}

response = requests.post(
    "http://localhost:8000/api/v1/compliance-reports",
    json=report
)

# Get a compliance report
response = requests.get(
    "http://localhost:8000/api/v1/compliance-reports/report_id"
)

# Toggle a feature flag
response = requests.patch(
    "http://localhost:8000/api/v1/feature-flags/flag_id",
    json={"is_active": False, "rollout_percentage": 0}
)
```

### Python - Feature Flag
```python
# Create a feature flag
flag = {
    "flag_name": "new_checkout_flow",
    "is_active": True,
    "rollout_percentage": 20
}

response = requests.post(
    "http://localhost:8000/api/v1/feature-flags",
    json=flag
)

# Toggle a feature flag
response = requests.patch(
    "http://localhost:8000/api/v1/feature-flags/flag_id",
    json={"is_active": False, "rollout_percentage": 0}
)
```

## Verification Checklist
- [ ] Advanced API endpoints operational
- [ ] AI anomaly detection trained and validated
- [ ] Admin UI enhanced with role-based access
- [ ] External partner integration framework operational
- [ ] Compliance reports generated and verified
- [ ] Feature flags operational with instant rollback
- [ ] All SDK usage examples operational
