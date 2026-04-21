"""Tests for the HTML renderer."""

from __future__ import annotations

from pathlib import Path

from codemap.domain.model import CodeGraph
from codemap.rendering.html_renderer import HtmlGraphRenderer


class TestHtmlRenderer:
    """Tests that the HTML renderer produces a self-contained interactive page."""

    """GIVEN a CodeGraph"""
    def test_produces_html_file(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we render to HTML"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)

        """THEN the output file exists and is a valid HTML document"""
        assert out.exists()
        assert out.suffix == ".html"
        content = out.read_text()
        assert "<!DOCTYPE html>" in content
        assert "d3.v7" in content

    """GIVEN a rendered HTML file"""
    def test_graph_data_embedded(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the embedded data"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN node labels are present in the file"""
        assert "a.py" in content
        assert "b.py" in content
        assert "c.py" in content

    """GIVEN an HtmlGraphRenderer instance"""
    def test_format_name(self) -> None:
        """WHEN we check the format name"""
        renderer = HtmlGraphRenderer()

        """THEN it returns 'html'"""
        assert renderer.format_name == "html"

    """GIVEN a rendered HTML file"""
    def test_html_contains_layout_controls(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the HTML"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains layout selector buttons"""
        assert 'data-layout="force"' in content
        assert 'data-layout="hierarchy"' in content
        assert 'data-layout="radial"' in content
        assert 'data-layout="cluster"' in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_view_modes(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the HTML"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains view mode buttons (All, Neighborhood, Impact)"""
        assert 'data-view="all"' in content
        assert 'data-view="neighborhood"' in content
        assert 'data-view="impact"' in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_color_modes(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the color mode selector"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains language, risk, and contributors options"""
        assert 'value="language"' in content
        assert 'value="risk"' in content
        assert 'value="contributors"' in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_sidebar_tabs(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the sidebar"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it has Explore, Details, Hotspots, and Authors tabs"""
        assert "tab-explore" in content
        assert "tab-details" in content
        assert "tab-hotspots" in content
        assert "tab-authors" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_i18n_dictionaries(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the HTML"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains i18n translation dictionaries for EN and PL"""
        assert "const I18N" in content
        assert '"en"' in content or "en:{" in content
        assert '"pl"' in content or "pl:{" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_language_switcher(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the HTML"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains the language switch dropdown with EN and PL options"""
        assert 'id="lang-switch"' in content
        assert 'value="en"' in content
        assert 'value="pl"' in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_flow_layout(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the layout buttons"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains a Flow layout option and its controls"""
        assert 'data-layout="flow"' in content
        assert 'id="flow-controls"' in content

    """GIVEN a rendered HTML file"""
    def test_html_data_includes_entry_points(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the embedded graph data"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN nodes include the isEntry field"""
        assert '"isEntry"' in content

    """GIVEN a graph with ownership data"""
    def test_html_data_includes_contributor_list(
        self, graph_with_ownership: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the embedded data"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(graph_with_ownership, tmp_path)
        content = out.read_text()

        """THEN nodes include per-node contribList and global contributors list"""
        assert '"contribList"' in content
        assert '"contributors"' in content
        assert "Alice" in content

    """GIVEN a graph with ownership data rendered to HTML"""
    def test_html_authors_tab_present(
        self, graph_with_ownership: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the HTML"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(graph_with_ownership, tmp_path)
        content = out.read_text()

        """THEN it contains the authors tab with author items"""
        assert "tab-authors" in content
        assert "author-item" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_display_mode_buttons(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the toolbar"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains display mode buttons (Overview, Readable, Focus, Presentation)"""
        assert 'data-dm="overview"' in content
        assert 'data-dm="readable"' in content
        assert 'data-dm="focus"' in content
        assert 'data-dm="presentation"' in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_zoom_aware_labeling(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the JS code"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains the zoom-aware label visibility functions"""
        assert "updateLabelVisibility" in content
        assert "labelText" in content
        assert "currentZoom" in content
        assert "showPaths" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_expanded_language_colors(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the language color mapping"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains colors for many languages beyond Python/JS/TS"""
        for lang_key in ["java", "go", "rust", "ruby", "html", "css", "swift", "kotlin"]:
            assert lang_key in content

    """GIVEN the Language enum in the domain model"""
    def test_language_enum_extended(self) -> None:
        """WHEN we check supported languages"""
        from codemap.domain.model import Language

        """THEN it recognizes extended file types"""
        assert Language.from_extension(".go") == Language.GO
        assert Language.from_extension(".rs") == Language.RUST
        assert Language.from_extension(".java") == Language.JAVA
        assert Language.from_extension(".html") == Language.HTML
        assert Language.from_extension(".css") == Language.CSS
        assert Language.from_extension(".vue") == Language.VUE
        assert Language.from_extension(".dart") == Language.DART
        assert Language.from_extension(".xyz") == Language.UNKNOWN

    """GIVEN a rendered HTML file"""
    def test_html_dynamic_legend_uses_data_languages(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the legend builder"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it iterates DATA.languages instead of LANG_COLORS keys"""
        assert "DATA.languages.forEach" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_show_paths_checkbox(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the explore tab"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains a Show paths checkbox"""
        assert 'id="chk-paths"' in content
        assert "showPaths" in content

    """GIVEN a rendered HTML file"""
    def test_html_tooltip_shows_full_path(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the tooltip builder"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it includes the full path field and dependency counts"""
        assert "dependsOn" in content
        assert "dependedOnBy" in content

    """GIVEN a rendered HTML file"""
    def test_html_data_includes_risk_and_depth(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the embedded graph data"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN nodes include riskScore and depth fields"""
        assert "riskScore" in content
        assert '"depth"' in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_spacious_display_mode(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the toolbar"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains a Spacious display mode button"""
        assert 'data-dm="spacious"' in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_focused_node_dropdown(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the toolbar"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains the node focus dropdown and focus bar"""
        assert 'id="node-focus-select"' in content
        assert 'id="focus-bar"' in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_minimap(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the HTML"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains the minimap container"""
        assert 'id="minimap"' in content
        assert 'id="minimap-svg"' in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_focused_exploration_functions(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the JS code"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it contains focused exploration functions"""
        assert "activateFocusedNode" in content
        assert "deactivateFocusedNode" in content
        assert "applyFocusedNodeView" in content
        assert "buildFocusBar" in content

    """GIVEN a rendered HTML file"""
    def test_html_polish_translations_complete(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we check for Polish translations"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN all new keys are present for both en and pl"""
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

    """GIVEN a rendered HTML file"""
    def test_html_contains_stronger_force_params(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the force simulation setup"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN it uses adaptive spacing parameters via simParams()"""
        assert "simParams()" in content
        assert "linkDist:280" in content
        assert "charge:-800" in content

    """GIVEN a rendered HTML file"""
    def test_html_sidebar_overflow_fix(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the sidebar CSS"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN sidebar selects have min-width:0 and overflow protection"""
        assert "min-width:0" in content
        assert "text-overflow:ellipsis" in content
        assert "overflow-x:hidden" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_about_footer(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the page footer"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN the about footer is present with project branding"""
        assert "app-footer" in content
        assert "buildAboutFooter" in content
        assert "POLPROG" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_manual_layout(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the layout modes"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN manual layout mode is supported"""
        assert 'data-layout="manual"' in content
        assert "manualLayoutActive" in content
        assert "manual-indicator" in content
        assert "returnToAuto" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_node_notes(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the notes feature"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN the node notes feature is present"""
        assert "nodeNotes" in content
        assert "openNoteEditor" in content
        assert "note-editor" in content
        assert "note-overlay" in content
        assert "updateNoteIndicators" in content

    """GIVEN a rendered HTML file"""
    def test_html_manual_layout_i18n(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the manual layout translations"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN manual layout i18n keys exist for both EN and PL"""
        assert "manualLayout" in content
        assert "dragToArrange" in content
        assert "returnToAuto" in content
        assert "Tryb r\\u0119cznego" in content or "R\\u0119czny" in content

    """GIVEN a rendered HTML file (regression for TDZ bug)"""
    def test_html_no_variable_use_before_declaration(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we locate the tick handler and noteG declaration"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()
        js_start = content.index("<script>")
        tick_pos = content.index('sim.on("tick"', js_start)
        noteg_decl = content.index("let noteG=null", js_start)

        """THEN noteG is declared before the tick handler (no TDZ error)"""
        assert noteg_decl < tick_pos, "noteG declared after sim tick handler (TDZ bug)"

    """GIVEN a rendered HTML file"""
    def test_html_note_editor_hidden_by_default(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the note editor CSS"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN the note editor is hidden by default and shown only via .visible"""
        assert "#note-editor{display:none" in content
        assert "#note-editor.visible{display:block}" in content

    """GIVEN a rendered HTML file"""
    def test_html_global_footer(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the app footer"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN the footer spans full width outside the sidebar"""
        assert 'id="app-footer"' in content
        assert "POLPROG" in content

    """GIVEN a rendered HTML file"""
    def test_html_manual_drag_updates_dom(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the manual layout drag behavior"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN manual mode calls manualTick() during drag to update positions"""
        assert "manualTick()" in content
        assert "function manualTick()" in content

    """GIVEN a rendered HTML file"""
    def test_html_save_restore_layout(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the layout persistence"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN save/restore layout functions backed by localStorage are present"""
        assert "saveManualLayout" in content
        assert "restoreManualLayout" in content
        assert "localStorage" in content

    """GIVEN a rendered HTML file"""
    def test_html_author_accordion(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the authors tab"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN accordion markup is present"""
        assert "author-accord" in content
        assert "author-accord-header" in content
        assert "author-accord-body" in content
        assert "aa-file-list" in content
