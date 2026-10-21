# build-phase6: Data Model

## Observability Entities

### LogEntry
- `log_entry_id`: UUID (primary key)
- `service`: string (service name)
- `level`: string (debug, info, warning, error, fatal)
- `message`: string (log message)
- `timestamp`: datetime (auto-now)
- `request_id`: UUID (correlates with tracing)
- `trace_id`: UUID (correlates with distributed tracing)
- `attributes`: JSONB (key-value log attributes)

### MetricFamily
- `metric_name`: string (prometheus metric name)
- `help_text`: string (human-readable description)
- `timestamp`: datetime (auto-now)
- `value`: float (metric value)
- `labels`: JSONB (metric labels: service, endpoint, status, etc.)

### AlertRule
- `alert_id`: UUID (primary key)
- `alert_name`: string (human-readable alert name)
- `expr`: string (Prometheus query expression)
- `for`: string (duration condition must persist)
- `labels`: JSONB (alert labels: severity, team, service)
- `status`: string (firing, resolved)
- `created_at`: datetime (auto-now)
- `updated_at`: datetime (auto-now-on-update)

### Runbook
- `runbook_id`: UUID (primary key)
- `title`: string (runbook title)
- `scenario`: string (described incident scenario)
- `steps`: JSONB (step-by-step resolution procedures)
- `author`: string (runbook creator)
- `created_at`: datetime (auto-now)
- `updated_at`: datetime (auto-now-on-update)

### ServiceMeshMetric
- `metric_id`: UUID (primary key)
- `service`: string (service name)
- `endpoint`: string (API endpoint)
- `latency`: float (request latency in ms)
- `throughput`: float (requests per second)
- `error_rate`: float (percentage of failed requests)
- `timestamp`: datetime (auto-now)

## Relationships
- **LogEntry → MetricFamily**: Many-to-Many (correlated through time range)
- **LogEntry → AlertRule**: Many-to-Many (log entries can trigger alerts; alerts reference correlated logs)
- **LogEntry → Runbook**: Many-to-Many (log patterns can reference runbooks; runbooks reference relevant log patterns)
- **ServiceMeshMetric → MetricFamily**: One-to-Many (service mesh metrics are a type of prometheus metric)

## Indexes
- `UNIQUE` on `LogEntry.log_entry_id`
- `UNIQUE` on `MetricFamily.metric_name`
- `UNIQUE` on `AlertRule.alert_id`
- `UNIQUE` on `Runbook.runbook_id`
- Index on `LogEntry.service`
- Index on `LogEntry.timestamp`
- Index on `LogEntry.request_id`
- Index on `MetricFamily.metric_name`
- Index on `AlertRule.status`
- Index on `Runbook.title`

## JSON Schemas (for Prometheus/Loki integration)

```json
{
  "LogEntry": {
    "type": "object",
    "required": ["service", "level", "message", "timestamp"],
    "properties": {
      "log_entry_id": {"type": "string", "format": "uuid"},
      "service": {"type": "string"},
      "level": {"type": "string", "enum": ["debug", "info", "warning", "error", "fatal"]},
      "message": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "request_id": {"type": "string", "format": "uuid"},
      "trace_id": {"type": "string", "format": "uuid"},
      "attributes": {"type": "object"}
    }
  },
  "MetricFamily": {
    "type": "object",
    "required": ["metric_name", "help_text", "timestamp", "value"],
    "properties": {
      "metric_name": {"type": "string"},
      "help_text": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "value": {"type": "number"},
      "labels": {"type": "object"}
    }
  },
  "AlertRule": {
    "type": "object",
    "required": ["alert_name", "expr", "for", "labels", "status"],
    "properties": {
      "alert_id": {"type": "string", "format": "uuid"},
      "alert_name": {"type": "string"},
      "expr": {"type": "string"},
      "for": {"type": "string"},
      "labels": {"type": "object"},
      "status": {"type": "string"},
      "created_at": {"type": "string", "format": "date-time"},
      "updated_at": {"type": "string", "format": "date-time"}
    }
  },
  "Runbook": {
    "type": "object",
    "required": ["title", "scenario", "steps", "author"],
    "properties": {
      "runbook_id": {"type": "string", "format": "uuid"},
      "title": {"type": "string"},
      "scenario": {"type": "string"},
      "steps": {"type": "array"},
      "author": {"type": "string"},
      "created_at": {"type": "string", "format": "date-time"},
      "updated_at": {"type": "string", "format": "date-time"}
    }
  }
}
```
