import logging
from pathlib import Path

import typer

from ontopoiesis import robot
from ontopoiesis.cli_ui import print_path_action
from ontopoiesis.output_paths import default_resolved_output_path

_log = logging.getLogger(__name__)


def resolve(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output_path: Path | None = typer.Option(None, "--output", "-o"),
    catalog: Path | None = typer.Option(
        None,
        "--catalog",
        exists=True,
        dir_okay=False,
        readable=True,
        help="XML catalog that maps import IRIs to reproducible local documents.",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing output file."),
) -> None:
    """Resolve and merge an ontology's import closure into one OWL/XML document.

    Runs `robot merge --collapse-import-closure true` using a user-provided
    ROBOT jar. Pass an XML catalog for deterministic offline import resolution.
    """
    resolved_output_path = output_path or default_resolved_output_path(input_path)
    if resolved_output_path.exists() and not force:
        raise typer.BadParameter("output_path already exists; pass --force to overwrite.")
    _log.info("Resolving the import closure of %s into %s", input_path, resolved_output_path)
    robot.resolve_imports_to_owlxml(
        input_path,
        resolved_output_path,
        catalog=catalog,
    )
    print_path_action("Wrote", resolved_output_path)
