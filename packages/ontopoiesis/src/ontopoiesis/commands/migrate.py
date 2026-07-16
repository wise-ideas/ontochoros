from __future__ import annotations

from pathlib import Path
from shutil import copyfile

import typer

from ontopoiesis.cli_ui import print_path_action, print_summary
from ontopoiesis.migrations.runner import MigrationRunner
from ontopoiesis.output_paths import default_lbug_output_path
from ontopoiesis.path_validation import require_lbug_output


def migrate(
    migrations_dir: Path = typer.Argument(..., exists=True, file_okay=False, readable=True),
    output_path: Path | None = typer.Option(None, "--output", "-o"),
    force: bool = typer.Option(False, "--force", help="Rebuild the output .lbug from scratch."),
) -> None:
    """Apply Cypher migration scripts and write the resulting .lbug projection."""
    resolved_output_path = require_lbug_output(
        output_path or default_lbug_output_path(migrations_dir)
    )
    start_from = resolved_output_path if resolved_output_path.exists() and not force else None
    if resolved_output_path.exists() and force:
        resolved_output_path.unlink()

    with MigrationRunner(start_from=start_from) as runner:
        result = runner.apply_all(migrations_dir)
        # Migrations mutate N/E directly, so the derived-edge cache is stale;
        # rebuild it before the projection is finalized (both fresh and
        # incremental paths persist from this same writable session).
        runner.refresh_derived_edges()
        if start_from is None:
            db_path = runner.database_path
            projection = runner.build_database()
            try:
                copyfile(db_path, resolved_output_path)
            finally:
                projection.close()

    print_path_action("Wrote", resolved_output_path)
    print_summary("Migrate Complete", [("nodes", result.node_count), ("edges", result.edge_count)])
