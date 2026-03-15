"""Interactive HTML graph renderer with multiple layouts, i18n, and exploration modes."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from codemap.domain.model import CodeGraph

_ENTRY_NAMES = frozenset(
    {
        "main.py",
        "__main__.py",
        "app.py",
        "manage.py",
        "wsgi.py",
        "asgi.py",
        "cli.py",
        "run.py",
        "index.js",
        "index.ts",
        "index.jsx",
        "index.tsx",
        "main.js",
        "main.ts",
        "app.js",
        "app.ts",
        "server.js",
        "server.ts",
    }
)


class HtmlGraphRenderer:
    """Produces a self-contained interactive HTML visualisation of a CodeGraph."""

    @property
    def format_name(self) -> str:
        return "html"

    def render(self, graph: CodeGraph, output_path: Path) -> Path:
        output_path.mkdir(parents=True, exist_ok=True)
        dest = output_path / "codemap.html"

        from codemap.rendering._html_template import HTML_TEMPLATE

        graph_json = json.dumps(self._prepare_data(graph))
        html = HTML_TEMPLATE.replace("__GRAPH_DATA__", graph_json)
        dest.write_text(html, encoding="utf-8")
        return dest

    # ------------------------------------------------------------------

    @staticmethod
    def _prepare_data(graph: CodeGraph) -> dict[str, Any]:
        successors: dict[str, set[str]] = defaultdict(set)
        predecessors: dict[str, set[str]] = defaultdict(set)
        for e in graph.edges:
            successors[e.source].add(e.target)
            predecessors[e.target].add(e.source)

        # Topological depth via BFS from roots
        all_ids = set(graph.nodes.keys())
        roots = all_ids - set(predecessors.keys())
        if not roots:
            roots = all_ids

        depth: dict[str, int] = {nid: 0 for nid in all_ids}
        queue: deque[str] = deque(roots)
        visited: set[str] = set()
        while queue:
            nid = queue.popleft()
            if nid in visited:
                continue
            visited.add(nid)
            for child in successors.get(nid, []):
                depth[child] = max(depth[child], depth[nid] + 1)
                if child not in visited:
                    queue.append(child)

        def _safe_max(values: list[float]) -> float:
            return max(values) if values else 1.0

        all_nodes = list(graph.nodes.values())
        max_churn = _safe_max([float(n.metrics.churn) for n in all_nodes]) or 1.0
        max_fanin = _safe_max([float(n.metrics.fan_in) for n in all_nodes]) or 1.0
        max_fanout = _safe_max([float(n.metrics.fan_out) for n in all_nodes]) or 1.0
        max_contrib = _safe_max([float(n.ownership.contributor_count) for n in all_nodes]) or 1.0
        max_central = _safe_max([float(n.metrics.centrality) for n in all_nodes]) or 1.0

        # Entry-point detection: topology + name heuristics
        target_ids = {e.target for e in graph.edges}

        # Build contributor aggregation for the Authors tab
        contrib_map: dict[str, dict[str, Any]] = {}
        for n in all_nodes:
            for c in n.ownership.contributors:
                if c.name not in contrib_map:
                    contrib_map[c.name] = {
                        "name": c.name,
                        "email": c.email,
                        "files": 0,
                        "commits": 0,
                    }
                contrib_map[c.name]["files"] += 1
                contrib_map[c.name]["commits"] += c.commit_count
        contributors_list = sorted(contrib_map.values(), key=lambda x: x["commits"], reverse=True)

        nodes = []
        for n in all_nodes:
            owner = n.ownership.primary_owner
            risk = (
                (n.metrics.churn / max_churn) * 0.30
                + (n.metrics.fan_in / max_fanin) * 0.25
                + (n.metrics.fan_out / max_fanout) * 0.15
                + (n.ownership.contributor_count / max_contrib) * 0.20
                + (n.metrics.centrality / max_central) * 0.10
            )
            is_entry = (
                n.id not in target_ids and n.metrics.fan_out > 0
            ) or n.label.lower() in _ENTRY_NAMES
            # Per-node contributor list
            node_contribs = [
                {"name": c.name, "commits": c.commit_count, "lastDate": c.last_commit_date or "-"}
                for c in sorted(
                    n.ownership.contributors, key=lambda x: x.commit_count, reverse=True
                )
            ]
            nodes.append(
                {
                    "id": n.id,
                    "label": n.label,
                    "group": n.group or "(root)",
                    "language": n.language.value,
                    "lineCount": n.line_count,
                    "fanIn": n.metrics.fan_in,
                    "fanOut": n.metrics.fan_out,
                    "centrality": round(n.metrics.centrality, 4),
                    "churn": n.metrics.churn,
                    "owner": owner.name if owner else "-",
                    "totalCommits": n.ownership.total_commits,
                    "lastModified": n.ownership.last_modified or "-",
                    "contributors": n.ownership.contributor_count,
                    "contribList": node_contribs,
                    "depth": depth.get(n.id, 0),
                    "riskScore": round(risk, 4),
                    "isEntry": is_entry,
                }
            )

        links = [
            {"source": e.source, "target": e.target, "type": e.edge_type.value} for e in graph.edges
        ]

        group_ids = sorted({n["group"] for n in nodes})
        languages = sorted({n["language"] for n in nodes if n["language"] != "unknown"})

        return {
            "nodes": nodes,
            "links": links,
            "groups": group_ids,
            "languages": languages,
            "contributors": contributors_list,
            "meta": {
                "nodeCount": len(nodes),
                "linkCount": len(links),
                "groupCount": len(group_ids),
            },
        }
