"""Derived binary-relation edges over the structural projection.

The projection stores every OWL 2 construct as a node and every structural
field as an edge, which is faithful but makes the *binary* relations — the ones
RDF encodes as a single triple — a two-hop traversal through an axiom node. This
module materializes those relations as first-class edges in a separate table so
that subsumption, typing, domain/range, and IRI-valued annotations are one hop.

Scope and guarantees:

- **Round-trip safe by construction.** Derived edges live in their own table
  (`D`); `Projection.graph()` reconstructs only from `N` and `E`, so the derived
  layer is invisible to serialization. The generic walker is never touched.
- **Opinion-free.** Every rule is a mechanical collapse of a single-triple OWL
  construct — a denormalized view of asserted axioms, not inference. Told
  structure only; no reasoner semantics.
- **Refreshable, not authoritative.** `derive_edges` clears and rebuilds `D`
  from current `N`/`E`, so it is correct after axioms are added *or* removed.
  Treat `D` as a cache: never hand-edit it, and re-run after a migration.

The rules themselves live in ``derive.cypher`` beside this module — one
statement per construct, executed in order by `derive_edges` — so the
per-construct knowledge lives in one place, mirroring how role knowledge lives
only in `owlxml._ROLES`.

Three decisions here are deliberate — do not relitigate them without new
evidence:

- **Symmetric relations are materialized in both directions** (`equivalent_*`,
  `disjoint_*`, `inverse_of`, `same_as`, `different_from`). Directed ``->``
  patterns then match without undirected syntax, at the cost of edge counts
  reflecting both directions.
- **No transitive closure is materialized** (no ``subclass_of_closure``). The
  closure can be quadratic in hierarchy size, and bounded recursive patterns
  (``-[:D*1..20 {relation:'subclass_of'}]->``) already give consumers
  depth-capped reachability at query time. The depth caps in ontopoiesis lint
  rules exist for the same reason.
- **Annotation edges fan out across puns.** An ``AnnotationAssertion``
  subject (and an IRI value) names an IRI, not an entity; the annotation
  rules attach an edge to *every* entity node carrying that IRI, so a punned
  Class and NamedIndividual each receive the annotation. One assertion can
  therefore yield several edges (a cross product when both ends are punned).
"""

from __future__ import annotations

from pathlib import Path

from ontoplexis.graph import DERIVED_TABLE, WritableProjection

_RULES_PATH = Path(__file__).with_name("derive.cypher")


def _statements() -> list[str]:
    """The derivation statements from ``derive.cypher``, in file order."""
    chunks = _RULES_PATH.read_text(encoding="utf-8").split(";")
    return [chunk for chunk in (c.strip() for c in chunks) if chunk]


def derive_edges(projection: WritableProjection) -> dict[str, int]:
    """(Re)build the derived-edge table ``D`` from the projection's ``N``/``E``.

    Clears any existing derived edges and repopulates from current structure,
    so the result is correct whether axioms were added or removed since the
    last run. The table itself is created with the projection schema. Returns
    a count of edges created per relation.
    """
    projection.execute(f"MATCH ()-[d:{DERIVED_TABLE}]->() DELETE d")
    for statement in _statements():
        projection.execute(statement)
    counts: dict[str, int] = {}
    rows = projection.execute(
        f"MATCH ()-[d:{DERIVED_TABLE}]->() RETURN d.relation AS relation, count(*) AS c"
    )
    for row in rows:
        relation = row.get("relation")
        count = row.get("c")
        if isinstance(relation, str) and isinstance(count, int):
            counts[relation] = count
    return counts


__all__ = ["DERIVED_TABLE", "derive_edges"]
