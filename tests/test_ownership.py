"""Tests for ownership analysis (GitAnalyzer) and ownership model."""

from __future__ import annotations

from codemap.domain.model import ContributorInfo, OwnershipInfo


class TestOwnershipInfo:
    """Tests that OwnershipInfo correctly identifies primary owners and counts."""

    """GIVEN an OwnershipInfo with two contributors where Alice has more commits"""
    def test_primary_owner_is_top_contributor(self) -> None:
        """WHEN we check the primary owner"""
        alice = ContributorInfo(name="Alice", email="a@test.com", commit_count=10)
        bob = ContributorInfo(name="Bob", email="b@test.com", commit_count=3)
        info = OwnershipInfo(contributors=[bob, alice], total_commits=13)
        owner = info.primary_owner

        """THEN Alice is reported as the primary owner"""
        assert owner is not None
        assert owner.name == "Alice"
        assert owner.commit_count == 10

    """GIVEN an OwnershipInfo with no contributors"""
    def test_primary_owner_none_when_empty(self) -> None:
        """WHEN we check the primary owner"""
        info = OwnershipInfo()
        owner = info.primary_owner

        """THEN None is returned"""
        assert owner is None

    """GIVEN an OwnershipInfo with three contributors"""
    def test_contributor_count(self) -> None:
        """WHEN we check the contributor count"""
        contribs = [
            ContributorInfo(name=f"Dev{i}", email=f"dev{i}@test.com", commit_count=i)
            for i in range(1, 4)
        ]
        info = OwnershipInfo(contributors=contribs)

        """THEN it returns 3"""
        assert info.contributor_count == 3


class TestOwnershipOnGraph:
    """Tests for ownership metadata attached to graph nodes."""

    """GIVEN a graph with a node that has ownership metadata"""
    def test_graph_node_has_ownership(self, graph_with_ownership) -> None:
        """WHEN we access the node's ownership"""
        node = graph_with_ownership.get_node("core.py")
        assert node is not None
        owner = node.ownership.primary_owner

        """THEN Alice is reported as the primary owner"""
        assert owner is not None
        assert owner.name == "Alice"
        assert node.ownership.total_commits == 13
        assert node.ownership.last_modifier == "Alice"

    """GIVEN a graph node with churn set to 15"""
    def test_graph_node_churn(self, graph_with_ownership) -> None:
        """WHEN we access the metrics"""
        node = graph_with_ownership.get_node("core.py")
        assert node is not None

        """THEN churn is correctly set"""
        assert node.metrics.churn == 15

    """GIVEN a node with fan_in=5, churn=15, and multiple contributors"""
    def test_hotspot_with_ownership(self, graph_with_ownership) -> None:
        """WHEN we check if it is a hotspot"""
        node = graph_with_ownership.get_node("core.py")
        assert node is not None

        """THEN it is identified as a hotspot with two contributors"""
        assert node.metrics.is_hotspot(churn_threshold=10, fanin_threshold=3)
        assert node.ownership.contributor_count == 2
