from __future__ import annotations

import pytest
import typer
from ontoplexis import OwlXmlStructureError, ProjectionStorageError

from ontopoiesis.errors import raise_cli_error, translate_cli_errors
from ontopoiesis.lint import LintRuleSelectionError
from ontopoiesis.migrations import MigrationError
from ontopoiesis.render import RenderDependencyError


@pytest.mark.parametrize(
    ("exc", "message"),
    [
        (OwlXmlStructureError("bad structure"), "bad structure"),
        (ProjectionStorageError("closed projection"), "closed projection"),
        (RenderDependencyError("graphviz missing"), "graphviz missing"),
        (LintRuleSelectionError("bad rule"), "bad rule"),
        (MigrationError("duplicate migration id"), "duplicate migration id"),
    ],
)
def test_raise_cli_error_translates_known_domain_errors(
    exc: Exception,
    message: str,
) -> None:
    with pytest.raises(typer.BadParameter) as exc_info:
        raise_cli_error(exc)

    assert exc_info.value.args == (message,)


def test_raise_cli_error_flattens_domain_exception_groups() -> None:
    exc = ExceptionGroup(
        "projection failures",
        [
            ProjectionStorageError("Projection is closed"),
            OwlXmlStructureError("Node missing kind"),
        ],
    )

    with pytest.raises(typer.BadParameter) as exc_info:
        raise_cli_error(exc)

    assert exc_info.value.args == ("Multiple errors:\n- Projection is closed\n- Node missing kind",)


def test_raise_cli_error_reraises_unknown_errors() -> None:
    exc = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        raise_cli_error(exc)


def test_raise_cli_error_reraises_mixed_exception_groups() -> None:
    exc = ExceptionGroup(
        "mixed failures",
        [
            ProjectionStorageError("Projection is closed"),
            RuntimeError("boom"),
        ],
    )

    with pytest.raises(ExceptionGroup) as exc_info:
        raise_cli_error(exc)

    assert exc_info.value is exc


def test_translate_cli_errors_applies_shared_domain_translation() -> None:
    with pytest.raises(typer.BadParameter) as exc_info:
        with translate_cli_errors():
            raise ProjectionStorageError("closed projection")

    assert exc_info.value.args == ("closed projection",)


def test_translate_cli_errors_reraises_unknown_errors() -> None:
    with pytest.raises(RuntimeError, match="boom"):
        with translate_cli_errors():
            raise RuntimeError("boom")
