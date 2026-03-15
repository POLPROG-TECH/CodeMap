"""Tests for metric computation (fan-in, fan-out, centrality, hotspots)."""

from __future__ import annotations

from codemap.domain.metrics import compute_all_metrics, compute_centrality, compute_fan_metrics
from codemap.domain.model import (
    CodeGraph,
    Node,
    NodeMetrics,
    NodeType,
)


class TestFanMetrics:
    """Fan-in and fan-out are correctly computed."""

    def test_fan_in_and_fan_out(self, sample_graph: CodeGraph) -> None:
        # GIVEN a graph with known edges:
        #   a.py → b.py, a.py → c.py, b.py → c.py

        # WHEN we compute fan metrics
        compute_fan_metrics(sample_graph)

        # THEN fan-out of a.py is 2, fan-in of c.py is 2
        assert sample_graph.nodes["a.py"].metrics.fan_out == 2
        assert sample_graph.nodes["a.py"].metrics.fan_in == 0
        assert sample_graph.nodes["c.py"].metrics.fan_in == 2
        assert sample_graph.nodes["c.py"].metrics.fan_out == 0
        assert sample_graph.nodes["b.py"].metrics.fan_in == 1
        assert sample_graph.nodes["b.py"].metrics.fan_out == 1

    def test_empty_graph(self) -> None:
        # GIVEN an empty graph
        graph = CodeGraph()

        # WHEN we compute fan metrics
        compute_fan_metrics(graph)

        # THEN nothing crashes
        assert graph.node_count == 0


class TestCentrality:
    """Centrality scores are proportional to connection density."""

    def test_most_connected_node_has_highest_centrality(self, sample_graph: CodeGraph) -> None:
        # GIVEN a graph: a→b, a→c, b→c
        #   a.py: fan_out=2, fan_in=0 → total=2
        #   b.py: fan_out=1, fan_in=1 → total=2
        #   c.py: fan_out=0, fan_in=2 → total=2

        # WHEN we compute all metrics
        compute_all_metrics(sample_graph)

        # THEN all three nodes have the same centrality (each has 2 connections)
        centralities = {nid: n.metrics.centrality for nid, n in sample_graph.nodes.items()}
        assert centralities["a.py"] == centralities["b.py"] == centralities["c.py"]
        assert centralities["a.py"] == 0.5

    def test_single_node_graph(self) -> None:
        # GIVEN a graph with one node and no edges
        graph = CodeGraph()
        graph.add_node(
            Node(id="solo.py", label="solo", node_type=NodeType.FILE, file_path="solo.py")
        )

        # WHEN we compute centrality
        compute_centrality(graph)

        # THEN centrality is 0 (no possible connections)
        assert graph.nodes["solo.py"].metrics.centrality == 0.0


class TestHotspotDetection:
    """Hotspot detection based on churn and fan-in thresholds."""

    def test_node_is_hotspot(self) -> None:
        # GIVEN a node with high churn (15) and high fan-in (5)
        metrics = NodeMetrics(fan_in=5, fan_out=2, churn=15)

        # WHEN we check if it's a hotspot with default thresholds
        result = metrics.is_hotspot(churn_threshold=10, fanin_threshold=3)

        # THEN it is identified as a hotspot
        assert result is True

    def test_node_is_not_hotspot_low_churn(self) -> None:
        # GIVEN a node with low churn (2) but high fan-in (5)
        metrics = NodeMetrics(fan_in=5, fan_out=2, churn=2)

        # WHEN we check if it's a hotspot
        result = metrics.is_hotspot(churn_threshold=10, fanin_threshold=3)

        # THEN it is NOT a hotspot
        assert result is False

    def test_node_is_not_hotspot_low_fanin(self) -> None:
        # GIVEN a node with high churn (20) but low fan-in (1)
        metrics = NodeMetrics(fan_in=1, fan_out=0, churn=20)

        # WHEN we check if it's a hotspot
        result = metrics.is_hotspot(churn_threshold=10, fanin_threshold=3)

        # THEN it is NOT a hotspot
        assert result is False
