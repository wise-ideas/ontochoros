"""Programmatic lint execution surface for running Cypher rules against a projection."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from ontoplexis import Projection

from ontopoiesis.lint.lint_registry import LintRule

QueryRow = dict[str, object]


@dataclass(frozen=True)
class LintViolation:
    """One rule that returned violation rows from a projection."""

    path: Path
    rows: list[QueryRow]
    is_warn: bool


@dataclass(frozen=True)
class LintResults:
    """Structured results from running a set of Cypher lint rules."""

    violations: list[LintViolation] = field(default_factory=list)

    @property
    def failures(self) -> list[LintViolation]:
        return [v for v in self.violations if not v.is_warn]

    @property
    def warnings(self) -> list[LintViolation]:
        return [v for v in self.violations if v.is_warn]


def run_lint_on_path(
    input_path: Path,
    *,
    rules: Iterable[LintRule],
) -> LintResults:
    """Run the selected lint rules against one persisted projection."""
    if input_path.suffix.lower() != ".lbug":
        raise ValueError(f"Lint requires a .lbug projection, got {input_path}.")
    violations: list[LintViolation] = []
    with Projection.open(input_path) as projection:
        for rule in rules:
            rows = rule.evaluate(projection)
            if rows:
                violations.append(LintViolation(path=rule.path, rows=rows, is_warn=rule.is_warn))
    return LintResults(violations=violations)
