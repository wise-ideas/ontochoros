from pathlib import Path

from ontoplexis import Edge, Graph, Node, Ontology
from ontoplexis.graph import save_projection

from ontopoiesis.diff_projection import diff_projections

_BASE = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="https://example.org/pizza">
  <Declaration><Class IRI="https://example.org/pizza#Pizza"/></Declaration>
  <Declaration><Class IRI="https://example.org/pizza#Food"/></Declaration>
{extra}
</Ontology>
"""

_SUBCLASS = """  <SubClassOf>
    <Class IRI="https://example.org/pizza#Pizza"/>
    <Class IRI="https://example.org/pizza#Food"/>
  </SubClassOf>"""


def _save_owlxml(extra: str, path: Path) -> None:
    projection = Ontology.from_owlxml(_BASE.format(extra=extra)).save_projection(path)
    projection.close()


def test_diff_projections_reports_no_rows_for_identical_documents(tmp_path: Path) -> None:
    before = tmp_path / "before.lbug"
    after = tmp_path / "after.lbug"
    _save_owlxml(_SUBCLASS, before)
    _save_owlxml(_SUBCLASS, after)

    assert diff_projections(before, after) == []


def test_diff_projections_reports_added_axiom_with_context(tmp_path: Path) -> None:
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    _save_owlxml("", before_path)
    _save_owlxml(_SUBCLASS, after_path)

    rows = diff_projections(before_path, after_path)

    assert len(rows) == 1
    axiom_row = rows[0]
    assert axiom_row.status == "added"
    assert axiom_row.kind == "SubClassOf"
    assert axiom_row.count == 1
    assert axiom_row.ontology_iri == "https://example.org/pizza"
    assert axiom_row.iri == "https://example.org/pizza#Pizza"


def test_diff_projections_reports_removed_axiom(tmp_path: Path) -> None:
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    _save_owlxml(_SUBCLASS, before_path)
    _save_owlxml("", after_path)

    rows = diff_projections(before_path, after_path)

    assert [row.status for row in rows] == ["removed"]
    assert rows[0].kind == "SubClassOf"


def test_diff_projections_handles_reference_cycles(tmp_path: Path) -> None:
    graph = Graph(
        nodes=(
            Node(uid="0x0", kind="Ontology", properties={"ontology_iri": "https://example.org"}),
            Node(uid="0x1", kind="ObjectComplementOf", properties={}),
            Node(uid="0x2", kind="ObjectComplementOf", properties={}),
        ),
        edges=(
            Edge(source="0x0", target="0x1", position=0, role="axiom"),
            Edge(source="0x1", target="0x2", position=0, role="operand"),
            Edge(source="0x2", target="0x1", position=0, role="operand"),
        ),
    )
    before = tmp_path / "before.lbug"
    after = tmp_path / "after.lbug"
    save_projection(graph, before).close()
    save_projection(graph, after).close()

    assert diff_projections(before, after) == []
