"""Ladybug-backed projection storage for OWL/XML graphs.

One node table ``N`` (kind plus the fixed scalar-property columns from the
OWL/XML mapping) and one relationship table ``E`` (position, role). The
`Projection` handle is read-only; `WritableProjection` supports graph-native
authoring with raw Cypher.
"""

from __future__ import annotations

import dataclasses

# real_ladybug (0.15.x) calls importlib.util during prepare() without
# importing the submodule; importing it here keeps that from blowing up.
import importlib.util  # noqa: F401
import os
import tempfile
from pathlib import Path
from typing import Protocol, cast

import pyarrow
import real_ladybug

from ontoplexis.owlxml import SCALAR_PROPERTIES, Edge, Graph, Node, OwlXmlStructureError

NODE_TABLE = "N"
RELATIONSHIP_TABLE = "E"

QueryRow = dict[str, object]


class ProjectionStorageError(ValueError):
    """Raised when a projection cannot be opened or has been closed."""


@dataclasses.dataclass(frozen=True, slots=True)
class _OwnedTempDir:
    temp_dir: tempfile.TemporaryDirectory[str]

    @property
    def database_path(self) -> Path:
        return Path(self.temp_dir.name) / "projection.lbug"

    def close(self) -> None:
        self.temp_dir.cleanup()


class Projection:
    """Read-only Ladybug-backed projection handle."""

    def __init__(
        self,
        *,
        database: real_ladybug.Database,
        connection: real_ladybug.Connection,
        database_path: str | Path,
        owned_temp_dir: _OwnedTempDir | None = None,
    ) -> None:
        self._database = database
        self._connection = connection
        self._database_path = Path(database_path)
        self._owned_temp_dir = owned_temp_dir
        self._closed = False

    def __enter__(self) -> Projection:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    @classmethod
    def open(cls, path: str | Path) -> Projection:
        return _open_projection(database_path=path, read_only=True, cls=cls)

    def execute(self, query: str, parameters: dict[str, object] | None = None) -> list[QueryRow]:
        if self._closed:
            raise ProjectionStorageError("Projection is closed.")
        response = self._connection.execute(query, parameters=parameters)
        return _query_rows(response)

    @property
    def node_count(self) -> int:
        return self._count(f"MATCH (n:{NODE_TABLE}) RETURN count(n) AS count")

    @property
    def edge_count(self) -> int:
        return self._count(f"MATCH ()-[r:{RELATIONSHIP_TABLE}]->() RETURN count(r) AS count")

    def _count(self, query: str) -> int:
        (row,) = self.execute(query)
        value = row.get("count")
        return value if isinstance(value, int) else 0

    @property
    def database_path(self) -> Path:
        return self._database_path

    def graph(self) -> Graph:
        """Load the entire projection back into an OWL/XML `Graph`.

        Raises `OwlXmlStructureError` if an authored node lacks a string
        `kind` or an authored edge lacks an integer `position`.
        """
        columns = ", ".join(
            ["n.uid AS uid", "n.kind AS kind"]
            + [f"n.{name} AS {name}" for name, _ in SCALAR_PROPERTIES]
        )
        nodes = []
        for row in self.execute(f"MATCH (n:{NODE_TABLE}) RETURN {columns}"):
            uid = row.get("uid")
            kind = row.get("kind")
            if not isinstance(uid, str) or not isinstance(kind, str):
                raise OwlXmlStructureError(
                    f"Projection node {uid!r} must have string uid and kind properties; "
                    f"got kind={kind!r}."
                )
            properties: dict[str, str | int] = {}
            for name, _ in SCALAR_PROPERTIES:
                value = row.get(name)
                if isinstance(value, str | int) and not isinstance(value, bool):
                    properties[name] = value
            nodes.append(Node(uid=uid, kind=kind, properties=properties))

        edges = []
        edge_rows = self.execute(
            f"MATCH (a:{NODE_TABLE})-[r:{RELATIONSHIP_TABLE}]->(b:{NODE_TABLE}) "
            "RETURN a.uid AS source, b.uid AS target, r.position AS position, r.role AS role"
        )
        for row in edge_rows:
            source = row.get("source")
            target = row.get("target")
            position = row.get("position")
            role = row.get("role")
            if not isinstance(source, str) or not isinstance(target, str):
                raise OwlXmlStructureError(
                    f"Projection edge {source!r}->{target!r} must join nodes with string uids."
                )
            if not isinstance(position, int) or isinstance(position, bool):
                raise OwlXmlStructureError(
                    f"Projection edge {source!r}->{target!r} must have an integer position; "
                    f"got {position!r}."
                )
            edges.append(
                Edge(
                    source=source,
                    target=target,
                    position=position,
                    role=role if isinstance(role, str) and role else None,
                )
            )
        return Graph(nodes=tuple(nodes), edges=tuple(edges))

    def _close_handles(self) -> None:
        self._closed = True
        for handle in (self._connection, self._database):
            close = getattr(handle, "close", None)
            if callable(close):
                close()

    def close(self) -> None:
        try:
            self._close_handles()
        finally:
            if self._owned_temp_dir is not None:
                self._owned_temp_dir.close()
                self._owned_temp_dir = None


