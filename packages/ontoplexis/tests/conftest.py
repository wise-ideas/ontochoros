"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.oracle import JAR, OracleConfig

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def animals_owlxml() -> str:
    return (FIXTURES / "animals.owlxml").read_text()


@pytest.fixture
def complex_owlxml() -> str:
    return (FIXTURES / "complex.owlxml").read_text()


@pytest.fixture
def oracle_config() -> OracleConfig:
    """Config for the ROBOT oracle jar; skips if it has not been downloaded."""
    if not JAR.exists():
        pytest.skip("ROBOT oracle jar not downloaded; run 'make fetch-robot'")
    return OracleConfig(jar=JAR)
