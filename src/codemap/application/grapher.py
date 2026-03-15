"""Graph rendering orchestration."""

from __future__ import annotations

from pathlib import Path

from codemap.application.config import CodeMapConfig
from codemap.domain.model import CodeGraph
from codemap.rendering.html_renderer import HtmlGraphRenderer
from codemap.rendering.json_renderer import JsonRenderer
from codemap.rendering.pdf_renderer import PdfReportRenderer

_RENDERERS: dict[str, type[HtmlGraphRenderer] | type[JsonRenderer] | type[PdfReportRenderer]] = {
    "html": HtmlGraphRenderer,
    "json": JsonRenderer,
    "pdf": PdfReportRenderer,
}

SUPPORTED_FORMATS: list[str] = sorted(_RENDERERS.keys())


def render_graph(graph: CodeGraph, config: CodeMapConfig, fmt: str = "html") -> Path:
    """Render *graph* to the chosen format and return the output path."""
    config.output_dir.mkdir(parents=True, exist_ok=True)

    renderer_cls = _RENDERERS.get(fmt)
    if renderer_cls is None:
        raise ValueError(f"Unknown format '{fmt}'. Supported: {', '.join(SUPPORTED_FORMATS)}")

    renderer = renderer_cls()
    return renderer.render(graph, config.output_dir)
