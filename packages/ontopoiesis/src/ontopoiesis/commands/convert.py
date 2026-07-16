import logging
from pathlib import Path

import typer

from ontopoiesis import robot
from ontopoiesis.cli_ui import print_path_action
from ontopoiesis.output_paths import default_owlxml_output_path

_log = logging.getLogger(__name__)


def convert(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output_path: Path | None = typer.Option(None, "--output", "-o"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing output file."),
) -> None:
    """Convert an ontology document to OWL/XML via ROBOT (requires ROBOT_JAR).

    The input format is inferred from the file extension (.ttl, .owl, .ofn,
    .omn, .obo, ...). This is the opt-in bridge for non-OWL/XML sources: it
    shells out to a user-provided ROBOT jar and therefore needs a JVM. The
    rest of the toolchain stays pure Python.
    """
    resolved_output_path = output_path or default_owlxml_output_path(input_path)
    if resolved_output_path.exists() and not force:
        raise typer.BadParameter("output_path already exists; pass --force to overwrite.")
    _log.info("Converting %s to %s via ROBOT", input_path, resolved_output_path)
    robot.convert_to_owlxml(input_path, resolved_output_path)
    print_path_action("Wrote", resolved_output_path)
