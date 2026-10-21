# build-phase6: Quickstart

## Prerequisites
- Docker and Docker Compose installed
- Python 3.13+ (via `.python-version`)
- `uv` package manager
- Prometheus and Grafana already running (from prior phases)
- OpenTelemetry Collector and Jaeger already running (from prior phases)
- Istio service mesh installed (from prior phases)

## Setup

### 1. Verify Prior Phases
```bash
# Ensure all prior phases are operational
make check

# Verify Prometheus is running
curl -s http://localhost:9090/-/healthy

# Verify Grafana is running
curl -s http://localhost:3000/api/health

# Verify Jaeger is running
curl -s http://localhost:14268/api/traces/ns/default

# Verify Istio is running
istioctl version --output=short
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Configure Log Aggregation (Loki)
```bash
# Configure Loki via Helm or manifest
# Ensure Loki is scraping from all service containers
# Configure Prometheus to scrape Loki metrics

# Add Loki data source to Grafana
# http://localhost:3100 (default Loki port)

# Add Prometheus data source to Grafana
# http://localhost:9090 (default Prometheus port)
```

### 3. Configure Alerting (Alertmanager)
```bash
# Configure Alertmanager routing rules
# Add email, Slack, and PagerDuty notification channels
# Test alert firing with `alertmanager test`

# Configure Alertmanager webhook
# http://internal.company.com/api/alerts
```

### 4. Configure Tracing (OpenTelemetry)
```bash
# Ensure OpenTelemetry Collector is configured
# with Jaeger exporter pointing to prior phase setup
# Verify trace propagation across all services

# Verify trace propagation
# Use Jaeger UI at http://localhost:14268
# Trace a request through all services
```

### 5. Configure Service Mesh (Istio)
```bash
# Verify Istio is installed and operational
istioctl experimental mesh-status

# Verify sidecar proxies are injecting
# Check envoy metrics at http://localhost:15020/metrics

# Configure observability budgets
# istioctl experimental mesh observe budgets
```

### 5. Configure Runbooks
```bash
# Add runbooks to the internal runbook repository
# Reference runbooks from alert notifications
# Test runbook execution for common scenarios

# Add runbook links to Grafana dashboards
# Add runbook links to alert notifications
```

### 6. Verification
```bash
# Log aggregation search test
curl -s "http://localhost:3100/api/loki/api/v1/search?query={service%22%22} | json | .message | contains%22error%22" | head -5

# Metrics exposition test
curl -s http://localhost:9090/metrics | head -20

# Alert test
istioctl experimental alert test --name service_error_rate_high

# Tracing test
# Use Jaeger UI to trace a request through all services

# Runbook test
# Reference runbooks from alert notifications
```

## SDK Usage (OpenTelemetry)

### Python - Log Aggregation
```python
from openteleiler import trace
from openteleiler.sdk import TracerProvider
from openteleiler.sdk.export import BatchSpanProcessor
from openteleiler.exporter.jaeger.thrift import JaegerExporter

# Configure tracer provider
resource = Resource.create({"service.name": "telco-platform"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(JaegerExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Create a span
with tracer.start_as_current_span("operation_name") as span:
    span.set_attribute("service.name", "telco-platform")
    span.set_attribute("operation.name", "operation_name")
    # ... business logic
```

### Python - Metrics
```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
REQUESTS_TOTAL = Counter('service_requests_total', 'Total requests per service')
REQUEST_DURATION = Histogram('service_request_duration_seconds', 'Request latency per service')
ERRORS_TOTAL = Counter('service_errors_total', 'Total errors per service')

# Start HTTP server
start_http_server(8000)

# Increment metrics in request handler
REQUESTS_TOTAL.inc()
REQUEST_DURATION.observe(latency)
if error:
    ERRORS_TOTAL.inc()
```

### Python - Alert Rules
```python
# Define alert rule in Prometheus format
alert_rule = """
  - alert: service_error_rate_high
    expr: sum(rate(service_errors_total[5m])) > 0.5
    for: 5m
    labels:
      severity: critical
      team: backend
    annotations:
      summary: "Error rate above threshold"
      description: "Error rate has been above threshold"
      runbook_url: "http://internal/runbooks/service-error-rate"
"""
```

## Verification Checklist
- [ ] Log aggregation search returns results in under 2 seconds
- [ ] Prometheus metrics exposition working at `/metrics`
- [ ] Alert notifications delivered to correct channels within 1 minute
- [ ] Tracing propagation visible across all service call chains
- [ ] Service mesh metrics collected and visible in Istio dashboards
- [ ] Runbooks created for 3 common incident scenarios
- [ ] Performance anomaly detection alerts operational
- [ ] All dashboards operational and displaying correct data
