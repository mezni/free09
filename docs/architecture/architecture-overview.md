# Architecture Overview
Status: Draft — decisions require review

## 1. System context

The system provides backend APIs for authorized customer-support and supervisory workflows. No frontend or AI agent is included in the core scope. External payment processing and live network provisioning are represented by adapters unless explicitly brought into scope.

## 2. Services and ownership

| Service | Owns | Examples of responsibilities |
|---|---|---|
| `auth-service` | `auth` schema | Users, roles, permissions, token issuance, security audit events |
| `crm-service` | `crm` schema | Customers, subscribers, contacts, tickets, ticket history and assignment |
| `inventory-service` | `inventory` schema | Catalog, rate plans, subscriptions, add-ons, devices, SIMs, provisioning jobs |
| `billing-service` | `billing` schema | Billing accounts, invoices, payments, allocations, ledger, credit memos |

Ownership boundaries must be validated against the final domain model. Do not duplicate mutable authoritative data across schemas without a documented synchronization strategy.

## 3. Database topology

Initial deployment: one PostgreSQL cluster/database with four schemas and separate service credentials.

Rules:
- Each service writes only to its owned schema.
- Cross-service reads should use owning-service APIs by default.
- Any exception, such as read-only reporting views, requires an ADR documenting consistency, permissions, and operational consequences.
- Foreign keys across schemas should be used only after an explicit decision; they can improve integrity but increase coupling.
- Do not imply that a single shared database provides independent database failure domains.

## 4. Communication

Use synchronous HTTP APIs for initial request/response interactions. Define request timeouts, bounded retries, correlation IDs, and error mapping.

Avoid automatic retries for non-idempotent operations unless an idempotency strategy is in place.

For long-running provisioning or financial workflows, specify lifecycle states and recovery behavior. An asynchronous message broker may be introduced later through an ADR if throughput or decoupling requirements justify it.

## 5. Security boundary

- Human users authenticate through `auth-service`.
- Each service validates token claims or uses a documented trusted gateway/library strategy.
- Authorization is enforced at the service handling the action.
- Service-to-service identity and permissions are explicit.
- Secrets are externalized.
- Audit events are recorded for sensitive actions.

The exact token issuance, signing-key distribution, revocation, and service-to-service authentication design must be specified before implementation.

## 6. Cross-service workflows to specify

1. Agent retrieves customer and subscriber information.
2. Agent views active subscriptions and add-ons.
3. Agent views invoices and payment status.
4. Agent requests a billing adjustment; authorized supervisor approves it.
5. Subscription activation triggers provisioning through a mock adapter.
6. Provisioning failure is recorded and can be retried or reconciled.

Each workflow must specify source-of-truth ownership, failure cases, idempotency, authorization, and audit events.

## 7. Architecture diagrams required

Maintain diagrams for:
- System context.
- Service/container architecture.
- Database schema ownership.
- Customer lookup sequence.
- Credit-memo approval and posting.
- Subscription activation and provisioning failure/recovery.

## 8. Open decisions

- API gateway or direct service access.
- JWT signing-key management and token revocation strategy.
- Whether cross-schema foreign keys are permitted.
- Whether audit events reside in each owning schema or a centralized append-only store.
- Whether any asynchronous broker is required for the first release.
- Tax, currency, billing-cycle, and invoice-finalization rules.
- Deployment target, availability target, retention, RPO, and RTO.
