# build-phase6: Monitoring Contract

## Log Aggregation Contract

### Loki Log Queries
- **Search query**: `{service="auth-service"} | json | .message | contains "error"`
- **Range vector**: `~{service="auth-service"} | json | .level |= "error" [5m]`
- **Result expansion**: `{service="auth-service"} | json | .message`

### Log Aggregation API
- **Endpoint**: `POST /api/v1/search-logs`
- **Request**: `{"query": "<loki_promql>", "time_range": "<start_time>-<end_time>"}`
- **Response**: Array of log entries with fields: `log_entry_id`, `service`, `level`, `message`, `timestamp`, `request_id`, `trace_id`, `attributes`

### Log Retention
- **Retention period**: 90 days
- **Compaction**: Daily at 02:00 UTC
- **Deleted entries**: Marked as deleted, physically removed during compaction

## Metrics Contract

### Prometheus Metrics Exposition
- **Endpoint**: `GET /metrics`
- **Format**: OpenMetrics text format
- **Must expose metrics for**: All services, system resources, business metrics

### Key Metrics
- `service_requests_total`: Counter - total requests per service
- `service_request_duration_seconds`: Histogram - request latency per service
- `service_errors_total`: Counter - total errors per service
- `otel_spans_created_total`: Counter - total OpenTelemetry spans created
- `otel_spans_exported_successful_total`: Counter - successfully exported spans

### Metrics Refresh
- **Scrape interval**: 15 seconds
- **Metrics endpoint must respond**: In under 10ms
- **Metric freshness**: Within 30 seconds of update

## Alert Contract

### Alert Rule Format
- **Alert name**: `service_error_rate_high`
- **Query**: `sum(rate(service_errors_total{service=~"$service"}[5m])) > 0.5`
- **For**: `5m`
- **Labels**: `severity=critical`, `team=backend`
- **Annotations**: 
  - `summary`: "Error rate above threshold for service {{ $labels.service }}"
  - `description`: "Error rate has been above 0.5 errors per second for the last 5 minutes"
  - `runbook_url`: "http://internal/runbooks/service-error-rate"

### Notification Channels
- **Email**: `team-alerts@company.com`
- **Slack**: `#team-alerts` channel
- **PagerDuty**: Critical alerts only
- **Webhook**: `https://internal.company.com/api/alerts`

### Alert Deduplication
- **Group by**: [`alertname`, `instance`, `job`]
- **Group wait**: `5m`
- **Group pause**: `1h`
- **Repeat interval**: `4h`

## Tracing Contract

### OpenTelemetry Propagation
- **Header**: `traceparent: <trace-id>\t<span-id>\t<trace-flags>\t<trace-state>`
- **Header**: `x-request-id: <uuid>`
- **Propagation**: W3C Trace Context across service boundaries

### Trace Exporter
- **Endpoint**: `http://jaeger:14268/api/traces`
- **Headers**: `Content-Type: application/json`
- **Batch**: `true` (export in batches of 100 spans)
- **Timeout**: `30s`

### Trace Visualization
- **Jaeger UI**: `http://localhost:14268`
- **Grafana Tempo**: `http://localhost:3200`
- **Span filters**: `service.name`, `operation.name`, `status_code`

## Service Mesh Contract

### Istio Observability
- **Pilot metrics endpoint**: `http://istio-pilot:15014/metrics`
- **Sidecar metrics endpoint**: `http://localhost:15020/metrics`
- **Control plane metrics**: Collected by Prometheus

### Service Mesh Metrics
- `istio_requests_total`: Total requests per service per destination
- `istio_requests_size`: Request size per service per destination
- `istio_requests_duration_ms`: Request latency per service per destination
- `istio_tcp_sent_bytes_total`: Total bytes sent per service per destination
- `istio_tcp_received_bytes_total`: Total bytes received per service per destination

### Service Mesh Health
- **Sidecar health check**: `http://localhost:15020/healthz`
- **Pilot health check**: `http://istio-pilot:15014/healthz`
- **Mesh wide health**: `istio-proxy health`

## Runbook Contract

### Runbook Format
- **Title**: Descriptive incident title
- **Scenario**: Description of the incident situation
- **Steps**: Ordered list of resolution procedures
- **Author**: Runbook creator
- **Last reviewed**: Date of last review

### Runbook API
- **Endpoint**: `GET /api/v1/runbooks/{runbook_id}`
- **Response**: Runbook object with title, scenario, steps, author, created_at, updated_at
- **Endpoint**: `POST /api/v1/runbooks`
- **Request**: Runbook object
- **Endpoint**: `PUT /api/v1/runbooks/{runbook_id}`
- **Request**: Updated runbook object

### Runbook Execution
- **Trigger**: From alert notifications or incident management system
- **Steps**: Follow step-by-step procedures
- **Post-run**: Update runbook status and add lessons learned

## Versioning
- **Monitoring API version**: v1.0.0 (current)
- **Runbook version**: v1.0.0 (current)
- **Backward compatibility**: Minor version updates maintain compatibility
- **Major version changes**: Require deprecation period and migration guide
