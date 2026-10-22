# Runbook: database connection failure

**Scenario:** `database_connection_failure`
**Trigger:** readiness probes failing, `ServiceDown`, connection errors in logs
**Owner:** database

## Steps

1. Run `docker compose ps postgres` and inspect the PostgreSQL container logs.
2. Check active connections and disk usage with `psql` or the provider console.
3. Release stale connections or restart PostgreSQL when it is wedged.
4. Confirm that each service can open a new connection and run `SELECT 1`.

## Verification

`GET /readyz` returns HTTP 200 with every service marked healthy, and the
`ServiceDown` alert clears.

## Escalation

If PostgreSQL does not recover after a restart, escalate to the database on-call
engineer and fail over to the standby if one is configured.
