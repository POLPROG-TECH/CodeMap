"""Metric computation over a CodeGraph: fan-in/out, centrality, hotspot scoring."""

from __future__ import annotations

from collections import Counter

from codemap.domain.model import CodeGraph


def compute_fan_metrics(graph: CodeGraph) -> None:
    """Populate fan_in and fan_out on every node in *graph* (mutates in place)."""
    out_counts: Counter[str] = Counter()
    in_counts: Counter[str] = Counter()

    for edge in graph.edges:
        out_counts[edge.source] += 1
        in_counts[edge.target] += 1

    for node in graph.nodes.values():
        node.metrics.fan_out = out_counts.get(node.id, 0)
        node.metrics.fan_in = in_counts.get(node.id, 0)


def compute_centrality(graph: CodeGraph) -> None:
    """
    Simplified betweenness-like centrality: proportion of total connections
    (in + out) relative to the maximum possible connections.
    """
    if graph.node_count <= 1:
        return

    max_connections = (graph.node_count - 1) * 2
    for node in graph.nodes.values():
        total = node.metrics.fan_in + node.metrics.fan_out
        node.metrics.centrality = round(total / max_connections, 4) if max_connections else 0.0


def compute_all_metrics(graph: CodeGraph) -> None:
    """Run the full metrics pipeline over *graph*."""
    compute_fan_metrics(graph)
    compute_centrality(graph)
