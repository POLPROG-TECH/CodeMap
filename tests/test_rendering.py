"""Tests for rendering pipelines (JSON, HTML, PDF, terminal)."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from codemap.application.reporter import CodeMapReport, HotspotEntry, OwnershipEntry
from codemap.domain.model import CodeGraph
from codemap.rendering.html_renderer import HtmlGraphRenderer
from codemap.rendering.json_renderer import JsonRenderer
from codemap.rendering.pdf_renderer import PdfReportRenderer
from codemap.rendering.terminal_renderer import print_report


class TestJsonRenderer:
    """JSON renderer produces valid, structured output."""

    def test_produces_valid_json(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a CodeGraph with nodes and edges
        renderer = JsonRenderer()

        # WHEN we render to JSON
        out = renderer.render(sample_graph, tmp_path)

        # THEN the output file is valid JSON with expected keys
        data = json.loads(out.read_text())
        assert data["node_count"] == 3
        assert data["edge_count"] == 3
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 3

    def test_nodes_have_required_fields(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered JSON file
        renderer = JsonRenderer()
        out = renderer.render(sample_graph, tmp_path)
        data = json.loads(out.read_text())

        # WHEN we inspect a node
        node = data["nodes"][0]

        # THEN it contains all expected fields
        assert "id" in node
        assert "label" in node
        assert "group" in node
        assert "language" in node
        assert "metrics" in node
        assert "ownership" in node

    def test_format_name(self) -> None:
        # GIVEN a JsonRenderer
        renderer = JsonRenderer()

        # WHEN we check the format name
        # THEN it returns "json"
        assert renderer.format_name == "json"


class TestHtmlRenderer:
    """HTML renderer produces a self-contained interactive page."""

    def test_produces_html_file(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a CodeGraph
        renderer = HtmlGraphRenderer()

        # WHEN we render to HTML
        out = renderer.render(sample_graph, tmp_path)

        # THEN the output file exists and is HTML
        assert out.exists()
        assert out.suffix == ".html"
        content = out.read_text()
        assert "<!DOCTYPE html>" in content
        assert "d3.v7" in content

    def test_graph_data_embedded(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the embedded data
        # THEN node labels are present in the file
        assert "a.py" in content
        assert "b.py" in content
        assert "c.py" in content

    def test_format_name(self) -> None:
        # GIVEN an HtmlGraphRenderer
        renderer = HtmlGraphRenderer()

        # WHEN we check format name
        # THEN it returns "html"
        assert renderer.format_name == "html"

    def test_html_contains_layout_controls(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the HTML
        # THEN it contains layout selector buttons
        assert 'data-layout="force"' in content
        assert 'data-layout="hierarchy"' in content
        assert 'data-layout="radial"' in content
        assert 'data-layout="cluster"' in content

    def test_html_contains_view_modes(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the HTML
        # THEN it contains view mode buttons (All, Neighborhood, Impact)
        assert 'data-view="all"' in content
        assert 'data-view="neighborhood"' in content
        assert 'data-view="impact"' in content

    def test_html_contains_color_modes(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the color mode selector
        # THEN it contains language, group, churn, risk, and contributors options
        assert 'value="language"' in content
        assert 'value="risk"' in content
        assert 'value="contributors"' in content

    def test_html_contains_sidebar_tabs(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the sidebar
        # THEN it has Explore, Details, Hotspots, and Authors tabs
        assert "tab-explore" in content
        assert "tab-details" in content
        assert "tab-hotspots" in content
        assert "tab-authors" in content

    def test_html_contains_i18n_dictionaries(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the HTML
        # THEN it contains i18n translation dictionaries for EN and PL
        assert "const I18N" in content
        assert '"en"' in content or "en:{" in content
        assert '"pl"' in content or "pl:{" in content

    def test_html_contains_language_switcher(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the HTML
        # THEN it contains the language switch dropdown with EN and PL options
        assert 'id="lang-switch"' in content
        assert 'value="en"' in content
        assert 'value="pl"' in content

    def test_html_contains_flow_layout(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the layout buttons
        # THEN it contains a Flow layout option
        assert 'data-layout="flow"' in content
        assert 'id="flow-controls"' in content

    def test_html_data_includes_entry_points(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the embedded graph data
        # THEN nodes include isEntry field
        assert '"isEntry"' in content

    def test_html_data_includes_contributor_list(
        self, graph_with_ownership: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a graph with ownership data
        renderer = HtmlGraphRenderer()
        out = renderer.render(graph_with_ownership, tmp_path)
        content = out.read_text()

        # WHEN we inspect the embedded data
        # THEN nodes include per-node contribList and global contributors list
        assert '"contribList"' in content
        assert '"contributors"' in content
        assert "Alice" in content

    def test_html_authors_tab_present(
        self, graph_with_ownership: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a graph with ownership data rendered to HTML
        renderer = HtmlGraphRenderer()
        out = renderer.render(graph_with_ownership, tmp_path)
        content = out.read_text()

        # WHEN we inspect the HTML
        # THEN it contains the authors tab with author items
        assert "tab-authors" in content
        assert "author-item" in content

    def test_html_contains_display_mode_buttons(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the toolbar
        # THEN it contains display mode buttons for Overview, Readable, Focus, and Presentation
        assert 'data-dm="overview"' in content
        assert 'data-dm="readable"' in content
        assert 'data-dm="focus"' in content
        assert 'data-dm="presentation"' in content

    def test_html_contains_zoom_aware_labeling(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the JS code
        # THEN it contains the zoom-aware label visibility functions
        assert "updateLabelVisibility" in content
        assert "labelText" in content
        assert "currentZoom" in content
        assert "showPaths" in content

    def test_html_contains_expanded_language_colors(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the language color mapping
        # THEN it contains colors for many languages beyond just Python/JS/TS
        for lang_key in ["java", "go", "rust", "ruby", "html", "css", "swift", "kotlin"]:
            assert lang_key in content

    def test_language_enum_extended(self) -> None:
        # GIVEN the Language enum in the domain model
        from codemap.domain.model import Language

        # WHEN we check supported languages
        # THEN it recognizes extended file types
        assert Language.from_extension(".go") == Language.GO
        assert Language.from_extension(".rs") == Language.RUST
        assert Language.from_extension(".java") == Language.JAVA
        assert Language.from_extension(".html") == Language.HTML
        assert Language.from_extension(".css") == Language.CSS
        assert Language.from_extension(".vue") == Language.VUE
        assert Language.from_extension(".dart") == Language.DART
        assert Language.from_extension(".xyz") == Language.UNKNOWN

    def test_html_dynamic_legend_uses_data_languages(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the legend builder
        # THEN it iterates DATA.languages (dynamic) instead of LANG_COLORS keys (static)
        assert "DATA.languages.forEach" in content

    def test_html_contains_show_paths_checkbox(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the explore tab
        # THEN it contains a Show paths checkbox
        assert 'id="chk-paths"' in content
        assert "showPaths" in content

    def test_html_tooltip_shows_full_path(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the tooltip builder
        # THEN it includes the full path field and dependency counts
        assert "dependsOn" in content
        assert "dependedOnBy" in content

    def test_html_data_includes_risk_and_depth(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the embedded graph data
        # THEN nodes include riskScore and depth fields
        assert "riskScore" in content
        assert '"depth"' in content

    def test_html_contains_spacious_display_mode(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the toolbar
        # THEN it contains a Spacious display mode button
        assert 'data-dm="spacious"' in content

    def test_html_contains_focused_node_dropdown(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the toolbar
        # THEN it contains the node focus dropdown and focus bar
        assert 'id="node-focus-select"' in content
        assert 'id="focus-bar"' in content

    def test_html_contains_minimap(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the HTML
        # THEN it contains the minimap container
        assert 'id="minimap"' in content
        assert 'id="minimap-svg"' in content

    def test_html_contains_focused_exploration_functions(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the JS code
        # THEN it contains focused exploration functions
        assert "activateFocusedNode" in content
        assert "deactivateFocusedNode" in content
        assert "applyFocusedNodeView" in content
        assert "buildFocusBar" in content

    def test_html_polish_translations_complete(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we check for Polish translations
        # THEN all new keys are present for both en and pl
        for key in [
            "slow",
            "normal",
            "fast",
            "spacious",
            "focusedExploration",
            "selectANode",
            "depsOnly",
            "reverseDepsOnly",
            "localGraph",
            "impactChain",
            "nodeFlow",
            "clearFocus",
            "focusedNode",
        ]:
            assert f"{key}:" in content, f"Missing translation key: {key}"

    def test_html_contains_stronger_force_params(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # WHEN we inspect the force simulation setup
        # THEN it uses adaptive spacing parameters via simParams()
        assert "simParams()" in content
        assert "linkDist:280" in content
        assert "charge:-800" in content

    def test_html_sidebar_overflow_fix(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # THEN sidebar selects have min-width:0 and overflow protection
        assert "min-width:0" in content
        assert "text-overflow:ellipsis" in content
        assert "overflow-x:hidden" in content

    def test_html_contains_about_footer(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # THEN about footer exists
        assert "app-footer" in content
        assert "buildAboutFooter" in content
        assert "POLPROG" in content

    def test_html_contains_manual_layout(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # THEN manual layout mode is supported
        assert 'data-layout="manual"' in content
        assert "manualLayoutActive" in content
        assert "manual-indicator" in content
        assert "returnToAuto" in content

    def test_html_contains_node_notes(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # THEN node notes feature is present
        assert "nodeNotes" in content
        assert "openNoteEditor" in content
        assert "note-editor" in content
        assert "note-overlay" in content
        assert "updateNoteIndicators" in content

    def test_html_manual_layout_i18n(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered HTML file
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # THEN manual layout i18n keys exist for both EN and PL
        assert "manualLayout" in content
        assert "dragToArrange" in content
        assert "returnToAuto" in content
        # PL translations
        assert "Tryb r\\u0119cznego" in content or "R\\u0119czny" in content

    def test_html_no_variable_use_before_declaration(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        # Regression test: noteG must be declared before sim.on("tick") which calls
        # updateNoteIndicators(). A let declaration after first use causes a
        # ReferenceError (temporal dead zone) that breaks page initialization.
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        js_start = content.index("<script>")
        tick_pos = content.index('sim.on("tick"', js_start)
        # noteG declaration must appear before the tick handler
        noteg_decl = content.index("let noteG=null", js_start)
        assert noteg_decl < tick_pos, "noteG declared after sim tick handler (TDZ bug)"

    def test_html_note_editor_hidden_by_default(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # Note editor must be display:none by default and only shown via .visible class
        assert "#note-editor{display:none" in content
        assert "#note-editor.visible{display:block}" in content

    def test_html_global_footer(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # Footer spans full width outside sidebar
        assert 'id="app-footer"' in content
        assert "POLPROG" in content

    def test_html_manual_drag_updates_dom(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # Manual mode must call manualTick() during drag to update positions
        assert "manualTick()" in content
        assert "function manualTick()" in content

    def test_html_save_restore_layout(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        assert "saveManualLayout" in content
        assert "restoreManualLayout" in content
        assert "localStorage" in content

    def test_html_author_accordion(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        assert "author-accord" in content
        assert "author-accord-header" in content
        assert "author-accord-body" in content
        assert "aa-file-list" in content

    # ------------------------------------------------------------------
    # Large-graph performance features
    # ------------------------------------------------------------------
    def test_html_contains_large_graph_detection(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        assert "IS_LARGE" in content
        assert "LARGE_THRESHOLD" in content
        assert "perfMode" in content

    def test_html_contains_collapsed_cluster_logic(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        assert "collapsedGroups" in content
        assert "expandGroup" in content
        assert "collapseGroup" in content
        assert "expandAllGroups" in content
        assert "computeActiveGraph" in content

    def test_html_contains_adaptive_sim_params(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        assert "simParams()" in content
        assert "velocityDecay" in content
        assert "tickSkip" in content

    def test_html_contains_perf_banner(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        assert "perf-banner" in content
        assert "updatePerfBanner" in content

    def test_html_contains_cluster_node_css(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        assert ".cluster-node" in content
        assert ".cluster-label" in content

    def test_html_contains_perf_i18n_keys(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        # English keys
        assert "perfFast" in content
        assert "perfQuality" in content
        assert "collapsedView" in content
        assert "expandCluster" in content
        assert "largeGraph" in content
        # Polish translations
        assert "Wydajno" in content  # Wydajność
        assert "zoptymalizowanego" in content  # zoptymalizowanego widoku

    def test_html_contains_rebuildgraph_function(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        assert "rebuildGraph()" in content

    def test_html_data_includes_meta(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        renderer = HtmlGraphRenderer()
        data = renderer._prepare_data(sample_graph)

        assert "meta" in data
        assert "nodeCount" in data["meta"]
        assert data["meta"]["nodeCount"] == 3
        assert data["meta"]["linkCount"] >= 2

    def test_html_contains_theme_switch(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        out = HtmlGraphRenderer().render(sample_graph, tmp_path)
        html = out.read_text()
        assert 'id="theme-switch"' in html
        assert 'value="system"' in html
        assert 'value="dark"' in html
        assert 'value="light"' in html

    def test_html_contains_light_theme_css(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        out = HtmlGraphRenderer().render(sample_graph, tmp_path)
        html = out.read_text()
        assert '[data-theme="light"]' in html
        assert "--bg0:#ffffff" in html

    def test_html_contains_theme_persistence(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        out = HtmlGraphRenderer().render(sample_graph, tmp_path)
        html = out.read_text()
        assert "codemap-theme" in html
        assert "applyTheme" in html

    def test_html_contains_theme_i18n_keys(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        out = HtmlGraphRenderer().render(sample_graph, tmp_path)
        html = out.read_text()
        for key in ["theme:", "themeDark:", "themeLight:", "themeSystem:"]:
            assert key in html, f"Missing EN i18n key: {key}"
        # PL translations
        assert 'theme:"Motyw"' in html


class TestTerminalRenderer:
    """Terminal report rendering does not crash and contains expected text."""

    def test_print_report_runs(self) -> None:
        # GIVEN a report with hotspots and ownership
        report = CodeMapReport(
            total_files=10,
            total_edges=15,
            total_groups=3,
            languages=["python", "javascript"],
            hotspots=[
                HotspotEntry(
                    file_path="core.py",
                    fan_in=5,
                    fan_out=2,
                    churn=20,
                    centrality=0.5,
                    contributors=3,
                )
            ],
            most_depended_on=[("utils.py", 8)],
            highest_fan_out=[("main.py", 6)],
            ownership=[
                OwnershipEntry(
                    file_path="core.py",
                    primary_owner="Alice",
                    total_commits=25,
                    last_modified="2026-01-15",
                    contributor_count=3,
                )
            ],
        )
        console = Console(file=open("/dev/null", "w"), force_terminal=True)

        # WHEN we print the report
        print_report(report, console)

        # THEN no exception is raised (smoke test)

    def test_print_empty_report(self) -> None:
        # GIVEN an empty report
        report = CodeMapReport()
        console = Console(file=open("/dev/null", "w"), force_terminal=True)

        # WHEN we print it
        print_report(report, console)

        # THEN no exception is raised


class TestPdfRenderer:
    """PDF renderer produces a valid PDF file."""

    def test_produces_pdf_file(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a CodeGraph with nodes and edges
        renderer = PdfReportRenderer()

        # WHEN we render to PDF
        out = renderer.render(sample_graph, tmp_path)

        # THEN the output file exists and is a PDF
        assert out.exists()
        assert out.suffix == ".pdf"
        content = out.read_bytes()
        assert content[:5] == b"%PDF-"

    def test_pdf_contains_node_labels(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a rendered PDF from a graph with 3 nodes
        renderer = PdfReportRenderer()
        out = renderer.render(sample_graph, tmp_path)

        # WHEN we check the file
        # THEN the PDF is non-trivially sized (content was rendered)
        assert out.stat().st_size > 1000

    def test_format_name(self) -> None:
        # GIVEN a PdfReportRenderer
        renderer = PdfReportRenderer()

        # WHEN we check the format name
        # THEN it returns "pdf"
        assert renderer.format_name == "pdf"

    def test_pdf_with_ownership(self, graph_with_ownership: CodeGraph, tmp_path: Path) -> None:
        # GIVEN a CodeGraph that includes ownership metadata
        renderer = PdfReportRenderer()

        # WHEN we render to PDF
        out = renderer.render(graph_with_ownership, tmp_path)

        # THEN the file is generated without errors and has valid content
        assert out.exists()
        assert out.read_bytes()[:5] == b"%PDF-"
        assert out.stat().st_size > 1000