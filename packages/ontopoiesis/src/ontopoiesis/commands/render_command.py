from __future__ import annotations

from pathlib import Path

import typer

from ontopoiesis.cli_ui import print_notice, print_path_action, print_summary
from ontopoiesis.path_validation import require_lbug_input
from ontopoiesis.render import RenderFormat, render_projection

_FORMAT_BY_SUFFIX: dict[str, RenderFormat] = {
    ".svg": RenderFormat.SVG,
    ".png": RenderFormat.PNG,
    ".dot": RenderFormat.DOT,
}


def render(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    iris: list[str] | None = typer.Argument(None),
    output_path: Path = typer.Option(..., "--output", "-o", help="Output file path."),
    output_format: str | None = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: svg, png, or dot. Inferred from the --output extension when omitted.",
    ),
    include_external: bool = typer.Option(
        False,
        "--include-external",
        help="Include constructs referenced from outside the selected set.",
    ),
) -> None:
    """Render a construct graph from a Ladybug projection to SVG, PNG, or DOT.

    When one or more IRIs are given, the graph is restricted to those constructs
    and their immediate references. With no IRIs, the entire projection is rendered.

    \b
    Examples:
      ontopoiesis render graph.lbug -o graph.svg
      ontopoiesis render graph.lbug http://example.org/Person -o person.svg
      ontopoiesis render graph.lbug http://example.org/Person http://example.org/hasChild -o family.svg
      ontopoiesis render graph.lbug -o graph.png
      ontopoiesis render graph.lbug -o graph.dot
    """
    require_lbug_input(input_path)

    try:
        resolved_format = (
            RenderFormat(output_format)
            if output_format
            else _FORMAT_BY_SUFFIX.get(output_path.suffix.lower(), RenderFormat.SVG)
        )
    except ValueError:
        raise typer.BadParameter(
            f"Unsupported format '{output_format}'. Use svg, png, or dot.",
            param_hint="'--format'",
        )

    result = render_projection(
        input_path,
        iris or None,
        output_format=resolved_format,
        include_external=include_external,
    )

    result.write_to(output_path)

    for iri in result.missing_iris:
        print_notice(f"IRI not found in projection: {iri}", err=True)

    print_path_action("Wrote", output_path)
    print_summary(
        "Render Complete",
        [
            ("nodes", result.node_count),
            ("edges", result.edge_count),
            ("format", resolved_format.value),
        ],
    )
