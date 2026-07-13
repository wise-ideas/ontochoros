# No service layer: thin wrapper around ontoplexis query execution. Not a priority for extraction.
from pathlib import Path

import typer
from ontoplexis import Projection

from ontopoiesis.cli_ui import print_query_table
from ontopoiesis.path_validation import require_lbug_input


def query(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    cypher: str = typer.Option(..., "--query", "-q"),
) -> None:
    """Run a Cypher query against a Ladybug graph projection."""
    require_lbug_input(input_path)
    with Projection.open(input_path) as projection:
        result = projection.execute(cypher)

    if not result:
        return

    print_query_table(result)
