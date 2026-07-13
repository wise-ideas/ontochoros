import logging
from pathlib import Path

import typer
from ontoplexis import Ontology, Projection

from ontopoiesis.cli_ui import print_path_action, print_summary
from ontopoiesis.output_paths import default_owlxml_output_path
from ontopoiesis.path_validation import require_lbug_input

_log = logging.getLogger(__name__)


def export(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output_path: Path | None = typer.Option(None, "--output", "-o"),
) -> None:
    """Serialize a Ladybug graph projection to an OWL/XML document."""
    require_lbug_input(input_path)
    resolved_output_path = output_path or default_owlxml_output_path(input_path)

    _log.info("Exporting projection %s to %s", input_path, resolved_output_path)
    with Projection.open(input_path) as projection:
        document = Ontology.from_projection(projection).to_owlxml()

    resolved_output_path.write_text(document, encoding="utf-8")
    print_path_action("Wrote", resolved_output_path)
    print_summary("Export Complete", [("characters", len(document))])
