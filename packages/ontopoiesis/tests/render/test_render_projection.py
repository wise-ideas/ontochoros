"""Integration tests for the production render path: projection -> slice -> render."""

from pathlib import Path

import pytest
from ontoplexis import Ontology

from ontopoiesis.render import RenderFormat, build_render_construct_graph, render_projection

PIZZA_IRI = "https://example.org/pizza#Pizza"
FOOD_IRI = "https://example.org/pizza#Food"

_PIZZA_OWX = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="https://example.org/pizza#">
  <SubClassOf>
    <Class IRI="https://example.org/pizza#Pizza"/>
    <Class IRI="https://example.org/pizza#Food"/>
  </SubClassOf>
</Ontology>
"""


@pytest.fixture
def pizza_ontology() -> Ontology:
    return Ontology.from_owlxml(_PIZZA_OWX)


@pytest.fixture
def pizza_lbug(tmp_path: Path, write_lbug) -> Path:
    return write_lbug(tmp_path / "pizza.lbug", _PIZZA_OWX)


def test_slice_by_iri_includes_ancestor_axioms(pizza_ontology: Ontology) -> None:
    graph = build_render_construct_graph(pizza_ontology.graph, [PIZZA_IRI])

    assert graph.requested_iris == (PIZZA_IRI,)
    assert graph.missing_iris == ()
    assert graph.node_count > 1
    contextual_kinds = {node.construct_kind for node in graph.nodes if node.contextual}
    assert "SubClassOf" in contextual_kinds
    selected = [node for node in graph.nodes if node.selected]
    assert [node.construct_kind for node in selected] == ["Class"]


def test_slice_by_iri_excludes_siblings_unless_external_included(
    pizza_ontology: Ontology,
) -> None:
    default_graph = build_render_construct_graph(pizza_ontology.graph, [PIZZA_IRI])
    external_graph = build_render_construct_graph(
        pizza_ontology.graph, [PIZZA_IRI], include_external=True
    )

    default_labels = {node.label for node in default_graph.nodes}
    assert not any(FOOD_IRI in label for label in default_labels)

    external_nodes = [node for node in external_graph.nodes if node.external]
    assert any(FOOD_IRI in node.label for node in external_nodes)


def test_render_projection_produces_svg_from_lbug(pizza_lbug: Path) -> None:
    result = render_projection(pizza_lbug, [PIZZA_IRI], output_format=RenderFormat.SVG)

    assert result.format is RenderFormat.SVG
    assert isinstance(result.content, str)
    assert result.content.startswith("<svg")
    assert result.node_count > 1
    assert result.missing_iris == []


def test_render_projection_reports_missing_iris(pizza_lbug: Path) -> None:
    result = render_projection(
        pizza_lbug,
        [PIZZA_IRI, "https://example.org/pizza#Nope"],
        output_format=RenderFormat.DOT,
    )

    assert result.missing_iris == ["https://example.org/pizza#Nope"]
