"""CLI service integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from ontoplexis import Ontology

from ontopoiesis.commands.impact import (
    _ImpactDirection,
    _ImpactSeedKind,
    _query_impact,
)
from ontopoiesis.lint import LintRuleSelectionError, resolve_lint_rule_selection

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------

_PIZZA_OWX = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="https://example.org/pizza#">
  <Declaration><Class IRI="https://example.org/pizza#Pizza"/></Declaration>
  <SubClassOf>
    <Class IRI="https://example.org/pizza#Pizza"/>
    <Class IRI="https://example.org/pizza#Food"/>
  </SubClassOf>
</Ontology>
"""


@pytest.fixture
def pizza_lbug(tmp_path: Path) -> Path:
    path = tmp_path / "pizza.lbug"
    Ontology.from_owlxml(_PIZZA_OWX).save_projection(path).close()
    return path


# ---------------------------------------------------------------------------
# impact
# ---------------------------------------------------------------------------


def test_query_upstream_impact_returns_referencing_constructs(pizza_lbug: Path) -> None:
    rows = _query_impact(
        pizza_lbug,
        "https://example.org/pizza#Pizza",
        seed_kind=_ImpactSeedKind.IRI,
        direction=_ImpactDirection.UPSTREAM,
    )

    kinds_by_depth = {(row["kind"], row["depth"]) for row in rows}
    assert ("Declaration", 1) in kinds_by_depth
    assert ("SubClassOf", 1) in kinds_by_depth
    assert ("Ontology", 2) in kinds_by_depth


def test_query_downstream_impact_returns_reachable_constructs(pizza_lbug: Path) -> None:
    rows = _query_impact(
        pizza_lbug,
        "https://example.org/pizza#Pizza",
        seed_kind=_ImpactSeedKind.IRI,
        direction=_ImpactDirection.DOWNSTREAM,
    )

    assert rows == []


def test_query_uid_impact_seeds_by_uid(pizza_lbug: Path) -> None:
    upstream_by_iri = _query_impact(
        pizza_lbug,
        "https://example.org/pizza#Pizza",
        seed_kind=_ImpactSeedKind.IRI,
        direction=_ImpactDirection.UPSTREAM,
    )
    subclass_uid = next(row["uid"] for row in upstream_by_iri if row["kind"] == "SubClassOf")
    assert isinstance(subclass_uid, str)

    rows = _query_impact(
        pizza_lbug,
        subclass_uid,
        seed_kind=_ImpactSeedKind.UID,
        direction=_ImpactDirection.DOWNSTREAM,
    )

    kinds = {row["kind"] for row in rows}
    assert kinds == {"Class"}
    iris = {row["iri"] for row in rows}
    assert iris == {"https://example.org/pizza#Pizza", "https://example.org/pizza#Food"}


def test_query_impact_returns_no_rows_for_unknown_seed(pizza_lbug: Path) -> None:
    rows = _query_impact(
        pizza_lbug,
        "https://example.org/pizza#Nope",
        seed_kind=_ImpactSeedKind.IRI,
        direction=_ImpactDirection.UPSTREAM,
    )

    assert rows == []


# ---------------------------------------------------------------------------
# lint
# ---------------------------------------------------------------------------


def test_resolve_lint_rules_default_returns_error_and_warning_rules() -> None:
    from ontopoiesis.lint import lint_rules

    rules = resolve_lint_rule_selection(profiles=[], select=[], extend_select=[], ignore=[])
    expected = [str(rule.path) for rule in lint_rules() if rule.code.startswith(("E", "W"))]
    assert [str(r.path) for r in rules] == expected


def test_resolve_lint_rules_select_overrides_default() -> None:
    from ontopoiesis.lint import lint_rule_lookup

    rules = resolve_lint_rule_selection(profiles=[], select=["E101"], extend_select=[], ignore=[])
    assert [str(r.path) for r in rules] == [str(lint_rule_lookup()["E101"].path)]


def test_resolve_lint_rules_extend_select_adds_rules() -> None:
    from ontopoiesis.lint import lint_rule_lookup, lint_rules

    rules = resolve_lint_rule_selection(profiles=[], select=[], extend_select=["M101"], ignore=[])
    path_strs = [str(r.path) for r in rules]
    assert str(lint_rule_lookup()["M101"].path) in path_strs
    for rule in lint_rules():
        if rule.code.startswith(("E", "W")):
            assert str(rule.path) in path_strs


def test_resolve_lint_rules_ignore_removes_rule() -> None:
    from ontopoiesis.lint import lint_rule_lookup

    rules = resolve_lint_rule_selection(profiles=[], select=[], extend_select=[], ignore=["W101"])
    assert str(lint_rule_lookup()["W101"].path) not in [str(r.path) for r in rules]


def test_resolve_lint_rules_extend_select_and_ignore() -> None:
    from ontopoiesis.lint import lint_rule_lookup, lint_rules

    rules = resolve_lint_rule_selection(
        profiles=[], select=[], extend_select=["M101"], ignore=["W101"]
    )
    path_strs = [str(r.path) for r in rules]
    assert str(lint_rule_lookup()["M101"].path) in path_strs
    assert str(lint_rule_lookup()["W101"].path) not in path_strs
    for rule in lint_rules():
        if rule.code.startswith("E"):
            assert str(rule.path) in path_strs


def test_resolve_lint_rules_with_profile() -> None:
    from ontopoiesis.lint import lint_rules

    rules = resolve_lint_rule_selection(
        profiles=["editorial", "description_logic"], select=[], extend_select=[], ignore=[]
    )
    path_strs = [str(r.path) for r in rules]
    for rule in lint_rules():
        if rule.code.startswith(("E", "W", "P", "D")):
            assert str(rule.path) in path_strs


def test_resolve_lint_rules_raises_for_unknown_profile() -> None:
    with pytest.raises(LintRuleSelectionError, match="Unknown lint profile"):
        resolve_lint_rule_selection(
            profiles=["nonexistent"], select=[], extend_select=[], ignore=[]
        )


def test_resolve_lint_rules_raises_for_unknown_selector() -> None:
    with pytest.raises(LintRuleSelectionError, match="Unknown lint selector"):
        resolve_lint_rule_selection(profiles=[], select=["Z999"], extend_select=[], ignore=[])
