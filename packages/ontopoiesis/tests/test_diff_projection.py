from pathlib import Path

from ontoplexis import Edge, Graph, Node
from ontoplexis.graph import save_projection

from ontopoiesis.diff_projection import diff_projections
from tests.conftest import WriteLbug

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


def _save_owlxml(write_lbug: WriteLbug, extra: str, path: Path) -> None:
    write_lbug(path, _BASE.format(extra=extra))


def test_diff_projections_reports_no_rows_for_identical_documents(
    tmp_path: Path, write_lbug: WriteLbug
) -> None:
    before = tmp_path / "before.lbug"
    after = tmp_path / "after.lbug"
    _save_owlxml(write_lbug, _SUBCLASS, before)
    _save_owlxml(write_lbug, _SUBCLASS, after)

    assert diff_projections(before, after) == []


def test_diff_projections_reports_added_axiom_with_context(
    tmp_path: Path, write_lbug: WriteLbug
) -> None:
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    _save_owlxml(write_lbug, "", before_path)
    _save_owlxml(write_lbug, _SUBCLASS, after_path)

    rows = diff_projections(before_path, after_path)

    assert len(rows) == 1
    axiom_row = rows[0]
    assert axiom_row.status == "added"
    assert axiom_row.kind == "SubClassOf"
    assert axiom_row.count == 1
    assert axiom_row.ontology_iri == "https://example.org/pizza"
    assert axiom_row.iri == "https://example.org/pizza#Pizza"


def test_diff_projections_reports_removed_axiom(tmp_path: Path, write_lbug: WriteLbug) -> None:
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    _save_owlxml(write_lbug, _SUBCLASS, before_path)
    _save_owlxml(write_lbug, "", after_path)

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


def test_diff_projections_reports_in_place_edit_as_removal_plus_addition(
    tmp_path: Path, write_lbug: WriteLbug
) -> None:
    # Node uids are not stable across builds, so an edited construct is one
    # removed fingerprint plus one added fingerprint — the module's headline
    # contract.
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    _save_owlxml(write_lbug, _SUBCLASS, before_path)
    _save_owlxml(
        write_lbug,
        _SUBCLASS.replace("pizza#Food", "pizza#Meal"),
        after_path,
    )

    rows = diff_projections(before_path, after_path)

    assert sorted((row.status, row.kind) for row in rows) == [
        ("added", "SubClassOf"),
        ("removed", "SubClassOf"),
    ]
    added, removed = (
        next(row for row in rows if row.status == "added"),
        next(row for row in rows if row.status == "removed"),
    )
    assert added.fingerprint != removed.fingerprint


def test_diff_projections_counts_duplicate_axioms(tmp_path: Path, write_lbug: WriteLbug) -> None:
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    _save_owlxml(write_lbug, "", before_path)
    _save_owlxml(write_lbug, _SUBCLASS + "\n" + _SUBCLASS, after_path)

    rows = diff_projections(before_path, after_path)

    assert [(row.status, row.kind, row.count) for row in rows] == [("added", "SubClassOf", 2)]


def test_diff_projections_detects_annotation_only_changes(
    tmp_path: Path, write_lbug: WriteLbug
) -> None:
    annotation = """  <AnnotationAssertion>
    <AnnotationProperty IRI="http://www.w3.org/2000/01/rdf-schema#label"/>
    <IRI>https://example.org/pizza#Pizza</IRI>
    <Literal xml:lang="en">{label}</Literal>
  </AnnotationAssertion>"""
    before_path = tmp_path / "before.lbug"
    after_path = tmp_path / "after.lbug"
    _save_owlxml(write_lbug, annotation.format(label="Pizza"), before_path)
    _save_owlxml(write_lbug, annotation.format(label="Flatbread"), after_path)

    rows = diff_projections(before_path, after_path)

    assert sorted((row.status, row.kind) for row in rows) == [
        ("added", "AnnotationAssertion"),
        ("removed", "AnnotationAssertion"),
    ]