class WritableProjection(Projection):
    """Writable Ladybug-backed projection handle for graph-native authoring."""

    @classmethod
    def open(cls, path: str | Path | None = None) -> WritableProjection:
        if path is None:
            return _create_writable(cls=cls)
        resolved_path = Path(path)
        if resolved_path.exists():
            return cast(
                WritableProjection,
                _open_projection(database_path=resolved_path, read_only=False, cls=cls),
            )
        return _create_writable(path=resolved_path, cls=cls)

    def reopen_readonly(self) -> Projection:
        database_path = self.database_path
        owned_temp_dir = self._owned_temp_dir
        self._owned_temp_dir = None
        self._close_handles()
        return _open_projection(
            database_path=database_path,
            read_only=True,
            cls=Projection,
            owned_temp_dir=owned_temp_dir,
        )


def build_projection(graph: Graph) -> Projection:
    """Build one in-memory (temp-file) read-only projection from a graph."""
    writable = _create_writable(cls=WritableProjection)
    try:
        _populate(writable._connection, graph)
    except Exception:
        writable.close()
        raise
    return writable.reopen_readonly()


def save_projection(graph: Graph, path: str | Path) -> Projection:
    """Materialize a projection at *path* and return a read-only handle."""
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target_path.stem}.", suffix=".lbug", dir=target_path.parent
    )
    os.close(fd)
    temp_path = Path(temp_name)
    writable = _create_writable(path=temp_path, cls=WritableProjection)
    try:
        try:
            _populate(writable._connection, graph)
        finally:
            writable.close()
        os.replace(temp_path, target_path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
    return Projection.open(target_path)


def _open_projection(
    *,
    database_path: str | Path | None = None,
    read_only: bool = False,
    cls: type[Projection],
    owned_temp_dir: _OwnedTempDir | None = None,
) -> Projection:
    resolved_path = database_path
    if resolved_path is None:
        if read_only:
            raise ProjectionStorageError("Read-only projections require a filesystem database path")
        owned_temp_dir = _OwnedTempDir(tempfile.TemporaryDirectory(prefix="ontoplexis-projection-"))
        resolved_path = owned_temp_dir.database_path
    database = real_ladybug.Database(resolved_path, read_only=read_only)
    connection = real_ladybug.Connection(database)
    return cls(
        database=database,
        connection=connection,
        database_path=resolved_path,
        owned_temp_dir=owned_temp_dir,
    )


def _create_writable(
    path: str | Path | None = None,
    *,
    cls: type[WritableProjection],
) -> WritableProjection:
    handle = cast(
        WritableProjection,
        _open_projection(database_path=path, read_only=False, cls=cls),
    )
    try:
        _initialize_schema(handle._connection)
    except Exception:
        handle.close()
        raise
    return handle


def _initialize_schema(conn: real_ladybug.Connection) -> None:
    property_columns = ", ".join(f"{name} {db_type}" for name, db_type in SCALAR_PROPERTIES)
    conn.execute(
        f"CREATE NODE TABLE {NODE_TABLE}(uid STRING PRIMARY KEY, kind STRING, {property_columns})"
    )
    conn.execute(
        f"CREATE REL TABLE {RELATIONSHIP_TABLE}"
        f"(FROM {NODE_TABLE} TO {NODE_TABLE}, position INT64, role STRING)"
    )


def _populate(conn: real_ladybug.Connection, graph: Graph) -> None:
    """Bulk-load a graph by COPY-ing in-memory Arrow tables.

    Arrow tables passed as query parameters are the only ingestion path that
    is simultaneously safe and fast; the two rejected alternatives are traps:

    - CSV temp files + ``COPY ... FROM '<path>'`` splice a filesystem path
      into a Cypher string (a quote in the path breaks the statement) and
      cannot represent NULL vs empty string.
    - Parameterized ``UNWIND $rows ... CREATE`` needs no dependency but costs
      ~1.6 ms per edge into high-degree nodes — and every ontology graph is
      hub-shaped, because the Ontology root has one edge per axiom. A
      50k-axiom load took minutes; this COPY path takes ~1 s.

    Values travel as query parameters, never through files or string
    interpolation, so quotes, newlines, and NULL-vs-empty survive verbatim.
    Explicit schemas keep all-NULL columns typed (pyarrow would otherwise
    infer an untyped null column, which COPY rejects).
    """
    arrow_types = {"STRING": pyarrow.string(), "INT64": pyarrow.int64()}

    node_columns: dict[str, list[object]] = {
        "uid": [node.uid for node in graph.nodes],
        "kind": [node.kind for node in graph.nodes],
    }
    for name, _ in SCALAR_PROPERTIES:
        node_columns[name] = [node.properties.get(name) for node in graph.nodes]
    node_schema = pyarrow.schema(
        [("uid", pyarrow.string()), ("kind", pyarrow.string())]
        + [(name, arrow_types[db_type]) for name, db_type in SCALAR_PROPERTIES]
    )
    conn.execute(
        f"COPY {NODE_TABLE} FROM $nodes",
        parameters={"nodes": pyarrow.table(node_columns, schema=node_schema)},
    )

    if not graph.edges:
        return
    edge_columns: dict[str, list[object]] = {
        "from": [edge.source for edge in graph.edges],
        "to": [edge.target for edge in graph.edges],
        "position": [edge.position for edge in graph.edges],
        "role": [edge.role for edge in graph.edges],
    }
    edge_schema = pyarrow.schema(
        [
            ("from", pyarrow.string()),
            ("to", pyarrow.string()),
            ("position", pyarrow.int64()),
            ("role", pyarrow.string()),
        ]
    )
    conn.execute(
        f"COPY {RELATIONSHIP_TABLE} FROM $edges",
        parameters={"edges": pyarrow.table(edge_columns, schema=edge_schema)},
    )


class _LadybugRows(Protocol):
    def get_all(self) -> list[QueryRow]: ...


class _LadybugRowsResult(Protocol):
    def rows_as_dict(self) -> _LadybugRows: ...


def _query_rows(
    response: real_ladybug.QueryResult | list[real_ladybug.QueryResult],
) -> list[QueryRow]:
    result = response[0] if isinstance(response, list) else response
    return cast(_LadybugRowsResult, result).rows_as_dict().get_all()


__all__ = [
    "NODE_TABLE",
    "Projection",
    "ProjectionStorageError",
    "QueryRow",
    "RELATIONSHIP_TABLE",
    "WritableProjection",
    "build_projection",
    "save_projection",
]
