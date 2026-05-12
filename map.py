"""
Iceland Fisheries — Interactive Catch/Value Map with Year Slider
================================================================
Generates a single self-contained HTML file with:
  • Leaflet map + year slider
  • Intro slideshow (1990 / 2000 / 2010 / 2020)
  • Catch ↔ Value toggle (navbar, always visible)
  • Monthly-charts side panel (updates per year, visible in both modes)
  • Stories navigation menu (placeholder links)

Requirements
------------
  afli_data1.csv, afli_data2.csv, afli_data3.csv
  iceland_towns_coordinates.csv   (columns: town, latitude, longitude)
  monthly_plots/
      monthly_catch_YYYY.png
      monthly_value_YYYY.png
      top10ports_YYYY.png
"""

import pandas as pd
import json

# ── Data loading ──────────────────────────────────────────────────────────────
df1 = pd.read_csv('afli_data1.csv')
df2 = pd.read_csv('afli_data2.csv')
df3 = pd.read_csv('afli_data3.csv')
combined_df = pd.concat([df1, df2, df3], ignore_index=True)

combined_df.drop(columns=['Unnamed: 0'], inplace=True)
combined_df.rename(columns={
    'Afli og aflaverðmæti eftir fisktegund, löndunarhöfn, '
    'landsvæðum og mánuðum 1982-2024': 'Afli'
}, inplace=True)

combined_df = combined_df[~combined_df['Löndunarhöfn'].isin([
    'A.-Þýskaland', 'Bandaríkin', 'Belgía', 'Bretland', 'Danmörk',
    'Domeniska Lýðveldið', 'Frakkland', 'Færeyjar', 'Grænland', 'Holland',
    'Írland', 'Japan', 'Kanada', 'Litháen', 'Namibía', 'Noregur', 'Skotland',
    'Spánn', 'Svíþjóð', 'Tyrkland', 'Þýskaland', 'Önnur löndun',
    'Domeniska lýðveldið'
])]

combined_df['Mánuður'] = combined_df['Mánuður'].map({
    'janúar': 1, 'febrúar': 2, 'mars': 3, 'apríl': 4, 'maí': 5, 'júní': 6,
    'júlí': 7, 'ágúst': 8, 'september': 9, 'október': 10, 'nóvember': 11,
    'desember': 12
})

combined_df['Afli'] = pd.to_numeric(combined_df['Afli'], errors='coerce')

combined_df = (
    combined_df
    .pivot_table(
        index=["Fisktegund", "Löndunarhöfn", "Ár", "Mánuður"],
        columns="Eining",
        values="Afli",
        aggfunc="first"
    )
    .reset_index()
)
combined_df.columns.name = None

combined_df.rename(columns={
    'Fisktegund': 'Species', 'Löndunarhöfn': 'Port', 'Ár': 'Year',
    'Mánuður': 'Month', 'Magn': 'Quantity', 'Verðmæti': 'Value'
}, inplace=True)

combined_df = combined_df[
    (combined_df["Quantity"] >= 0) & (combined_df["Value"] >= 0)
]

top_ports = (
    combined_df.groupby("Port")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(50)
    .index.tolist()
)
coords = pd.read_csv("iceland_towns_coordinates.csv")

# ── 1. Aggregate Quantity AND Value per Port per Year ─────────────────────────
port_year = (
    combined_df[combined_df["Port"].isin(top_ports)]
    .groupby(["Year", "Port"], as_index=False)[["Quantity", "Value"]]
    .sum()
)
port_year = port_year.merge(coords, left_on="Port", right_on="town", how="inner")

# ── 2. Build JSON blobs ───────────────────────────────────────────────────────
years            = sorted(port_year["Year"].unique().tolist())
global_max_catch = float(port_year["Quantity"].max())
global_max_value = float(port_year["Value"].max())

# All-time max share of annual value any single port has held.
# Used as a fixed ceiling so equal percentages always get equal dot sizes.
_year_value_totals = port_year.groupby("Year")["Value"].transform("sum")
global_max_pct_value = float((port_year["Value"] / _year_value_totals).max())

data_by_year_catch = {}
data_by_year_value = {}
for year in years:
    yr = port_year[port_year["Year"] == year]
    data_by_year_catch[str(year)] = [
        {"port": r["Port"], "lat": round(r["latitude"], 5),
         "lon": round(r["longitude"], 5), "qty": round(r["Quantity"], 1)}
        for _, r in yr.iterrows()
    ]
    data_by_year_value[str(year)] = [
        {"port": r["Port"], "lat": round(r["latitude"], 5),
         "lon": round(r["longitude"], 5), "qty": round(r["Value"], 1)}
        for _, r in yr.iterrows()
    ]

