"""Render-oriented construct graph views for the render layer (`ontopoiesis.render`).

Owns the visibility selection policy: given a projection's full graph and an
optional set of focus IRIs, choose which constructs to draw.

- No IRIs: the entire graph is drawn.
- With IRIs: the *seed* nodes carrying those IRIs are selected; every
  construct on a reference path down to a seed (axioms, expressions) is
  included as *context*; remaining descendants of those constructs — the
  entities and expressions a shared axiom also references — are *external*
  and only drawn when `include_external` is set.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field

from ontoplexis import Edge, Graph, Node


@dataclass(frozen=True, slots=True)
class RenderConstructNode:
    uid: str
    label: str
    construct_kind: str | None = None
    selected: bool = False
    contextual: bool = False
    external: bool = False


@dataclass(frozen=True, slots=True)
class RenderConstructEdge:
    source_uid: str
    target_uid: str
    edge_key: str
    label: str
    position: int | None = None


@dataclass(frozen=True, slots=True)
class RenderConstructGraph:
    requested_iris: tuple[str, ...]
    selected_uids: tuple[str, ...]
    missing_iris: tuple[str, ...]
    external_uids: tuple[str, ...]
    nodes: tuple[RenderConstructNode, ...] = field(default_factory=tuple)
    edges: tuple[RenderConstructEdge, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "requested_iris", tuple(self.requested_iris))
        object.__setattr__(self, "selected_uids", tuple(self.selected_uids))
        object.__setattr__(self, "missing_iris", tuple(self.missing_iris))
        object.__setattr__(self, "external_uids", tuple(self.external_uids))
        object.__setattr__(self, "nodes", tuple(self.nodes))
        object.__setattr__(self, "edges", tuple(self.edges))

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)


def node_visual_style(node: RenderConstructNode) -> tuple[str, str, str]:
    if node.external:
        return ("#f1f5f9", "#94a3b8", "rounded,dashed,filled")
    if node.contextual:
        return ("#fef3c7", "#b45309", "rounded,filled")
    return ("#dbeafe", "#1d4ed8", "rounded,filled")


def build_render_construct_graph(
    graph: Graph,
    iris: list[str] | None = None,
    *,
    include_external: bool = False,
) -> RenderConstructGraph:
    """Apply the visibility selection policy and build a render graph."""
    nodes_by_uid = {node.uid: node for node in graph.nodes}
    if not iris:
        return _render_graph(
            nodes_by_uid,
            graph.edges,
            requested_iris=(),
            seed_uids=set(),
            contextual_uids=set(),
            external_uids=set(),
            missing_iris=(),
            visible_uids=set(nodes_by_uid),
        )

    requested = tuple(dict.fromkeys(iris))
    seed_uids = {node.uid for node in graph.nodes if node.properties.get("iri") in set(requested)}
    found_iris = {
        iri
        for node in graph.nodes
        if isinstance(iri := node.properties.get("iri"), str) and node.uid in seed_uids
    }
    missing_iris = tuple(iri for iri in requested if iri not in found_iris)

    reverse: dict[str, list[str]] = defaultdict(list)
    forward: dict[str, list[str]] = defaultdict(list)
    for edge in graph.edges:
        reverse[edge.target].append(edge.source)
        forward[edge.source].append(edge.target)

    contextual_uids = _reachable(seed_uids, reverse, skip_kinds={"Ontology"}, nodes=nodes_by_uid)
    contextual_uids -= seed_uids
    completion = _reachable(contextual_uids, forward, skip_kinds=set(), nodes=nodes_by_uid)
    external_uids = completion - contextual_uids - seed_uids

    visible_uids = seed_uids | contextual_uids
    if include_external:
        visible_uids |= external_uids

    return _render_graph(
        nodes_by_uid,
        graph.edges,
        requested_iris=requested,
        seed_uids=seed_uids,
        contextual_uids=contextual_uids,
        external_uids=external_uids if include_external else set(),
        missing_iris=missing_iris,
        visible_uids=visible_uids,
    )


def _reachable(
    origins: set[str],
    adjacency: dict[str, list[str]],
    *,
    skip_kinds: set[str],
    nodes: dict[str, Node],
) -> set[str]:
    seen = set(origins)
    queue = deque(origins)
    while queue:
        uid = queue.popleft()
        for neighbour in adjacency.get(uid, ()):
            if neighbour in seen:
                continue
            node = nodes.get(neighbour)
            if node is not None and node.kind in skip_kinds:
                continue
            seen.add(neighbour)
            queue.append(neighbour)
    return seen


def _render_graph(
    nodes_by_uid: dict[str, Node],
    edges: tuple[Edge, ...],
    *,
    requested_iris: tuple[str, ...],
    seed_uids: set[str],
    contextual_uids: set[str],
    external_uids: set[str],
    missing_iris: tuple[str, ...],
    visible_uids: set[str],
) -> RenderConstructGraph:
    render_nodes = [
        RenderConstructNode(
            uid=node.uid,
            construct_kind=node.kind,
            label=_node_label(node),
            selected=node.uid in seed_uids,
            contextual=node.uid in contextual_uids,
            external=node.uid in external_uids,
        )
        for node in nodes_by_uid.values()
        if node.uid in visible_uids
    ]
    visible_edges = tuple(
        edge for edge in edges if edge.source in visible_uids and edge.target in visible_uids
    )
    return RenderConstructGraph(
        requested_iris=requested_iris,
        selected_uids=tuple(sorted(seed_uids)),
        missing_iris=missing_iris,
        external_uids=tuple(sorted(external_uids)),
        nodes=tuple(render_nodes),
        edges=tuple(_label_edges(visible_edges)),
    )


def _node_label(node: Node) -> str:
    parts = [node.uid, node.kind]
    iri = node.properties.get("iri")
    text = node.properties.get("text")
    if isinstance(iri, str):
        parts.append(iri)
    elif isinstance(text, str):
        parts.append(text)
    return "\n".join(parts)


def _label_edges(edges: tuple[Edge, ...]) -> list[RenderConstructEdge]:
    role_of = {id(edge): edge.role or "" for edge in edges}
    collision_counts = Counter((edge.source, role_of[id(edge)]) for edge in edges)
    labelled: list[RenderConstructEdge] = []
    for edge in edges:
        label = role_of[id(edge)]
        if collision_counts[(edge.source, label)] > 1:
            label = f"{label} [{edge.position}]".strip()
        labelled.append(
            RenderConstructEdge(
                source_uid=edge.source,
                target_uid=edge.target,
                edge_key=role_of[id(edge)],
                position=edge.position,
                label=label,
            )
        )
    return labelled
