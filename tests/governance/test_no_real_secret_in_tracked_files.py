"""Tracked-file secret test — no usable credential is tracked.

Test ID: `test_no_real_secret_in_tracked_files`
"""

import subprocess
import sys

import pytest

from tests.governance.helpers import REPO_ROOT

pytestmark = pytest.mark.governance

# A variable whose name marks its value as credential material.
CREDENTIAL_MARKERS = (
    "PASSWORD",
    "SECRET",
    "TOKEN",
    "CREDENTIAL",
    "API_KEY",
    "PRIVATE_KEY",
)


def _is_credential_bearing(name: str) -> bool:
    """Return whether a variable name marks its value as credential material."""
    upper = name.upper()
    return any(marker in upper for marker in CREDENTIAL_MARKERS)


class TestNoRealSecretInTrackedFiles:
    """The tracked tree holds no usable credential."""

    def test_no_real_secret_in_tracked_files(self):
        """The secret scanner finds no credential in the tracked tree."""
        result = subprocess.run(
            [sys.executable, "ci/secret_scan.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (
            f"The tracked tree holds secret material:\n{result.stdout}"
        )

    def test_the_example_configuration_holds_placeholders_only(self):
        """`.env.example` carries no usable credential."""
        example = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
        checked = 0

        for line in example.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name, _, value = stripped.partition("=")
            name = name.strip()
            value = value.strip().strip('"').strip("'")

            if not _is_credential_bearing(name):
                continue

            checked += 1
            assert "PLACEHOLDER" in value or value == "", (
                f".env.example carries a usable credential for {name}: {value}"
            )

        assert checked, ".env.example declares no credential-bearing variable."

    def test_no_connection_string_carries_a_credential(self):
        """No URL in `.env.example` carries userinfo."""
        example = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
        for line in example.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name, _, value = stripped.partition("=")
            value = value.strip()
            if "://" not in value:
                continue
            assert "@" not in value.split("://", 1)[1], (
                f".env.example carries credentials in the connection string for "
                f"{name.strip()}"
            )
