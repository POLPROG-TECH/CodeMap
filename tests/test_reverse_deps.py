"""Tests for reverse dependency analysis."""

from __future__ import annotations

from codemap.domain.model import CodeGraph, Edge, Node, NodeType


class TestReverseDependencies:
    """Tests for reverse dependency (fan-in) queries on the graph."""

    """GIVEN a graph where a.py imports utils.py"""
    def test_single_reverse_dependency(self) -> None:
        """WHEN we query reverse dependencies of utils.py"""
        graph = CodeGraph()
        graph.add_node(Node(id="a.py", label="a", node_type=NodeType.FILE, file_path="a.py"))
        graph.add_node(
            Node(id="utils.py", label="utils", node_type=NodeType.FILE, file_path="utils.py")
        )
        graph.add_edge(Edge(source="a.py", target="utils.py"))
        rev = graph.get_reverse_dependencies("utils.py")

        """THEN a.py is returned as a dependent"""
        assert len(rev) == 1
        assert rev[0].source == "a.py"

    """GIVEN a graph where three files all import shared.py"""
    def test_multiple_reverse_dependencies(self) -> None:
        """WHEN we query reverse dependencies of shared.py"""
        graph = CodeGraph()
        for name in ["a.py", "b.py", "c.py", "shared.py"]:
            graph.add_node(Node(id=name, label=name, node_type=NodeType.FILE, file_path=name))
        for src in ["a.py", "b.py", "c.py"]:
            graph.add_edge(Edge(source=src, target="shared.py"))
        rev = graph.get_reverse_dependencies("shared.py")

        """THEN all three dependents are returned"""
        sources = {e.source for e in rev}
        assert sources == {"a.py", "b.py", "c.py"}

    """GIVEN a graph where leaf.py has no incoming edges"""
    def test_no_reverse_dependencies(self) -> None:
        """WHEN we query reverse dependencies of leaf.py"""
        graph = CodeGraph()
        graph.add_node(
            Node(id="leaf.py", label="leaf", node_type=NodeType.FILE, file_path="leaf.py")
        )
        graph.add_node(
            Node(id="other.py", label="other", node_type=NodeType.FILE, file_path="other.py")
        )
        graph.add_edge(Edge(source="leaf.py", target="other.py"))
        rev = graph.get_reverse_dependencies("leaf.py")

        """THEN no dependents are found"""
        assert rev == []

    """GIVEN a graph where c.py is depended on by a.py and b.py"""
    def test_impact_analysis_through_reverse_deps(self, sample_graph: CodeGraph) -> None:
        """WHEN we compute the set of files impacted by changing c.py"""
        impacted = {e.source for e in sample_graph.get_reverse_dependencies("c.py")}

        """THEN both a.py and b.py are reported as affected"""
        assert impacted == {"a.py", "b.py"}
