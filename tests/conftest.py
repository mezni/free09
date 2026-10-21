"""Conftest.py — Shared fixtures and marker registration for telco platform."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (slower, cross-component)")
    config.addinivalue_line("markers", "contract: Contract tests (API surface validation)")
    config.addinivalue_line("markers", "governance: Governance-related tests (constitution, ADRs, templates)")
    config.addinivalue_line("markers", "slow: Marks that require significant time or resources")


def pytest_collection_modifyitems(config, items):
    """Optionally reorder or skip items based on markers."""
    pass
