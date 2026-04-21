"""Tests for the JSON renderer."""

from __future__ import annotations

import json
from pathlib import Path

from codemap.domain.model import CodeGraph
from codemap.rendering.json_renderer import JsonRenderer


class TestJsonRenderer:
    """Tests that the JSON renderer produces valid, structured output."""

    """GIVEN a CodeGraph with nodes and edges"""
    def test_produces_valid_json(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we render to JSON"""
        renderer = JsonRenderer()
        out = renderer.render(sample_graph, tmp_path)

        """THEN the output file is valid JSON with expected keys"""
        data = json.loads(out.read_text())
        assert data["node_count"] == 3
        assert data["edge_count"] == 3
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 3

    """GIVEN a rendered JSON file"""
    def test_nodes_have_required_fields(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect a node"""
        renderer = JsonRenderer()
        out = renderer.render(sample_graph, tmp_path)
        data = json.loads(out.read_text())
        node = data["nodes"][0]

        """THEN it contains all expected fields"""
        assert "id" in node
        assert "label" in node
        assert "group" in node
        assert "language" in node
        assert "metrics" in node
        assert "ownership" in node

    """GIVEN a JsonRenderer instance"""
    def test_format_name(self) -> None:
        """WHEN we check the format name"""
        renderer = JsonRenderer()

        """THEN it returns 'json'"""
        assert renderer.format_name == "json"
