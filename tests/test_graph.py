"""Tests for the CodeGraph domain model."""

from __future__ import annotations

from codemap.domain.model import (
    CodeGraph,
    Edge,
    Node,
    NodeGroup,
    NodeType,
)


class TestCodeGraphConstruction:
    """Adding nodes, edges, and groups to a CodeGraph."""

    def test_add_nodes(self) -> None:
        # GIVEN an empty graph
        graph = CodeGraph()

        # WHEN we add two nodes
        graph.add_node(Node(id="a.py", label="a.py", node_type=NodeType.FILE, file_path="a.py"))
        graph.add_node(Node(id="b.py", label="b.py", node_type=NodeType.FILE, file_path="b.py"))

        # THEN both nodes are present
        assert graph.node_count == 2
        assert graph.get_node("a.py") is not None
        assert graph.get_node("b.py") is not None

    def test_add_edge_between_existing_nodes(self) -> None:
        # GIVEN a graph with two nodes
        graph = CodeGraph()
        graph.add_node(Node(id="a.py", label="a", node_type=NodeType.FILE, file_path="a.py"))
        graph.add_node(Node(id="b.py", label="b", node_type=NodeType.FILE, file_path="b.py"))

        # WHEN we add an edge between them
        graph.add_edge(Edge(source="a.py", target="b.py"))

        # THEN the edge is recorded
        assert graph.edge_count == 1

    def test_edge_to_unknown_node_is_dropped(self) -> None:
        # GIVEN a graph with one node
        graph = CodeGraph()
        graph.add_node(Node(id="a.py", label="a", node_type=NodeType.FILE, file_path="a.py"))

        # WHEN we add an edge to a non-existent node
        graph.add_edge(Edge(source="a.py", target="missing.py"))

        # THEN the edge is silently dropped
        assert graph.edge_count == 0

    def test_add_group(self) -> None:
        # GIVEN an empty graph
        graph = CodeGraph()

        # WHEN we add a group
        graph.add_group(NodeGroup(id="pkg", label="pkg"))

        # THEN the group is present
        assert "pkg" in graph.groups


class TestCodeGraphQueries:
    """Forward and reverse dependency queries."""

    def test_get_dependencies(self, sample_graph: CodeGraph) -> None:
        # GIVEN a graph where a.py depends on b.py and c.py
        # (from sample_graph fixture)

        # WHEN we query a.py's dependencies
        deps = sample_graph.get_dependencies("a.py")

        # THEN both b.py and c.py are returned
        targets = {e.target for e in deps}
        assert targets == {"b.py", "c.py"}

    def test_get_reverse_dependencies(self, sample_graph: CodeGraph) -> None:
        # GIVEN a graph where both a.py and b.py depend on c.py

        # WHEN we query c.py's reverse dependencies
        rev = sample_graph.get_reverse_dependencies("c.py")

        # THEN both a.py and b.py are returned
        sources = {e.source for e in rev}
        assert sources == {"a.py", "b.py"}

    def test_get_nodes_in_group(self, sample_graph: CodeGraph) -> None:
        # GIVEN a graph where b.py and c.py are in group "pkg"

        # WHEN we query nodes in the "pkg" group
        nodes = sample_graph.get_nodes_in_group("pkg")

        # THEN b.py and c.py are returned
        ids = {n.id for n in nodes}
        assert ids == {"b.py", "c.py"}

    def test_get_node_returns_none_for_missing(self) -> None:
        # GIVEN an empty graph
        graph = CodeGraph()

        # WHEN we query a non-existent node
        result = graph.get_node("nope.py")

        # THEN None is returned
        assert result is None
