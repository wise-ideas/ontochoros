"""Typed layout for SVG rendering of construct graphs."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field

from ontopoiesis.render.construct_graph import RenderConstructEdge, RenderConstructGraph

NODE_WIDTH = 220
NODE_HEIGHT = 56
HORIZONTAL_GAP = 120
VERTICAL_GAP = 28
PADDING = 24
EDGE_SEPARATION = 18


@dataclass(frozen=True, slots=True)
class SvgLayoutNode:
    uid: str
    x: float
    y: float
    width: float = NODE_WIDTH
    height: float = NODE_HEIGHT


@dataclass(frozen=True, slots=True)
class SvgLayoutEdge:
    source_uid: str
    target_uid: str
    edge_key: str
    position: int | None
    path_d: str
    label: str
    label_x: float
    label_y: float


@dataclass(frozen=True, slots=True)
class SvgLayout:
    width: float
    height: float
    nodes: tuple[SvgLayoutNode, ...] = field(default_factory=tuple)
    edges: tuple[SvgLayoutEdge, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "nodes", tuple(self.nodes))
        object.__setattr__(self, "edges", tuple(self.edges))


def build_svg_layout(graph: RenderConstructGraph) -> SvgLayout:
    """Compute typed layout geometry for SVG rendering."""
    positions = layout_nodes(graph)
    rank_counts = Counter(rank for rank, _ in positions.values())
    max_rank = max((rank for rank, _ in positions.values()), default=0)
    max_rows = max(rank_counts.values(), default=1)
    width = PADDING * 2 + (max_rank + 1) * NODE_WIDTH + max_rank * HORIZONTAL_GAP
    height = PADDING * 2 + max_rows * NODE_HEIGHT + max(max_rows - 1, 0) * VERTICAL_GAP

    nodes = tuple(
        SvgLayoutNode(
            uid=node.uid,
            x=float(PADDING + positions[node.uid][0] * (NODE_WIDTH + HORIZONTAL_GAP)),
            y=float(PADDING + positions[node.uid][1] * (NODE_HEIGHT + VERTICAL_GAP)),
        )
        for node in graph.nodes
        if node.uid in positions
    )
    boxes_by_uid = {node.uid: node for node in nodes}
    edge_offsets = _edge_offsets(graph.edges)

    edges: list[SvgLayoutEdge] = []
    for edge in graph.edges:
        source = boxes_by_uid.get(edge.source_uid)
        target = boxes_by_uid.get(edge.target_uid)
        if source is None or target is None:
            continue
        offset = edge_offsets.get(_edge_identity(edge), 0.0)
        sx, sy = source.x + source.width, source.y + source.height / 2
        tx, ty = target.x, target.y + target.height / 2
        cx1, cx2 = sx + 36, tx - 36
        path_sy, path_ty = sy + offset, ty + offset
        mid_x = cubic_bezier(sx, cx1, cx2, tx, 0.5)
        mid_y = cubic_bezier(path_sy, path_sy, path_ty, path_ty, 0.5)
        edges.append(
            SvgLayoutEdge(
                source_uid=edge.source_uid,
                target_uid=edge.target_uid,
                edge_key=edge.edge_key,
                position=edge.position,
                path_d=f"M {sx} {sy} C {cx1} {path_sy}, {cx2} {path_ty}, {tx} {ty}",
                label=edge.label,
                label_x=mid_x,
                label_y=mid_y - 8 + offset * 0.2,
            )
        )

    return SvgLayout(width=width, height=height, nodes=nodes, edges=tuple(edges))


def layout_nodes(graph: RenderConstructGraph) -> dict[str, tuple[int, int]]:
    """Assign (rank, row) grid positions to each node via topological sort."""
    node_ids = [node.uid for node in graph.nodes]
    if not node_ids:
        return {}

    outgoing: dict[str, set[str]] = defaultdict(set)
    indegree = {uid: 0 for uid in node_ids}
    for edge in graph.edges:
        if edge.source_uid not in indegree or edge.target_uid not in indegree:
            continue
        if edge.target_uid in outgoing[edge.source_uid]:
            continue
        outgoing[edge.source_uid].add(edge.target_uid)
        indegree[edge.target_uid] += 1

    queue = deque(sorted(uid for uid, degree in indegree.items() if degree == 0))
    ranks = {uid: 0 for uid in node_ids}
    visited: list[str] = []
    while queue:
        uid = queue.popleft()
        visited.append(uid)
        for target_uid in sorted(outgoing[uid]):
            ranks[target_uid] = max(ranks[target_uid], ranks[uid] + 1)
            indegree[target_uid] -= 1
            if indegree[target_uid] == 0:
                queue.append(target_uid)

    for uid in sorted(set(node_ids) - set(visited)):
        ranks.setdefault(uid, 0)

    rows_by_rank: dict[int, int] = defaultdict(int)
    positions: dict[str, tuple[int, int]] = {}
    for uid in sorted(node_ids, key=lambda value: (ranks[value], value)):
        rank = ranks[uid]
        positions[uid] = (rank, rows_by_rank[rank])
        rows_by_rank[rank] += 1
    return positions


def _edge_offsets(
    edges: tuple[RenderConstructEdge, ...],
) -> dict[tuple[str, str, str, int | None], float]:
    grouped_edges: dict[str, list[RenderConstructEdge]] = defaultdict(list)
    for edge in edges:
        grouped_edges[edge.source_uid].append(edge)

    offsets: dict[tuple[str, str, str, int | None], float] = {}
    for group in grouped_edges.values():
        ordered_group = sorted(
            group,
            key=lambda edge: (
                edge.target_uid,
                edge.edge_key,
                -1 if edge.position is None else edge.position,
            ),
        )
        midpoint = (len(ordered_group) - 1) / 2
        for index, edge in enumerate(ordered_group):
            offsets[_edge_identity(edge)] = (index - midpoint) * EDGE_SEPARATION
    return offsets


def _edge_identity(edge: RenderConstructEdge) -> tuple[str, str, str, int | None]:
    return (edge.source_uid, edge.target_uid, edge.edge_key, edge.position)


def cubic_bezier(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
    inverse_t = 1 - t
    return inverse_t**3 * p0 + 3 * inverse_t**2 * t * p1 + 3 * inverse_t * t**2 * p2 + t**3 * p3
