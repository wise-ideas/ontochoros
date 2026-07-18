"""Migration runner for concrete Cypher-based ontology projections."""

from __future__ import annotations

import functools
import logging
from pathlib import Path
from typing import Any, NamedTuple, cast

import jinja2
from ontoplexis import (
    NODE_TABLE,
    RELATIONSHIP_TABLE,
    Graph,
    Projection,
    ProjectionStorageError,
    WritableProjection,
    derive_edges,
)

from ontopoiesis.errors import OntopoiesisDomainError
from ontopoiesis.migrations.uids import axiom_uid, scalar_uid

_log = logging.getLogger(__name__)
MIGRATION_METADATA_TABLE = "OntopoiesisMigration"


class MigrationError(OntopoiesisDomainError, ValueError):
    """Raised when a migration set is invalid before execution."""


class MigrationRecord(NamedTuple):
    """Metadata for one applied migration."""

    migration_id: str
    path: Path


class MigrationResult(NamedTuple):
    """Summary returned by apply_all."""

    applied: list[MigrationRecord]
    node_count: int
    edge_count: int


class MigrationRunner:
    """Apply rendered Cypher migrations directly against a writable projection."""

    def __init__(self, start_from: Path | None = None) -> None:
        self._projection: WritableProjection | None = WritableProjection.open(start_from)
        projection = self._require_projection()
        _ensure_migration_metadata_schema(projection)
        self._applied: list[str] = _load_applied_migration_ids(projection)

    def __enter__(self) -> MigrationRunner:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @property
    def applied_migrations(self) -> list[str]:
        return list(self._applied)

    def _require_projection(self) -> WritableProjection:
        if self._projection is None:
            raise ProjectionStorageError("MigrationRunner has been closed")
        return self._projection

    @property
    def node_count(self) -> int:
        return self._require_projection().node_count

    @property
    def edge_count(self) -> int:
        return self._require_projection().edge_count

    def close(self) -> None:
        if self._projection is not None:
            self._projection.close()
            self._projection = None

    def apply_all(self, migrations_dir: str | Path) -> MigrationResult:
        migrations_dir = Path(migrations_dir)
        _log.info("Applying migrations from %s", migrations_dir)
        applied: list[MigrationRecord] = []
        migration_paths = tuple(sorted(migrations_dir.glob("*.cypher")))
        _validate_unique_migration_ids(migration_paths)
        for path in migration_paths:
            record = self.apply_file(path)
            if record is not None:
                applied.append(record)
        node_count = self.node_count
        edge_count = self.edge_count
        _log.info(
            "Applied %d migration(s): %d nodes, %d edges",
            len(applied),
            node_count,
            edge_count,
        )
        return MigrationResult(applied=applied, node_count=node_count, edge_count=edge_count)

    def apply_file(self, path: str | Path) -> MigrationRecord | None:
        projection = self._require_projection()
        path = Path(path)
        text = _render_template(path)
        migration_id = _migration_id_for_path(path)
        if migration_id in self._applied:
            _log.debug("Skipping already-applied migration: %s", migration_id)
            return None
        _log.debug("Applying migration: %s", migration_id)
        if _has_executable_content(text):
            projection.execute(text)
        _record_applied_migration(projection, migration_id)
        self._applied.append(migration_id)
        return MigrationRecord(
            migration_id=migration_id,
            path=path,
        )

    def refresh_derived_edges(self) -> None:
        """Rebuild the derived-edge table (``D``) after migrations mutate N/E.

        Migrations author the structural ``N``/``E`` tables directly, which
        leaves any previously materialized derived edges stale. Re-derive so the
        query convenience layer matches the migrated structure.
        """
        derive_edges(self._require_projection())

    def graph(self) -> Graph:
        return self._require_projection().graph()

    @property
    def database_path(self) -> Path:
        return self._require_projection().database_path

    def build_database(self) -> Projection:
        """Convert the writable projection to a read-only connection.

        Reopens the underlying file directly without a full graph load/write
        round-trip. After this call the runner is closed and must not be used.
        """
        writable = self._require_projection()
        self._projection = None
        return writable.reopen_readonly()


@functools.lru_cache(maxsize=None)
def _make_template_env(directory: Path) -> jinja2.Environment:
    env = jinja2.Environment(
        block_start_string="{%",
        block_end_string="%}",
        variable_start_string="<<",
        variable_end_string=">>",
        loader=jinja2.FileSystemLoader(str(directory)),
        keep_trailing_newline=True,
    )
    globals_: dict[str, Any] = cast(dict[str, Any], env.globals)
    globals_["node_table"] = lambda kind: NODE_TABLE
    globals_["rel_table"] = lambda role, endpoint_order=None: RELATIONSHIP_TABLE
    globals_["scalar_uid"] = scalar_uid
    globals_["axiom_uid"] = axiom_uid
    return env


def _render_template(path: Path) -> str:
    """Render a Cypher migration template file using Jinja2."""
    return _make_template_env(path.parent).get_template(path.name).render()


def _migration_id_for_path(path: Path) -> str:
    return path.stem.partition("__")[0] or path.stem


def _validate_unique_migration_ids(paths: tuple[Path, ...]) -> None:
    seen: dict[str, Path] = {}
    for path in paths:
        migration_id = _migration_id_for_path(path)
        previous = seen.get(migration_id)
        if previous is not None:
            raise MigrationError(
                f"Duplicate migration id {migration_id!r} in {previous.name!r} and {path.name!r}"
            )
        seen[migration_id] = path


def _ensure_migration_metadata_schema(projection: WritableProjection) -> None:
    projection.execute(
        f"CREATE NODE TABLE IF NOT EXISTS {MIGRATION_METADATA_TABLE}"
        "(migration_id STRING PRIMARY KEY)"
    )


def _load_applied_migration_ids(projection: WritableProjection) -> list[str]:
    rows = projection.execute(
        f"MATCH (m:{MIGRATION_METADATA_TABLE}) "
        "RETURN m.migration_id AS migration_id ORDER BY m.migration_id"
    )
    migration_ids: list[str] = []
    for row in rows:
        migration_id = row.get("migration_id")
        if not isinstance(migration_id, str):
            raise MigrationError("Stored migration metadata row is missing migration_id")
        migration_ids.append(migration_id)
    return migration_ids


def _record_applied_migration(projection: WritableProjection, migration_id: str) -> None:
    projection.execute(
        f"MERGE (m:{MIGRATION_METADATA_TABLE} {{migration_id: $migration_id}})",
        parameters={"migration_id": migration_id},
    )


def _has_executable_content(text: str) -> bool:
    """Return whether a migration has any statement to run.

    The engine parses ``//`` line comments (leading and trailing) natively, so
    migrations are executed verbatim and ``//`` inside a string literal is left
    intact. This only screens out comment-only files, which the parser would
    otherwise reject with a spurious "expecting statement" error.
    """
    return any(
        stripped and not stripped.startswith("//")
        for line in text.splitlines()
        if (stripped := line.strip())
    )
