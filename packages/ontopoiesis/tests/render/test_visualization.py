import re
import subprocess

import pytest
from ontoplexis import Edge, Graph, Node, Ontology

from ontopoiesis.render import (
    RenderDependencyError,
    build_render_construct_graph,
    render_construct_graph_png,
    render_construct_graph_svg,
)
from ontopoiesis.render.construct_graph import (
    RenderConstructEdge,
    RenderConstructGraph,
    RenderConstructNode,
)
from ontopoiesis.render.svg_layout import build_svg_layout

_PIZZA_OWX = """<?xml version="1.0"?>
<Ontology xmlns="http://www.w3.org/2002/07/owl#"
          ontologyIRI="https://example.org/pizza#">
  <SubClassOf>
    <Class IRI="https://example.org/pizza#Pizza"/>
    <Class IRI="https://example.org/pizza#Food"/>
  </SubClassOf>
</Ontology>
"""


def _pizza_graph() -> Graph:
    return Ontology.from_owlxml(_PIZZA_OWX).graph


def _empty_graph() -> Graph:
    return Graph(nodes=(), edges=())


def test_build_render_construct_graph_renders_whole_graph_without_iris() -> None:
    graph = build_render_construct_graph(_pizza_graph())

    assert graph.requested_iris == ()
    assert graph.missing_iris == ()
    assert graph.selected_uids == ()
    # Ontology, SubClassOf, and the two merged classes.
    assert graph.node_count == 4
    assert graph.edge_count == 3
    assert sorted(edge.label for edge in graph.edges) == ["axiom", "sub", "super"]


def test_build_render_construct_graph_marks_seeds_and_context() -> None:
    graph = build_render_construct_graph(
        _pizza_graph(), ["https://example.org/pizza#Pizza"], include_external=True
    )

    by_kind = {node.construct_kind: node for node in graph.nodes}
    assert by_kind["SubClassOf"].contextual is True
    assert by_kind["SubClassOf"].selected is False
    seeds = [node for node in graph.nodes if node.selected]
    assert len(seeds) == 1
    assert "Pizza" in seeds[0].label
    externals = [node for node in graph.nodes if node.external]
    assert len(externals) == 1
    assert "Food" in externals[0].label


def test_build_render_construct_graph_returns_empty_graph_for_missing_selection() -> None:
    missing_graph = build_render_construct_graph(_pizza_graph(), ["https://example.org/nope"])

    assert missing_graph.requested_iris == ("https://example.org/nope",)
    assert missing_graph.selected_uids == ()
    assert missing_graph.missing_iris == ("https://example.org/nope",)
    assert missing_graph.node_count == 0


def test_render_construct_graph_svg_offsets_colliding_labels() -> None:
    source = Graph(
        nodes=(
            Node(uid="0x1001", kind="Class", properties={"iri": "https://example.org/A"}),
            Node(uid="0x1002", kind="Class", properties={"iri": "https://example.org/B"}),
            Node(uid="0x2001", kind="Declaration", properties={}),
            Node(uid="0x2002", kind="Declaration", properties={}),
            Node(uid="0x3001", kind="Ontology", properties={}),
        ),
        edges=(
            Edge(source="0x3001", target="0x2001", position=0, role="axiom"),
            Edge(source="0x3001", target="0x2002", position=1, role="axiom"),
            Edge(source="0x2001", target="0x1001", position=0, role="entity"),
            Edge(source="0x2002", target="0x1002", position=0, role="entity"),
        ),
    )
    graph = build_render_construct_graph(source)

    svg = render_construct_graph_svg(graph)
    matches = re.findall(r'<text x="(?P<x>[^"]+)" y="(?P<y>[^"]+)".*?>axiom \[\d\]</text>', svg)

    assert len(matches) == 2
    assert matches[0] != matches[1]


def test_build_svg_layout_assigns_left_to_right_ranks() -> None:
    layout = build_svg_layout(build_render_construct_graph(_pizza_graph()))
    nodes_by_uid = {node.uid: node for node in layout.nodes}
    render_graph = build_render_construct_graph(_pizza_graph())
    uid_by_kind = {node.construct_kind: node.uid for node in render_graph.nodes}

    assert nodes_by_uid[uid_by_kind["Ontology"]].x < nodes_by_uid[uid_by_kind["SubClassOf"]].x


def test_build_svg_layout_keeps_cycles_in_one_rank() -> None:
    graph = RenderConstructGraph(
        requested_iris=(),
        selected_uids=(),
        missing_iris=(),
        external_uids=(),
        nodes=(
            RenderConstructNode(uid="a", label="a"),
            RenderConstructNode(uid="b", label="b"),
        ),
        edges=(
            RenderConstructEdge(source_uid="a", target_uid="b", edge_key="next", label="next"),
            RenderConstructEdge(source_uid="b", target_uid="a", edge_key="prev", label="prev"),
        ),
    )

    layout = build_svg_layout(graph)
    nodes_by_uid = {node.uid: node for node in layout.nodes}

    assert nodes_by_uid["a"].x == nodes_by_uid["b"].x
    assert nodes_by_uid["a"].y != nodes_by_uid["b"].y


def test_render_construct_graph_png_requires_dot(monkeypatch: pytest.MonkeyPatch) -> None:
    graph = build_render_construct_graph(_empty_graph())
    monkeypatch.setattr("ontopoiesis.render.graph_output.which", lambda _name: None)

    with pytest.raises(RenderDependencyError, match="Graphviz `dot` is required"):
        _ = render_construct_graph_png(graph)


def test_render_construct_graph_png_surfaces_dot_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph = build_render_construct_graph(_empty_graph())
    monkeypatch.setattr("ontopoiesis.render.graph_output.which", lambda _name: "/usr/bin/dot")

    def raise_called_process_error(*_args: object, **_kwargs: object) -> object:
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=["/usr/bin/dot", "-Tpng"],
            stderr=b"syntax error near line 1",
        )

    monkeypatch.setattr(
        "ontopoiesis.render.graph_output.subprocess.run", raise_called_process_error
    )

    with pytest.raises(
        RenderDependencyError,
        match=r"Graphviz `dot` failed to render PNG output: syntax error near line 1",
    ):
        _ = render_construct_graph_png(graph)


def test_render_construct_graph_svg_does_not_call_graphviz(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph = build_render_construct_graph(_empty_graph())
    monkeypatch.setattr(
        "ontopoiesis.render.graph_output._render_with_dot",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected Graphviz call")),
    )

    svg = render_construct_graph_svg(graph)

    assert svg.startswith("<svg")
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg
