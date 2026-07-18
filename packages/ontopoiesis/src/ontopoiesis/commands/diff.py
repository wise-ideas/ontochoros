import dataclasses
import json
from pathlib import Path

import typer

from ontopoiesis.cli_ui import print_notice, print_query_table
from ontopoiesis.diff_projection import DiffRow, diff_projections
from ontopoiesis.path_validation import require_lbug_input


def _render_diff_rows(rows: list[DiffRow], output_format: str) -> str:
    if output_format == "json":
        return json.dumps([dataclasses.asdict(row) for row in rows], indent=2) + "\n"
    headers = (
        "status",
        "kind",
        "iri",
        "count",
        "fingerprint",
        "ontology_iri",
    )
    lines: list[str] = ["\t".join(headers)]
    for row in rows:
        lines.append(
            "\t".join(
                [
                    row.status,
                    row.kind,
                    row.iri,
                    str(row.count),
                    row.fingerprint,
                    row.ontology_iri or "",
                ]
            )
        )
    return "\n".join(lines) + "\n"


def diff(
    before_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    after_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output_path: Path | None = typer.Option(None, "--output", "-o"),
    output_format: str = typer.Option("table", "--format"),
) -> None:
    """Compute a semantic diff between two Ladybug projections."""
    require_lbug_input(before_path, parameter_name="before_path")
    require_lbug_input(after_path, parameter_name="after_path")
    if output_format not in {"table", "json"}:
        raise typer.BadParameter("output_format must be one of: table, json")

    rows = diff_projections(before_path, after_path)

    if output_path is not None:
        output_path.write_text(_render_diff_rows(rows, output_format), encoding="utf-8")
    elif not rows:
        print_notice("No differences found.")
    elif output_format == "json":
        typer.echo(_render_diff_rows(rows, output_format), nl=False)
    else:
        print_query_table([dataclasses.asdict(row) for row in rows])
    raise typer.Exit(code=1 if rows else 0)
