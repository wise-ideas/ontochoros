"""SVG formatter for construct graph layouts."""

from __future__ import annotations

from html import escape

from ontopoiesis.render.construct_graph import RenderConstructGraph, node_visual_style
from ontopoiesis.render.svg_layout import build_svg_layout


def render_svg(graph: RenderConstructGraph) -> str:
    """Render a construct graph as SVG."""
    layout = build_svg_layout(graph)

    fragments = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{layout.width}" height="{layout.height}" viewBox="0 0 {layout.width} {layout.height}" role="img" aria-label="Construct graph">',
        "  <defs>",
        '    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '      <path d="M 0 0 L 10 5 L 0 10 z" fill="#4b5563" />',
        "    </marker>",
        "  </defs>",
        f'  <rect width="{layout.width}" height="{layout.height}" fill="white" />',
    ]

    for edge in layout.edges:
        fragments.append(
            f'  <path d="{edge.path_d}" fill="none" stroke="#4b5563" stroke-width="1.5" marker-end="url(#arrow)" />'
        )
        if edge.label:
            fragments.append(
                f'  <text x="{edge.label_x}" y="{edge.label_y}" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="10" fill="#334155">{escape(edge.label)}</text>'
            )

    boxes = {node.uid: node for node in layout.nodes}
    for node in graph.nodes:
        box = boxes[node.uid]
        fill, stroke, style = node_visual_style(node)
        dash = ' stroke-dasharray="5 3"' if "dashed" in style else ""
        fragments.append(
            f'  <rect x="{box.x}" y="{box.y}" width="{box.width}" height="{box.height}" rx="10" ry="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash} />'
        )
        for index, line in enumerate(node.label.splitlines()):
            fragments.append(
                f'  <text x="{box.x + 12}" y="{box.y + 18 + index * 14}" font-family="Helvetica, Arial, sans-serif" font-size="11" fill="#0f172a">{escape(line)}</text>'
            )

    fragments.append("</svg>")
    return "\n".join(fragments)
