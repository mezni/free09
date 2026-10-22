# build-phase6: Quickstart

## Prerequisites
- Docker and Docker Compose installed
- Python 3.13+ (via `.python-version`)
- `uv` package manager

The monitoring stack is part of this repository. No prior Prometheus, Loki,
Alertmanager, Grafana or Istio installation is required for local verification.

## Setup

### 1. Verify the repository

```bash
uv sync
make verify
```

`make verify` runs the required fast and slow checks. The phase-6 contract
tests run as part of the slow lane; they can also be run directly:

```bash
uv run pytest tests/contract/test_monitoring_logs.py \
  tests/contract/test_monitoring_metrics.py \
  tests/contract/test_monitoring_alerts.py \
  tests/contract/test_monitoring_tracing_mesh.py \
  tests/contract/test_monitoring_runbooks.py \
  tests/contract/test_monitoring_stack.py -q
```

### 2. Start the monitoring overlay

```bash
docker compose -f deploy/compose/compose.yaml \
  -f deploy/compose/observability.yaml up -d
```

| Service | URL |
| --- | --- |
| Jaeger UI | http://localhost:16686 |
| Loki | http://localhost:3100 |
| Prometheus | http://localhost:9090 |
| Alertmanager | http://localhost:9093 |
| Grafana | http://localhost:3000 |

Grafana is provisioned with Prometheus and Loki data sources and the
`Telco Services` dashboard. Alertmanager uses placeholder notification
destinations; replace them before using the stack for real paging.

### 3. Configure log shipping

Set `TELECO_LOG_LOKI_URL=http://localhost:3100` for the service process, then
call the flush endpoint after exercising the service:

```bash
curl -s -X POST http://localhost:8000/api/v1/logs/flush
curl -s -X POST http://localhost:8000/api/v1/search-logs \
  -H 'content-type: application/json' \
  -d '{"query":"{service=\"auth-service\"} |= \"error\""}'
```

If Loki is unreachable the flush reports the failure and keeps entries
buffered; request handling is never blocked.

### 4. Inspect metrics and alerts

```bash
curl -s http://localhost:8000/metrics | head -30
curl -s http://localhost:9090/api/v1/rules | head
curl -s http://localhost:8000/api/v1/alerts
```

Prometheus scrapes every service on `/metrics` every 15 seconds and evaluates
`deploy/prometheus/alerts.yml`. Alertmanager groups by `alertname`, `instance`
and `job`, repeats after four hours, and routes critical alerts to PagerDuty.

### 5. Exercise anomaly detection and runbooks

```bash
for value in 100 101 99 100 100 1000; do
  curl -s -X POST http://localhost:8000/api/v1/anomalies/observe \
    -H 'content-type: application/json' \
    -d "{\"metric\":\"latency_ms\",\"value\":$value}"
done

curl -s http://localhost:8000/api/v1/runbooks
curl -s -X POST http://localhost:8000/api/v1/runbooks/<runbook-id>/execute \
  -H 'content-type: application/json' \
  -d '{"target_service":"auth-service"}'
```

### 6. Verify mesh tracing

Trace IDs propagate through `traceparent` headers on outbound calls. Jaeger
shows the same trace ID across service boundaries. Istio telemetry is
declared in `deploy/istio/telemetry.yaml` and sidecar metrics are scraped from
port `15020` when the mesh is installed.

The documented incident procedures live in `docs/runbooks/`.
