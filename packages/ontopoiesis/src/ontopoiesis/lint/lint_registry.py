from __future__ import annotations

import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

from ontopoiesis.errors import OntopoiesisDomainError

if TYPE_CHECKING:
    from ontoplexis import Projection

    QueryRow = dict[str, object]


class LintRuleSelectionError(OntopoiesisDomainError, ValueError):
    """Raised when lint rule selection fails due to invalid profiles or selectors."""


_PROFILE_DIRS: dict[str, Path] = {
    "core": Path(__file__).parent / "lint",
    "editorial": Path(__file__).parent / "lint_profiles" / "editorial",
    "modeling_risk": Path(__file__).parent / "lint_profiles" / "modeling_risk",
    "description_logic": Path(__file__).parent / "lint_profiles" / "description_logic",
}


@dataclass(frozen=True)
class LintRule:
    code: str
    path: Path
    summary: str
    severity: str
    profile: str

    @property
    def is_warn(self) -> bool:
        return self.severity == "warn"

    def evaluate(self, connection: Projection) -> list[QueryRow]:
        """Run this rule's Cypher query and return any violation rows."""
        query = self.path.read_text()
        return connection.execute(query)


def lint_rules_root() -> Path:
    return Path(__file__).parent


@cache
def lint_rules() -> list[LintRule]:
    rules: list[LintRule] = []
    for profile, directory in _PROFILE_DIRS.items():
        registry_path = directory / "registry.toml"
        with registry_path.open("rb") as f:
            data = tomllib.load(f)
        for entry in data.get("rules", []):
            rules.append(
                LintRule(
                    code=entry["code"],
                    path=directory / entry["file"],
                    summary=entry["summary"],
                    severity=entry["severity"],
                    profile=profile,
                )
            )
    return rules


def lint_rule_lookup() -> dict[str, LintRule]:
    return {rule.code: rule for rule in lint_rules()}


def available_lint_profiles() -> list[str]:
    return sorted({rule.profile for rule in lint_rules() if rule.profile != "core"})


def selectors_for_profile(name: str) -> tuple[str, ...]:
    selectors = {rule.code[0] for rule in lint_rules() if rule.profile == name and rule.code}
    if not selectors:
        raise KeyError(name)
    return tuple(sorted(selectors))


def resolve_lint_rules(
    *,
    select: list[str],
    extend_select: list[str],
    ignore: list[str],
) -> list[LintRule]:
    rules = lint_rules()
    if select:
        active = _match_rules(rules, select)
    else:
        active = _match_rules(rules, ["E", "W"])
        active.update(_match_rules(rules, extend_select))
    active.difference_update(_match_rules(rules, ignore))
    return [rule for rule in rules if rule in active]


def resolve_lint_rule_paths(
    *,
    select: list[str],
    extend_select: list[str],
    ignore: list[str],
) -> list[Path]:
    return [
        rule.path
        for rule in resolve_lint_rules(select=select, extend_select=extend_select, ignore=ignore)
    ]


def expand_selector_values(values: list[str]) -> list[str]:
    selectors: list[str] = []
    for value in values:
        for selector in value.split(","):
            normalized = selector.strip().upper()
            if normalized:
                selectors.append(normalized)
    return selectors


def unknown_lint_selectors(selectors: list[str]) -> list[str]:
    rules = lint_rules()
    unknown: list[str] = []
    for selector in selectors:
        if not _match_rules(rules, [selector]):
            unknown.append(selector)
    return unknown


def _match_rules(rules: list[LintRule], selectors: list[str]) -> set[LintRule]:
    matched: set[LintRule] = set()
    for selector in selectors:
        matched.update(rule for rule in rules if rule.code.startswith(selector))
    return matched


def resolve_lint_rule_selection(
    *,
    profiles: list[str],
    select: list[str],
    extend_select: list[str],
    ignore: list[str],
) -> list[LintRule]:
    """Resolve and validate lint rules for the given selector arguments."""
    unknown_profiles = [name for name in profiles if name not in available_lint_profiles()]
    if unknown_profiles:
        supported = ", ".join(available_lint_profiles())
        raise LintRuleSelectionError(
            f"Unknown lint profile(s): {', '.join(unknown_profiles)}. "
            f"Supported profiles: {supported}."
        )
    select_selectors = expand_selector_values(select)
    extend_selectors = expand_selector_values(extend_select)
    ignore_selectors = expand_selector_values(ignore)
    profile_selectors = [selector for name in profiles for selector in selectors_for_profile(name)]
    invalid_selectors = unknown_lint_selectors(
        select_selectors + extend_selectors + ignore_selectors + profile_selectors
    )
    if invalid_selectors:
        supported = ", ".join(sorted(lint_rule_lookup()))
        raise LintRuleSelectionError(
            f"Unknown lint selector(s): {', '.join(invalid_selectors)}. "
            f"Supported rule codes: {supported}."
        )
    rules = resolve_lint_rules(
        select=select_selectors,
        extend_select=extend_selectors + profile_selectors,
        ignore=ignore_selectors,
    )
    if not rules:
        raise LintRuleSelectionError("The active lint selection resolved to zero rules.")
    return rules
