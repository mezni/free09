# Contract: Environment Configuration

**Feature**: `SPEC-001` — Project Setup and Governance
**Status**: Active | **Date**: 2026-10-21
**Governed by**: `specs/001-project-setup/spec.md` (FR-013, FR-014, FR-015, BR-007), Constitution Article III

---

## Purpose

This contract fixes the **names and shapes** of every environment variable the
repository requires. It never carries a value. The only configuration artefact
tracked in version control is `.env.example`, which realises this contract
with placeholder values.

A variable name that is fixed here cannot be renamed later without breaking a
tracked consumer, a documented setup path, or a CI job. Adding a name is
cheap; renaming one is not.

## Naming Convention

```
<SERVICE>_<DOMAIN>_<NAME>      service-scoped, e.g. BILLING_LEDGER_...
TELECO_<DOMAIN>_<NAME>         cross-cutting, applies to every service
COMMON_<DOMAIN>_<NAME>         shared library configuration
```

Service prefixes are fixed by Constitution Article II: `AUTH`, `CRM`,
`BILLING`, `INVENTORY`. The `<DOMAIN>` segment names the subject area
(`DB`, `LOG`, `API`, `JWT`, `OTEL`), and `<NAME>` is the specific setting.

Rules:

1. A name never contains a value, a host, or a path.
2. A name that leaves the repository — a CI secret, a container environment
   variable — keeps the same spelling it has here.
3. A service-specific name never appears in the cross-cutting prefix, and a
   cross-cutting name never carries a service prefix.

## Requirement Markers

| Marker | Meaning | Behaviour when absent |
|---|---|---|
| **Required** | Neither the check suite nor a service process can proceed without it. | Fail fast with a message naming the variable, its purpose, and where to obtain a value. |
| **Optional** | A documented default exists. | The default applies; no message. |
| **Reserved** | The name is fixed now; the consumer arrives in a later phase. | Absent is normal and produces no message. |

A variable is additionally marked **secret-bearing** when its value is a
credential or a credential-equivalent. A secret-bearing variable MUST be
supplied through the environment, MUST be excluded from version control, and
MUST appear in `.env.example` as a placeholder only.

## Declared Variables

### Tooling and environment

| Name | Marker | Secret | Type | Default | Purpose |
|---|---|---|---|---|---|
| `TELECO_ENV` | Required | No | `dev` \| `test` \| `ci` \| `prod` | — | Selects environment-specific behaviour. The setup path refuses to run against `prod` when `TELECO_ALLOW_PROD_CHECKS` is not explicitly set, mirroring the constitution's environment data policy. |
| `TELECO_LOG_LEVEL` | Optional | No | string | `INFO` | Minimum severity emitted to stdout. |
| `TELECO_LOG_FORMAT` | Optional | No | `json` \| `text` | `json` | Log serialisation. `json` in CI so results are parseable. |
| `TELECO_LOG_CORRELATION_HEADER` | Optional | No | string | `X-Correlation-ID` | Header carrying the correlation identifier, satisfying the constitution's correlation-identifier requirement. |

### Service identity

| Name | Marker | Secret | Type | Default | Purpose |
|---|---|---|---|---|---|
| `TELECO_SERVICE_NAME` | Required | No | string | — | Name of the running service. A process that cannot name itself cannot be traced, so the value is mandatory. |
| `TELECO_SERVICE_ROLE` | Optional | No | string | `default` | Role assumed by the service in the topology. |

### Database connection

Shared by all four services. Each service reads the same host, port, and
credentials but binds to its own schema.

| Name | Marker | Secret | Type | Default | Purpose |
|---|---|---|---|---|---|
| `TELECO_DB_URL` | Optional | **Yes** | string | `sqlite:///./telco_platform.db` | Full connection URL used by the running service. Takes precedence over the `TELECO_DB_*` components. The default is a local SQLite file so that a checkout runs without a database server; a deployed service MUST set it to the PostgreSQL URL. |
| `TELECO_DB_HOST` | Optional | No | string | `127.0.0.1` | PostgreSQL host. Provided by `deploy/compose/compose.yaml` locally. |
| `TELECO_DB_PORT` | Optional | No | int | `5432` | PostgreSQL port. |
| `TELECO_DB_NAME` | Optional | No | string | `telco_si` | Database name. One database, four schemas. |
| `TELECO_DB_USER` | Optional | No | string | `telco_app` | Least-privilege application role. |
| `TELECO_DB_PASSWORD` | Optional | **Yes** | string | `localdevpassword` | Application role password. The default is a local-only placeholder and MUST be overridden outside local development. |
| `TELECO_DB_SSLMODE` | Optional | No | `disable` \| `allow` \| `prefer` \| `require` \| `verify-full` | `prefer` | TLS mode for the connection. `verify-full` is mandatory for `TELECO_ENV=prod`. |
| `TELECO_DB_POOL_SIZE` | Optional | No | int | `5` | Connections held open per process. |
| `TELECO_DB_POOL_MAX_OVERFLOW` | Optional | No | int | `10` | Additional connections permitted under load. |
| `TELECO_DB_CONNECT_TIMEOUT_SECONDS` | Optional | No | int | `10` | Connection establishment timeout. |
| `TELECO_DB_STATEMENT_TIMEOUT_MS` | Optional | No | int | `30000` | Server-side statement timeout, bounding a stuck query. |

**Connection-URL resolution.** The URL a service connects to is resolved in
exactly one order, with no second interpretation:

