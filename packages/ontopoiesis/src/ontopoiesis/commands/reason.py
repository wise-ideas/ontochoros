import logging
from pathlib import Path

import typer

from ontopoiesis import robot
from ontopoiesis.cli_ui import print_path_action

_log = logging.getLogger(__name__)


def _default_reasoned_output_path(input_path: Path) -> Path:
    return input_path.with_suffix(".reasoned.owx")


def reason(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output_path: Path | None = typer.Option(None, "--output", "-o"),
    reasoner: str = typer.Option(
        "ELK", "--reasoner", help="Reasoner to run: ELK, HermiT, whelk, JFact, EMR."
    ),
    annotate: bool = typer.Option(
        True,
        "--annotate/--no-annotate",
        help="Annotate each inferred axiom with `is_inferred true` for provenance.",
    ),
    include_indirect: bool = typer.Option(
        False,
        "--include-indirect",
        help="Also assert indirect inferred axioms (the full hierarchy, not just "
        "direct non-redundant inferences), so every entailed subsumption is one edge.",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing output file."),
) -> None:
    """Materialize inferred axioms into a new OWL/XML document via ROBOT.

    Runs `robot reason` (requires ROBOT_JAR and a JVM): the output document
    contains the original axioms plus the reasoner's inferences. Build it like
    any other document — inferred axioms are then ordinary told structure, and
    the derived-edge cache makes entailed subsumptions one hop. Reasoning
    itself always stays outside the graph.
    """
    resolved_output_path = output_path or _default_reasoned_output_path(input_path)
    if resolved_output_path.exists() and not force:
        raise typer.BadParameter("output_path already exists; pass --force to overwrite.")
    _log.info("Reasoning %s with %s into %s", input_path, reasoner, resolved_output_path)
    robot.reason_to_owlxml(
        input_path,
        resolved_output_path,
        reasoner=reasoner,
        annotate=annotate,
        include_indirect=include_indirect,
    )
    print_path_action("Wrote", resolved_output_path)
