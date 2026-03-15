"""Tests for reverse dependency analysis."""

from __future__ import annotations

from codemap.domain.model import CodeGraph, Edge, Node, NodeType


class TestReverseDependencies:
    """Reverse dependency (fan-in) queries on the graph."""

    def test_single_reverse_dependency(self) -> None:
        # GIVEN a graph where a.py imports utils.py
        graph = CodeGraph()
        graph.add_node(Node(id="a.py", label="a", node_type=NodeType.FILE, file_path="a.py"))
        graph.add_node(
            Node(id="utils.py", label="utils", node_type=NodeType.FILE, file_path="utils.py")
        )
        graph.add_edge(Edge(source="a.py", target="utils.py"))

        # WHEN we query reverse dependencies of utils.py
        rev = graph.get_reverse_dependencies("utils.py")

        # THEN a.py is returned as a dependent
        assert len(rev) == 1
        assert rev[0].source == "a.py"

    def test_multiple_reverse_dependencies(self) -> None:
        # GIVEN a graph where three files all import shared.py
        graph = CodeGraph()
        for name in ["a.py", "b.py", "c.py", "shared.py"]:
            graph.add_node(Node(id=name, label=name, node_type=NodeType.FILE, file_path=name))
        for src in ["a.py", "b.py", "c.py"]:
            graph.add_edge(Edge(source=src, target="shared.py"))

        # WHEN we query reverse dependencies of shared.py
        rev = graph.get_reverse_dependencies("shared.py")

        # THEN all three dependents are returned
        sources = {e.source for e in rev}
        assert sources == {"a.py", "b.py", "c.py"}

    def test_no_reverse_dependencies(self) -> None:
        # GIVEN a graph where leaf.py has no incoming edges
        graph = CodeGraph()
        graph.add_node(
            Node(id="leaf.py", label="leaf", node_type=NodeType.FILE, file_path="leaf.py")
        )
        graph.add_node(
            Node(id="other.py", label="other", node_type=NodeType.FILE, file_path="other.py")
        )
        graph.add_edge(Edge(source="leaf.py", target="other.py"))

        # WHEN we query reverse dependencies of leaf.py
        rev = graph.get_reverse_dependencies("leaf.py")

        # THEN no dependents are found
        assert rev == []

    def test_impact_analysis_through_reverse_deps(self, sample_graph: CodeGraph) -> None:
        # GIVEN a graph where c.py is depended on by both a.py and b.py

        # WHEN we compute the set of files impacted by changing c.py
        impacted = {e.source for e in sample_graph.get_reverse_dependencies("c.py")}

        # THEN both a.py and b.py would be affected
        assert impacted == {"a.py", "b.py"}
