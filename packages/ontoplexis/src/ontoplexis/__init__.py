"""Cypher-queryable OWL 2 ontologies.

One ontology has two representations, bijective by construction:

    OWL/XML (the structural spec)  ⇄  Ladybug graph

`Ontology` fronts the document/graph conversions; `Projection` and
`WritableProjection` front the Ladybug database.

OWL/XML is the only document format. Other serializations (Turtle, RDF/XML,
functional syntax, …) are one `robot convert`, Protégé export, or OWLAPI call
away — pre-convert with the tool you already use.
"""

from __future__ import annotations

from pathlib import Path

from ontoplexis.derive import DERIVED_TABLE, derive_edges
from ontoplexis.graph import (
    NODE_TABLE,
    RELATIONSHIP_TABLE,
    Projection,
    ProjectionStorageError,
    WritableProjection,
    build_projection,
    save_projection,
)
from ontoplexis.owlxml import (
    Edge,
    Graph,
    Node,
    OwlXmlStructureError,
    parse_owlxml,
    serialize_owlxml,
)


class Ontology:
    """One ontology held as its OWL/XML structural graph."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    @classmethod
    def from_owlxml(cls, text: str) -> Ontology:
        """Parse an OWL/XML document."""
        return cls(parse_owlxml(text))

    @property
    def graph(self) -> Graph:
        return self._graph

    def to_owlxml(self) -> str:
        return serialize_owlxml(self._graph)

    def project(self) -> Projection:
        """Build an in-memory queryable Ladybug projection."""
        return build_projection(self._graph)

    def save_projection(self, path: str | Path) -> Projection:
        """Materialize the projection to a `.lbug` file; return a handle."""
        return save_projection(self._graph, path)

    @classmethod
    def from_projection(cls, projection: Projection) -> Ontology:
        """Rebuild an Ontology from a (possibly Cypher-authored) projection."""
        return cls(projection.graph())


__all__ = [
    "DERIVED_TABLE",
    "Edge",
    "Graph",
    "NODE_TABLE",
    "Node",
    "Ontology",
    "OwlXmlStructureError",
    "Projection",
    "ProjectionStorageError",
    "RELATIONSHIP_TABLE",
    "WritableProjection",
    "derive_edges",
]
