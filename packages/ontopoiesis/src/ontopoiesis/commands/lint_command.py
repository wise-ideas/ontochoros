from pathlib import Path

import typer

from ontopoiesis.cli_ui import print_notice, print_summary, print_violation_rows
from ontopoiesis.lint import resolve_lint_rule_selection, run_lint_on_path
from ontopoiesis.path_validation import require_lbug_input


def lint(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    profile: list[str] = typer.Option(
        [],
        "--profile",
        help="Include a bundled supplemental lint profile.",
    ),
    select: list[str] = typer.Option(
        [],
        "--select",
        help="Comma-delimited rule codes or prefixes to run, replacing the default selection.",
    ),
    extend_select: list[str] = typer.Option(
        [],
        "--extend-select",
        help="Comma-delimited rule codes or prefixes to add to the default selection.",
    ),
    ignore: list[str] = typer.Option(
        [],
        "--ignore",
        help="Comma-delimited rule codes or prefixes to exclude from the final selection.",
    ),
) -> None:
    """Run built-in structural quality checks against a Ladybug projection."""
    require_lbug_input(input_path)
    rules = resolve_lint_rule_selection(
        profiles=profile,
        select=select,
        extend_select=extend_select,
        ignore=ignore,
    )
    results = run_lint_on_path(
        input_path,
        rules=rules,
    )

    for violation in results.failures:
        print_notice(f"FAIL {violation.path.name}", err=True)
        print_violation_rows(violation.rows, err=True)
    for violation in results.warnings:
        print_notice(f"WARN {violation.path.name}")
        print_violation_rows(violation.rows)

    if not results.violations:
        print_notice("No lint violations found.")

    print_summary(
        "Lint Complete",
        [
            ("rules", len(rules)),
            ("failures", len(results.failures)),
            ("warnings", len(results.warnings)),
        ],
    )
    raise typer.Exit(1 if results.failures else 0)
