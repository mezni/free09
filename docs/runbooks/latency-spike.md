# Runbook: latency spike

**Scenario:** `service_latency_high`
**Trigger:** `ServiceLatencyHigh` or `PerformanceAnomalyDetected`
**Owner:** platform

## Steps

1. Compare the current p95 latency with the one-hour rolling baseline on the
   Telco Services dashboard.
2. Check database connection usage and downstream latency for the affected
   service.
3. Scale the service replicas or raise the connection pool limit when the
   bottleneck is capacity.
4. Confirm that no background job, migration or exporter is competing for CPU
   or database connections.

## Verification

p95 latency is below 1.5 seconds and remains stable for ten minutes. The
`PerformanceAnomalyDetected` alert resolves without further deviation.

## Escalation

If latency does not recover after scaling, escalate to the platform on-call
engineer and capture a trace from Jaeger for the slow endpoint.
