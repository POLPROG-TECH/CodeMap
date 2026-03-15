"""Self-contained HTML template for the CodeMap interactive graph viewer."""

# ruff: noqa: E501  — HTML template lines are necessarily long

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CodeMap</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg0:#0d1117;--bg1:#161b22;--bg2:#1c2128;--bg3:#21262d;
  --border:#30363d;--text:#c9d1d9;--text2:#8b949e;--text3:#484f58;
  --accent:#58a6ff;--accent2:#79c0ff;--highlight:#f0883e;
  --danger:#f85149;--success:#3fb950;--warning:#d29922;
  --font:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  --radius:6px;
}
[data-theme="light"]{
  --bg0:#ffffff;--bg1:#f6f8fa;--bg2:#eaeef2;--bg3:#d0d7de;
  --border:#d0d7de;--text:#1f2328;--text2:#656d76;--text3:#8b949e;
  --accent:#0969da;--accent2:#218bff;--highlight:#bf8700;
  --danger:#cf222e;--success:#1a7f37;--warning:#9a6700;
}
body{font-family:var(--font);background:var(--bg0);color:var(--text);overflow:hidden}
#app{display:flex;height:100vh;flex-direction:column}
#main-row{display:flex;flex:1;overflow:hidden}
#sidebar{width:340px;min-width:300px;max-width:340px;background:var(--bg1);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;overflow-x:hidden;flex-shrink:0}
#main-area{flex:1;display:flex;flex-direction:column;position:relative;overflow:hidden}
#sidebar-header{padding:14px 16px;border-bottom:1px solid var(--border)}
#sidebar-header h1{font-size:15px;color:var(--accent);display:flex;align-items:center;gap:6px}
.header-row{display:flex;align-items:center;justify-content:space-between}
#lang-switch,#theme-switch{background:var(--bg0);color:var(--text2);border:1px solid var(--border);border-radius:var(--radius);
  padding:3px 6px;font-size:11px;font-family:var(--font);cursor:pointer}
.header-controls{display:flex;align-items:center;gap:6px}
.summary-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:10px}
.summary-card{background:var(--bg0);border:1px solid var(--border);border-radius:var(--radius);padding:8px;text-align:center}
.summary-card .val{font-size:18px;font-weight:700;color:var(--accent)}
.summary-card .lbl{font-size:10px;color:var(--text2);text-transform:uppercase;letter-spacing:.4px;margin-top:2px}
.tab-bar{display:flex;border-bottom:1px solid var(--border);background:var(--bg2)}
.tab-bar button{flex:1;padding:8px 4px;background:none;border:none;color:var(--text2);
  font-size:11px;cursor:pointer;border-bottom:2px solid transparent;font-family:var(--font)}
.tab-bar button:hover{color:var(--text)}
.tab-bar button.active{color:var(--accent);border-bottom-color:var(--accent)}
.tab-content{display:none;flex:1;overflow-y:auto;overflow-x:hidden;padding:12px 14px}
.tab-content.active{display:block}
.section-label{font-size:10px;color:var(--text2);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;margin-top:12px}
.section-label:first-child{margin-top:0}
#search{width:100%;max-width:100%;background:var(--bg0);color:var(--text);border:1px solid var(--border);
  border-radius:var(--radius);padding:7px 10px;font-size:13px;font-family:var(--font)}
#search:focus{border-color:var(--accent);outline:none}
.filter-row{display:flex;gap:6px;margin-top:8px;max-width:100%}
.filter-row select{flex:1;min-width:0;background:var(--bg0);color:var(--text);border:1px solid var(--border);
  border-radius:var(--radius);padding:5px 6px;font-size:12px;font-family:var(--font);overflow:hidden;text-overflow:ellipsis}
.sort-row{display:flex;align-items:center;gap:6px;margin-top:10px;margin-bottom:6px;max-width:100%}
.sort-row label{font-size:11px;color:var(--text2);white-space:nowrap}
.sort-row select{flex:1;min-width:0;background:var(--bg0);color:var(--text);border:1px solid var(--border);
  border-radius:var(--radius);padding:4px 6px;font-size:12px;font-family:var(--font);overflow:hidden;text-overflow:ellipsis}
.node-item{display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:var(--radius);
  cursor:pointer;font-size:12px;border:1px solid transparent;margin-bottom:2px}
.node-item:hover{background:var(--bg2);border-color:var(--border)}
.node-item.active{background:var(--bg3);border-color:var(--accent)}
.node-item .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.node-item .name{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text)}
.node-item .metric{font-size:11px;color:var(--text2);min-width:28px;text-align:right}
.detail-empty{color:var(--text3);font-size:13px;padding:20px 0;text-align:center}
.detail-section{margin-bottom:14px}
.detail-section h4{font-size:13px;color:var(--accent);margin-bottom:6px;display:flex;align-items:center;gap:6px}
.detail-row{display:flex;justify-content:space-between;padding:3px 0;font-size:12px;border-bottom:1px solid var(--bg3)}
.detail-row .dl{color:var(--text2)}.detail-row .dv{color:var(--text);font-weight:500}
.dep-link{font-size:12px;color:var(--accent);cursor:pointer;padding:2px 0;display:block}
.dep-link:hover{color:var(--accent2);text-decoration:underline}
.risk-badge{display:inline-block;padding:1px 6px;border-radius:10px;font-size:10px;font-weight:600}
.risk-low{background:color-mix(in srgb,var(--success) 15%,transparent);color:var(--success)}
.risk-med{background:color-mix(in srgb,var(--warning) 15%,transparent);color:var(--warning)}
.risk-high{background:color-mix(in srgb,var(--danger) 15%,transparent);color:var(--danger)}
.hotspot-item{display:flex;align-items:center;gap:8px;padding:8px;background:var(--bg0);
  border:1px solid var(--border);border-radius:var(--radius);margin-bottom:6px;cursor:pointer}
