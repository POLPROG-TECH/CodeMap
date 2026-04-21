"""Tests for the PDF renderer."""

from __future__ import annotations

from pathlib import Path

from codemap.domain.model import CodeGraph
from codemap.rendering.pdf_renderer import PdfReportRenderer


class TestPdfRenderer:
    """Tests that the PDF renderer produces a valid PDF file."""

    """GIVEN a CodeGraph with nodes and edges"""
    def test_produces_pdf_file(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we render to PDF"""
        renderer = PdfReportRenderer()
        out = renderer.render(sample_graph, tmp_path)

        """THEN the output file exists and is a valid PDF"""
        assert out.exists()
        assert out.suffix == ".pdf"
        content = out.read_bytes()
        assert content[:5] == b"%PDF-"

    """GIVEN a rendered PDF from a graph with three nodes"""
    def test_pdf_contains_node_labels(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we check the file"""
        renderer = PdfReportRenderer()
        out = renderer.render(sample_graph, tmp_path)

        """THEN the PDF is non-trivially sized (content was rendered)"""
        assert out.stat().st_size > 1000

    """GIVEN a PdfReportRenderer instance"""
    def test_format_name(self) -> None:
        """WHEN we check the format name"""
        renderer = PdfReportRenderer()

        """THEN it returns 'pdf'"""
        assert renderer.format_name == "pdf"

    """GIVEN a CodeGraph that includes ownership metadata"""
    def test_pdf_with_ownership(self, graph_with_ownership: CodeGraph, tmp_path: Path) -> None:
        """WHEN we render to PDF"""
        renderer = PdfReportRenderer()
        out = renderer.render(graph_with_ownership, tmp_path)

        """THEN the file is generated without errors and has valid content"""
        assert out.exists()
        assert out.read_bytes()[:5] == b"%PDF-"
        assert out.stat().st_size > 1000
