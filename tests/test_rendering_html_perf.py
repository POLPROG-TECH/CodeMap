"""Tests for HTML renderer - performance features and theme support."""

from __future__ import annotations

from pathlib import Path

from codemap.domain.model import CodeGraph
from codemap.rendering.html_renderer import HtmlGraphRenderer


class TestHtmlPerformanceFeatures:
    """Tests for large-graph performance features in the HTML renderer."""

    """GIVEN a rendered HTML file (large-graph detection)"""
    def test_html_contains_large_graph_detection(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the performance logic"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN large-graph detection and perf mode constants are present"""
        assert "IS_LARGE" in content
        assert "LARGE_THRESHOLD" in content
        assert "perfMode" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_collapsed_cluster_logic(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the cluster collapsing logic"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN cluster collapse/expand functions are present"""
        assert "collapsedGroups" in content
        assert "expandGroup" in content
        assert "collapseGroup" in content
        assert "expandAllGroups" in content
        assert "computeActiveGraph" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_adaptive_sim_params(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the simulation parameter function"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN adaptive parameters including velocityDecay and tickSkip are present"""
        assert "simParams()" in content
        assert "velocityDecay" in content
        assert "tickSkip" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_perf_banner(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the performance banner"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN the perf-banner element and updater are present"""
        assert "perf-banner" in content
        assert "updatePerfBanner" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_cluster_node_css(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the cluster node CSS"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN .cluster-node and .cluster-label styles are present"""
        assert ".cluster-node" in content
        assert ".cluster-label" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_perf_i18n_keys(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect performance-related translations"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN both English and Polish perf keys are present"""
        assert "perfFast" in content
        assert "perfQuality" in content
        assert "collapsedView" in content
        assert "expandCluster" in content
        assert "largeGraph" in content
        assert "Wydajno" in content
        assert "zoptymalizowanego" in content

    """GIVEN a rendered HTML file"""
    def test_html_contains_rebuildgraph_function(
        self, sample_graph: CodeGraph, tmp_path: Path
    ) -> None:
        """WHEN we inspect the graph rebuild logic"""
        renderer = HtmlGraphRenderer()
        out = renderer.render(sample_graph, tmp_path)
        content = out.read_text()

        """THEN the rebuildGraph() function is present"""
        assert "rebuildGraph()" in content

    """GIVEN a CodeGraph prepared for rendering"""
    def test_html_data_includes_meta(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we prepare the data payload"""
        renderer = HtmlGraphRenderer()
        data = renderer._prepare_data(sample_graph)

        """THEN meta contains accurate node and link counts"""
        assert "meta" in data
        assert "nodeCount" in data["meta"]
        assert data["meta"]["nodeCount"] == 3
        assert data["meta"]["linkCount"] >= 2


class TestHtmlThemeSupport:
    """Tests for light/dark/system theme support in the HTML renderer."""

    """GIVEN a rendered HTML file"""
    def test_html_contains_theme_switch(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the theme switcher"""
        out = HtmlGraphRenderer().render(sample_graph, tmp_path)
        html = out.read_text()

        """THEN the theme-switch and its options are present"""
        assert 'id="theme-switch"' in html
        assert 'value="system"' in html
        assert 'value="dark"' in html
        assert 'value="light"' in html

    """GIVEN a rendered HTML file"""
    def test_html_contains_light_theme_css(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the theme CSS"""
        out = HtmlGraphRenderer().render(sample_graph, tmp_path)
        html = out.read_text()

        """THEN a light theme CSS block with correct background is present"""
        assert '[data-theme="light"]' in html
        assert "--bg0:#ffffff" in html

    """GIVEN a rendered HTML file"""
    def test_html_contains_theme_persistence(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we inspect the theme persistence logic"""
        out = HtmlGraphRenderer().render(sample_graph, tmp_path)
        html = out.read_text()

        """THEN theme is persisted using localStorage and applied via applyTheme"""
        assert "codemap-theme" in html
        assert "applyTheme" in html

    """GIVEN a rendered HTML file"""
    def test_html_contains_theme_i18n_keys(self, sample_graph: CodeGraph, tmp_path: Path) -> None:
        """WHEN we check theme translation keys"""
        out = HtmlGraphRenderer().render(sample_graph, tmp_path)
        html = out.read_text()

        """THEN theme keys exist in both English and Polish"""
        for key in ["theme:", "themeDark:", "themeLight:", "themeSystem:"]:
            assert key in html, f"Missing EN i18n key: {key}"
        assert 'theme:"Motyw"' in html
