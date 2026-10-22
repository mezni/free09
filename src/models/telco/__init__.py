"""The four domain schemas and the metadata the migration set is built from.

Each module owns one schema and one owning service (ADR-0001, D-01):

* `auth` — `auth-service`
* `crm` — `crm-service`
* `inventory` — `inventory-service`
* `billing` — `billing-service`

The metadata lives on `TelcoBase`, separate from the platform application's
`src.models.Base`, so the application tables and the domain schemas have
independent lifecycles. The migration set under `migrations/versions/` is
generated from `TelcoBase.metadata` and is the only thing that creates the
domain schemas (FR-036, NFR-030).
"""

from src.models.telco import auth, billing, crm, inventory
from src.models.telco.base import AuditMixin, TelcoBase

__all__ = [
    "AuditMixin",
    "TelcoBase",
    "auth",
    "billing",
    "crm",
    "inventory",
]
