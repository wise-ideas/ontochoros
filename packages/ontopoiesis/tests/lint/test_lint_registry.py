from ontopoiesis.lint import (
    available_lint_profiles,
    lint_rule_lookup,
    lint_rules,
    resolve_lint_rule_paths,
)


def test_available_lint_profiles_excludes_core_baseline() -> None:
    assert available_lint_profiles() == ["description_logic", "editorial", "modeling_risk"]


def test_lint_rule_codes_are_unique() -> None:
    codes = [rule.code for rule in lint_rules()]

    assert len(codes) == len(set(codes))


def test_resolve_lint_rule_paths_defaults_to_core_error_and_warning_rules() -> None:
    paths = resolve_lint_rule_paths(select=[], extend_select=[], ignore=[])

    assert paths == [rule.path for rule in lint_rules() if rule.code.startswith(("E", "W"))]


def test_resolve_lint_rule_paths_supports_prefix_selection_and_ignore() -> None:
    paths = resolve_lint_rule_paths(select=["E"], extend_select=[], ignore=["E101"])

    assert paths == [
        rule.path for rule in lint_rules() if rule.code.startswith("E") and rule.code != "E101"
    ]


def test_lint_rule_lookup_includes_specific_rule() -> None:
    rule = lint_rule_lookup()["P101"]

    assert rule.path.name == "warn_missing_label.cypher"
