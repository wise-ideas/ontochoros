"""Facts about the real rule registry (policy lives in test_selection_policy)."""

from ontopoiesis.lint import (
    available_lint_profiles,
    lint_rule_lookup,
    lint_rules,
    resolve_lint_rule_paths,
    resolve_lint_rule_selection,
)
from ontopoiesis.lint.lint_registry import lint_rules_root


def test_available_lint_profiles_match_the_bundled_profile_directories() -> None:
    # Derived from the filesystem so adding a profile directory cannot
    # silently diverge from what selection offers.
    profile_dirs = sorted(
        path.name for path in (lint_rules_root() / "lint_profiles").iterdir() if path.is_dir()
    )

    assert available_lint_profiles() == profile_dirs
    assert "core" not in available_lint_profiles()


def test_every_registered_rule_file_exists() -> None:
    missing = [str(rule.path) for rule in lint_rules() if not rule.path.is_file()]

    assert missing == []


def test_lint_rule_codes_are_unique() -> None:
    codes = [rule.code for rule in lint_rules()]

    assert len(codes) == len(set(codes))


def test_resolve_lint_rule_paths_agrees_with_rule_selection() -> None:
    paths = resolve_lint_rule_paths(select=[], extend_select=[], ignore=[])
    rules = resolve_lint_rule_selection(profiles=[], select=[], extend_select=[], ignore=[])

    assert paths == [rule.path for rule in rules]


def test_lint_rule_lookup_includes_specific_rule() -> None:
    rule = lint_rule_lookup()["P101"]

    assert rule.path.name == "warn_missing_label.cypher"
