"""PDF report renderer using fpdf2 - produces a printable architecture report."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from codemap.domain.model import CodeGraph


class PdfReportRenderer:
    """Renders a CodeGraph as a polished, printable PDF report."""

    @property
    def format_name(self) -> str:
        return "pdf"

    def render(self, graph: CodeGraph, output_path: Path) -> Path:
        try:
            from fpdf import FPDF  # noqa: F401  - availability check only
        except ImportError as exc:
            raise RuntimeError(
                "PDF export requires fpdf2. Install it with: pip install fpdf2"
            ) from exc

        output_path.mkdir(parents=True, exist_ok=True)
        dest = output_path / "codemap.pdf"

        pdf = _ReportPdf(graph)
        pdf.build()
        pdf.output(str(dest))
        return dest


class _ReportPdf:
    """Internal builder that lays out the CodeMap report as a multi-page PDF."""

    # Design tokens
    _CLR_TITLE = (15, 52, 96)  # dark navy
    _CLR_HEADING = (22, 33, 62)  # section headings
    _CLR_ACCENT = (83, 52, 131)  # purple accent
    _CLR_BODY = (30, 30, 30)
    _CLR_MUTED = (120, 120, 120)
    _CLR_HEADER_BG = (22, 33, 62)
    _CLR_HEADER_FG = (255, 255, 255)
    _CLR_ROW_ALT = (245, 247, 255)
    _CLR_HOTSPOT = (220, 50, 50)

    def __init__(self, graph: CodeGraph) -> None:
        from fpdf import FPDF

        self._graph = graph
        self._pdf = FPDF(orientation="L", unit="mm", format="A4")
        self._pdf.set_auto_page_break(auto=True, margin=18)
        self._pdf.set_title("CodeMap Report")

    @staticmethod
    def _safe(text: str) -> str:
        """Replace non-latin-1 characters for built-in PDF fonts."""
        return text.replace("\u2014", "-").replace("\u2013", "-").replace("\u2026", "...")

    def build(self) -> None:
        self._cover_page()
        self._files_page()
        self._dependencies_page()
        self._reverse_deps_page()
        self._hotspots_page()
        self._ownership_page()

    def output(self, path: str) -> None:
        self._pdf.output(path)

    # -- pages -------------------------------------------------------------

    def _cover_page(self) -> None:
        pdf = self._pdf
        g = self._graph
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_text_color(*self._CLR_TITLE)
        pdf.cell(0, 20, text="CodeMap Report", new_x="LMARGIN", new_y="NEXT")

        # Subtitle
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*self._CLR_MUTED)
        pdf.cell(0, 8, text=g.root_path, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(12)

        # Summary cards
        langs = sorted(
            {n.language.value for n in g.nodes.values() if n.language.value != "unknown"}
        )
        cards = [
            ("Files", str(g.node_count)),
            ("Dependencies", str(g.edge_count)),
            ("Groups", str(len(g.groups))),
            ("Languages", ", ".join(langs) or "-"),
        ]
        card_w = 60
        start_x = pdf.get_x()
        for label, value in cards:
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.set_fill_color(240, 244, 255)
            pdf.rect(x, y, card_w, 22, style="F")
            # accent left bar
            pdf.set_fill_color(*self._CLR_TITLE)
            pdf.rect(x, y, 2, 22, style="F")

            pdf.set_xy(x + 6, y + 3)
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(*self._CLR_TITLE)
            pdf.cell(card_w - 8, 8, text=value)

            pdf.set_xy(x + 6, y + 12)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*self._CLR_MUTED)
            pdf.cell(card_w - 8, 6, text=label.upper())

            pdf.set_xy(x + card_w + 6, y)

        pdf.set_xy(start_x, pdf.get_y() + 30)

        # Groups summary
        if g.groups:
            self._section("Directory Groups")
            rows = []
            for grp in sorted(g.groups.values(), key=lambda x: x.id):
                count = len(g.get_nodes_in_group(grp.id))
                rows.append((grp.id, grp.parent or "(root)", str(count)))
            self._table(["Group", "Parent", "Files"], rows, col_widths=[100, 80, 30])

    def _files_page(self) -> None:
        pdf = self._pdf
        pdf.add_page()
        self._section("All Files")

        nodes = sorted(self._graph.nodes.values(), key=lambda n: n.file_path)
        rows = []
        for n in nodes:
            owner = n.ownership.primary_owner
            rows.append(
                (
                    n.file_path,
                    n.language.value,
                    str(n.line_count),
                    str(n.metrics.fan_in),
                    str(n.metrics.fan_out),
                    str(n.metrics.churn),
                    owner.name if owner else "-",
                )
            )
        self._table(
            ["File", "Language", "Lines", "Fan-in", "Fan-out", "Churn", "Owner"],
            rows,
            col_widths=[90, 30, 22, 22, 24, 22, 50],
        )

    def _dependencies_page(self) -> None:
        pdf = self._pdf
        edges = self._graph.edges
        if not edges:
            return

        pdf.add_page()
        self._section("Dependencies (what each file imports)")

        mapping: dict[str, list[str]] = {}
        for e in edges:
            mapping.setdefault(e.source, []).append(e.target)

        rows = [(src, ", ".join(sorted(targets))) for src, targets in sorted(mapping.items())]
        self._table(["File", "Depends on"], rows, col_widths=[90, 180])

    def _reverse_deps_page(self) -> None:
        pdf = self._pdf
        edges = self._graph.edges
        if not edges:
            return

        pdf.add_page()
        self._section("Reverse Dependencies (what depends on each file)")

        mapping: dict[str, list[str]] = {}
        for e in edges:
            mapping.setdefault(e.target, []).append(e.source)

        rows = [(target, ", ".join(sorted(sources))) for target, sources in sorted(mapping.items())]
        self._table(["File", "Depended on by"], rows, col_widths=[90, 180])

    def _hotspots_page(self) -> None:
        pdf = self._pdf
        hotspots = [n for n in self._graph.nodes.values() if n.metrics.is_hotspot()]
        if not hotspots:
            return

        pdf.add_page()
        self._section("Hotspots (high churn + high fan-in)")

        rows = []
        for n in sorted(hotspots, key=lambda x: x.metrics.churn, reverse=True):
            rows.append(
                (
                    n.file_path,
                    str(n.metrics.churn),
                    str(n.metrics.fan_in),
                    str(n.metrics.fan_out),
                    f"{n.metrics.centrality:.4f}",
                    str(n.ownership.contributor_count),
                )
            )
        self._table(
            ["File", "Churn", "Fan-in", "Fan-out", "Centrality", "Contributors"],
            rows,
            col_widths=[90, 25, 25, 28, 35, 35],
        )

    def _ownership_page(self) -> None:
        pdf = self._pdf
        with_owners = [
            n for n in self._graph.nodes.values() if n.ownership.primary_owner is not None
        ]
        if not with_owners:
            return

        pdf.add_page()
        self._section("Ownership")

        rows = []
        for n in sorted(with_owners, key=lambda x: x.ownership.total_commits, reverse=True):
            owner = n.ownership.primary_owner
            rows.append(
                (
                    n.file_path,
                    owner.name if owner else "-",
                    str(n.ownership.total_commits),
                    str(n.ownership.contributor_count),
                    n.ownership.last_modified or "-",
                )
            )
        self._table(
            ["File", "Primary Owner", "Commits", "Contributors", "Last Modified"],
            rows,
            col_widths=[90, 50, 30, 38, 50],
        )

    # -- helpers -----------------------------------------------------------

    def _section(self, title: str) -> None:
        pdf = self._pdf
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*self._CLR_HEADING)
        pdf.cell(0, 10, text=title, new_x="LMARGIN", new_y="NEXT")
        # underline
        y = pdf.get_y()
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.ln(3)

    def _table(
        self,
        headers: list[str],
        rows: Sequence[tuple[str, ...]],
        col_widths: list[int] | None = None,
    ) -> None:
        pdf = self._pdf
        n_cols = len(headers)
        if col_widths is None:
            avail = pdf.w - pdf.l_margin - pdf.r_margin
            col_widths = [int(avail / n_cols)] * n_cols

        row_h = 7

        # Header
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(*self._CLR_HEADER_BG)
        pdf.set_text_color(*self._CLR_HEADER_FG)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], row_h, text=h, border=0, fill=True)
        pdf.ln(row_h)

        # Rows
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*self._CLR_BODY)
        for row_idx, row in enumerate(rows):
            # Check if we need a new page
            if pdf.get_y() + row_h > pdf.h - pdf.b_margin:
                pdf.add_page()
                # Re-draw header
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_fill_color(*self._CLR_HEADER_BG)
                pdf.set_text_color(*self._CLR_HEADER_FG)
                for i, h in enumerate(headers):
                    pdf.cell(col_widths[i], row_h, text=h, border=0, fill=True)
                pdf.ln(row_h)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*self._CLR_BODY)

            if row_idx % 2 == 1:
                pdf.set_fill_color(*self._CLR_ROW_ALT)
                fill = True
            else:
                fill = False

            for i, cell in enumerate(row):
                # Truncate long cell values to fit
                max_chars = max(10, col_widths[i] // 2)
                display = cell if len(cell) <= max_chars else cell[: max_chars - 1] + "..."
                pdf.cell(col_widths[i], row_h, text=display, border=0, fill=fill)
            pdf.ln(row_h)

        pdf.ln(4)
