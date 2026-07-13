"""Render construct graphs to DOT, SVG, or PNG."""

from __future__ import annotations

import logging
import subprocess
from shutil import which
from typing import Literal

from ontopoiesis.errors import RenderDependencyError
from ontopoiesis.render.construct_graph import RenderConstructGraph, node_visual_style
from ontopoiesis.render.svg_renderer import render_svg

_log = logging.getLogger(__name__)


def construct_graph_to_dot(graph: RenderConstructGraph) -> str:
    """Render a construct graph to Graphviz DOT."""
    lines = [
        "digraph RenderConstructGraph {",
        '  graph [rankdir=LR, bgcolor="white", pad="0.3", nodesep="0.45", ranksep="0.8"];',
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, margin="0.16,0.10", color="#264653", fillcolor="#f1f5f9"];',
        '  edge [fontname="Helvetica", fontsize=10, color="#4b5563", arrowsize=0.8, arrowhead="normal"];',
    ]
    for node in graph.nodes:
        fill, color, style = node_visual_style(node)
        label = node.label.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        lines.append(
            f'  "{node.uid}" [label="{label}", style="{style}", fillcolor="{fill}", color="{color}"];'
        )
    for edge in graph.edges:
        label = edge.label.replace("\\", "\\\\").replace('"', '\\"')
        suffix = f' [label="{label}"]' if label else ""
        lines.append(f'  "{edge.source_uid}" -> "{edge.target_uid}"{suffix};')
    lines.append("}")
    return "\n".join(lines)


def render_construct_graph_svg(graph: RenderConstructGraph) -> str:
    """Render a construct graph as SVG."""
    _log.debug(
        "Rendering construct graph as SVG (%d nodes, %d edges)",
        graph.node_count,
        graph.edge_count,
    )
    return render_svg(graph)


def render_construct_graph_png(graph: RenderConstructGraph) -> bytes:
    """Render a construct graph as PNG."""
    _log.debug(
        "Rendering construct graph as PNG (%d nodes, %d edges)",
        graph.node_count,
        graph.edge_count,
    )
    dot_png = _render_with_dot(construct_graph_to_dot(graph), output_format="png")
    if dot_png is None:
        raise RenderDependencyError("Graphviz `dot` is required to render PNG output.")
    return dot_png


def _render_with_dot(dot_source: str, *, output_format: Literal["png"]) -> bytes | None:
    dot_path = which("dot")
    if dot_path is None:
        _log.warning("Graphviz `dot` not found; cannot render %s output", output_format)
        return None
    _log.debug("Running Graphviz `dot` for %s output", output_format)
    try:
        result = subprocess.run(
            [dot_path, f"-T{output_format}"],
            input=dot_source.encode("utf-8"),
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        message = _dot_failure_message(output_format, detail=exc.stderr, fallback=str(exc))
        _log.warning(message)
        raise RenderDependencyError(message) from exc
    except (OSError, subprocess.SubprocessError) as exc:
        message = _dot_failure_message(output_format, fallback=str(exc))
        _log.warning(message)
        raise RenderDependencyError(message) from exc
    return result.stdout or None


def _dot_failure_message(
    output_format: str,
    *,
    detail: bytes | str | None = None,
    fallback: str | None = None,
) -> str:
    detail_text = _decode_dot_error_detail(detail) or fallback
    if detail_text:
        return f"Graphviz `dot` failed to render {output_format.upper()} output: {detail_text}"
    return f"Graphviz `dot` failed to render {output_format.upper()} output."


def _decode_dot_error_detail(detail: bytes | str | None) -> str | None:
    if detail is None:
        return None
    if isinstance(detail, bytes):
        return detail.decode("utf-8", errors="replace").strip() or None
    return detail.strip() or None
