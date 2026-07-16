from __future__ import annotations

from pathlib import Path

import typer
from ontoplexis import Ontology

from ontopoiesis.cli_ui import print_path_action, print_summary
from ontopoiesis.output_paths import default_lbug_output_path
from ontopoiesis.path_validation import require_lbug_output


def build(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output_path: Path | None = typer.Option(None, "--output", "-o"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing .lbug output file."),
) -> None:
    """Build a Ladybug graph projection from an OWL/XML document.

    Other serializations (Turtle, RDF/XML, functional syntax, …) must be
    pre-converted to OWL/XML with an external tool such as ROBOT or Protégé.
    """
    output_path = require_lbug_output(output_path or default_lbug_output_path(input_path))
    if output_path.exists():
        if not force:
            raise typer.BadParameter("output_path already exists; pass --force to overwrite.")
    ontology = Ontology.from_owlxml(input_path.read_text(encoding="utf-8"))
    projection = ontology.save_projection(output_path)
    try:
        node_count = projection.node_count
        edge_count = projection.edge_count
        derived_count = projection.derived_count
    finally:
        projection.close()
    print_path_action("Wrote", output_path)
    print_summary(
        "Build Complete",
        [("nodes", node_count), ("edges", edge_count), ("derived", derived_count)],
    )
