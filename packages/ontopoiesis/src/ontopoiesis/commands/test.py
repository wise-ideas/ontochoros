# No service layer: thin wrapper around ontopoiesis's Cypher test runtime plus pytest. Not a priority for extraction.
from pathlib import Path

import pytest
import typer

from ontopoiesis.cypher_test import cypher_plugin, resolve_cypher_tests
from ontopoiesis.path_validation import require_lbug_input


def test(
    ctx: typer.Context,
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    tests_paths: list[Path] | None = typer.Argument(None, exists=True, readable=True),
) -> None:
    """Run Cypher test queries against a Ladybug graph via pytest."""
    require_lbug_input(input_path)
    resolved = resolve_cypher_tests(tests_paths)
    if not resolved:
        location = ", ".join(str(path) for path in (tests_paths or [Path("tests")]))
        typer.echo(
            "No test_*.cypher, *_test.cypher, warn_*.cypher, or *_warn.cypher files found "
            f"in {location}",
            err=True,
        )
        raise typer.Exit(2)

    pytest_args = [
        "--ontology",
        str(input_path),
    ]
    pytest_args.extend(str(path) for path in (tests_paths or [Path("tests")]))
    pytest_args.extend(ctx.args)
    raise typer.Exit(pytest.main(pytest_args, plugins=[cypher_plugin]))
