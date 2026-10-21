# Domain Model Overview
Status: Draft — not a substitute for detailed ERD and data dictionary

## 1. Identity and customer concepts

Keep these concepts distinct:
- **Customer:** a person or organization receiving commercial services.
- **Subscriber:** a service identity associated with telecom service; exact meaning must be confirmed for the target business.
- **Billing account:** entity responsible for invoices and payments.
- **Subscription:** an instance of a product or rate plan assigned to a customer/subscriber for a period.
- **Service/device asset:** a device or SIM/eSIM assigned to a subscription or subscriber.

Do not assume one customer equals one subscriber, one billing account, or one subscription.

## 2. Catalog and subscription concepts

- Product: sellable commercial definition.
- Product version: time-bounded or versioned definition.
- Rate plan: commercial/technical plan definition.
- Rate-plan version: versioned prices, quotas, and terms.
- Add-on: optional product or feature.
- Subscription: customer-specific purchase/activation with status and effective dates.
- Subscription add-on: an add-on attached to a subscription with its own lifecycle.

Historical invoices must remain explainable when prices or plan definitions change.

## 3. Device and provisioning concepts

- Device: physical equipment, with relevant identifiers such as IMEI and serial number.
- SIM/eSIM: SIM identity, with ICCID and lifecycle state; eSIM profile lifecycle may require additional entities.
- Assignment: time-bounded association between an asset and subscriber/subscription.
- Provisioning profile: configuration template such as APN or VoLTE parameters.
- Provisioning job: an activation/change request with status, attempts, timestamps, and sanitized failure details.

An inventory assignment does not prove that a service is provisioned. Commercial and network lifecycle states must remain distinct.

## 4. Billing concepts

- Billing account: owns billing relationship.
- Invoice: statement with lifecycle and totals.
- Invoice line: charge or adjustment component with a description and applicable price/tax context.
- Payment: recorded payment event.
- Payment allocation: amount of a payment applied to an invoice or other eligible obligation.
- Ledger entry: immutable posted financial movement.
- Credit memo: formal credit linked to a source charge/invoice.
- Adjustment request: approval workflow before posting, when required.

## 5. Invariants to formalize

- Every subscription references a valid customer/subscriber and valid product/plan version.
- Asset identifiers follow explicit uniqueness and lifecycle rules.
- Every invoice line belongs to an invoice.
- Invoice totals reconcile according to documented tax and rounding rules.
- Payment allocations cannot exceed the permitted allocatable payment amount or obligation balance, unless a documented exception applies.
- Posted ledger entries are immutable.
- Credit memos obey approval policy and reference a valid source transaction where required.
- A provisioning job's outcome is not silently inferred from subscription status.
- Historical prices and terms are retained or snapshotted sufficiently to explain past charges.

## 6. Required next artifacts

- ER diagram.
- Table-by-table data dictionary.
- Status-transition diagrams.
- Index and uniqueness plan.
- Retention and audit policy.
- Migration and backfill strategy.
- Open-question register for business rules not yet decided.
