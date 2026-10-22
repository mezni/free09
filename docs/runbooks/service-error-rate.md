# Runbook: service error rate above threshold

**Scenario:** `service_error_rate_high`
**Trigger:** `ServiceErrorRateHigh` (more than 1% 5xx over five minutes)
**Owner:** backend

## Steps

1. Open the Telco Services Grafana dashboard and identify the service and
   endpoint responsible for the errors.
2. Search logs with a query such as
   `{service="auth-service"} |= "error"` over the last 15 minutes.
3. Compare the error start time with recent deployments, configuration changes
   and dependency incidents.
4. If a bad deployment is responsible, roll back the service. Otherwise restart
   the affected replicas and watch the error rate for ten minutes.

## Verification

The error rate must stay below 1% for ten minutes and `GET /healthz` must return
`{"status":"healthy"}` for every replica.

## Escalation

If the error rate remains above 1% after the rollback, page the on-call backend
engineer and open an incident channel.
