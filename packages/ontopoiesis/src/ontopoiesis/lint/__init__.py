from pathlib import Path

from .checker import (
    LintResults,
    LintViolation,
    run_lint_on_path,
)
from .lint_registry import (
    LintRule,
    LintRuleSelectionError,
    available_lint_profiles,
    expand_selector_values,
    lint_rule_lookup,
    lint_rules,
    resolve_lint_rule_paths,
    resolve_lint_rule_selection,
    resolve_lint_rules,
    selectors_for_profile,
    unknown_lint_selectors,
)


def lint_dir() -> Path:
    """Return the path to the built-in lint rule directory."""
    return Path(__file__).parent / "lint"


def lint_profile_dir(name: str) -> Path:
    """Return the path to a supplemental lint profile directory."""
    return Path(__file__).parent / "lint_profiles" / name


__all__ = [
    "LintResults",
    "LintRule",
    "LintViolation",
    "LintRuleSelectionError",
    "available_lint_profiles",
    "expand_selector_values",
    "lint_dir",
    "lint_profile_dir",
    "lint_rule_lookup",
    "lint_rules",
    "resolve_lint_rule_paths",
    "resolve_lint_rule_selection",
    "resolve_lint_rules",
    "run_lint_on_path",
    "selectors_for_profile",
    "unknown_lint_selectors",
]
