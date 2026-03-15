"""Tests for ownership analysis (GitAnalyzer) and ownership model."""

from __future__ import annotations

from codemap.domain.model import ContributorInfo, OwnershipInfo


class TestOwnershipInfo:
    """OwnershipInfo correctly identifies primary owners and counts."""

    def test_primary_owner_is_top_contributor(self) -> None:
        # GIVEN an OwnershipInfo with two contributors
        alice = ContributorInfo(name="Alice", email="a@test.com", commit_count=10)
        bob = ContributorInfo(name="Bob", email="b@test.com", commit_count=3)
        info = OwnershipInfo(contributors=[bob, alice], total_commits=13)

        # WHEN we check the primary owner
        owner = info.primary_owner

        # THEN Alice is the primary owner (most commits)
        assert owner is not None
        assert owner.name == "Alice"
        assert owner.commit_count == 10

    def test_primary_owner_none_when_empty(self) -> None:
        # GIVEN an OwnershipInfo with no contributors
        info = OwnershipInfo()

        # WHEN we check the primary owner
        owner = info.primary_owner

        # THEN None is returned
        assert owner is None

    def test_contributor_count(self) -> None:
        # GIVEN an OwnershipInfo with 3 contributors
        contribs = [
            ContributorInfo(name=f"Dev{i}", email=f"dev{i}@test.com", commit_count=i)
            for i in range(1, 4)
        ]
        info = OwnershipInfo(contributors=contribs)

        # WHEN we check contributor count
        # THEN it returns 3
        assert info.contributor_count == 3


class TestOwnershipOnGraph:
    """Ownership metadata attached to graph nodes."""

    def test_graph_node_has_ownership(self, graph_with_ownership) -> None:
        # GIVEN a graph with a node that has ownership metadata

        # WHEN we access the node's ownership
        node = graph_with_ownership.get_node("core.py")
        assert node is not None
        owner = node.ownership.primary_owner

        # THEN the primary owner is Alice
        assert owner is not None
        assert owner.name == "Alice"
        assert node.ownership.total_commits == 13
        assert node.ownership.last_modifier == "Alice"

    def test_graph_node_churn(self, graph_with_ownership) -> None:
        # GIVEN a graph node with churn = 15

        # WHEN we access the metrics
        node = graph_with_ownership.get_node("core.py")
        assert node is not None

        # THEN churn is correctly set
        assert node.metrics.churn == 15

    def test_hotspot_with_ownership(self, graph_with_ownership) -> None:
        # GIVEN a node with fan_in=5, churn=15, and multiple contributors

        # WHEN we check if it's a hotspot
        node = graph_with_ownership.get_node("core.py")
        assert node is not None

        # THEN it IS a hotspot
        assert node.metrics.is_hotspot(churn_threshold=10, fanin_threshold=3)
        assert node.ownership.contributor_count == 2