# ── 3. Generate HTML ──────────────────────────────────────────────────────────
slideshow_years   = [1990, 2000, 2010, 2020]
slideshow_indices = [years.index(y) for y in slideshow_years if y in years]
n_ports           = len(top_ports)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Iceland Fisheries — Catch by Port</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'DM Sans', sans-serif;
    background: #0d1117;
    color: #c9d1d9;
  }}

  #map {{ width: 100%; height: 100vh; }}

  /* ═══════════════════════════════════════════
     NAVBAR
  ═══════════════════════════════════════════ */
  .navbar {{
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 52px;
    background: rgba(13,17,23,0.94);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid #21262d;
    z-index: 3000;
    display: flex;
    align-items: center;
    padding: 0 18px;
    gap: 14px;
  }}

  .navbar-brand {{
    font-size: 14px;
    font-weight: 700;
    color: #f0f6fc;
    white-space: nowrap;
    flex-shrink: 0;
    line-height: 1.15;
  }}

  .navbar-brand .brand-sub {{
    display: block;
    font-size: 10px;
    font-weight: 400;
    color: #8b949e;
    letter-spacing: 0.02em;
  }}

  .navbar-sep {{
    width: 1px;
    height: 26px;
    background: #21262d;
    flex-shrink: 0;
  }}

  .stories-label {{
    font-size: 10px;
    font-weight: 600;
    color: #484f58;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    flex-shrink: 0;
    white-space: nowrap;
  }}

  .navbar-stories {{
    display: flex;
    align-items: center;
    gap: 2px;
    flex: 1;
    min-width: 0;
    overflow: hidden;
  }}

  .navbar-stories a {{
    font-size: 12.5px;
    color: #8b949e;
    text-decoration: none;
    padding: 5px 9px;
    border-radius: 6px;
    white-space: nowrap;
    transition: color 0.2s, background 0.2s;
    display: flex;
    align-items: center;
    gap: 5px;
  }}

  .navbar-stories a:hover {{
    color: #c9d1d9;
    background: rgba(255,255,255,0.06);
  }}

  .placeholder-badge {{
    font-size: 9px;
    background: #21262d;
    color: #484f58;
    border-radius: 3px;
    padding: 1px 4px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }}

  /* ── Mode toggle (Catch / Value) ── */
  .mode-toggle {{
    display: flex;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 3px;
    gap: 2px;
    flex-shrink: 0;
  }}

  .mode-btn {{
    padding: 5px 13px;
    border-radius: 16px;
    border: none;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.25s, color 0.25s;
    color: #8b949e;
    background: transparent;
    white-space: nowrap;
  }}

  .mode-btn.active-catch {{
    background: #58a6ff;
    color: #0d1117;
  }}

  .mode-btn.active-value {{
    background: #ffa657;
    color: #0d1117;
  }}

  /* ═══════════════════════════════════════════
     CHARTS PANEL
  ═══════════════════════════════════════════ */
  .charts-panel {{
    position: fixed;
    top: 52px;
    right: 0;
    width: 420px;
    height: calc(100vh - 52px);
    background: rgba(13,17,23,0.94);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-left: 1px solid #21262d;
    z-index: 2100;
    display: flex;
    flex-direction: column;
    transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
    transform: translateX(0);
  }}

  .charts-panel.collapsed {{
    transform: translateX(420px);
  }}

  /* Pull-tab (arrow handle on left edge of panel) */
  .charts-pull {{
    position: absolute;
    left: -34px;
    top: 50%;
    transform: translateY(-50%);
    width: 34px;
    height: 68px;
    background: rgba(13,17,23,0.94);
    backdrop-filter: blur(12px);
    border: 1px solid #21262d;
    border-right: none;
    border-radius: 10px 0 0 10px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    transition: background 0.2s;
    z-index: 2101;
  }}

  .charts-pull:hover {{
    background: rgba(26,32,40,0.97);
  }}

  .charts-pull .pull-arrow {{
    font-size: 13px;
    color: #58a6ff;
    transition: transform 0.35s;
    line-height: 1;
  }}

  .charts-pull .pull-text {{
    font-size: 9px;
    color: #484f58;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    writing-mode: vertical-lr;
    transform: rotate(180deg);
  }}

  .charts-panel.collapsed .charts-pull .pull-arrow {{
    transform: rotate(180deg);
  }}

  /* Panel header */
  .charts-header {{
    padding: 12px 16px 10px;
    border-bottom: 1px solid #21262d;
    flex-shrink: 0;
  }}

  .charts-header-top {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
  }}

  .charts-header h3 {{
    font-size: 11px;
    font-weight: 600;
    color: #484f58;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}

  .charts-panel-year {{
    font-size: 26px;
    font-weight: 700;
    color: #58a6ff;
    letter-spacing: -1.5px;
    line-height: 1;
    margin-top: 3px;
  }}

  /* Tabs */
  .charts-tabs {{
    display: flex;
    border-bottom: 1px solid #21262d;
    flex-shrink: 0;
  }}

  .charts-tab {{
    flex: 1;
    padding: 9px 4px;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    color: #8b949e;
    cursor: pointer;
    transition: color 0.2s, border-color 0.2s;
    font-weight: 500;
    text-align: center;
  }}

  .charts-tab.active {{
    color: #58a6ff;
    border-bottom-color: #58a6ff;
  }}

  .charts-tab:hover:not(.active) {{
    color: #c9d1d9;
  }}

  /* Image area */
  .charts-img-area {{
    flex: 1;
    overflow-y: auto;
    padding: 14px;
    display: flex;
    align-items: flex-start;
    justify-content: center;
  }}

  .charts-img {{
    width: 100%;
    border-radius: 6px;
    border: 1px solid #21262d;
    display: none;
    background: #161b22;
  }}

  .charts-img.active {{
    display: block;
  }}

  .charts-missing-msg {{
    display: none;
    width: 100%;
    padding: 40px 20px;
    text-align: center;
    color: #484f58;
    font-size: 13px;
    font-style: italic;
    border: 1px solid #21262d;
    border-radius: 6px;
    background: #161b22;
  }}

  .charts-missing-msg.active {{
    display: block;
  }}

  /* ── Chart image expand cursor ── */
  .charts-img {{
    cursor: zoom-in;
  }}

  /* ── Lightbox ── */
  .chart-lightbox {{
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9000;
    background: rgba(0,0,0,0.82);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    align-items: center;
    justify-content: center;
    cursor: zoom-out;
  }}

  .chart-lightbox.open {{
    display: flex;
  }}

  .chart-lightbox img {{
    max-width: 92vw;
    max-height: 88vh;
    border-radius: 8px;
    border: 1px solid #30363d;
    box-shadow: 0 16px 60px rgba(0,0,0,0.7);
    pointer-events: none;
  }}

  /* ═══════════════════════════════════════════
     PANEL-OPEN SHIFTS (right-edge elements)
     Applied by JS when panel is visible
  ═══════════════════════════════════════════ */
  body.panel-open .controls {{
    right: 420px;
  }}

  body.panel-open .slideshow-year-display {{
    right: 420px;
  }}

  body.panel-open .slideshow-nav.right {{
    right: 444px; /* 420 + 24 */
  }}

  body.panel-open .play-btn {{
    right: 460px; /* 420 + 40 */
  }}

  /* ═══════════════════════════════════════════
     SLIDESHOW OVERLAY
  ═══════════════════════════════════════════ */
  .slideshow-overlay {{
    position: fixed;
    top: 52px; /* below navbar */
    left: 0; right: 0; bottom: 0;
    z-index: 2000;
    pointer-events: none;
  }}

  .slideshow-overlay.active {{
    pointer-events: auto;
  }}

  .slideshow-nav {{
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    z-index: 2001;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    border: 2px solid rgba(88,166,255,0.4);
    background: rgba(13,17,23,0.85);
    color: #58a6ff;
    font-size: 24px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(8px);
    transition: transform 0.15s, background 0.15s, opacity 0.4s;
    opacity: 0;
  }}

  .slideshow-nav:hover {{
    background: rgba(88,166,255,0.15);
    transform: translateY(-50%) scale(1.1);
  }}

  .slideshow-nav.visible {{ opacity: 1; }}
  .slideshow-nav.left  {{ left: 24px; }}
  .slideshow-nav.right {{ right: 24px; }}

  .slideshow-year-display {{
    position: fixed;
    bottom: 0;
    left: 0; right: 0;
    z-index: 2001;
    background: linear-gradient(transparent, rgba(13,17,23,0.95) 30%);
    padding: 40px 40px 32px;
    text-align: center;
    opacity: 0;
    transition: opacity 0.4s, right 0.35s cubic-bezier(0.4,0,0.2,1);
  }}

  .slideshow-year-display.visible {{ opacity: 1; }}

  .slideshow-year-display .slide-year {{
    font-size: 72px;
    font-weight: 700;
    color: #58a6ff;
    letter-spacing: -3px;
    line-height: 1;
  }}

  .slideshow-year-display .slide-stats {{
    font-size: 15px;
    color: #8b949e;
    margin-top: 6px;
  }}

  .slideshow-year-display .slide-stats span {{
    color: #c9d1d9;
    font-weight: 500;
  }}

  .slide-dots {{
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 16px;
  }}

  .slide-dot {{
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #30363d;
    transition: background 0.3s, transform 0.3s;
  }}

  .slide-dot.active {{
    background: #58a6ff;
    transform: scale(1.3);
  }}

  .explore-btn {{
    margin-top: 20px;
    padding: 10px 28px;
    border-radius: 8px;
    border: 1px solid #30363d;
    background: rgba(88,166,255,0.1);
    color: #58a6ff;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s, transform 0.15s;
    opacity: 0;
  }}

  .explore-btn.visible {{ opacity: 1; }}

  .explore-btn:hover {{
    background: rgba(88,166,255,0.2);
    transform: scale(1.03);
  }}

  /* ═══════════════════════════════════════════
     INTERACTIVE CONTROLS (slider page)
  ═══════════════════════════════════════════ */
  .controls {{
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(transparent, rgba(13,17,23,0.95) 30%);
    padding: 40px 40px 32px;
    z-index: 1000;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.5s, right 0.35s cubic-bezier(0.4,0,0.2,1);
  }}

  .controls.visible {{
    opacity: 1;
    pointer-events: auto;
  }}

  .controls-inner {{
    max-width: 900px;
    margin: 0 auto;
  }}

  .year-display {{
    font-size: 56px;
    font-weight: 700;
    color: #58a6ff;
    letter-spacing: -2px;
    line-height: 1;
    margin-bottom: 4px;
  }}

  .stats {{
    font-size: 14px;
    color: #8b949e;
    margin-bottom: 16px;
  }}

  .stats span {{ color: #c9d1d9; font-weight: 500; }}

  input[type="range"] {{
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 6px;
    background: #21262d;
    border-radius: 3px;
    outline: none;
    cursor: pointer;
  }}

  input[type="range"]::-webkit-slider-thumb {{
    -webkit-appearance: none;
    width: 22px; height: 22px;
    border-radius: 50%;
    background: #58a6ff;
    border: 3px solid #0d1117;
    box-shadow: 0 0 12px rgba(88,166,255,0.4);
    cursor: grab;
  }}

  input[type="range"]::-moz-range-thumb {{
    width: 22px; height: 22px;
    border-radius: 50%;
    background: #58a6ff;
    border: 3px solid #0d1117;
    box-shadow: 0 0 12px rgba(88,166,255,0.4);
    cursor: grab;
  }}

  .year-ticks {{
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    font-size: 11px;
    color: #484f58;
  }}

  /* ═══════════════════════════════════════════
     PLAY BUTTON
  ═══════════════════════════════════════════ */
  .play-btn {{
    position: fixed;
    bottom: 130px;
    right: 40px;
    z-index: 1001;
    width: 48px; height: 48px;
    border-radius: 50%;
    border: none;
    background: #58a6ff;
    color: #0d1117;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(88,166,255,0.3);
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.5s,
                right 0.35s cubic-bezier(0.4,0,0.2,1);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    pointer-events: none;
  }}

  .play-btn.visible {{
    opacity: 1;
    pointer-events: auto;
  }}

  .play-btn:hover {{
    transform: scale(1.1);
    box-shadow: 0 4px 28px rgba(88,166,255,0.5);
  }}

  /* ═══════════════════════════════════════════
     POPUPS
  ═══════════════════════════════════════════ */
  .leaflet-popup-content-wrapper {{
    background: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }}

  .leaflet-popup-tip {{ background: #161b22; border: 1px solid #30363d; }}
  .leaflet-popup-content {{ font-family: 'DM Sans', sans-serif; font-size: 13px; line-height: 1.5; }}

  .popup-port {{ font-weight: 700; font-size: 15px; color: #f0f6fc; margin-bottom: 4px; }}
  .popup-qty-catch {{ color: #58a6ff; font-weight: 500; }}
  .popup-qty-value {{ color: #ffa657; font-weight: 500; }}
</style>
</head>
<body class="panel-open">

<!-- ── Navbar ──────────────────────────────────────────────────────────── -->
<nav class="navbar">
  <div class="navbar-brand">
    Iceland Fisheries
    <span class="brand-sub" id="navSubtitle">Top {n_ports} ports &middot; dot size = catch (tonnes)</span>
  </div>

  <div class="navbar-sep"></div>
  <span class="stories-label">Stories</span>

  <div class="navbar-stories">
    <a href="grindavik.html">
      Grindavík
    </a>
    <a href="capelin.html">
      The Collapse of Capelin
    </a>
    <a href="mackerel.html">
      The Mackerel Revolution
    </a>
    <a href="stories/cod_wars.html" title="Placeholder — coming soon">
      The Cod Wars <span class="placeholder-badge">soon</span>
    </a>
    <a href="stories/port_decline.html" title="Placeholder — coming soon">
      Rise &amp; Fall of Ports <span class="placeholder-badge">soon</span>
    </a>
    <a href="stories/species.html" title="Placeholder — coming soon">
      Species Through Time <span class="placeholder-badge">soon</span>
    </a>
    <a href="stories/200_mile.html" title="Placeholder — coming soon">
      The 200-Mile Limit <span class="placeholder-badge">soon</span>
    </a>
    <a href="stories/economy.html" title="Placeholder — coming soon">
      Fishing Economy <span class="placeholder-badge">soon</span>
    </a>
  </div>

  <!-- Catch / Value toggle -->
  <div class="mode-toggle">
    <button class="mode-btn active-catch" id="modeBtnCatch">Catch</button>
    <button class="mode-btn" id="modeBtnValue">Value</button>
  </div>
</nav>

<!-- ── Map ─────────────────────────────────────────────────────────────── -->
<div id="map"></div>

<!-- ── Charts panel ────────────────────────────────────────────────────── -->
<div class="charts-panel" id="chartsPanel">
  <button class="charts-pull" id="chartsPull" title="Toggle charts panel">
    <span class="pull-arrow">&#9654;</span>
    <span class="pull-text">Charts</span>
  </button>

  <div class="charts-header">
    <div class="charts-header-top">
      <h3>Monthly Charts</h3>
    </div>
    <div class="charts-panel-year" id="chartsPanelYear"></div>
  </div>

  <div class="charts-tabs">
    <button class="charts-tab active" data-tab="0">Monthly Catch</button>
    <button class="charts-tab"        data-tab="1">Monthly Value</button>
    <button class="charts-tab"        data-tab="2">Top 10 Ports</button>
  </div>

  <div class="charts-img-area">
    <img class="charts-img active" id="chartImgCatch" src="" alt="Monthly catch chart">
    <img class="charts-img"        id="chartImgValue" src="" alt="Monthly value chart">
    <img class="charts-img"        id="chartImgTop10" src="" alt="Top 10 ports chart">
    <div class="charts-missing-msg" id="chartsMissingMsg">Monthly data missing for this year</div>
  </div>
</div>

<!-- ── Slideshow UI ─────────────────────────────────────────────────────── -->
<div class="slideshow-overlay active" id="slideshowOverlay">
  <button class="slideshow-nav left"          id="slideLeft">&#9664;</button>
  <button class="slideshow-nav right visible" id="slideRight">&#9654;</button>
  <div class="slideshow-year-display visible" id="slideInfo">
    <div class="slide-year"  id="slideYear"></div>
    <div class="slide-stats" id="slideStats"></div>
    <div class="slide-dots"  id="slideDots"></div>
    <button class="explore-btn" id="exploreBtn">Explore All Years &rarr;</button>
  </div>
</div>

<!-- ── Interactive controls (slider page) ──────────────────────────────── -->
<button class="play-btn" id="playBtn" title="Animate">&#9654;</button>

<!-- ── Chart lightbox ───────────────────────────────────────────────────── -->
<div class="chart-lightbox" id="chartLightbox">
  <img id="lightboxImg" src="" alt="Expanded chart">
</div>

<div class="controls" id="controlsPanel">
  <div class="controls-inner">
    <div class="year-display" id="yearLabel"></div>
    <div class="stats"        id="statsLabel"></div>
    <input type="range" id="slider" min="0" max="{len(years)-1}" value="0" step="1">
    <div class="year-ticks"   id="ticks"></div>
  </div>
</div>

<script>
// ── Data ──────────────────────────────────────────────────────────────────────
const DATA_CATCH        = {json.dumps(data_by_year_catch)};
const DATA_VALUE        = {json.dumps(data_by_year_value)};
const YEARS             = {json.dumps(years)};
const GLOBAL_MAX_C      = {global_max_catch};
const GLOBAL_MAX_V      = {global_max_value};
const GLOBAL_MAX_PCT_V  = {global_max_pct_value};
const SLIDESHOW_IDX     = {json.dumps(slideshow_indices)};

// ── State ─────────────────────────────────────────────────────────────────────
let currentMode   = 'catch';  // 'catch' | 'value'
let slideshowMode = true;
let currentSlide  = 0;

// ── Map setup ─────────────────────────────────────────────────────────────────
const map = L.map('map', {{
  center: [65.0, -18.5],
  zoom: 6,
  zoomControl: false,
  attributionControl: false
}});

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  maxZoom: 12,
  subdomains: 'abcd'
}}).addTo(map);

L.control.zoom({{ position: 'topright' }}).addTo(map);

// ── Helpers ───────────────────────────────────────────────────────────────────
let markers = [];

function formatNum(n) {{
  return n.toLocaleString('en', {{ maximumFractionDigits: 0 }});
}}

// ── updateCharts: swap images for the given year ──────────────────────────────
const MISSING_MONTHLY_YEARS = [1984, 1999];
let currentChartYear = null;

function applyTabState(tabIdx) {{
  const missingMsg = document.getElementById('chartsMissingMsg');
  const imgCatch   = document.getElementById('chartImgCatch');
  const imgValue   = document.getElementById('chartImgValue');
  const imgTop10   = document.getElementById('chartImgTop10');

  imgCatch.classList.remove('active');
  imgValue.classList.remove('active');
  imgTop10.classList.remove('active');

  // Tabs 0 (Monthly Catch) and 1 (Monthly Value) show missing message for missing years;
  // Tab 2 (Top 10 Ports) always shows the image.
  if (MISSING_MONTHLY_YEARS.includes(currentChartYear) && tabIdx !== 2) {{
    missingMsg.classList.add('active');
  }} else {{
    missingMsg.classList.remove('active');
    [imgCatch, imgValue, imgTop10][tabIdx].classList.add('active');
  }}
}}

function updateCharts(year) {{
  currentChartYear = year;
  document.getElementById('chartsPanelYear').textContent = year;
  const base = 'monthly_plots/';
  document.getElementById('chartImgTop10').src = base + 'top10ports_' + year + '.png';
  if (!MISSING_MONTHLY_YEARS.includes(year)) {{
    document.getElementById('chartImgCatch').src = base + 'monthly_catch_' + year + '.png';
    document.getElementById('chartImgValue').src = base + 'monthly_value_' + year + '.png';
  }}
  const activeTabIdx = [...document.querySelectorAll('.charts-tab')].findIndex(b => b.classList.contains('active'));
  applyTabState(activeTabIdx);
}}

// ── updateMap: render circles for a given year index ─────────────────────────
function updateMap(yearIdx) {{
  markers.forEach(m => map.removeLayer(m));
  markers = [];

  const year      = YEARS[yearIdx];
  const isCatch   = (currentMode === 'catch');
  const DATA      = isCatch ? DATA_CATCH : DATA_VALUE;
  const GLOBAL_MAX = isCatch ? GLOBAL_MAX_C : GLOBAL_MAX_V;
  const colour   = isCatch ? '#58a6ff' : '#ffa657';
  const unitLong = isCatch ? 'tonnes total' : 'th. ISK total';

  const ports = DATA[String(year)] || [];
  let totalQty = 0;
  ports.forEach(p => {{ totalQty += p.qty; }});

  ports.forEach(p => {{
    let radius, opacity;
    if (isCatch) {{
      const f = p.qty / (GLOBAL_MAX || 1);
      radius  = Math.max(3, f * 35);
      opacity = Math.max(0.3, Math.min(0.85, f + 0.3));
    }} else {{
      // f = this port's share of the year's total value (0–1).
      // Scaled against the all-time max share so the same percentage
      // always produces the same dot size regardless of year.
      const f = p.qty / (totalQty || 1);
      radius  = Math.max(3, Math.pow(f / GLOBAL_MAX_PCT_V, 0.7) * 35);
      opacity = Math.max(0.3, Math.min(0.85, (f / GLOBAL_MAX_PCT_V) * 0.55 + 0.3));
    }}

    const circle = L.circleMarker([p.lat, p.lon], {{
      radius:      radius,
      color:       colour,
      weight:      1.5,
      fillColor:   colour,
      fillOpacity: opacity
    }}).addTo(map);

    const qClass = isCatch ? 'popup-qty-catch' : 'popup-qty-value';
    let displayVal;
    if (isCatch) {{
      displayVal = formatNum(p.qty) + ' tonnes';
    }} else {{
      const pct = totalQty > 0 ? (p.qty / totalQty * 100) : 0;
      displayVal = pct.toFixed(1) + '% of total value';
    }}
    circle.bindPopup(
      '<div class="popup-port">' + p.port + '</div>' +
      '<div class="' + qClass + '">' + displayVal + '</div>'
    );
    circle.bindTooltip(p.port + ': ' + displayVal, {{
      direction: 'top', offset: [0, -radius]
    }});
    markers.push(circle);
  }});

  // Update slider-page labels
  document.getElementById('yearLabel').textContent = year;
  document.getElementById('statsLabel').innerHTML =
    '<span>' + ports.length + '</span> ports &middot; ' +
    '<span>' + formatNum(totalQty) + '</span> ' + unitLong;

  // Update charts panel
  updateCharts(year);

  return {{ ports: ports.length, totalQty: totalQty, unitLong: unitLong }};
}}

// ── Charts panel: tabs ────────────────────────────────────────────────────────
const chartTabBtns = document.querySelectorAll('.charts-tab');
const chartImgEls  = [
  document.getElementById('chartImgCatch'),
  document.getElementById('chartImgValue'),
  document.getElementById('chartImgTop10')
];

chartTabBtns.forEach((btn, i) => {{
  btn.addEventListener('click', () => {{
    chartTabBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    applyTabState(i);
  }});
}});

// ── Charts panel: open/collapse ───────────────────────────────────────────────
const chartsPanel = document.getElementById('chartsPanel');
document.getElementById('chartsPull').addEventListener('click', () => {{
  const isCollapsed = chartsPanel.classList.toggle('collapsed');
  document.body.classList.toggle('panel-open', !isCollapsed);
}});

// ── Mode toggle ───────────────────────────────────────────────────────────────
const modeBtnCatch  = document.getElementById('modeBtnCatch');
const modeBtnValue  = document.getElementById('modeBtnValue');
const navSubtitle   = document.getElementById('navSubtitle');

function setMode(mode) {{
  currentMode = mode;
  if (mode === 'catch') {{
    modeBtnCatch.className = 'mode-btn active-catch';
    modeBtnValue.className = 'mode-btn';
    navSubtitle.textContent = 'Top {n_ports} ports \u00b7 dot size = catch (tonnes)';
  }} else {{
    modeBtnCatch.className = 'mode-btn';
    modeBtnValue.className = 'mode-btn active-value';
    navSubtitle.textContent = 'Top {n_ports} ports \u00b7 dot size = value \u00b7 label = % of total';
  }}
  // Re-render current state
  if (slideshowMode) {{
    showSlide(currentSlide);
  }} else {{
    updateMap(parseInt(slider.value));
  }}
}}

modeBtnCatch.addEventListener('click', () => setMode('catch'));
modeBtnValue.addEventListener('click', () => setMode('value'));

// ── Slideshow ─────────────────────────────────────────────────────────────────
const slideLeft   = document.getElementById('slideLeft');
const slideRight  = document.getElementById('slideRight');
const slideYear   = document.getElementById('slideYear');
const slideStatsEl = document.getElementById('slideStats');
const slideDots   = document.getElementById('slideDots');
const exploreBtn  = document.getElementById('exploreBtn');
const overlay     = document.getElementById('slideshowOverlay');

// Build dots
SLIDESHOW_IDX.forEach((_, i) => {{
  const dot = document.createElement('div');
  dot.className = 'slide-dot' + (i === 0 ? ' active' : '');
  slideDots.appendChild(dot);
}});

function showSlide(idx) {{
  currentSlide = idx;
  const yearIdx = SLIDESHOW_IDX[idx];
  const info    = updateMap(yearIdx);

  slideYear.textContent = YEARS[yearIdx];
  slideStatsEl.innerHTML =
    '<span>' + info.ports + '</span> ports &middot; ' +
    '<span>' + formatNum(info.totalQty) + '</span> ' + info.unitLong;

  slideDots.querySelectorAll('.slide-dot').forEach((d, i) => {{
    d.classList.toggle('active', i === idx);
  }});

  slideLeft.classList.toggle('visible',  idx > 0);
  slideRight.classList.toggle('visible', idx < SLIDESHOW_IDX.length - 1);
  exploreBtn.classList.toggle('visible', idx === SLIDESHOW_IDX.length - 1);
}}

slideLeft.addEventListener('click',  () => {{ if (currentSlide > 0) showSlide(currentSlide - 1); }});
slideRight.addEventListener('click', () => {{ if (currentSlide < SLIDESHOW_IDX.length - 1) showSlide(currentSlide + 1); }});

function exitSlideshow() {{
  slideshowMode = false;
  overlay.classList.remove('active');
  slideLeft.style.display  = 'none';
  slideRight.style.display = 'none';
  document.getElementById('slideInfo').style.display = 'none';

  document.getElementById('controlsPanel').classList.add('visible');
  document.getElementById('playBtn').classList.add('visible');

  slider.value = 0;
  updateMap(0);
}}

exploreBtn.addEventListener('click', exitSlideshow);

// ── Slider ────────────────────────────────────────────────────────────────────
const slider = document.getElementById('slider');
slider.addEventListener('input', () => updateMap(parseInt(slider.value)));

// Year ticks
const ticksEl = document.getElementById('ticks');
const step    = Math.max(1, Math.floor(YEARS.length / 8));
for (let i = 0; i < YEARS.length; i += step) {{
  const span = document.createElement('span');
  span.textContent = YEARS[i];
  ticksEl.appendChild(span);
}}
if (YEARS.length % step !== 1) {{
  const span = document.createElement('span');
  span.textContent = YEARS[YEARS.length - 1];
  ticksEl.appendChild(span);
}}

// ── Play / animate ────────────────────────────────────────────────────────────
let playing  = false;
let interval = null;
const playBtn = document.getElementById('playBtn');

playBtn.addEventListener('click', () => {{
  if (playing) {{
    clearInterval(interval);
    playBtn.innerHTML = '&#9654;';
    playing = false;
  }} else {{
    playing = true;
    playBtn.innerHTML = '&#9646;&#9646;';
    interval = setInterval(() => {{
      let v = parseInt(slider.value);
      v = (v >= YEARS.length - 1) ? 0 : v + 1;
      slider.value = v;
      updateMap(v);
    }}, 600);
  }}
}});

// ── Keyboard ──────────────────────────────────────────────────────────────────
document.addEventListener('keydown', (e) => {{
  if (slideshowMode) {{
    if      (e.key === 'ArrowRight' && currentSlide < SLIDESHOW_IDX.length - 1) showSlide(currentSlide + 1);
    else if (e.key === 'ArrowLeft'  && currentSlide > 0)                        showSlide(currentSlide - 1);
    else if (e.key === 'Enter' || e.key === 'Escape')                           exitSlideshow();
  }} else {{
    const v = parseInt(slider.value);
    if      (e.key === 'ArrowRight' && v < YEARS.length - 1) {{ slider.value = v + 1; updateMap(v + 1); }}
    else if (e.key === 'ArrowLeft'  && v > 0)                {{ slider.value = v - 1; updateMap(v - 1); }}
    else if (e.key === ' ')                                  {{ e.preventDefault(); playBtn.click(); }}
  }}
}});

// ── Lightbox ──────────────────────────────────────────────────────────────────
const lightbox    = document.getElementById('chartLightbox');
const lightboxImg = document.getElementById('lightboxImg');

document.querySelector('.charts-img-area').addEventListener('click', (e) => {{
  if (e.target.classList.contains('charts-img') && e.target.classList.contains('active')) {{
    lightboxImg.src = e.target.src;
    lightbox.classList.add('open');
  }}
}});

lightbox.addEventListener('click', () => lightbox.classList.remove('open'));

document.addEventListener('keydown', (e) => {{
  if (e.key === 'Escape') lightbox.classList.remove('open');
}});

// ── Init ──────────────────────────────────────────────────────────────────────
showSlide(0);
</script>
</body>
</html>"""

# ── 4. Save ────────────────────────────────────────────────────────────────────
output_path = "iceland_catch_map_slider.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✓ Saved interactive map → {output_path}")
print(f"  {len(years)} years ({years[0]}–{years[-1]})")
print(f"  {len(port_year['Port'].unique())} ports with coordinates")
print(f"  Open in any browser — use slider, arrow keys, or play button")