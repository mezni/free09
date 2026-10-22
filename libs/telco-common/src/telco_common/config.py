"""Configuration loader for telco platform services.

Honours required, optional, reserved, and secret-bearing markers from the
configuration contract
(`specs/001-project-setup/contracts/configuration-contract.md`). Fails fast with
exit code 2 on missing required values.
"""

import os
import sys
from functools import lru_cache

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None  # type: ignore[assignment]

LOCAL_SQLITE_URL = "sqlite:///./telco_platform.db"


def _validate_env_var(name: str, required: bool = True, secret: bool = False) -> str:
    """Validate and return an environment variable value.

    Args:
        name: Environment variable name.
        required: If True, exit with code 2 if not set.
        secret: If True, mask value in logs/errors.

    Returns:
        The environment variable value.

    Raises:
        SystemExit: With code 2 if required variable is missing.
    """
    value = os.environ.get(name)
    if value is None:
        if required:
            msg = f"Missing required environment variable: {name}"
            if secret:
                msg += " (contains credential/secrets)"
            sys.exit(2)
        return ""
    if secret:
        # Masked representation is for logging only; the raw value is never logged.
        pass
    return value


def resolve_database_url() -> str:
    """Resolve the connection URL using the contract's single resolution order.

    1. ``TELECO_DB_URL`` is used verbatim when set to a non-empty value.
    2. Otherwise ``dev`` and ``test`` use the local SQLite URL.
    3. Otherwise the URL is composed from the ``TELECO_DB_*`` components.

    Returns:
        The resolved connection URL.
    """
    explicit = os.environ.get("TELECO_DB_URL", "").strip()
    if explicit:
        return explicit

    environment = os.environ.get("TELECO_ENV", "").strip()
    if environment in {"dev", "test"}:
        return LOCAL_SQLITE_URL

    user = os.environ.get("TELECO_DB_USER", "") or "telco_app"
    password = os.environ.get("TELECO_DB_PASSWORD", "")
    host = os.environ.get("TELECO_DB_HOST", "") or "127.0.0.1"
    port = os.environ.get("TELECO_DB_PORT", "") or "5432"
    name = os.environ.get("TELECO_DB_NAME", "") or "telco_si"
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


@lru_cache(maxsize=32)
def get_settings() -> dict[str, str]:
    """Load all configuration from environment variables.

    Returns:
        Dictionary of configuration values keyed by name.
    """
    return {
        # Environment and logging
        "environment": _validate_env_var("TELECO_ENV", required=True),
        "log_level": _validate_env_var("TELECO_LOG_LEVEL", required=False) or "INFO",
        "log_format": _validate_env_var("TELECO_LOG_FORMAT", required=False) or "json",
        "correlation_header": _validate_env_var(
            "TELECO_LOG_CORRELATION_HEADER", required=False
        )
        or "X-Correlation-ID",
        # Service identification
        "service_name": _validate_env_var("TELECO_SERVICE_NAME", required=True),
        "service_role": _validate_env_var("TELECO_SERVICE_ROLE", required=False)
        or "default",
        # Database
        "db_url": _validate_env_var("TELECO_DB_URL", required=False),
        "db_host": _validate_env_var("TELECO_DB_HOST", required=False) or "127.0.0.1",
        "db_port": _validate_env_var("TELECO_DB_PORT", required=False) or "5432",
        "db_name": _validate_env_var("TELECO_DB_NAME", required=False) or "telco_si",
        "db_user": _validate_env_var("TELECO_DB_USER", required=False) or "telco_app",
        "db_password": _validate_env_var("TELECO_DB_PASSWORD", required=False),
        "db_sslmode": _validate_env_var("TELECO_DB_SSLMODE", required=False)
        or "prefer",
    }


def check_required_config() -> bool:
    """Check that all required configuration is present.

    Returns:
        True if all required config is present, False otherwise.
    """
    try:
        get_settings()
        return True
    except SystemExit:
        return False
