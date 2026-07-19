"""Rule-selection policy, asserted against a small fake registry.

Testing selection against the real registry forces the expected values to be
re-derived with the same startswith logic as the implementation — a
tautology. A fixed fake registry lets each test state its expected outcome
as a literal list of codes. Facts about the real registry (unique codes,
profile inventory) are pinned in test_lint_registry.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ontopoiesis.lint import LintRuleSelectionError, resolve_lint_rule_selection
from ontopoiesis.lint.lint_registry import LintRule


def _rule(code: str, severity: str = "error", profile: str = "core") -> LintRule:
    return LintRule(
        code=code,
        path=Path(f"/rules/{code}.cypher"),
        summary=f"rule {code}",
        severity=severity,
        profile=profile,
    )


_FAKE_RULES = [
    _rule("E101"),
    _rule("E102"),
    _rule("W101", severity="warn"),
    _rule("M101", severity="warn", profile="modeling_risk"),
    _rule("P101", severity="warn", profile="editorial"),
    _rule("D101", profile="description_logic"),
]


@pytest.fixture(autouse=True)
def fake_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ontopoiesis.lint.lint_registry.lint_rules", lambda: _FAKE_RULES)


def _codes(
    *,
    profiles: list[str] = [],
    select: list[str] = [],
    extend_select: list[str] = [],
    ignore: list[str] = [],
) -> list[str]:
    rules = resolve_lint_rule_selection(
        profiles=profiles, select=select, extend_select=extend_select, ignore=ignore
    )
    return [rule.code for rule in rules]


def test_default_selection_is_errors_and_warnings() -> None:
    assert _codes() == ["E101", "E102", "W101"]


def test_select_replaces_the_default_selection() -> None:
    assert _codes(select=["E101"]) == ["E101"]
    assert _codes(select=["E"]) == ["E101", "E102"]


def test_extend_select_adds_to_the_default_selection() -> None:
    assert _codes(extend_select=["M101"]) == ["E101", "E102", "W101", "M101"]


def test_ignore_removes_from_the_final_selection() -> None:
    assert _codes(ignore=["W101"]) == ["E101", "E102"]
    assert _codes(extend_select=["M101"], ignore=["W101"]) == ["E101", "E102", "M101"]


def test_profiles_extend_the_default_selection_by_code_prefix() -> None:
    assert _codes(profiles=["editorial"]) == ["E101", "E102", "W101", "P101"]
    assert _codes(profiles=["editorial", "description_logic"]) == [
        "E101",
        "E102",
        "W101",
        "P101",
        "D101",
    ]


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(LintRuleSelectionError, match="Unknown lint profile"):
        _codes(profiles=["nonexistent"])


def test_unknown_selector_is_rejected() -> None:
    with pytest.raises(LintRuleSelectionError, match="Unknown lint selector"):
        _codes(select=["Z999"])


def test_empty_resolution_is_rejected() -> None:
    with pytest.raises(LintRuleSelectionError, match="zero rules"):
        _codes(select=["E"], ignore=["E"])