.hotspot-item:hover{border-color:var(--accent)}
.hotspot-rank{font-size:14px;font-weight:700;color:var(--text3);min-width:22px}
.hotspot-info{flex:1;overflow:hidden}
.hotspot-name{font-size:12px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hotspot-meta{font-size:11px;color:var(--text2);margin-top:2px}
.hotspot-bar{width:60px;height:6px;background:var(--bg3);border-radius:3px;overflow:hidden}
.hotspot-bar-fill{height:100%;border-radius:3px}
/* Author / contributor items */
.author-item{display:flex;align-items:center;gap:10px;padding:8px 10px;background:var(--bg0);
  border:1px solid var(--border);border-radius:var(--radius);margin-bottom:6px;cursor:pointer}
.author-item:hover{border-color:var(--accent)}
.author-item.active{border-color:var(--highlight);background:var(--bg3)}
.author-avatar{width:32px;height:32px;border-radius:50%;background:var(--bg3);display:flex;align-items:center;
  justify-content:center;font-size:14px;font-weight:700;color:var(--accent);flex-shrink:0}
.author-info{flex:1;overflow:hidden}
.author-name{font-size:13px;font-weight:600;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.author-stats{font-size:11px;color:var(--text2);margin-top:2px}
.contrib-mini{font-size:11px;color:var(--text2);padding:2px 0;border-bottom:1px solid var(--bg3);display:flex;justify-content:space-between}
.contrib-mini .cn{color:var(--text)}.contrib-mini .cc{color:var(--accent)}
/* Toolbar */
#toolbar{display:flex;align-items:center;gap:4px;padding:8px 12px;background:var(--bg1);border-bottom:1px solid var(--border);flex-wrap:wrap}
.tb-group{display:flex;align-items:center;gap:2px;background:var(--bg0);border-radius:var(--radius);border:1px solid var(--border);overflow:hidden}
.tb-group button{padding:6px 10px;background:none;border:none;color:var(--text2);font-size:11px;cursor:pointer;font-family:var(--font);white-space:nowrap}
.tb-group button:hover{background:var(--bg2);color:var(--text)}
.tb-group button.active{background:var(--accent);color:#fff}
.tb-sep{width:1px;height:24px;background:var(--border);margin:0 6px}
.tb-label{font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:.5px;margin-right:4px}
.tb-select{background:var(--bg0);color:var(--text);border:1px solid var(--border);border-radius:var(--radius);padding:5px 8px;font-size:11px;font-family:var(--font)}
.tb-btn{padding:6px 12px;background:var(--bg0);border:1px solid var(--border);border-radius:var(--radius);color:var(--text2);font-size:11px;cursor:pointer;font-family:var(--font)}
.tb-btn:hover{background:var(--bg2);color:var(--text);border-color:var(--accent)}
/* Flow controls */
#flow-controls{display:none;align-items:center;gap:6px;padding:6px 12px;background:var(--bg2);border-bottom:1px solid var(--border)}
#flow-controls.visible{display:flex}
#flow-controls button{padding:4px 10px;background:var(--bg0);border:1px solid var(--border);border-radius:var(--radius);
  color:var(--text);font-size:13px;cursor:pointer;font-family:var(--font)}
#flow-controls button:hover{border-color:var(--accent)}
#flow-controls button.playing{background:var(--accent);color:#fff;border-color:var(--accent)}
#flow-step{font-size:12px;color:var(--text2);margin:0 8px}
#flow-speed{background:var(--bg0);color:var(--text);border:1px solid var(--border);border-radius:var(--radius);padding:3px 6px;font-size:11px}
/* Graph */
#graph-container{flex:1;position:relative;overflow:hidden}
svg{width:100%;height:100%}
.link{stroke:var(--border);stroke-opacity:.5;fill:none;marker-end:url(#arrow)}
.link.highlighted{stroke:var(--highlight);stroke-opacity:1;stroke-width:2px;marker-end:url(#arrow-hl)}
.link.dep-fwd{stroke:var(--accent);stroke-opacity:.8;stroke-width:1.5px;marker-end:url(#arrow-fwd)}
.link.dep-rev{stroke:var(--danger);stroke-opacity:.8;stroke-width:1.5px;marker-end:url(#arrow-rev)}
.link.flow-active{stroke:var(--success);stroke-opacity:.9;stroke-width:2px;marker-end:url(#arrow-flow)}
.node-circle{cursor:pointer;stroke:var(--bg0);stroke-width:1.5px;transition:opacity .2s}
.node-circle:hover{filter:brightness(1.3)}
.node-circle.selected{stroke:var(--highlight);stroke-width:3px}
.node-circle.dimmed{opacity:.12}
.node-circle.flow-future{opacity:.1}
.node-circle.flow-current{stroke:var(--success);stroke-width:3px;filter:brightness(1.3)}
.node-label{fill:var(--text2);pointer-events:none;text-anchor:middle;transition:opacity .15s;font-size:10px}
.node-label.dimmed{opacity:.08}
.mode-overview .node-label{display:none}
.mode-presentation .node-label{font-size:12px;font-weight:500;fill:var(--text)}
.group-hull{fill-opacity:.04;stroke-opacity:.18;stroke-width:1.5px;stroke-dasharray:5 3}
.group-label{font-size:11px;fill:var(--text3);text-anchor:middle;pointer-events:none;font-weight:600}
.hotspot-ring{fill:none;stroke:var(--danger);stroke-width:2px;stroke-dasharray:3 2;pointer-events:none;opacity:.7}
.entry-marker{fill:none;stroke:var(--success);stroke-width:2px;pointer-events:none}
.tooltip{position:absolute;background:var(--bg2);border:1px solid var(--border);border-radius:8px;
  padding:10px 14px;font-size:12px;pointer-events:none;opacity:0;transition:opacity .12s;
  max-width:280px;box-shadow:0 4px 16px rgba(0,0,0,.5);z-index:100}
.tooltip .tt-title{font-weight:600;color:var(--text);margin-bottom:4px;font-size:13px}
.tooltip .tt-row{color:var(--text2);line-height:1.5}.tooltip .tt-row span{color:var(--text)}
#stats-bar{position:absolute;bottom:10px;left:10px;background:var(--bg1);border:1px solid var(--border);
  border-radius:8px;padding:6px 14px;font-size:11px;color:var(--text2);display:flex;gap:14px;z-index:50}
#stats-bar .sv{color:var(--accent);font-weight:600}
#legend-panel{position:absolute;bottom:10px;right:10px;background:var(--bg1);border:1px solid var(--border);
  border-radius:8px;padding:10px 14px;font-size:11px;z-index:50;max-width:200px}
#legend-panel h5{color:var(--text2);font-size:10px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}
.legend-row{display:flex;align-items:center;gap:6px;margin-bottom:3px;color:var(--text)}
.legend-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
/* Focused exploration bar */
#focus-bar{display:none;align-items:center;gap:8px;padding:6px 12px;background:var(--bg2);border-bottom:1px solid var(--border);flex-wrap:wrap}
#focus-bar.visible{display:flex}
#focus-bar .fb-label{font-size:11px;color:var(--text2)}
#focus-bar select{background:var(--bg0);color:var(--text);border:1px solid var(--border);border-radius:var(--radius);padding:5px 8px;font-size:12px;font-family:var(--font);max-width:280px}
#focus-bar .fb-modes{display:flex;gap:2px;background:var(--bg0);border-radius:var(--radius);border:1px solid var(--border);overflow:hidden}
#focus-bar .fb-modes button{padding:5px 10px;background:none;border:none;color:var(--text2);font-size:11px;cursor:pointer;font-family:var(--font);white-space:nowrap}
#focus-bar .fb-modes button:hover{background:var(--bg2);color:var(--text)}
#focus-bar .fb-modes button.active{background:var(--accent);color:#fff}
#focus-bar .fb-info{font-size:11px;color:var(--text2);margin-left:auto;max-width:350px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#focus-bar .fb-close{padding:4px 10px;background:var(--bg0);border:1px solid var(--border);border-radius:var(--radius);color:var(--text2);font-size:11px;cursor:pointer;font-family:var(--font)}
#focus-bar .fb-close:hover{border-color:var(--danger);color:var(--danger)}
/* Minimap */
#minimap{position:absolute;bottom:50px;right:10px;width:180px;height:130px;background:var(--bg1);border:1px solid var(--border);
  border-radius:8px;z-index:60;overflow:hidden;cursor:pointer}
#minimap svg{width:100%;height:100%}
#minimap .mm-viewport{fill:var(--accent);fill-opacity:.08;stroke:var(--accent);stroke-width:1.5;stroke-opacity:.6}
#minimap .mm-node{fill:var(--text3);opacity:.6}
/* Spacious mode overrides */
.mode-spacious .node-label{font-size:11px;font-weight:500;fill:var(--text)}
.mode-spacious .group-label{font-size:13px;font-weight:700}
/* About footer — full-width app footer */
#app-footer{display:flex;align-items:center;justify-content:center;gap:12px;padding:6px 16px;
  background:var(--bg2);border-top:1px solid var(--border);font-size:11px;color:var(--text3);flex-shrink:0}
#app-footer a{color:var(--accent);text-decoration:none}
#app-footer a:hover{text-decoration:underline}
#app-footer .footer-sep{color:var(--border)}
/* Manual layout indicator */
#manual-indicator{display:none;align-items:center;gap:6px;padding:5px 12px;background:var(--bg2);border-bottom:1px solid var(--accent);font-size:11px;color:var(--accent)}
#manual-indicator.visible{display:flex}
#manual-indicator .mi-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);animation:mi-pulse 1.5s infinite}
#manual-indicator button{white-space:nowrap}
@keyframes mi-pulse{0%,100%{opacity:1}50%{opacity:.4}}
/* Author accordion */
.author-accord{border:1px solid var(--border);border-radius:var(--radius);margin-bottom:6px;overflow:hidden}
.author-accord-header{display:flex;align-items:center;gap:8px;padding:8px 10px;cursor:pointer;background:var(--bg0);transition:background .15s}
.author-accord-header:hover{background:var(--bg3)}
.author-accord-header.active{background:var(--bg3);border-bottom:1px solid var(--border)}
.author-accord-header .aa-chevron{font-size:10px;color:var(--text3);transition:transform .15s;flex-shrink:0}
.author-accord-header.active .aa-chevron{transform:rotate(90deg)}
.author-accord-body{display:none;padding:8px 10px;font-size:11px;background:var(--bg1)}
.author-accord-body.open{display:block}
.aa-row{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid var(--border)}
.aa-row:last-child{border-bottom:none}
.aa-row .aa-label{color:var(--text2)}.aa-row .aa-val{color:var(--text);font-weight:500}
.aa-file-list{margin-top:6px;max-height:120px;overflow-y:auto}
.aa-file{display:flex;justify-content:space-between;padding:2px 0;font-size:10px;cursor:pointer;color:var(--accent)}
.aa-file:hover{text-decoration:underline}
/* Node notes */
.note-indicator{fill:var(--warning);cursor:pointer;pointer-events:all}
.note-badge{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--warning);margin-left:4px;vertical-align:middle}
#note-editor{display:none;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:var(--bg1);border:1px solid var(--border);
  border-radius:10px;padding:16px;z-index:200;width:340px;box-shadow:0 8px 32px rgba(0,0,0,.6)}
#note-editor.visible{display:block}
#note-editor h4{color:var(--accent);font-size:13px;margin-bottom:8px;display:flex;align-items:center;gap:6px}
#note-editor textarea{width:100%;height:90px;background:var(--bg0);color:var(--text);border:1px solid var(--border);border-radius:var(--radius);
  padding:8px;font-size:12px;font-family:var(--font);resize:vertical}
#note-editor .ne-actions{display:flex;gap:6px;margin-top:8px;justify-content:flex-end}
#note-editor .ne-actions button{padding:5px 14px;border-radius:var(--radius);border:1px solid var(--border);font-size:11px;
  cursor:pointer;font-family:var(--font);background:var(--bg0);color:var(--text)}
#note-editor .ne-actions button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
#note-editor .ne-actions button.danger{color:var(--danger);border-color:var(--danger)}
#note-overlay{display:none;position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.4);z-index:190}
#note-overlay.visible{display:block}
/* Collapsed cluster nodes */
.cluster-node{cursor:pointer;stroke:var(--bg0);stroke-width:2px;transition:opacity .2s}
.cluster-node:hover{filter:brightness(1.2);stroke:var(--accent)}
.cluster-label{fill:var(--text);pointer-events:none;text-anchor:middle;font-weight:600;font-size:12px}
.cluster-count{fill:var(--text2);pointer-events:none;text-anchor:middle;font-size:10px}
/* Performance banner */
#perf-banner{display:none;align-items:center;gap:8px;padding:5px 12px;background:var(--bg2);
  border-bottom:1px solid var(--accent);font-size:11px;color:var(--accent)}
#perf-banner.visible{display:flex}
#perf-banner button{padding:3px 10px;background:var(--bg0);border:1px solid var(--border);border-radius:var(--radius);
  color:var(--text2);font-size:10px;cursor:pointer;font-family:var(--font);white-space:nowrap}
#perf-banner button:hover{border-color:var(--accent);color:var(--text)}
</style>
</head>
<body>
<div id="app"><div id="main-row">
<!-- SIDEBAR -->
<div id="sidebar">
  <div id="sidebar-header">
    <div class="header-row">
      <h1><span class="icon">&#9670;</span> CodeMap</h1>
      <div class="header-controls">
        <select id="theme-switch"><option value="system">&#9788; System</option><option value="dark">&#9790; Dark</option><option value="light">&#9788; Light</option></select>
        <select id="lang-switch"><option value="en">EN</option><option value="pl">PL</option></select>
      </div>
    </div>
    <div class="summary-cards" id="summary-cards"></div>
  </div>
  <div class="tab-bar" id="tab-bar"></div>
  <div class="tab-content active" id="tab-explore"></div>
  <div class="tab-content" id="tab-details"><div class="detail-empty" id="detail-placeholder"></div></div>
  <div class="tab-content" id="tab-hotspots"></div>
  <div class="tab-content" id="tab-authors"></div>
</div>
<!-- MAIN -->
<div id="main-area">
  <div id="toolbar"></div>
  <div id="perf-banner"></div>
  <div id="flow-controls">
    <button id="fc-prev">&#9198;</button>
    <button id="fc-play">&#9654;</button>
    <button id="fc-next">&#9197;</button>
    <button id="fc-reset">&#8634;</button>
    <span id="flow-step"></span>
    <select id="flow-speed"><option value="1500" id="fs-slow">Slow</option><option value="800" selected id="fs-normal">Normal</option><option value="350" id="fs-fast">Fast</option></select>
  </div>
  <div id="focus-bar"></div>
  <div id="manual-indicator"></div>
  <div id="graph-container">
    <svg id="graph-svg"></svg>
    <div class="tooltip" id="tooltip"></div>
    <div id="stats-bar"></div>
    <div id="legend-panel"></div>
    <div id="minimap"><svg id="minimap-svg"></svg></div>
    <div id="note-overlay"></div>
    <div id="note-editor"></div>
  </div>
</div>
</div>
<div id="app-footer"></div>
</div>

<script>
// =====================================================================
// I18N — translation dictionaries
// =====================================================================
const I18N = {
en:{
  explore:"Explore",details:"Details",hotspots:"Hotspots",authors:"Authors",
  search:"Search",filterFiles:"Filter files...",allGroups:"All groups",allLangs:"All languages",
  allRisk:"All risk levels",highRisk:"High risk (>0.6)",medRisk:"Medium risk (0.3-0.6)",lowRisk:"Low risk (<0.3)",
  sort:"Sort",name:"Name",fanIn:"Fan-in",fanOut:"Fan-out",churn:"Churn",risk:"Risk",lines:"Lines",
  contributors:"Contributors",layout:"Layout",force:"Force",tree:"Tree",radial:"Radial",
  cluster:"Cluster",flow:"Flow",manual:"Manual",view:"View",all:"All",neighborhood:"Neighborhood",impact:"Impact",
  display:"Display",compact:"Compact",readable:"Readable",presentation:"Presentation",
  overview:"Overview",focus:"Focus",spacious:"Spacious",showPaths:"Show full paths",
  color:"Color",language:"Language",group:"Group",riskScore:"Risk Score",reset:"Reset",
  files:"Files",edges:"Edges",groups:"Groups",clickToInspect:"Click a node to inspect",
  path:"Path",depth:"Depth",metrics:"Metrics",centrality:"Centrality",
  ownership:"Ownership",owner:"Owner",commits:"Commits",lastModified:"Last modified",
  dependsOn:"Depends on",dependedOnBy:"Depended on by",none:"None",
  highestRisk:"Highest Risk Nodes",legend:"Legend",low:"Low",medium:"Medium",high:"High",
  few:"Few",some:"Some",many:"Many",
  nodeContributors:"Node Contributors",flowStep:"Step",of:"of",
  authorFiles:"files",authorCommits:"commits",noContributors:"No contributor data available",
  entryPoint:"Entry point",step:"Step",playing:"Playing",paused:"Paused",
  filterByAuthor:"Filter by contributor",allAuthors:"All contributors",
  riskPct:"risk",
  slow:"Slow",normal:"Normal",fast:"Fast",
  focusedExploration:"Focused Exploration",selectANode:"Select a node...",
  depsOnly:"Dependencies",reverseDepsOnly:"Reverse deps",localGraph:"Local graph",
  impactChain:"Impact chain",nodeFlow:"Node flow",clearFocus:"Clear",
  showingDepsOf:"Showing dependencies of",showingReverseDepsOf:"Showing reverse dependencies of",
  showingLocalGraphOf:"Showing local graph of",showingImpactOf:"Showing impact chain of",
  showingFlowOf:"Showing flow path of",focusedNode:"Focused Node",
  minimap:"Minimap",zoomIn:"Zoom in",zoomOut:"Zoom out",fitAll:"Fit all",
  hierarchy:"Hierarchy",
  about:"About",version:"Version",author:"Author",repository:"Repository",license:"License",builtWith:"Built with",
  manualLayout:"Manual",autoLayout:"Auto layout",dragToArrange:"Drag nodes to arrange",returnToAuto:"Return to auto layout",
  pinNode:"Pin node",unpinNode:"Unpin node",manualMode:"Manual arrangement mode",
  addNote:"Add note",editNote:"Edit note",removeNote:"Remove note",noteLabel:"Note",notes:"Notes",
  noNotes:"No notes yet",notePlaceholder:"Type a note for this node...",saveNote:"Save",cancelNote:"Cancel",
  nodeHasNote:"\ud83d\udcdd",
  saveLayout:"Save layout",restoreLayout:"Restore layout",layoutSaved:"Layout saved",noSavedLayout:"No saved layout",
  authorTopFiles:"Top files",authorRecentActivity:"Recent activity",authorOwnership:"Ownership",
  authorTotalCommits:"Total commits",authorFilesTouched:"Files touched",
  appFooter:"Built by",
  theme:"Theme",themeDark:"Dark",themeLight:"Light",themeSystem:"System",
  performance:"Performance",perfFast:"Fast",perfQuality:"Quality",
  collapsedView:"Collapsed view — click a cluster to expand",expandCluster:"Click to expand",
  collapseCluster:"Collapse",expandAll:"Expand all",collapseAll:"Collapse all",
  largeGraph:"Large graph detected — using optimized view",
  nodesVisible:"nodes visible",progressiveHint:"Click groups to expand",
},
pl:{
  explore:"Eksploruj",details:"Szczeg\u00f3\u0142y",hotspots:"Hotspoty",authors:"Autorzy",
  search:"Szukaj",filterFiles:"Filtruj pliki...",allGroups:"Wszystkie grupy",allLangs:"Wszystkie j\u0119zyki",
  allRisk:"Wszystkie poziomy ryzyka",highRisk:"Wysokie ryzyko (>0.6)",medRisk:"\u015arednie ryzyko (0.3-0.6)",lowRisk:"Niskie ryzyko (<0.3)",
  sort:"Sortuj",name:"Nazwa",fanIn:"Fan-in",fanOut:"Fan-out",churn:"Churn",risk:"Ryzyko",lines:"Linie",
  contributors:"Kontrybutorzy",layout:"Uk\u0142ad",force:"Si\u0142owy",tree:"Drzewo",radial:"Radialny",
  cluster:"Klaster",flow:"Przep\u0142yw",manual:"R\u0119czny",view:"Widok",all:"Wszystko",neighborhood:"S\u0105siedztwo",impact:"Wp\u0142yw",
  display:"Wy\u015bwietlanie",compact:"Kompakt",readable:"Czytelny",presentation:"Prezentacja",
  overview:"Przegl\u0105d",focus:"Fokus",spacious:"Przestrzenny",showPaths:"Poka\u017c pe\u0142ne \u015bcie\u017cki",
  color:"Kolor",language:"J\u0119zyk",group:"Grupa",riskScore:"Wska\u017anik ryzyka",reset:"Resetuj",
  files:"Pliki",edges:"Kraw\u0119dzie",groups:"Grupy",clickToInspect:"Kliknij w\u0119ze\u0142, aby sprawdzi\u0107",
  path:"\u015acie\u017cka",depth:"G\u0142\u0119boko\u015b\u0107",metrics:"Metryki",centrality:"Centralno\u015b\u0107",
  ownership:"W\u0142asno\u015b\u0107",owner:"W\u0142a\u015bciciel",commits:"Commity",lastModified:"Ostatnia modyfikacja",
  dependsOn:"Zale\u017cy od",dependedOnBy:"U\u017cywany przez",none:"Brak",
  highestRisk:"Najwy\u017csze ryzyko",legend:"Legenda",low:"Niski",medium:"\u015aredni",high:"Wysoki",
  few:"Ma\u0142o",some:"Troch\u0119",many:"Du\u017co",
  nodeContributors:"Kontrybutorzy w\u0119z\u0142a",flowStep:"Krok",of:"z",
  authorFiles:"plik\u00f3w",authorCommits:"commit\u00f3w",noContributors:"Brak danych o kontrybutorach",
  entryPoint:"Punkt wej\u015bcia",step:"Krok",playing:"Odtwarzanie",paused:"Pauza",
  filterByAuthor:"Filtruj wg kontrybutora",allAuthors:"Wszyscy kontrybutorzy",
  riskPct:"ryzyka",
  slow:"Wolno",normal:"Normalnie",fast:"Szybko",
  focusedExploration:"Eksploracja skupiona",selectANode:"Wybierz w\u0119ze\u0142...",
  depsOnly:"Zale\u017cno\u015bci",reverseDepsOnly:"Odwrotne zale\u017cno\u015bci",localGraph:"Lokalny graf",
  impactChain:"\u0141a\u0144cuch wp\u0142ywu",nodeFlow:"Przep\u0142yw w\u0119z\u0142a",clearFocus:"Wyczy\u015b\u0107",
  showingDepsOf:"Zale\u017cno\u015bci dla",showingReverseDepsOf:"Odwrotne zale\u017cno\u015bci dla",
  showingLocalGraphOf:"Lokalny graf dla",showingImpactOf:"\u0141a\u0144cuch wp\u0142ywu dla",
  showingFlowOf:"Przep\u0142yw dla",focusedNode:"Wybrany w\u0119ze\u0142",
  minimap:"Minimapa",zoomIn:"Przybli\u017c",zoomOut:"Oddal",fitAll:"Dopasuj",
  hierarchy:"Hierarchia",
  about:"O aplikacji",version:"Wersja",author:"Autor",repository:"Repozytorium",license:"Licencja",builtWith:"Zbudowano z",
  manualLayout:"R\u0119czny",autoLayout:"Automatyczny uk\u0142ad",dragToArrange:"Przeci\u0105gnij w\u0119z\u0142y, aby u\u0142o\u017cy\u0107",returnToAuto:"Powr\u00f3t do auto uk\u0142adu",
  pinNode:"Przypnij w\u0119ze\u0142",unpinNode:"Odepnij w\u0119ze\u0142",manualMode:"Tryb r\u0119cznego uk\u0142adania",
  addNote:"Dodaj notatk\u0119",editNote:"Edytuj notatk\u0119",removeNote:"Usu\u0144 notatk\u0119",noteLabel:"Notatka",notes:"Notatki",
  noNotes:"Brak notatek",notePlaceholder:"Wpisz notatk\u0119 dla tego w\u0119z\u0142a...",saveNote:"Zapisz",cancelNote:"Anuluj",
  nodeHasNote:"\ud83d\udcdd",
  saveLayout:"Zapisz uk\u0142ad",restoreLayout:"Przywr\u00f3\u0107 uk\u0142ad",layoutSaved:"Uk\u0142ad zapisany",noSavedLayout:"Brak zapisanego uk\u0142adu",
  authorTopFiles:"G\u0142\u00f3wne pliki",authorRecentActivity:"Ostatnia aktywno\u015b\u0107",authorOwnership:"W\u0142asno\u015b\u0107",
  authorTotalCommits:"Wszystkie commity",authorFilesTouched:"Zmienione pliki",
  appFooter:"Stworzone przez",
  theme:"Motyw",themeDark:"Ciemny",themeLight:"Jasny",themeSystem:"Systemowy",
  performance:"Wydajno\u015b\u0107",perfFast:"Szybki",perfQuality:"Jako\u015b\u0107",
  collapsedView:"Widok zwinięty \u2014 kliknij klaster, aby rozwinąć",expandCluster:"Kliknij, aby rozwinąć",
  collapseCluster:"Zwiń",expandAll:"Rozwiń wszystko",collapseAll:"Zwiń wszystko",
  largeGraph:"Wykryto duży graf \u2014 użyto zoptymalizowanego widoku",
  nodesVisible:"widocznych węzłów",progressiveHint:"Kliknij grupy, aby rozwinąć",
}
};
let lang="en";
function T(k){return (I18N[lang]&&I18N[lang][k])||I18N.en[k]||k}

// =====================================================================
// DATA & CONSTANTS
// =====================================================================
const DATA = __GRAPH_DATA__;
const LANG_COLORS={
  python:"#3572A5",javascript:"#f1e05a",typescript:"#3178c6",jsx:"#f1e05a",tsx:"#3178c6",
  java:"#b07219",go:"#00ADD8",rust:"#dea584",ruby:"#701516",php:"#4F5D95",
  swift:"#F05138",kotlin:"#A97BFF",csharp:"#178600",cpp:"#f34b7d",c:"#555555",
  html:"#e34c26",css:"#563d7c",scss:"#c6538c",vue:"#41b883",svelte:"#ff3e00",
  dart:"#00B4AB",scala:"#c22d40",shell:"#89e051",sql:"#e38c00",
  json:"#a3a3a3",yaml:"#cb171e",markdown:"#083fa1",toml:"#9c4221",
  unknown:"#6e7681"
};
function getRiskColors(){const s=getComputedStyle(document.documentElement);
  return{low:s.getPropertyValue("--success").trim(),med:s.getPropertyValue("--warning").trim(),high:s.getPropertyValue("--danger").trim()}}
function riskLevel(s){return s>=0.6?"high":s>=0.3?"med":"low"}
function riskColor(s){return getRiskColors()[riskLevel(s)]}

// =====================================================================
// STATE
// =====================================================================
let currentLayout="force",currentView="all",colorMode="language",selectedId=null,selectedAuthor=null;
let displayMode="readable"; // overview | readable | focus | presentation | spacious
let showPaths=false;
let currentZoom=1;
let width,height;
let flowStep=0,flowPlaying=false,flowTimer=null;
let focusedNodeId=null,focusMode="local"; // local | deps | reverse | impact | flow
let manualLayoutActive=false;
const nodeNotes=new Map(); // nodeId -> string
let noteG=null;
const maxDepth=d3.max(DATA.nodes,d=>d.depth)||0;

// =====================================================================
// LARGE-GRAPH PERFORMANCE
// =====================================================================
const LARGE_THRESHOLD=(DATA.meta&&DATA.meta.nodeCount)||DATA.nodes.length;
const IS_LARGE=LARGE_THRESHOLD>200;
let perfMode=IS_LARGE?"fast":"quality"; // fast | quality
let collapsedGroups=new Set(); // group IDs that are currently collapsed (showing cluster node)
let expandedGroups=new Set();  // groups the user explicitly expanded
let allNodesData=DATA.nodes;   // original full node set
let activeNodes=[];             // currently visible nodes (may be subset)
let activeLinks=[];
let clusterNodes=[];            // virtual cluster nodes for collapsed groups

// Compute which groups should start collapsed
function initCollapsedState(){
  if(!IS_LARGE||perfMode==="quality"){collapsedGroups.clear();return}
  // Collapse all groups except small ones (<=5 nodes)
  const groupCounts=new Map();
  allNodesData.forEach(n=>{groupCounts.set(n.group,(groupCounts.get(n.group)||0)+1)});
  groupCounts.forEach((count,gid)=>{
    if(count>5&&!expandedGroups.has(gid))collapsedGroups.add(gid);
  });
}
// Build the active node/link set based on collapsed state
function computeActiveGraph(){
  if(!collapsedGroups.size){
    activeNodes=allNodesData.map(d=>({...d,_hidden:false,_dimmed:false,_targetX:0,_targetY:0,_isCluster:false}));
    activeLinks=DATA.links.map(d=>({...d}));
    clusterNodes=[];
    return;
  }
  const fileNodes=[];const clMap=new Map();
  allNodesData.forEach(n=>{
    if(collapsedGroups.has(n.group)){
      if(!clMap.has(n.group)){
        // Aggregate cluster node
        const members=allNodesData.filter(m=>m.group===n.group);
        const avgDepth=Math.round(members.reduce((s,m)=>s+m.depth,0)/members.length);
        const totalLines=members.reduce((s,m)=>s+(m.lineCount||0),0);
        const maxRisk=Math.max(...members.map(m=>m.riskScore||0));
        const topLang=d3.rollups(members,v=>v.length,d=>d.language).sort((a,b)=>b[1]-a[1])[0];
        clMap.set(n.group,{
          id:"__cluster__"+n.group,label:n.group.split("/").pop()||n.group,
          group:n.group,language:topLang?topLang[0]:"unknown",lineCount:totalLines,
          fanIn:0,fanOut:0,centrality:0,churn:0,owner:"-",totalCommits:0,
          lastModified:"-",contributors:members.length,contribList:[],
          depth:avgDepth,riskScore:maxRisk,isEntry:false,
          _hidden:false,_dimmed:false,_targetX:0,_targetY:0,
          _isCluster:true,_memberCount:members.length,_memberIds:members.map(m=>m.id)
        });
      }
    } else {
      fileNodes.push({...n,_hidden:false,_dimmed:false,_targetX:0,_targetY:0,_isCluster:false});
    }
  });
  clusterNodes=[...clMap.values()];
  activeNodes=[...fileNodes,...clusterNodes];

  // Remap links — if either end is in a collapsed group, point to cluster node
  const nodeIdToActive=new Map();
  allNodesData.forEach(n=>{
    if(collapsedGroups.has(n.group)){nodeIdToActive.set(n.id,"__cluster__"+n.group)}
    else{nodeIdToActive.set(n.id,n.id)}
  });
  const linkSet=new Set();
  activeLinks=[];
  DATA.links.forEach(l=>{
    const s=nodeIdToActive.get(l.source)||l.source;
    const t=nodeIdToActive.get(l.target)||l.target;
    if(s===t)return; // skip internal cluster links
    const key=s+">>"+t;
    if(!linkSet.has(key)){linkSet.add(key);activeLinks.push({source:s,target:t,type:l.type})}
  });
}
function expandGroup(gid){
  collapsedGroups.delete(gid);expandedGroups.add(gid);
  rebuildGraph();
}
function collapseGroup(gid){
  collapsedGroups.add(gid);expandedGroups.delete(gid);
  rebuildGraph();
}
function expandAllGroups(){
  collapsedGroups.clear();DATA.groups.forEach(g=>expandedGroups.add(g));
  rebuildGraph();
}
function collapseAllGroups(){
  expandedGroups.clear();initCollapsedState();
  rebuildGraph();
}

// Initialize
initCollapsedState();
computeActiveGraph();

// =====================================================================
// D3 SETUP
// =====================================================================
const svg=d3.select("#graph-svg"),container=document.getElementById("graph-container"),tooltip=d3.select("#tooltip");
function updateDimensions(){width=container.clientWidth;height=container.clientHeight}
updateDimensions();
const defs=svg.append("defs");
function addArrow(id,color){defs.append("marker").attr("id",id).attr("viewBox","0 -5 10 10").attr("refX",22).attr("refY",0)
  .attr("markerWidth",5).attr("markerHeight",5).attr("orient","auto").append("path").attr("d","M0,-4L10,0L0,4").attr("fill",color)}
const cs=getComputedStyle(document.documentElement);
function cssVar(v){return cs.getPropertyValue(v).trim()}
addArrow("arrow",cssVar("--border"));addArrow("arrow-hl",cssVar("--highlight"));addArrow("arrow-fwd",cssVar("--accent"));addArrow("arrow-rev",cssVar("--danger"));addArrow("arrow-flow",cssVar("--success"));
const gRoot=svg.append("g"),zoom=d3.zoom().scaleExtent([.04,10]).on("zoom",e=>{
  gRoot.attr("transform",e.transform);currentZoom=e.transform.k;updateLabelVisibility();buildMinimap()});
svg.call(zoom);
const hullG=gRoot.append("g"),linkG=gRoot.append("g"),nodeG=gRoot.append("g"),labelG=gRoot.append("g"),glabelG=gRoot.append("g"),ringG=gRoot.append("g"),entryG=gRoot.append("g"),noteGContainer=gRoot.append("g");

// =====================================================================
// BUILD DATA
// =====================================================================
let nodes=activeNodes;
let links=activeLinks;
let nodeById=new Map(nodes.map(n=>[n.id,n]));
links=links.filter(l=>nodeById.has(l.source)&&nodeById.has(l.target));
const groupColorScale=d3.scaleOrdinal(d3.schemeTableau10).domain(DATA.groups);

// Adaptive simulation parameters based on graph size
function simParams(){
  const n=nodes.length;
  if(n>500)return{linkDist:400,charge:-1200,distMax:2000,collIter:2,alpha:.8,velDecay:.55};
  if(n>200)return{linkDist:320,charge:-1000,distMax:1600,collIter:3,alpha:.9,velDecay:.45};
  return{linkDist:280,charge:-800,distMax:1200,collIter:4,alpha:1,velDecay:.4};
}
function modeSpacing(){return displayMode==="spacious"?4.0:displayMode==="presentation"?2.5:displayMode==="overview"?0.5:1.5}
function labelCollisionR(d){
  const base=nodeR(d);
  if(d._isCluster)return base+40; // cluster nodes need more space
  if(displayMode==="overview")return base+4;
  if(displayMode==="spacious"){const lblLen=showPaths?d.id.length:d.label.length;return base+Math.min(lblLen*4,120)+20}
  if(displayMode==="focus")return base+12;
  const lblLen=showPaths?d.id.length:d.label.length;
  const textW=Math.min(lblLen*3.5,90);
  return displayMode==="presentation"?base+textW+16:base+textW*0.6+10;
}

const sp0=simParams();
const sim=d3.forceSimulation(nodes)
  .velocityDecay(sp0.velDecay)
  .force("link",d3.forceLink(links).id(d=>d.id).distance(sp0.linkDist).strength(.12))
  .force("charge",d3.forceManyBody().strength(sp0.charge).distanceMax(sp0.distMax))
  .force("center",d3.forceCenter(width/2,height/2))
  .force("collision",d3.forceCollide().radius(d=>labelCollisionR(d)*modeSpacing()).iterations(sp0.collIter))
  .force("x",d3.forceX(width/2).strength(.025)).force("y",d3.forceY(height/2).strength(.025));

function nodeR(d){
  if(d._isCluster)return Math.max(14,Math.min(40,Math.sqrt(d._memberCount||10)*3));
  return Math.max(5,Math.min(22,Math.sqrt(d.lineCount||10)*1.3));
}
function nodeColor(d){
  if(colorMode==="language")return LANG_COLORS[d.language]||LANG_COLORS.unknown;
  if(colorMode==="group")return groupColorScale(d.group);
  if(colorMode==="churn"){const t=Math.min(d.churn/Math.max(1,d3.max(nodes,n=>n.churn)),1);return d3.interpolateYlOrRd(t*.8+.1)}
  if(colorMode==="risk")return riskColor(d.riskScore);
  if(colorMode==="contributors"){const t=Math.min(d.contributors/Math.max(1,d3.max(nodes,n=>n.contributors)),1);return d3.interpolateYlGnBu(t*.8+.15)}
  return cssVar("--text3")||"#6e7681";
}

const dragBehavior=d3.drag()
  .on("start",(e,d)=>{if(!e.active&&!manualLayoutActive)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y})
  .on("drag",(e,d)=>{d.fx=e.x;d.fy=e.y;if(manualLayoutActive){d.x=e.x;d.y=e.y;manualTick()}})
  .on("end",(e,d)=>{if(manualLayoutActive)return;if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null});

let linkEls=linkG.selectAll("line").data(links).join("line").attr("class","link").attr("stroke-width",1);
let circleEls=nodeG.selectAll("circle").data(nodes,d=>d.id).join("circle")
  .attr("class",d=>d._isCluster?"cluster-node":"node-circle").attr("r",d=>nodeR(d)).attr("fill",d=>nodeColor(d))
  .attr("rx",d=>d._isCluster?4:0)
  .call(dragBehavior);
function manualTick(){
  linkEls.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  circleEls.attr("cx",d=>d.x).attr("cy",d=>d.y);labelEls.attr("x",d=>d.x).attr("y",d=>d.y);
  drawHulls();drawEntryMarkers();updateNoteIndicators();
}
noteG=noteGContainer;
function labelText(d){
  if(d._isCluster)return d.label+" ("+d._memberCount+")";
  if(displayMode==="overview")return"";
  const raw=showPaths?d.id:d.label;
  if(displayMode==="spacious"){return raw.length>45?raw.slice(0,45)+"\u2026":raw}
  if(displayMode==="presentation"){return raw.length>35?raw.slice(0,35)+"\u2026":raw}
  if(displayMode==="focus"){return raw.length>20?raw.slice(0,20)+"\u2026":raw}
  // Large graphs: stricter zoom gating
  const zoomThresh=IS_LARGE&&perfMode==="fast"?{z3:2.5,z2:1.8,z1:1.0}:{z3:2.0,z2:1.2,z1:0.6};
  const max=currentZoom>zoomThresh.z3?30:currentZoom>zoomThresh.z2?18:currentZoom>zoomThresh.z1?14:0;
  if(max===0)return"";
  return raw.length>max?raw.slice(0,max)+"\u2026":raw;
}
function labelFontSize(){
  if(IS_LARGE&&perfMode==="fast")return"10px";
  return displayMode==="presentation"?"12px":displayMode==="spacious"?"11px":"10px";
}
function shouldShowLabel(d){
  if(d._hidden)return false;
  if(d._isCluster)return true; // always show cluster labels
  if(displayMode==="overview")return false;
  if(focusedNodeId){return !d._dimmed}
  if(d.id===selectedId)return true;
  if(displayMode==="focus"){
    if(!selectedId)return d.isEntry;
    const isNeighbor=links.some(l=>(getLinkId(l,"source")===selectedId&&getLinkId(l,"target")===d.id)||(getLinkId(l,"target")===selectedId&&getLinkId(l,"source")===d.id));
    return isNeighbor;
  }
  if(d._dimmed)return false;
  if(displayMode==="spacious"||displayMode==="presentation")return true;
  // Large graph: only show labels for important/nearby nodes when zoomed out
  if(IS_LARGE&&perfMode==="fast"&&currentZoom<0.8){
    return d.isEntry||d.riskScore>=0.6;
  }
  // readable: zoom-gated
  if(d.isEntry&&currentZoom>=0.3)return true;
  return currentZoom>=0.6;
}
function updateLabelVisibility(){
  labelEls.text(d=>labelText(d)).attr("font-size",labelFontSize())
    .attr("opacity",d=>shouldShowLabel(d)?1:0);
}
let labelEls=labelG.selectAll("text").data(nodes).join("text").attr("class","node-label").attr("dy",d=>nodeR(d)+13).text(d=>labelText(d)).attr("font-size",labelFontSize());

// =====================================================================
// TOOLTIP
// =====================================================================
circleEls.on("mouseover",(e,d)=>{
  if(d._isCluster){
    tooltip.style("opacity",1).html(
      `<div class="tt-title">&#128193; ${d.label}</div>`+
      `<div class="tt-row">${T("group")}: <span>${d.group}</span></div>`+
      `<div class="tt-row">${T("files")}: <span>${d._memberCount}</span></div>`+
      `<div class="tt-row">${T("lines")}: <span>${d.lineCount}</span></div>`+
      `<div class="tt-row">${T("risk")}: <span style="color:${riskColor(d.riskScore)}">${(d.riskScore*100).toFixed(0)}%</span></div>`+
      `<div class="tt-row" style="color:var(--accent)">${T("expandCluster")}</div>`
    );
  } else {
  const fwdN=links.filter(l=>getLinkId(l,"source")===d.id).length;
  const revN=links.filter(l=>getLinkId(l,"target")===d.id).length;
  tooltip.style("opacity",1).html(
    `<div class="tt-title">${d.label}${d.isEntry?" &#9733;":""}</div>`+
    `<div class="tt-row">${T("path")}: <span>${d.id}</span></div>`+
    `<div class="tt-row">${T("group")}: <span>${d.group}</span> &middot; ${T("language")}: <span>${d.language}</span></div>`+
    `<div class="tt-row">${T("lines")}: <span>${d.lineCount}</span> &middot; ${T("depth")}: <span>${d.depth}</span></div>`+
    `<div class="tt-row">${T("fanIn")}: <span>${d.fanIn}</span> &middot; ${T("fanOut")}: <span>${d.fanOut}</span> &middot; ${T("churn")}: <span>${d.churn}</span></div>`+
    `<div class="tt-row">${T("dependsOn")}: <span>${fwdN}</span> &middot; ${T("dependedOnBy")}: <span>${revN}</span></div>`+
    `<div class="tt-row">${T("risk")}: <span style="color:${riskColor(d.riskScore)}">${(d.riskScore*100).toFixed(0)}%</span> &middot; ${T("owner")}: <span>${d.owner}</span></div>`+
    (d.contribList.length?`<div class="tt-row">${T("contributors")}: <span>${d.contribList.map(c=>c.name).join(", ")}</span></div>`:"")
  );}
}).on("mousemove",e=>{const r=container.getBoundingClientRect();
  tooltip.style("left",(e.clientX-r.left+14)+"px").style("top",(e.clientY-r.top-10)+"px");
}).on("mouseout",()=>tooltip.style("opacity",0));

// =====================================================================
// SELECTION
// =====================================================================
circleEls.on("click",(e,d)=>{
  e.stopPropagation();
  // Cluster node: expand the group
  if(d._isCluster){expandGroup(d.group);return}
  selectedId=selectedId===d.id?null:d.id;
  applyView();showDetails(selectedId?d:null);highlightNodeInList(selectedId);if(selectedId)switchTab("details")});
svg.on("click",()=>{selectedId=null;applyView();showDetails(null);highlightNodeInList(null)});
function getLinkId(l,end){const n=l[end];return typeof n==="object"?n.id:n}

function applyView(){
  const sel=selectedId!=null;
  // Focused-node exploration overrides
  if(focusedNodeId){
    applyFocusedNodeView();return;
  }
  if(currentView==="all"||!sel) nodes.forEach(n=>{n._dimmed=false});
  else if(currentView==="neighborhood"&&sel){
    const vis=new Set([selectedId]);
    links.forEach(l=>{if(getLinkId(l,"source")===selectedId)vis.add(getLinkId(l,"target"));if(getLinkId(l,"target")===selectedId)vis.add(getLinkId(l,"source"))});
    nodes.forEach(n=>{n._dimmed=!vis.has(n.id)});
  } else if(currentView==="impact"&&sel){
    const imp=new Set([selectedId]),q=[selectedId];
    while(q.length){const c=q.shift();links.forEach(l=>{const s=getLinkId(l,"source"),t=getLinkId(l,"target");if(t===c&&!imp.has(s)){imp.add(s);q.push(s)}})}
    links.forEach(l=>{if(getLinkId(l,"source")===selectedId)imp.add(getLinkId(l,"target"))});
    nodes.forEach(n=>{n._dimmed=!imp.has(n.id)});
  }
  // Author filter overlay
  if(selectedAuthor){nodes.forEach(n=>{if(!n.contribList.some(c=>c.name===selectedAuthor))n._dimmed=true})}

  circleEls.classed("selected",d=>d.id===selectedId).classed("dimmed",d=>d._dimmed)
    .attr("opacity",d=>d._hidden?0:d._dimmed?.12:1);
  linkEls.attr("class",l=>{if(!sel)return"link";const s=getLinkId(l,"source"),t=getLinkId(l,"target");
    if(s===selectedId)return"link dep-fwd";if(t===selectedId)return"link dep-rev";return"link"})
    .attr("opacity",l=>{const s=getLinkId(l,"source"),t=getLinkId(l,"target");
      const sn=nodeById.get(s),tn=nodeById.get(t);if((sn&&sn._hidden)||(tn&&tn._hidden))return 0;
      if(!sel)return.5;if(s===selectedId||t===selectedId)return 1;return(sn&&sn._dimmed)||(tn&&tn._dimmed)?.04:.3});
  updateLabelVisibility();drawEntryMarkers();
}

// Entry point markers
function drawEntryMarkers(){
  const ep=nodes.filter(d=>d.isEntry&&!d._hidden);
  const sel=entryG.selectAll("rect").data(ep,d=>d.id);
  sel.exit().remove();
  sel.enter().append("rect").attr("class","entry-marker").attr("rx",3).merge(sel)
    .attr("x",d=>d.x-nodeR(d)-4).attr("y",d=>d.y-nodeR(d)-4)
    .attr("width",d=>(nodeR(d)+4)*2).attr("height",d=>(nodeR(d)+4)*2);
}

// =====================================================================
// LAYOUTS
// =====================================================================
function applyLayout(layout){
  currentLayout=layout;updateDimensions();stopFlow();
  document.getElementById("flow-controls").classList.toggle("visible",layout==="flow");
  const mi=document.getElementById("manual-indicator");
  if(layout==="manual"){
    manualLayoutActive=true;
    sim.stop();
    nodes.forEach(d=>{d.fx=d.x;d.fy=d.y});
    mi.classList.add("visible");
    mi.innerHTML=`<span class="mi-dot"></span><span>${T("manualMode")} \u2014 ${T("dragToArrange")}</span>
      <button class="tb-btn" style="margin-left:auto;font-size:10px" id="btn-save-layout">&#128190; ${T("saveLayout")}</button>
      <button class="tb-btn" style="font-size:10px" id="btn-restore-layout">&#128194; ${T("restoreLayout")}</button>
      <button class="tb-btn" style="font-size:10px" id="btn-return-auto">&#8634; ${T("returnToAuto")}</button>`;
    document.getElementById("btn-save-layout").addEventListener("click",saveManualLayout);
    document.getElementById("btn-restore-layout").addEventListener("click",restoreManualLayout);
    document.getElementById("btn-return-auto").addEventListener("click",()=>applyLayout("force"));
    updateToolbar("layout-btns","manual");updateStatsBar();return;
  }
  manualLayoutActive=false;
  mi.classList.remove("visible");
  nodes.forEach(d=>{d.fx=null;d.fy=null});
  const sp=modeSpacing();const sparams=simParams();
  sim.force("collision",d3.forceCollide().radius(d=>labelCollisionR(d)*sp).iterations(sparams.collIter));
  if(layout==="force"){
    sim.force("link",d3.forceLink(links).id(d=>d.id).distance(sparams.linkDist*sp).strength(.12));
    sim.force("charge",d3.forceManyBody().strength(sparams.charge*sp).distanceMax(sparams.distMax*sp));
    sim.force("center",d3.forceCenter(width/2,height/2));
    sim.force("x",d3.forceX(width/2).strength(.025)).force("y",d3.forceY(height/2).strength(.025));
    sim.force("posX",null).force("posY",null);
  } else {
    if(layout==="hierarchy")computeHierarchy();
    else if(layout==="radial")computeRadial();
    else if(layout==="cluster")computeCluster();
    else if(layout==="flow")computeFlow();
    sim.force("link",d3.forceLink(links).id(d=>d.id).distance(80*sp).strength(.02));
    sim.force("charge",d3.forceManyBody().strength(-100*sp));
    sim.force("center",null);sim.force("x",null).force("y",null);
    sim.force("posX",d3.forceX(d=>d._targetX).strength(.7));
    sim.force("posY",d3.forceY(d=>d._targetY).strength(.7));
  }
  sim.alpha(1).restart();updateToolbar("layout-btns",layout);updateStatsBar();updateLabelVisibility();
}
function computeHierarchy(){
  const sp=modeSpacing();const maxD=d3.max(nodes,d=>d.depth)||0,lH=(height*sp*1.2)/(maxD+2);
  const byL=d3.group(nodes,d=>d.depth);
  byL.forEach((lv,dep)=>{lv.sort((a,b)=>a.group.localeCompare(b.group)||a.label.localeCompare(b.label));
    const xS=(width*sp)/(lv.length+1);lv.forEach((n,i)=>{n._targetX=(i+1)*xS;n._targetY=(dep+1)*lH})});
}
function computeRadial(){
  const sp=modeSpacing();
  const sorted=[...nodes].sort((a,b)=>(b.fanIn+b.fanOut+b.centrality*10)-(a.fanIn+a.fanOut+a.centrality*10));
  const cx=width/2,cy=height/2,maxR=Math.min(width,height)*.42*sp;
  if(!sorted.length)return;if(sorted.length===1){sorted[0]._targetX=cx;sorted[0]._targetY=cy;return}
  sorted[0]._targetX=cx;sorted[0]._targetY=cy;
  const rings=Math.max(1,Math.ceil(Math.sqrt(sorted.length/4)));let idx=1;
  for(let r=1;r<=rings&&idx<sorted.length;r++){const radius=(r/rings)*maxR;
    const cap=Math.min(Math.max(6,Math.floor(2*Math.PI*radius/50)),sorted.length-idx);
    for(let j=0;j<cap&&idx<sorted.length;j++,idx++){const a=(j/cap)*2*Math.PI-Math.PI/2;
      sorted[idx]._targetX=cx+radius*Math.cos(a);sorted[idx]._targetY=cy+radius*Math.sin(a)}}
}
function computeCluster(){
  const sp=modeSpacing();
  const uG=[...new Set(nodes.map(n=>n.group))],cols=Math.max(1,Math.ceil(Math.sqrt(uG.length))),
    rows=Math.max(1,Math.ceil(uG.length/cols)),cW=(width*sp)/(cols+1),cH=(height*sp)/(rows+1);
  const ctrs=new Map();uG.forEach((g,i)=>{ctrs.set(g,{x:(i%cols+1)*cW,y:(Math.floor(i/cols)+1)*cH})});
  const byG=d3.group(nodes,d=>d.group);
  byG.forEach((gn,gid)=>{const c=ctrs.get(gid),r=Math.min(cW,cH)*.32*sp;
    gn.forEach((n,i)=>{const a=(i/gn.length)*2*Math.PI;n._targetX=c.x+r*Math.cos(a);n._targetY=c.y+r*Math.sin(a)})});
}
function computeFlow(){
  const sp=modeSpacing();const maxD=d3.max(nodes,d=>d.depth)||0;
  const colW=(width*sp)/(maxD+2);
  const byD=d3.group(nodes,d=>d.depth);
  byD.forEach((lv,dep)=>{lv.sort((a,b)=>a.group.localeCompare(b.group)||a.label.localeCompare(b.label));
    const rowSp=Math.max(40*sp,Math.min(80*sp,height*sp/(lv.length+2)));
    const totalH=lv.length*rowSp;const startY=(height-totalH)/2;
    lv.forEach((n,i)=>{n._targetX=(dep+1)*colW;n._targetY=startY+i*rowSp})});
  flowStep=0;updateFlowVisuals();
}

// =====================================================================
// FLOW ANIMATION
// =====================================================================
function updateFlowVisuals(){
  if(currentLayout!=="flow")return;
  document.getElementById("flow-step").textContent=`${T("step")} ${flowStep} ${T("of")} ${maxDepth}`;
  circleEls.classed("flow-future",d=>d.depth>flowStep).classed("flow-current",d=>d.depth===flowStep)
    .attr("opacity",d=>d._hidden?0:d.depth<=flowStep?1:.08);
  // Labels: only current step + previous step to prevent overlap
  labelEls.text(d=>labelText(d))
    .attr("opacity",d=>{
      if(d._hidden)return 0;
      if(d.depth===flowStep)return 1;
      if(d.depth===flowStep-1)return 0.6;
      return 0;
    });
  linkEls.attr("class",l=>{const sd=nodeById.get(getLinkId(l,"source")),td=nodeById.get(getLinkId(l,"target"));
    if(sd&&td&&sd.depth<flowStep&&td.depth<=flowStep)return"link flow-active";
    if(sd&&td&&sd.depth===flowStep-1&&td.depth===flowStep)return"link flow-active";return"link"})
    .attr("opacity",l=>{const sd=nodeById.get(getLinkId(l,"source")),td=nodeById.get(getLinkId(l,"target"));
      return(sd&&sd.depth<=flowStep&&td&&td.depth<=flowStep)?.7:.05});
}
function flowNext(){if(flowStep<=maxDepth){flowStep++;updateFlowVisuals()}}
function flowPrev(){if(flowStep>0){flowStep--;updateFlowVisuals()}}
function flowPlayPause(){
  if(flowPlaying){flowPlaying=false;clearInterval(flowTimer);flowTimer=null;
    document.getElementById("fc-play").classList.remove("playing");document.getElementById("fc-play").innerHTML="&#9654;";
  }else{flowPlaying=true;document.getElementById("fc-play").classList.add("playing");document.getElementById("fc-play").innerHTML="&#9646;&#9646;";
    const spd=parseInt(document.getElementById("flow-speed").value)||800;
    flowTimer=setInterval(()=>{if(flowStep>maxDepth){flowPlaying=false;clearInterval(flowTimer);flowTimer=null;
      document.getElementById("fc-play").classList.remove("playing");document.getElementById("fc-play").innerHTML="&#9654;";return}flowNext()},spd)}
}
function stopFlow(){flowPlaying=false;if(flowTimer){clearInterval(flowTimer);flowTimer=null}flowStep=0;
  document.getElementById("fc-play").classList.remove("playing");document.getElementById("fc-play").innerHTML="&#9654;";
  circleEls.classed("flow-future",false).classed("flow-current",false);
  linkEls.classed("flow-active",false)}
document.getElementById("fc-play").addEventListener("click",flowPlayPause);
document.getElementById("fc-next").addEventListener("click",flowNext);
document.getElementById("fc-prev").addEventListener("click",flowPrev);
document.getElementById("fc-reset").addEventListener("click",()=>{stopFlow();if(currentLayout==="flow"){flowStep=0;updateFlowVisuals()}});
document.getElementById("flow-speed").addEventListener("change",()=>{if(flowPlaying){flowPlayPause();flowPlayPause()}});

// =====================================================================
// HULLS & GROUP LABELS
// =====================================================================
function drawHulls(){
  const grouped=d3.group(nodes.filter(n=>!n._hidden),d=>d.group);
  const hullData=[];
  grouped.forEach((pts,key)=>{if(pts.length<3)return;const hull=d3.polygonHull(pts.map(p=>[p.x,p.y]));if(hull)hullData.push({key,hull,pts})});
  const sel=hullG.selectAll("path").data(hullData,d=>d.key);sel.exit().remove();
  sel.enter().append("path").attr("class","group-hull").merge(sel)
    .attr("d",d=>{const cx=d3.mean(d.pts,p=>p.x),cy=d3.mean(d.pts,p=>p.y);
      return"M"+d.hull.map(p=>{const dx=p[0]-cx,dy=p[1]-cy,dist=Math.sqrt(dx*dx+dy*dy),f=dist>0?(dist+18)/dist:1;return[cx+dx*f,cy+dy*f]}).join("L")+"Z"})
    .attr("fill",d=>groupColorScale(d.key)).attr("stroke",d=>groupColorScale(d.key));
  const lblData=[];grouped.forEach((pts,key)=>{if(pts.length<1||key==="(root)")return;lblData.push({key,x:d3.mean(pts,p=>p.x),y:d3.min(pts,p=>p.y)-20})});
  const ls=glabelG.selectAll("text").data(lblData,d=>d.key);ls.exit().remove();
  ls.enter().append("text").attr("class","group-label").merge(ls).attr("x",d=>d.x).attr("y",d=>d.y).text(d=>d.key);
}
function drawHotspotRings(){
  if(colorMode!=="risk"){ringG.selectAll("circle").remove();return}
  const hot=nodes.filter(d=>d.riskScore>=.6&&!d._hidden);
  const sel=ringG.selectAll("circle").data(hot,d=>d.id);sel.exit().remove();
  sel.enter().append("circle").attr("class","hotspot-ring").merge(sel).attr("cx",d=>d.x).attr("cy",d=>d.y).attr("r",d=>nodeR(d)+6);
}
// Throttled tick for large graphs — skip expensive operations during rapid simulation
let tickCount=0;
const tickSkip=IS_LARGE?3:1; // only do full DOM update every Nth tick for large graphs
sim.on("tick",()=>{
  tickCount++;
  // Always update node/link positions (cheap)
  linkEls.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  circleEls.attr("cx",d=>d.x).attr("cy",d=>d.y);labelEls.attr("x",d=>d.x).attr("y",d=>d.y);
  // Expensive ops: throttle for large graphs
  if(tickCount%tickSkip===0){
    drawHulls();drawHotspotRings();drawEntryMarkers();updateNoteIndicators();
    if(currentLayout==="flow")updateFlowVisuals();
  }
  if(sim.alpha()<0.05)buildMinimap();
});

// =====================================================================
// REBUILD GRAPH (for expand/collapse)
// =====================================================================
function rebuildGraph(){
  computeActiveGraph();
  nodes=activeNodes;links=activeLinks;
  nodeById=new Map(nodes.map(n=>[n.id,n]));
  links=links.filter(l=>nodeById.has(l.source)||nodeById.has(typeof l.source==="object"?l.source.id:l.source));

  // Rejoin data
  linkEls=linkG.selectAll("line").data(links,d=>(typeof d.source==="object"?d.source.id:d.source)+">>"+(typeof d.target==="object"?d.target.id:d.target));
  linkEls.exit().remove();
  linkEls=linkEls.enter().append("line").attr("class","link").attr("stroke-width",1).merge(linkEls);

  circleEls=nodeG.selectAll("circle").data(nodes,d=>d.id);
  circleEls.exit().remove();
  circleEls=circleEls.enter().append("circle").merge(circleEls)
    .attr("class",d=>d._isCluster?"cluster-node":"node-circle")
    .attr("r",d=>nodeR(d)).attr("fill",d=>nodeColor(d))
    .call(dragBehavior);
  // Re-bind tooltip and click
  circleEls.on("mouseover",(e,d)=>{
    if(d._isCluster){
      tooltip.style("opacity",1).html(
        `<div class="tt-title">&#128193; ${d.label}</div>`+
        `<div class="tt-row">${T("group")}: <span>${d.group}</span></div>`+
        `<div class="tt-row">${T("files")}: <span>${d._memberCount}</span></div>`+
        `<div class="tt-row">${T("expandCluster")}</div>`);
    } else {
      const fwdN=links.filter(l=>getLinkId(l,"source")===d.id).length;
      const revN=links.filter(l=>getLinkId(l,"target")===d.id).length;
      tooltip.style("opacity",1).html(
        `<div class="tt-title">${d.label}${d.isEntry?" &#9733;":""}</div>`+
        `<div class="tt-row">${T("path")}: <span>${d.id}</span></div>`+
        `<div class="tt-row">${T("group")}: <span>${d.group}</span> &middot; ${T("language")}: <span>${d.language}</span></div>`+
        `<div class="tt-row">${T("risk")}: <span style="color:${riskColor(d.riskScore)}">${(d.riskScore*100).toFixed(0)}%</span></div>`);
    }
  }).on("mousemove",e=>{const r=container.getBoundingClientRect();
    tooltip.style("left",(e.clientX-r.left+14)+"px").style("top",(e.clientY-r.top-10)+"px");
  }).on("mouseout",()=>tooltip.style("opacity",0));
  circleEls.on("click",(e,d)=>{
    e.stopPropagation();
    if(d._isCluster){expandGroup(d.group);return}
    selectedId=selectedId===d.id?null:d.id;
    applyView();showDetails(selectedId?d:null);highlightNodeInList(selectedId);if(selectedId)switchTab("details")});

  labelEls=labelG.selectAll("text").data(nodes,d=>d.id);
  labelEls.exit().remove();
  labelEls=labelEls.enter().append("text").attr("class","node-label").merge(labelEls)
    .attr("dy",d=>nodeR(d)+13).text(d=>labelText(d)).attr("font-size",labelFontSize());

  // Update simulation
  const sp=simParams();
  sim.nodes(nodes);
  sim.force("link",d3.forceLink(links).id(d=>d.id).distance(sp.linkDist).strength(.12));
  sim.force("charge",d3.forceManyBody().strength(sp.charge).distanceMax(sp.distMax));
  sim.force("collision",d3.forceCollide().radius(d=>labelCollisionR(d)*modeSpacing()).iterations(sp.collIter));
  sim.alpha(sp.alpha).restart();

  updatePerfBanner();updateStatsBar();updateLabelVisibility();buildUI();
}

// =====================================================================
// FILTERS
// =====================================================================
function applyFilters(){
  const gf=document.getElementById("filter-group").value,lf=document.getElementById("filter-lang").value,
    rf=document.getElementById("filter-risk").value,af=document.getElementById("filter-author")?document.getElementById("filter-author").value:"__all__",
    sq=document.getElementById("search").value.toLowerCase();
  nodes.forEach(n=>{let show=true;
    if(gf!=="__all__"&&n.group!==gf)show=false;if(lf!=="__all__"&&n.language!==lf)show=false;
    if(rf==="high"&&n.riskScore<.6)show=false;if(rf==="medium"&&(n.riskScore<.3||n.riskScore>=.6))show=false;
    if(rf==="low"&&n.riskScore>=.3)show=false;
    if(af!=="__all__"&&!n.contribList.some(c=>c.name===af))show=false;
    if(sq&&!n.id.toLowerCase().includes(sq)&&!n.label.toLowerCase().includes(sq))show=false;n._hidden=!show});
  circleEls.attr("display",d=>d._hidden?"none":null);labelEls.attr("display",d=>d._hidden?"none":null);
  linkEls.attr("display",l=>{const s=nodeById.get(getLinkId(l,"source")),t=nodeById.get(getLinkId(l,"target"));return(s&&s._hidden)||(t&&t._hidden)?"none":null});
  applyView();updateNodeList();updateStatsBar();
}

// =====================================================================
// UI BUILDERS — called on init and on language change
// =====================================================================
function buildUI(){
  // Translate flow speed labels
  const fsSlow=document.getElementById("fs-slow"),fsNorm=document.getElementById("fs-normal"),fsFast=document.getElementById("fs-fast");
  if(fsSlow)fsSlow.textContent=T("slow");if(fsNorm)fsNorm.textContent=T("normal");if(fsFast)fsFast.textContent=T("fast");
  // Summary cards
  document.getElementById("summary-cards").innerHTML=
    `<div class="summary-card"><div class="val">${nodes.length}</div><div class="lbl">${T("files")}</div></div>`+
    `<div class="summary-card"><div class="val">${links.length}</div><div class="lbl">${T("edges")}</div></div>`+
    `<div class="summary-card"><div class="val">${DATA.groups.length}</div><div class="lbl">${T("groups")}</div></div>`;
  // Tab bar
  document.getElementById("tab-bar").innerHTML=
    `<button class="tab active" data-tab="explore">&#128269; ${T("explore")}</button>`+
    `<button class="tab" data-tab="details">&#128203; ${T("details")}</button>`+
    `<button class="tab" data-tab="hotspots">&#9888;&#65039; ${T("hotspots")}</button>`+
    `<button class="tab" data-tab="authors">&#128101; ${T("authors")}</button>`;
  document.querySelectorAll(".tab-bar button").forEach(btn=>btn.addEventListener("click",()=>switchTab(btn.dataset.tab)));
  // Explore tab
  buildExploreTab();
  // Details placeholder
  document.getElementById("detail-placeholder").textContent=T("clickToInspect");
  // Hotspots
  buildHotspots();
  // Authors
  buildAuthorsTab();
  // Toolbar
  buildToolbar();
  // Legend
  buildLegend();
  // Stats
  updateStatsBar();
  // About
  buildAboutFooter();
}

function buildExploreTab(){
  const el=document.getElementById("tab-explore");
  el.innerHTML=`<div class="section-label">${T("search")}</div>
    <input id="search" type="text" placeholder="${T("filterFiles")}">
    <div class="filter-row">
      <select id="filter-group"><option value="__all__">${T("allGroups")}</option></select>
      <select id="filter-lang"><option value="__all__">${T("allLangs")}</option></select>
    </div>
    <div class="filter-row">
      <select id="filter-risk"><option value="__all__">${T("allRisk")}</option>
        <option value="high">${T("highRisk")}</option><option value="medium">${T("medRisk")}</option><option value="low">${T("lowRisk")}</option></select>
      <select id="filter-author"><option value="__all__">${T("allAuthors")}</option></select>
    </div>
    <div class="sort-row"><label>${T("sort")}:</label>
      <select id="sort-by"><option value="name">${T("name")}</option><option value="fanIn">${T("fanIn")} &#8595;</option>
        <option value="fanOut">${T("fanOut")} &#8595;</option><option value="churn">${T("churn")} &#8595;</option>
        <option value="riskScore">${T("risk")} &#8595;</option><option value="lineCount">${T("lines")} &#8595;</option>
        <option value="contributors">${T("contributors")} &#8595;</option></select></div>
    <div class="sort-row"><label><input type="checkbox" id="chk-paths"> ${T("showPaths")}</label></div>
    <div id="node-list"></div>`;
  const gf=document.getElementById("filter-group");DATA.groups.forEach(g=>{const o=document.createElement("option");o.value=g;o.textContent=g;gf.appendChild(o)});
  const lf=document.getElementById("filter-lang");DATA.languages.forEach(l=>{const o=document.createElement("option");o.value=l;o.textContent=l;lf.appendChild(o)});
  const af=document.getElementById("filter-author");(DATA.contributors||[]).forEach(c=>{const o=document.createElement("option");o.value=c.name;o.textContent=c.name;af.appendChild(o)});
  document.getElementById("search").addEventListener("input",applyFilters);
  document.getElementById("filter-group").addEventListener("change",applyFilters);
  document.getElementById("filter-lang").addEventListener("change",applyFilters);
  document.getElementById("filter-risk").addEventListener("change",applyFilters);
  document.getElementById("filter-author").addEventListener("change",applyFilters);
  document.getElementById("sort-by").addEventListener("change",updateNodeList);
// Also rebind collision on showPaths toggle
  document.getElementById("chk-paths").addEventListener("change",e=>{
    showPaths=e.target.checked;
    sim.force("collision",d3.forceCollide().radius(d=>labelCollisionR(d)*modeSpacing()).iterations(4));
    sim.alpha(.3).restart();updateLabelVisibility();updateNodeList();
  });
  updateNodeList();
}

function buildToolbar(){
  const sortedNodes=[...nodes].filter(d=>!d._isCluster).sort((a,b)=>a.label.localeCompare(b.label));
  const nodeOpts=sortedNodes.map(n=>`<option value="${n.id}">${n.label} (${n.group})</option>`).join("");
  const perfToggle=IS_LARGE?`<div class="tb-sep"></div>
    <span class="tb-label">${T("performance")}</span>
    <div class="tb-group" id="perf-btns">
      <button class="${perfMode==="fast"?"active":""}" data-pm="fast">${T("perfFast")}</button>
      <button class="${perfMode==="quality"?"active":""}" data-pm="quality">${T("perfQuality")}</button>
    </div>`:"";
  document.getElementById("toolbar").innerHTML=
    `<span class="tb-label">${T("layout")}</span>
    <div class="tb-group" id="layout-btns">
      <button class="active" data-layout="force">${T("force")}</button>
      <button data-layout="hierarchy">${T("tree")}</button>
      <button data-layout="radial">${T("radial")}</button>
      <button data-layout="cluster">${T("cluster")}</button>
      <button data-layout="flow">${T("flow")}</button>
      <button data-layout="manual">${T("manualLayout")}</button>
    </div><div class="tb-sep"></div>
    <span class="tb-label">${T("view")}</span>
    <div class="tb-group" id="view-btns">
      <button class="active" data-view="all">${T("all")}</button>
      <button data-view="neighborhood">${T("neighborhood")}</button>
      <button data-view="impact">${T("impact")}</button>
    </div><div class="tb-sep"></div>
    <span class="tb-label">${T("display")}</span>
    <div class="tb-group" id="display-btns">
      <button data-dm="overview">${T("overview")}</button>
      <button class="active" data-dm="readable">${T("readable")}</button>
      <button data-dm="focus">${T("focus")}</button>
      <button data-dm="presentation">${T("presentation")}</button>
      <button data-dm="spacious">${T("spacious")}</button>
    </div><div class="tb-sep"></div>
    <span class="tb-label">${T("color")}</span>
    <select class="tb-select" id="color-mode">
      <option value="language">${T("language")}</option><option value="group">${T("group")}</option>
      <option value="churn">${T("churn")}</option><option value="risk">${T("riskScore")}</option>
      <option value="contributors">${T("contributors")}</option></select>
    <div class="tb-sep"></div>
    <span class="tb-label">${T("focusedNode")}</span>
    <select class="tb-select" id="node-focus-select" style="max-width:200px">
      <option value="">${T("selectANode")}</option>${nodeOpts}</select>
    ${perfToggle}
    <div class="tb-sep"></div>
    <button class="tb-btn" id="btn-reset">&#8634; ${T("reset")}</button>`;
  document.querySelectorAll("#layout-btns button").forEach(b=>b.addEventListener("click",()=>applyLayout(b.dataset.layout)));
  document.querySelectorAll("#view-btns button").forEach(b=>b.addEventListener("click",()=>{currentView=b.dataset.view;updateToolbar("view-btns",currentView);applyView()}));
  document.querySelectorAll("#display-btns button").forEach(b=>b.addEventListener("click",()=>applyDisplayMode(b.dataset.dm)));
  document.getElementById("color-mode").addEventListener("change",e=>{colorMode=e.target.value;circleEls.attr("fill",d=>nodeColor(d));drawHotspotRings();buildLegend();updateNodeList()});
  document.getElementById("node-focus-select").addEventListener("change",e=>{const nid=e.target.value;if(nid){activateFocusedNode(nid)}else{deactivateFocusedNode()}});
  if(IS_LARGE){
    document.querySelectorAll("#perf-btns button").forEach(b=>b.addEventListener("click",()=>{
      perfMode=b.dataset.pm;
      document.querySelectorAll("#perf-btns button").forEach(x=>x.classList.toggle("active",x.dataset.pm===perfMode));
      if(perfMode==="fast"){initCollapsedState();rebuildGraph()}
      else{expandAllGroups()}
    }));
  }
  document.getElementById("btn-reset").addEventListener("click",resetAll);
  updateToolbar("layout-btns",currentLayout);updateToolbar("view-btns",currentView);updateDisplayBtns();
}

function applyDisplayMode(mode){
  displayMode=mode;
  const svgEl=document.getElementById("graph-svg");
  svgEl.classList.remove("mode-overview","mode-readable","mode-focus","mode-presentation","mode-spacious");
  svgEl.classList.add("mode-"+mode);
  updateDisplayBtns();
  sim.force("collision",d3.forceCollide().radius(d=>labelCollisionR(d)*modeSpacing()).iterations(4));
  applyLayout(currentLayout);
  updateLabelVisibility();
}
function updateDisplayBtns(){
  document.querySelectorAll("#display-btns button").forEach(b=>b.classList.toggle("active",b.dataset.dm===displayMode));
}

function resetAll(){
  selectedId=null;selectedAuthor=null;currentView="all";focusedNodeId=null;focusMode="local";stopFlow();
  manualLayoutActive=false;
  document.getElementById("manual-indicator").classList.remove("visible");
  nodes.forEach(d=>{d.fx=null;d.fy=null});
  document.getElementById("focus-bar").classList.remove("visible");
  document.getElementById("search").value="";
  document.getElementById("filter-group").value="__all__";document.getElementById("filter-lang").value="__all__";
  document.getElementById("filter-risk").value="__all__";
  const af=document.getElementById("filter-author");if(af)af.value="__all__";
  applyFilters();applyView();showDetails(null);highlightNodeInList(null);highlightAuthor(null);
  updateToolbar("view-btns","all");svg.transition().duration(400).call(zoom.transform,d3.zoomIdentity);
}

function updateToolbar(gid,val){
  const attrMap={"layout-btns":"layout","view-btns":"view"};
  const attr=attrMap[gid]||"view";
  document.querySelectorAll(`#${gid} button`).forEach(b=>b.classList.toggle("active",b.dataset[attr]===val));
}

// =====================================================================
// TABS
// =====================================================================
function switchTab(tab){
  document.querySelectorAll(".tab-bar button").forEach(b=>b.classList.toggle("active",b.dataset.tab===tab));
  document.querySelectorAll(".tab-content").forEach(c=>c.classList.toggle("active",c.id==="tab-"+tab));
}

// =====================================================================
// NODE LIST
// =====================================================================
function updateNodeList(){
  const sortKey=document.getElementById("sort-by")?document.getElementById("sort-by").value:"name";
  const visible=nodes.filter(n=>!n._hidden);
  if(sortKey==="name")visible.sort((a,b)=>a.label.localeCompare(b.label));else visible.sort((a,b)=>(b[sortKey]||0)-(a[sortKey]||0));
  const c=document.getElementById("node-list");if(!c)return;
  c.innerHTML=visible.map(n=>{const mv=sortKey==="name"?"":sortKey==="riskScore"?(n.riskScore*100).toFixed(0)+"%":n[sortKey];
    const displayName=showPaths?n.id:n.label;
    return`<div class="node-item${n.id===selectedId?" active":""}" data-id="${n.id}">
      <div class="dot" style="background:${nodeColor(n)}"></div><div class="name" title="${n.id}">${displayName}${n.isEntry?" &#9733;":""}</div><div class="metric">${mv}</div></div>`}).join("");
  c.querySelectorAll(".node-item").forEach(el=>el.addEventListener("click",()=>{const nid=el.dataset.id;selectedId=selectedId===nid?null:nid;
    applyView();showDetails(selectedId?nodeById.get(nid):null);highlightNodeInList(selectedId);
    if(selectedId){switchTab("details");focusOnNode(nodeById.get(nid))}}));
}
function highlightNodeInList(id){document.querySelectorAll(".node-item").forEach(el=>el.classList.toggle("active",el.dataset.id===id))}
function focusOnNode(d){if(!d||d.x==null)return;svg.transition().duration(500).call(zoom.transform,d3.zoomIdentity.translate(width/2,height/2).scale(1.5).translate(-d.x,-d.y))}

// =====================================================================
// DETAILS
// =====================================================================
function showDetails(d){
  const el=document.getElementById("tab-details");
  if(!d){el.innerHTML=`<div class="detail-empty">${T("clickToInspect")}</div>`;return}
  const rl=riskLevel(d.riskScore),rc=rl==="high"?"risk-high":rl==="med"?"risk-med":"risk-low",rp=(d.riskScore*100).toFixed(0);
  const fwd=links.filter(l=>getLinkId(l,"source")===d.id).map(l=>getLinkId(l,"target"));
  const rev=links.filter(l=>getLinkId(l,"target")===d.id).map(l=>getLinkId(l,"source"));
  const contribHtml=d.contribList.length?d.contribList.map(c=>`<div class="contrib-mini"><span class="cn">${c.name}</span><span class="cc">${c.commits} ${T("commits")}</span></div>`).join("")
    :`<span class="dl">${T("noContributors")}</span>`;
  el.innerHTML=`<div class="detail-section"><h4>${d.label}${d.isEntry?" &#9733; "+T("entryPoint"):""} <span class="risk-badge ${rc}">${rp}% ${T("riskPct")}</span></h4>
    <div class="detail-row"><span class="dl">${T("path")}</span><span class="dv">${d.id}</span></div>
    <div class="detail-row"><span class="dl">${T("language")}</span><span class="dv">${d.language}</span></div>
    <div class="detail-row"><span class="dl">${T("group")}</span><span class="dv">${d.group}</span></div>
    <div class="detail-row"><span class="dl">${T("lines")}</span><span class="dv">${d.lineCount}</span></div></div>
    <div class="detail-section"><h4>&#128200; ${T("metrics")}</h4>
    <div class="detail-row"><span class="dl">${T("fanIn")}</span><span class="dv">${d.fanIn}</span></div>
    <div class="detail-row"><span class="dl">${T("fanOut")}</span><span class="dv">${d.fanOut}</span></div>
    <div class="detail-row"><span class="dl">${T("centrality")}</span><span class="dv">${d.centrality.toFixed(4)}</span></div>
    <div class="detail-row"><span class="dl">${T("churn")}</span><span class="dv">${d.churn}</span></div>
    <div class="detail-row"><span class="dl">${T("depth")}</span><span class="dv">${d.depth}</span></div></div>
    <div class="detail-section"><h4>&#128101; ${T("ownership")}</h4>
    <div class="detail-row"><span class="dl">${T("owner")}</span><span class="dv">${d.owner}</span></div>
    <div class="detail-row"><span class="dl">${T("commits")}</span><span class="dv">${d.totalCommits}</span></div>
    <div class="detail-row"><span class="dl">${T("lastModified")}</span><span class="dv">${d.lastModified}</span></div>
    <div class="detail-row"><span class="dl">${T("contributors")}</span><span class="dv">${d.contributors}</span></div>
    ${contribHtml}</div>
    <div class="detail-section"><h4>&#8594; ${T("dependsOn")} (${fwd.length})</h4>
    ${fwd.length?fwd.map(f=>`<span class="dep-link" data-id="${f}">${f}</span>`).join(""):`<span class="dl">${T("none")}</span>`}</div>
    <div class="detail-section"><h4>&#8592; ${T("dependedOnBy")} (${rev.length})</h4>
    ${rev.length?rev.map(f=>`<span class="dep-link" data-id="${f}">${f}</span>`).join(""):`<span class="dl">${T("none")}</span>`}</div>
    <div class="detail-section"><h4>&#128221; ${T("notes")}</h4>
    ${nodeNotes.has(d.id)?`<div style="background:var(--bg0);padding:8px;border-radius:var(--radius);font-size:12px;white-space:pre-wrap;margin-bottom:6px">${escHtml(nodeNotes.get(d.id))}</div>
      <button class="tb-btn" style="font-size:10px;margin-right:4px" onclick="openNoteEditor('${d.id}')">${T("editNote")}</button>
      <button class="tb-btn" style="font-size:10px;color:var(--danger)" onclick="removeNodeNote('${d.id}')">${T("removeNote")}</button>`
      :`<div class="dl">${T("noNotes")}</div><button class="tb-btn" style="font-size:10px" onclick="openNoteEditor('${d.id}')">${T("addNote")}</button>`}
    </div>`;
  el.querySelectorAll(".dep-link").forEach(lnk=>lnk.addEventListener("click",()=>{const nd=nodeById.get(lnk.dataset.id);
    if(nd){selectedId=nd.id;applyView();showDetails(nd);highlightNodeInList(nd.id);focusOnNode(nd)}}));
}

// =====================================================================
// HOTSPOTS
// =====================================================================
function buildHotspots(){
  const sorted=[...nodes].sort((a,b)=>b.riskScore-a.riskScore).slice(0,20);
  const maxR=sorted[0]?sorted[0].riskScore:1;
  const el=document.getElementById("tab-hotspots");
  el.innerHTML=`<div class="section-label">${T("highestRisk")}</div>`+sorted.map((n,i)=>{
    const pct=maxR>0?(n.riskScore/maxR*100):0;
    return`<div class="hotspot-item" data-id="${n.id}"><div class="hotspot-rank">#${i+1}</div>
      <div class="hotspot-info"><div class="hotspot-name">${n.label}${n.isEntry?" &#9733;":""}</div>
      <div class="hotspot-meta">${T("fanIn")}:${n.fanIn} ${T("fanOut")}:${n.fanOut} ${T("churn")}:${n.churn}</div></div>
      <div class="hotspot-bar"><div class="hotspot-bar-fill" style="width:${pct}%;background:${riskColor(n.riskScore)}"></div></div></div>`}).join("");
  el.querySelectorAll(".hotspot-item").forEach(el=>el.addEventListener("click",()=>{const nd=nodeById.get(el.dataset.id);
    if(nd){selectedId=nd.id;applyView();showDetails(nd);highlightNodeInList(nd.id);switchTab("details");focusOnNode(nd)}}));
}

// =====================================================================
// AUTHORS TAB
// =====================================================================
function buildAuthorsTab(){
  const el=document.getElementById("tab-authors");
  const contribs=DATA.contributors||[];
  if(!contribs.length){el.innerHTML=`<div class="detail-empty">${T("noContributors")}</div>`;return}
  el.innerHTML=`<div class="section-label">${T("authors")} (${contribs.length})</div>`+contribs.map((c,i)=>{
    const initial=c.name.charAt(0).toUpperCase();
    const fileNodes=nodes.filter(n=>n.contribList.some(x=>x.name===c.name));
    const topFiles=fileNodes.sort((a,b)=>{
      const ac=a.contribList.find(x=>x.name===c.name);const bc=b.contribList.find(x=>x.name===c.name);
      return (bc?bc.commits:0)-(ac?ac.commits:0);
    }).slice(0,8);
    const avgRisk=fileNodes.length?(fileNodes.reduce((s,n)=>s+n.riskScore,0)/fileNodes.length*100).toFixed(0):0;
    const topGroups=[...new Set(fileNodes.map(n=>n.group))].slice(0,4).join(", ");
    return`<div class="author-accord" data-author="${c.name}">
      <div class="author-accord-header${selectedAuthor===c.name?" active":""}" data-idx="${i}">
        <span class="aa-chevron">&#9654;</span>
        <div class="author-avatar">${initial}</div>
        <div class="author-info"><div class="author-name">${c.name}</div>
          <div class="author-stats">${c.files} ${T("authorFiles")} &middot; ${c.commits} ${T("authorCommits")}</div></div></div>
      <div class="author-accord-body" data-idx="${i}">
        <div class="aa-row"><span class="aa-label">${T("authorTotalCommits")}</span><span class="aa-val">${c.commits}</span></div>
        <div class="aa-row"><span class="aa-label">${T("authorFilesTouched")}</span><span class="aa-val">${fileNodes.length}</span></div>
        <div class="aa-row"><span class="aa-label">${T("risk")} (${T("medium")})</span><span class="aa-val">${avgRisk}%</span></div>
        <div class="aa-row"><span class="aa-label">${T("groups")}</span><span class="aa-val">${topGroups||T("none")}</span></div>
        <div class="section-label" style="margin-top:8px">${T("authorTopFiles")}</div>
        <div class="aa-file-list">${topFiles.map(n=>{
          const nc=n.contribList.find(x=>x.name===c.name);
          return`<div class="aa-file" data-id="${n.id}"><span>${n.label}</span><span>${nc?nc.commits:0} ${T("commits")}</span></div>`}).join("")}</div>
      </div></div>`}).join("");
  // Accordion toggle
  el.querySelectorAll(".author-accord-header").forEach(hdr=>hdr.addEventListener("click",()=>{
    const idx=hdr.dataset.idx;const body=el.querySelector(`.author-accord-body[data-idx="${idx}"]`);
    const wasOpen=body.classList.contains("open");
    // Close all
    el.querySelectorAll(".author-accord-header").forEach(h=>h.classList.remove("active"));
    el.querySelectorAll(".author-accord-body").forEach(b=>b.classList.remove("open"));
    if(!wasOpen){hdr.classList.add("active");body.classList.add("open")}
    // Author highlight on graph
    const name=hdr.closest(".author-accord").dataset.author;
    if(wasOpen||selectedAuthor===name){highlightAuthor(null)}else{highlightAuthor(name)}
  }));
  // File clicks navigate to node
  el.querySelectorAll(".aa-file").forEach(f=>f.addEventListener("click",(e)=>{
    e.stopPropagation();const nd=nodeById.get(f.dataset.id);
    if(nd){selectedId=nd.id;applyView();showDetails(nd);highlightNodeInList(nd.id);switchTab("details");focusOnNode(nd)}
  }));
}
function highlightAuthor(name){
  selectedAuthor=name;
  // Update accordion active states
  document.querySelectorAll(".author-accord-header").forEach(h=>{
    const aName=h.closest(".author-accord").dataset.author;
    h.classList.toggle("active",aName===name);
  });
  document.querySelectorAll(".author-accord-body").forEach(b=>{
    const aName=b.closest(".author-accord").dataset.author;
    b.classList.toggle("open",aName===name);
  });
  applyView();
}

// =====================================================================
// FOCUSED-NODE EXPLORATION
// =====================================================================
function activateFocusedNode(nid){
  focusedNodeId=nid;focusMode="local";selectedId=nid;
  const nd=nodeById.get(nid);if(!nd)return;
  buildFocusBar();applyView();showDetails(nd);highlightNodeInList(nid);
  switchTab("details");focusOnNode(nd);
  document.getElementById("node-focus-select").value=nid;
}
function deactivateFocusedNode(){
  focusedNodeId=null;focusMode="local";
  document.getElementById("focus-bar").classList.remove("visible");
  document.getElementById("node-focus-select").value="";
  nodes.forEach(n=>{n._dimmed=false});applyView();
}
function buildFocusBar(){
  const nd=nodeById.get(focusedNodeId);if(!nd)return;
  const bar=document.getElementById("focus-bar");
  bar.classList.add("visible");
  const modeInfoMap={
    local:T("showingLocalGraphOf"),deps:T("showingDepsOf"),
    reverse:T("showingReverseDepsOf"),impact:T("showingImpactOf"),flow:T("showingFlowOf")
  };
  bar.innerHTML=
    `<span class="fb-label">&#128269; ${T("focusedExploration")}:</span>
    <div class="fb-modes" id="focus-mode-btns">
      <button class="${focusMode==="local"?"active":""}" data-fm="local">${T("localGraph")}</button>
      <button class="${focusMode==="deps"?"active":""}" data-fm="deps">${T("depsOnly")}</button>
      <button class="${focusMode==="reverse"?"active":""}" data-fm="reverse">${T("reverseDepsOnly")}</button>
      <button class="${focusMode==="impact"?"active":""}" data-fm="impact">${T("impactChain")}</button>
      <button class="${focusMode==="flow"?"active":""}" data-fm="flow">${T("nodeFlow")}</button>
    </div>
    <span class="fb-info">${modeInfoMap[focusMode]||""} <strong>${nd.label}</strong></span>
    <button class="fb-close" id="fb-close">&#10005; ${T("clearFocus")}</button>`;
  bar.querySelectorAll("#focus-mode-btns button").forEach(b=>b.addEventListener("click",()=>{
    focusMode=b.dataset.fm;buildFocusBar();applyView();
  }));
  document.getElementById("fb-close").addEventListener("click",deactivateFocusedNode);
}
function applyFocusedNodeView(){
  if(!focusedNodeId){nodes.forEach(n=>{n._dimmed=false});return}
  const vis=new Set([focusedNodeId]);
  if(focusMode==="local"){
    links.forEach(l=>{const s=getLinkId(l,"source"),t=getLinkId(l,"target");
      if(s===focusedNodeId)vis.add(t);if(t===focusedNodeId)vis.add(s)});
  } else if(focusMode==="deps"){
    links.forEach(l=>{if(getLinkId(l,"source")===focusedNodeId)vis.add(getLinkId(l,"target"))});
  } else if(focusMode==="reverse"){
    links.forEach(l=>{if(getLinkId(l,"target")===focusedNodeId)vis.add(getLinkId(l,"source"))});
  } else if(focusMode==="impact"){
    const q=[focusedNodeId];
    while(q.length){const c=q.shift();links.forEach(l=>{const s=getLinkId(l,"source"),t=getLinkId(l,"target");
      if(t===c&&!vis.has(s)){vis.add(s);q.push(s)}})}
    links.forEach(l=>{if(getLinkId(l,"source")===focusedNodeId)vis.add(getLinkId(l,"target"))});
  } else if(focusMode==="flow"){
    // Show the full dependency chain from entry points through the focused node
    const fwd=new Set([focusedNodeId]),bwd=new Set([focusedNodeId]);
    let fq=[focusedNodeId];while(fq.length){const c=fq.shift();links.forEach(l=>{const s=getLinkId(l,"source"),t=getLinkId(l,"target");if(s===c&&!fwd.has(t)){fwd.add(t);fq.push(t)}})}
    let bq=[focusedNodeId];while(bq.length){const c=bq.shift();links.forEach(l=>{const s=getLinkId(l,"source"),t=getLinkId(l,"target");if(t===c&&!bwd.has(s)){bwd.add(s);bq.push(s)}})}
    fwd.forEach(x=>vis.add(x));bwd.forEach(x=>vis.add(x));
  }
  if(selectedAuthor){nodes.forEach(n=>{if(!n.contribList.some(c=>c.name===selectedAuthor))vis.delete(n.id)})}
  nodes.forEach(n=>{n._dimmed=!vis.has(n.id)});
  circleEls.classed("selected",d=>d.id===focusedNodeId).classed("dimmed",d=>d._dimmed)
    .attr("opacity",d=>d._hidden?0:d._dimmed?.06:1);
  linkEls.attr("class",l=>{const s=getLinkId(l,"source"),t=getLinkId(l,"target");
    if(s===focusedNodeId)return"link dep-fwd";if(t===focusedNodeId)return"link dep-rev";
    const sn=nodeById.get(s),tn=nodeById.get(t);if(sn&&!sn._dimmed&&tn&&!tn._dimmed)return"link highlighted";return"link"})
    .attr("opacity",l=>{const s=getLinkId(l,"source"),t=getLinkId(l,"target");
      const sn=nodeById.get(s),tn=nodeById.get(t);
      if((sn&&sn._hidden)||(tn&&tn._hidden))return 0;
      if(sn&&!sn._dimmed&&tn&&!tn._dimmed)return .8;return .03});
  updateLabelVisibility();drawEntryMarkers();
}

// =====================================================================
// MINIMAP
// =====================================================================
function buildMinimap(){
  const mm=d3.select("#minimap-svg");mm.selectAll("*").remove();
  const pad=8,mw=180-pad*2,mh=130-pad*2;
  const xs=nodes.map(d=>d.x).filter(v=>v!=null),ys=nodes.map(d=>d.y).filter(v=>v!=null);
  if(!xs.length)return;
  const x0=d3.min(xs)-50,x1=d3.max(xs)+50,y0=d3.min(ys)-50,y1=d3.max(ys)+50;
  const gw=x1-x0||1,gh=y1-y0||1,scale=Math.min(mw/gw,mh/gh);
  const mg=mm.append("g").attr("transform",`translate(${pad},${pad})`);
  mg.selectAll("circle").data(nodes.filter(d=>!d._hidden&&!d._dimmed)).join("circle").attr("class","mm-node")
    .attr("cx",d=>(d.x-x0)*scale).attr("cy",d=>(d.y-y0)*scale).attr("r",1.5);
  // Viewport rect based on current zoom transform
  const t=d3.zoomTransform(svg.node());
  const vx=(-t.x/t.k-x0)*scale,vy=(-t.y/t.k-y0)*scale,vw=(width/t.k)*scale,vh=(height/t.k)*scale;
  mg.append("rect").attr("class","mm-viewport").attr("x",vx).attr("y",vy).attr("width",Math.max(vw,4)).attr("height",Math.max(vh,4));
  // Click to navigate
  document.getElementById("minimap").onclick=function(e){
    const rect=this.getBoundingClientRect();
    const mx=(e.clientX-rect.left-pad)/scale+x0,my=(e.clientY-rect.top-pad)/scale+y0;
    svg.transition().duration(300).call(zoom.transform,d3.zoomIdentity.translate(width/2-mx*currentZoom,height/2-my*currentZoom).scale(currentZoom));
  };
}

// =====================================================================
// STATS BAR
// =====================================================================
function updateStatsBar(){
  const vis=nodes.filter(n=>!n._hidden).length;
  const total=IS_LARGE?allNodesData.length:nodes.length;
  const visL=links.filter(l=>{const s=nodeById.get(getLinkId(l,"source")),t=nodeById.get(getLinkId(l,"target"));return s&&!s._hidden&&t&&!t._hidden}).length;
  document.getElementById("stats-bar").innerHTML=
    `<span>${T("files")}: <span class="sv">${vis}</span>/${total}</span>`+
    `<span>${T("edges")}: <span class="sv">${visL}</span>/${links.length}</span>`+
    `<span>${T("groups")}: <span class="sv">${DATA.groups.length}</span></span>`+
    `<span>${T("layout")}: <span class="sv">${T(currentLayout)}</span></span>`+
    (IS_LARGE?`<span>${T("performance")}: <span class="sv">${T(perfMode==="fast"?"perfFast":"perfQuality")}</span></span>`:"");
}

// =====================================================================
// LEGEND
// =====================================================================
function buildLegend(){
  let html=`<h5>${T("legend")}</h5>`;
  if(colorMode==="language"){DATA.languages.forEach(k=>{const v=LANG_COLORS[k]||LANG_COLORS.unknown;html+=`<div class="legend-row"><div class="legend-dot" style="background:${v}"></div>${k}</div>`})}
  else if(colorMode==="group"){DATA.groups.slice(0,10).forEach(g=>html+=`<div class="legend-row"><div class="legend-dot" style="background:${groupColorScale(g)}"></div>${g}</div>`)}
  else if(colorMode==="churn"){html+=`<div class="legend-row"><div class="legend-dot" style="background:${d3.interpolateYlOrRd(.15)}"></div>${T("low")}</div>`;
    html+=`<div class="legend-row"><div class="legend-dot" style="background:${d3.interpolateYlOrRd(.5)}"></div>${T("medium")}</div>`;
    html+=`<div class="legend-row"><div class="legend-dot" style="background:${d3.interpolateYlOrRd(.85)}"></div>${T("high")}</div>`}
  else if(colorMode==="risk"){const rc=getRiskColors();html+=`<div class="legend-row"><div class="legend-dot" style="background:${rc.low}"></div>${T("low")} (&lt;30%)</div>`;
    html+=`<div class="legend-row"><div class="legend-dot" style="background:${rc.med}"></div>${T("medium")} (30-60%)</div>`;
    html+=`<div class="legend-row"><div class="legend-dot" style="background:${rc.high}"></div>${T("high")} (&gt;60%)</div>`}
  else if(colorMode==="contributors"){html+=`<div class="legend-row"><div class="legend-dot" style="background:${d3.interpolateYlGnBu(.2)}"></div>${T("few")}</div>`;
    html+=`<div class="legend-row"><div class="legend-dot" style="background:${d3.interpolateYlGnBu(.55)}"></div>${T("some")}</div>`;
    html+=`<div class="legend-row"><div class="legend-dot" style="background:${d3.interpolateYlGnBu(.85)}"></div>${T("many")}</div>`}
  document.getElementById("legend-panel").innerHTML=html;
  repositionMinimap();
}
function repositionMinimap(){
  const lp=document.getElementById("legend-panel"),mm=document.getElementById("minimap");
  if(!lp||!mm)return;
  const lh=lp.offsetHeight;
  mm.style.bottom=(lh+20)+"px";
}

// =====================================================================
// NODE NOTES
// =====================================================================
function escHtml(s){const d=document.createElement("div");d.textContent=s;return d.innerHTML}
function openNoteEditor(nodeId){
  const existing=nodeNotes.get(nodeId)||"";
  const nd=nodeById.get(nodeId);
  const name=nd?nd.label:nodeId;
  document.getElementById("note-overlay").classList.add("visible");
  const ed=document.getElementById("note-editor");
  ed.classList.add("visible");
  ed.innerHTML=
    `<h4>&#128221; ${T("noteLabel")}: ${escHtml(name)}</h4>
    <textarea id="note-text" placeholder="${T("notePlaceholder")}">${escHtml(existing)}</textarea>
    <div class="ne-actions">
      <button onclick="closeNoteEditor()">${T("cancelNote")}</button>
      <button class="primary" onclick="saveNodeNote('${nodeId}')">${T("saveNote")}</button>
    </div>`;
  document.getElementById("note-text").focus();
}
function closeNoteEditor(){
  document.getElementById("note-overlay").classList.remove("visible");
  const ed=document.getElementById("note-editor");
  ed.classList.remove("visible");
  ed.innerHTML="";
}
function saveNodeNote(nodeId){
  const text=(document.getElementById("note-text").value||"").trim();
  if(text){nodeNotes.set(nodeId,text)}else{nodeNotes.delete(nodeId)}
  closeNoteEditor();updateNoteIndicators();
  const nd=nodeById.get(nodeId);if(nd&&selectedId===nodeId)showDetails(nd);
}
function removeNodeNote(nodeId){
  nodeNotes.delete(nodeId);updateNoteIndicators();
  const nd=nodeById.get(nodeId);if(nd&&selectedId===nodeId)showDetails(nd);
}
function updateNoteIndicators(){
  circleEls.classed("has-note",d=>nodeNotes.has(d.id));
  if(!noteG)return;
  const noted=nodes.filter(n=>nodeNotes.has(n.id)&&!n._hidden);
  const ind=noteG.selectAll("text").data(noted,d=>d.id);
  ind.exit().remove();
  ind.enter().append("text").attr("class","note-indicator").attr("font-size","10px").attr("text-anchor","middle").text(T("nodeHasNote"))
    .on("click",(e,d)=>{e.stopPropagation();openNoteEditor(d.id)})
    .merge(ind).attr("x",d=>d.x).attr("y",d=>d.y-nodeR(d)-6);
}

// =====================================================================
// MANUAL LAYOUT PERSISTENCE
// =====================================================================
function layoutStorageKey(){return "codemap-layout-"+btoa(location.pathname).slice(0,32)}
function saveManualLayout(){
  const positions={};
  nodes.forEach(d=>{positions[d.id]={x:d.x,y:d.y}});
  try{localStorage.setItem(layoutStorageKey(),JSON.stringify(positions))}catch(e){}
  const btn=document.getElementById("btn-save-layout");
  if(btn){btn.textContent="\u2705 "+T("layoutSaved");setTimeout(()=>{btn.textContent="\ud83d\udcbe "+T("saveLayout")},1500)}
}
function restoreManualLayout(){
  try{
    const raw=localStorage.getItem(layoutStorageKey());
    if(!raw){const btn=document.getElementById("btn-restore-layout");if(btn){btn.textContent="\u274c "+T("noSavedLayout");setTimeout(()=>{btn.textContent="\ud83d\udcc2 "+T("restoreLayout")},1500)}return}
    const positions=JSON.parse(raw);
    nodes.forEach(d=>{const p=positions[d.id];if(p){d.x=p.x;d.y=p.y;d.fx=p.x;d.fy=p.y}});
    manualTick();buildMinimap();
  }catch(e){}
}

// =====================================================================
// ABOUT FOOTER
// =====================================================================
function buildAboutFooter(){
  const ver=DATA.metadata&&DATA.metadata.version?DATA.metadata.version:"1.0.0";
  const el=document.getElementById("app-footer");
  el.innerHTML=`<span style="font-weight:600;color:var(--text2)">CodeMap</span>
    <span class="footer-sep">|</span>
    <span>v${escHtml(ver)}</span>
    <span class="footer-sep">|</span>
    <span>${T("appFooter")} <a href="https://polprog.pl/" target="_blank" rel="noopener" style="font-weight:700;color:var(--text)">POLPROG</a></span>
    <span class="footer-sep">|</span>
    <a href="https://github.com/polprog-tech/CodeMap" target="_blank" rel="noopener">${T("repository")} \u2197</a>`;
}

// =====================================================================
// PERFORMANCE BANNER
// =====================================================================
function updatePerfBanner(){
  const banner=document.getElementById("perf-banner");
  if(!IS_LARGE||perfMode==="quality"){banner.classList.remove("visible");return}
  const collapsed=collapsedGroups.size;
  if(collapsed===0){banner.classList.remove("visible");return}
  banner.classList.add("visible");
  banner.innerHTML=`<span>&#9889; ${T("largeGraph")} &mdash; ${collapsed} ${T("groups")} ${T("collapsedView").toLowerCase()}</span>
    <span style="margin-left:auto;color:var(--text2)">${nodes.length} ${T("nodesVisible")} / ${allNodesData.length} ${T("files")}</span>
    <button id="btn-expand-all">${T("expandAll")}</button>
    <button id="btn-collapse-all">${T("collapseAll")}</button>`;
  document.getElementById("btn-expand-all").addEventListener("click",expandAllGroups);
  document.getElementById("btn-collapse-all").addEventListener("click",collapseAllGroups);
}

// =====================================================================
// LANGUAGE SWITCH
// =====================================================================
document.getElementById("lang-switch").addEventListener("change",e=>{lang=e.target.value;buildUI()});

// =====================================================================
// THEME SWITCH
// =====================================================================
function refreshArrows(){const s=getComputedStyle(document.documentElement);
  [["arrow","--border"],["arrow-hl","--highlight"],["arrow-fwd","--accent"],["arrow-rev","--danger"],["arrow-flow","--success"]].forEach(([id,v])=>{
    const el=document.getElementById(id);if(el)el.querySelector("path").setAttribute("fill",s.getPropertyValue(v).trim())
  })}
function applyTheme(t){
  const root=document.documentElement;
  if(t==="system"){root.removeAttribute("data-theme");
    const prefersDark=window.matchMedia("(prefers-color-scheme:dark)").matches;
    if(!prefersDark)root.setAttribute("data-theme","light");
  }else{root.setAttribute("data-theme",t)}
  try{localStorage.setItem("codemap-theme",t)}catch(e){}
  setTimeout(refreshArrows,0);
}
(function initTheme(){
  const saved=localStorage.getItem("codemap-theme")||"system";
  const sel=document.getElementById("theme-switch");
  sel.value=saved;applyTheme(saved);
  sel.addEventListener("change",e=>applyTheme(e.target.value));
  window.matchMedia("(prefers-color-scheme:dark)").addEventListener("change",()=>{
    if((localStorage.getItem("codemap-theme")||"system")==="system")applyTheme("system");
  });
})();

// =====================================================================
// RESIZE
// =====================================================================
window.addEventListener("resize",()=>{updateDimensions();if(currentLayout==="force"){sim.force("center",d3.forceCenter(width/2,height/2));
  sim.force("x",d3.forceX(width/2).strength(.04));sim.force("y",d3.forceY(height/2).strength(.04))}sim.alpha(.2).restart()});

// =====================================================================
// INIT
// =====================================================================
document.getElementById("graph-svg").classList.add("mode-readable");
document.getElementById("note-overlay").addEventListener("click",closeNoteEditor);
buildUI();
updatePerfBanner();
</script>
</body>
</html>"""
