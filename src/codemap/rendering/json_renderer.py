"""Machine-readable JSON renderer."""

from __future__ import annotations

import json
from pathlib import Path

from codemap.domain.model import CodeGraph


class JsonRenderer:
    """Serialises a CodeGraph to a self-contained JSON file."""

    @property
    def format_name(self) -> str:
        return "json"

    def render(self, graph: CodeGraph, output_path: Path) -> Path:
        output_path.mkdir(parents=True, exist_ok=True)
        dest = output_path / "codemap.json"
        dest.write_text(json.dumps(self._serialise(graph), indent=2))
        return dest

    @staticmethod
    def _serialise(graph: CodeGraph) -> dict[str, object]:
        nodes = []
        for n in graph.nodes.values():
            owner = n.ownership.primary_owner
            nodes.append(
                {
                    "id": n.id,
                    "label": n.label,
                    "type": n.node_type.value,
                    "group": n.group,
                    "language": n.language.value,
                    "line_count": n.line_count,
                    "metrics": {
                        "fan_in": n.metrics.fan_in,
                        "fan_out": n.metrics.fan_out,
                        "centrality": n.metrics.centrality,
                        "churn": n.metrics.churn,
                    },
                    "ownership": {
                        "primary_owner": owner.name if owner else None,
                        "total_commits": n.ownership.total_commits,
                        "last_modified": n.ownership.last_modified,
                        "contributor_count": n.ownership.contributor_count,
                    },
                }
            )

        edges = [
            {"source": e.source, "target": e.target, "type": e.edge_type.value} for e in graph.edges
        ]

        groups = [{"id": g.id, "label": g.label, "parent": g.parent} for g in graph.groups.values()]

        return {
            "root_path": graph.root_path,
            "node_count": graph.node_count,
            "edge_count": graph.edge_count,
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
        }
