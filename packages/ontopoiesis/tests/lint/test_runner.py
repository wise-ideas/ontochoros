from __future__ import annotations

from pathlib import Path

import pytest

from ontopoiesis.cypher_test.plugin import open_cypher_runtime
from ontopoiesis.lint.checker import run_lint_on_path
from ontopoiesis.lint.lint_registry import LintRule


def test_open_cypher_runtime_opens_lbug_inputs_directly(
    monkeypatch,
    tmp_path: Path,
) -> None:
    graph_path = tmp_path / "ontology.lbug"
    graph_path.write_text("stub")
    seen: dict[str, Path] = {}

    class FakeProjection:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

    def fake_open(path: Path) -> FakeProjection:
        seen["path"] = path
        return FakeProjection()

    monkeypatch.setattr("ontopoiesis.cypher_test.plugin.Projection.open", fake_open)

    with open_cypher_runtime(graph_path):
        pass

    assert seen["path"] == graph_path


def test_run_lint_on_path_executes_rules_against_opened_runtime(
    monkeypatch,
    tmp_path: Path,
) -> None:
    graph_path = tmp_path / "ontology.lbug"
    graph_path.write_text("stub")
    rule_path = tmp_path / "warn_quality.cypher"
    rule_path.write_text("MATCH (n) RETURN n.uid AS uid")
    rule = LintRule(
        code="W000",
        path=rule_path,
        summary="test rule",
        severity="warn",
        profile="core",
    )

    class FakeProjection:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def execute(self, query: str, parameters=None) -> list[dict[str, object]]:
            return [{"uid": "0x1"}]

    monkeypatch.setattr(
        "ontopoiesis.lint.checker.Projection.open",
        lambda path: FakeProjection(),
    )

    results = run_lint_on_path(graph_path, rules=[rule])

    assert len(results.failures) == 0
    assert len(results.warnings) == 1
    assert results.warnings[0].path == rule_path


def test_open_cypher_runtime_rejects_non_lbug_inputs(tmp_path: Path) -> None:
    ontology_path = tmp_path / "ontology.txt"
    ontology_path.write_text("ontology")

    with pytest.raises(ValueError, match=r"Cypher tests require a \.lbug projection"):
        open_cypher_runtime(ontology_path)
