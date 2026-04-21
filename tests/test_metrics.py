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
    """Tests for fan-in and fan-out computation."""

    """GIVEN a graph with edges a.py -> b.py, a.py -> c.py, b.py -> c.py"""
    def test_fan_in_and_fan_out(self, sample_graph: CodeGraph) -> None:
        """WHEN we compute fan metrics"""
        compute_fan_metrics(sample_graph)

        """THEN fan-out of a.py is 2 and fan-in of c.py is 2"""
        assert sample_graph.nodes["a.py"].metrics.fan_out == 2
        assert sample_graph.nodes["a.py"].metrics.fan_in == 0
        assert sample_graph.nodes["c.py"].metrics.fan_in == 2
        assert sample_graph.nodes["c.py"].metrics.fan_out == 0
        assert sample_graph.nodes["b.py"].metrics.fan_in == 1
        assert sample_graph.nodes["b.py"].metrics.fan_out == 1

    """GIVEN an empty graph"""
    def test_empty_graph(self) -> None:
        """WHEN we compute fan metrics"""
        graph = CodeGraph()
        compute_fan_metrics(graph)

        """THEN nothing crashes and the graph remains empty"""
        assert graph.node_count == 0


class TestCentrality:
    """Tests for centrality score computation."""

    """GIVEN a graph with three equally connected nodes a, b, c"""
    def test_most_connected_node_has_highest_centrality(self, sample_graph: CodeGraph) -> None:
        """WHEN we compute all metrics"""
        compute_all_metrics(sample_graph)

        """THEN all three nodes share the same centrality of 0.5"""
        centralities = {nid: n.metrics.centrality for nid, n in sample_graph.nodes.items()}
        assert centralities["a.py"] == centralities["b.py"] == centralities["c.py"]
        assert centralities["a.py"] == 0.5

    """GIVEN a graph with a single isolated node"""
    def test_single_node_graph(self) -> None:
        """WHEN we compute centrality"""
        graph = CodeGraph()
        graph.add_node(
            Node(id="solo.py", label="solo", node_type=NodeType.FILE, file_path="solo.py")
        )
        compute_centrality(graph)

        """THEN centrality is 0 because no connections are possible"""
        assert graph.nodes["solo.py"].metrics.centrality == 0.0


class TestHotspotDetection:
    """Tests for hotspot detection via churn and fan-in thresholds."""

    """GIVEN a node with high churn (15) and high fan-in (5)"""
    def test_node_is_hotspot(self) -> None:
        """WHEN we check if it is a hotspot with default thresholds"""
        metrics = NodeMetrics(fan_in=5, fan_out=2, churn=15)
        result = metrics.is_hotspot(churn_threshold=10, fanin_threshold=3)

        """THEN it is identified as a hotspot"""
        assert result is True

    """GIVEN a node with low churn (2) but high fan-in (5)"""
    def test_node_is_not_hotspot_low_churn(self) -> None:
        """WHEN we check if it is a hotspot"""
        metrics = NodeMetrics(fan_in=5, fan_out=2, churn=2)
        result = metrics.is_hotspot(churn_threshold=10, fanin_threshold=3)

        """THEN it is not a hotspot"""
        assert result is False

    """GIVEN a node with high churn (20) but low fan-in (1)"""
    def test_node_is_not_hotspot_low_fanin(self) -> None:
        """WHEN we check if it is a hotspot"""
        metrics = NodeMetrics(fan_in=1, fan_out=0, churn=20)
        result = metrics.is_hotspot(churn_threshold=10, fanin_threshold=3)

        """THEN it is not a hotspot"""
        assert result is False
