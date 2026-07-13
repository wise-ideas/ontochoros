"""End-to-end render pipeline: projection → slice → graph → formatted output."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ontoplexis import Projection

from ontopoiesis.render.construct_graph import build_render_construct_graph
from ontopoiesis.render.graph_output import (
    construct_graph_to_dot,
    render_construct_graph_png,
    render_construct_graph_svg,
)

_log = logging.getLogger(__name__)


class RenderFormat(str, Enum):
    SVG = "svg"
    PNG = "png"
    DOT = "dot"


@dataclass(frozen=True)
class RenderResult:
    format: RenderFormat
    content: str | bytes
    node_count: int
    edge_count: int
    missing_iris: list[str]

    def write_to(self, path: Path) -> None:
        if isinstance(self.content, bytes):
            path.write_bytes(self.content)
        else:
            path.write_text(self.content, encoding="utf-8")


def render_projection(
    projection_path: Path,
    iris: list[str] | None = None,
    *,
    output_format: RenderFormat,
    include_external: bool = False,
) -> RenderResult:
    """Load a projection slice and render it to the requested output format."""
    _log.info(
        "Rendering projection %s as %s (iris=%s, include_external=%s)",
        projection_path,
        output_format,
        len(iris) if iris else "all",
        include_external,
    )
    with Projection.open(projection_path) as projection:
        graph = projection.graph()

    render_graph = build_render_construct_graph(
        graph,
        iris,
        include_external=include_external,
    )
    if render_graph.missing_iris:
        _log.warning(
            "IRIs not found in projection: %s",
            ", ".join(render_graph.missing_iris),
        )
    _log.info(
        "Rendering graph: %d nodes, %d edges",
        render_graph.node_count,
        render_graph.edge_count,
    )

    if output_format == RenderFormat.PNG:
        content: str | bytes = render_construct_graph_png(render_graph)
    elif output_format == RenderFormat.DOT:
        content = construct_graph_to_dot(render_graph)
    else:
        content = render_construct_graph_svg(render_graph)

    return RenderResult(
        format=output_format,
        content=content,
        node_count=render_graph.node_count,
        edge_count=render_graph.edge_count,
        missing_iris=list(render_graph.missing_iris),
    )