1. If `TELECO_DB_URL` is set, it is used verbatim.
2. Otherwise, if `TELECO_ENV` is `dev` or `test`, the local SQLite URL
   `sqlite:///./telco_platform.db` is used.
3. Otherwise the URL is composed from the `TELECO_DB_*` components as
   `postgresql://<TELECO_DB_USER>:<TELECO_DB_PASSWORD>@<TELECO_DB_HOST>:<TELECO_DB_PORT>/<TELECO_DB_NAME>`.

A service MUST NOT connect to a database other than the one this rule
produces, and MUST NOT read an undeclared variable to build a connection.

### Per-service database URLs — Reserved

Each service binds to its own schema in the shared database, and the
constitution requires per-service least-privilege credentials. The URL
variables are fixed now so that Phase 2 does not have to invent names.

| Name | Marker | Secret | Type | Default | Purpose |
|---|---|---|---|---|---|
| `AUTH_DATABASE_URL` | Reserved | **Yes** | string | *(none)* | Connection URL for the `auth` schema, bound to the `auth` role. |
| `CRM_DATABASE_URL` | Reserved | **Yes** | string | *(none)* | Connection URL for the `crm` schema, bound to the `crm` role. |
| `BILLING_DATABASE_URL` | Reserved | **Yes** | string | *(none)* | Connection URL for the `billing` schema, bound to the `billing` role. |
| `INVENTORY_DATABASE_URL` | Reserved | **Yes** | string | *(none)* | Connection URL for the `inventory` schema, bound to the `inventory` role. |

Each service MUST use only its own URL and MUST NOT be able to reach another
service's schema. The grant separation is asserted by the integration test
`test_crm_role_cannot_write_billing_schema` from Phase 2 onward; Phase 0
records the variable names and the topology, and creates no roles or schemas.

### Runtime — Reserved

| Name | Marker | Secret | Type | Default | Purpose |
|---|---|---|---|---|---|
| `TELECO_API_HOST` | Reserved | No | string | `127.0.0.1` | Bind address for a service's HTTP server. |
| `TELECO_API_PORT` | Reserved | No | int | `8000` | Bind port for a service's HTTP server. |
| `TELECO_JWT_SIGNING_KEY` | Reserved | **Yes** | string | *(none)* | Signing key for token issuance. |
| `TELECO_JWT_ALGORITHM` | Reserved | No | `RS256` | `EdDSA` | Token signing algorithm. Asymmetric only; symmetric signing is prohibited by the constitution's security requirements. |
| `TELECO_JWT_ISSUER` | Reserved | No | string | `telco-si` | Expected token issuer. |
| `TELECO_JWT_AUDIENCE` | Reserved | No | string | `telco-si` | Expected token audience. |
| `TELECO_JWT_TTL_SECONDS` | Reserved | No | int | `900` | Access-token lifetime. |
| `TELECO_OTEL_EXPORTER_OTLP_ENDPOINT` | Reserved | No | string | *(none)* | OpenTelemetry export endpoint, for the observability requirements of Article VIII. |

### Explicitly not declared

No variable is declared for payment gateways, mobile-network provisioning,
SMS delivery, or any other out-of-scope integration. The constitution places
those behind adapters with mocked implementations, and declaring configuration
for an adapter that does not exist would be a requirement invented by this
phase.

## Failure Model

| Condition | Detection | Message | Exit |
|---|---|---|---|
| A Required variable is absent | At process start, before any check runs | `Missing required environment variable <NAME>. Purpose: <purpose>. Set it in your environment or copy .env.example to .env.` | `2` |
| A secret-bearing variable holds a placeholder while `TELECO_ENV` is `ci` | At start of the `test` check | `Refusing to run CI checks with placeholder credentials.` | `2` |
| An integer variable holds a non-integer | At read time | `<NAME> must be an integer, got <value>.` | `2` |
| An enum variable holds an unlisted value | At read time | `<NAME> must be one of <allowed>, got <value>.` | `2` |
| A variable name in `.env.example` is absent from this contract | `governance` check | `Variable <NAME> in .env.example is not declared in the configuration contract.` | `1` |
| A variable in this contract is absent from `.env.example` | `governance` check | `Variable <NAME> is declared in the configuration contract but absent from .env.example.` | `1` |

Exit code `2` means *could not run*. At the CI gate it is treated as a
failure, exactly like exit code `1` (BR-003).

## Invariants

1. This contract carries **no real value** for any variable, secret-bearing or
   otherwise (BR-007, FR-014).
2. Every variable in `.env.example` appears in this contract, and every
   variable in this contract appears in `.env.example`. The check is
   bidirectional, so neither file can drift alone.
3. `.env.example` MUST NOT contain a value that a secret scanner would flag,
   and MUST NOT contain a value that works against a real system.
4. `.env` and every file matching a local-override pattern MUST be excluded
   from version control (FR-016) and MUST be listed in `.gitignore`.
5. Verification output MUST NOT echo a supplied secret value (Art. III).

## Change Procedure

1. Add or change the variable in this contract.
2. Add or change the matching entry in `.env.example`, with a placeholder.
3. Update the `governance` check if a new validation rule is introduced.
4. If the change affects a service, update that service's documentation in the
   same change set — the constitution's Article X.5 requires operational
   behaviour, architecture, API contracts, and setup instructions to change
   together with the thing that alters them.
5. Record the decision as an ADR if it constrains a service's architecture
   rather than merely naming a setting.
