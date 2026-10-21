"""Configuration loader for telco platform services.

Honours required, optional, reserved, and secret-bearing markers from the
configuration contract. Fails fast with exit code 2 on missing required values.
"""

import os
import sys
from functools import lru_cache

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None  # type: ignore[assignment]


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


@lru_cache(maxsize=32)
def get_settings() -> dict:
    """Load all configuration from environment variables.

    Returns:
        Dictionary of configuration values keyed by name.
    """
    return {
        # Database
        "db_host": _validate_env_var("DB_HOST", required=True),
        "db_port": _validate_env_var("DB_PORT", required=False, secret=False) or "5432",
        "db_name": _validate_env_var("DB_NAME", required=True),
        "db_user": _validate_env_var("DB_USER", required=True),
        "db_password": _validate_env_var("DB_PASSWORD", secret=True),
        # Service identification
        "service_name": _validate_env_var("SERVICE_NAME", required=True),
        "service_role": _validate_env_var("SERVICE_ROLE", required=False, secret=False)
        or "default",
        # Feature flags
        "feature_flag_a": _validate_env_var("FEATURE_FLAG_A", required=False),
        "feature_flag_b": _validate_env_var("FEATURE_FLAG_B", required=False),
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
