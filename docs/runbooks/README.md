# Incident runbooks

Runbooks are the human-readable counterpart of the API exposed by
`/api/v1/runbooks`. Each document covers one alertable failure mode, the steps
to confirm it, the mitigation, and the evidence that closes the incident.

| Runbook | Trigger | Owning team |
| --- | --- | --- |
| [Service error rate](service-error-rate.md) | `ServiceErrorRateHigh` | backend |
| [Latency spike](latency-spike.md) | `ServiceLatencyHigh`, `PerformanceAnomalyDetected` | platform |
| [Database connection failure](database-connection-failure.md) | `ServiceDown`, readiness probes failing | database |

The seeded API runbooks use the same scenarios. Update both the Markdown file
and the seeded runbook in `src/services/runbooks.py` when a procedure changes.
