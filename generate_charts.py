"""
Generate chart PNGs for the Iceland Fisheries interactive map.
================================================================
Produces three charts per year, saved into chart_plots/:

  chart_plots/
      species_catch_YYYY.png     — top species line chart (quantity)
      species_value_YYYY.png     — top species line chart (value)
      concentration_YYYY.png     — quota/catch concentration stackplot
      profit_YYYY.png            — net profit bar chart

All charts use a rolling window centred on each year.
Run this BEFORE the HTML generator.

Parameters
----------
Edit the constants below to tune output.

Requirements
------------
  afli_data1.csv, afli_data2.csv, afli_data3.csv
  rekstur_data.csv       (optional — for profit chart)
  kvoti_data.csv         (optional — falls back to catch-share data)
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ══════════════════════════════════════════════════════════════════════════════
#  PARAMETERS — edit these
# ══════════════════════════════════════════════════════════════════════════════
ROLLING_WINDOW    = 10       # years shown in every chart
TOP_N_SPECIES     = 5        # species lines in chart 1
TOP_N_OPERATORS   = 10       # operators in the concentration chart
OUTPUT_DIR        = "chart_plots"
FIG_WIDTH         = 7        # inches (all charts)
FIG_DPI           = 150

SPECIES_COLORS = [
    "#00d4aa", "#ff8a50", "#7ea6ff", "#c084fc", "#f97316",
]

STACK_COLORS = [
    "#7eb8da", "#f4a582", "#b2d8b2", "#c4a8d1", "#f7dc8a",
    "#a8d5e2", "#ffb7b2", "#cce2cb", "#d4b8e0", "#f9e4ad",
]
OTHERS_COLOR = "#e0e0e0"

# ══════════════════════════════════════════════════════════════════════════════
#  DARK THEME
# ══════════════════════════════════════════════════════════════════════════════
BG       = "#0d1219"
FG       = "#c0c8d4"
GRID_CLR = "#1e2530"
AXIS_CLR = "#3d4a5c"

def apply_dark(ax, title=""):
    ax.set_facecolor(BG)
    ax.figure.set_facecolor(BG)
    ax.title.set_color(FG)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.tick_params(colors=AXIS_CLR, labelsize=11)
    for spine in ax.spines.values():
        spine.set_color(GRID_CLR)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, alpha=0.25, color=GRID_CLR, axis="y")
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", color=FG, pad=10)

# ══════════════════════════════════════════════════════════════════════════════
#  DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════
print("Loading catch data …")
df1 = pd.read_csv("afli_data1.csv")
df2 = pd.read_csv("afli_data2.csv")
df3 = pd.read_csv("afli_data3.csv")
combined_df = pd.concat([df1, df2, df3], ignore_index=True)

combined_df.drop(columns=["Unnamed: 0"], inplace=True)
combined_df.rename(columns={
    "Afli og aflaverðmæti eftir fisktegund, löndunarhöfn, "
    "landsvæðum og mánuðum 1982-2024": "Afli"
}, inplace=True)

FOREIGN_PORTS = [
    "A.-Þýskaland", "Bandaríkin", "Belgía", "Bretland", "Danmörk",
    "Domeniska Lýðveldið", "Frakkland", "Færeyjar", "Grænland", "Holland",
    "Írland", "Japan", "Kanada", "Litháen", "Namibía", "Noregur", "Skotland",
    "Spánn", "Svíþjóð", "Tyrkland", "Þýskaland", "Önnur löndun",
    "Domeniska lýðveldið",
]
combined_df = combined_df[~combined_df["Löndunarhöfn"].isin(FOREIGN_PORTS)]

combined_df["Mánuður"] = combined_df["Mánuður"].map({
    "janúar": 1, "febrúar": 2, "mars": 3, "apríl": 4, "maí": 5, "júní": 6,
    "júlí": 7, "ágúst": 8, "september": 9, "október": 10, "nóvember": 11,
    "desember": 12,
})
combined_df["Afli"] = pd.to_numeric(combined_df["Afli"], errors="coerce")

combined_df = (
    combined_df
    .pivot_table(
        index=["Fisktegund", "Löndunarhöfn", "Ár", "Mánuður"],
        columns="Eining", values="Afli", aggfunc="first",
    )
    .reset_index()
)
combined_df.columns.name = None
combined_df.rename(columns={
    "Fisktegund": "Species", "Löndunarhöfn": "Port",
    "Ár": "Year", "Mánuður": "Month",
    "Magn": "Quantity", "Verðmæti": "Value",
}, inplace=True)
combined_df = combined_df[
    (combined_df["Quantity"] >= 0) & (combined_df["Value"] >= 0)
]

ALL_YEARS = sorted(combined_df["Year"].unique().tolist())

# ── Top species ───────────────────────────────────────────────────────────────
top_species = (
    combined_df.groupby("Species")["Quantity"]
    .sum().sort_values(ascending=False)
    .head(TOP_N_SPECIES).index.tolist()
)

species_year = (
    combined_df[combined_df["Species"].isin(top_species)]
    .groupby(["Year", "Species"], as_index=False)[["Quantity", "Value"]].sum()
)

# ── Concentration data ────────────────────────────────────────────────────────
try:
    df_quota = pd.read_csv("kvoti_data.csv")
    op_year_all = (
        df_quota[df_quota["Species"].isin(["Cod", "Haddock", "Herring", "Capelin"])]
        .groupby(["Year", "Operator"])["Share End"].sum().reset_index()
    )
    print("  Using kvoti_data.csv for concentration chart")
except Exception:
    op_year_all = (
        combined_df.groupby(["Year", "Port"], as_index=False)["Quantity"].sum()
        .rename(columns={"Port": "Operator", "Quantity": "Share End"})
    )
    print("  kvoti_data.csv not found — using catch shares as proxy")

top_ops = (
    op_year_all.groupby("Operator")["Share End"]
    .mean().nlargest(TOP_N_OPERATORS).index.tolist()
)
op_year_all["Group"] = op_year_all["Operator"].where(
    op_year_all["Operator"].isin(top_ops), "Others"
)
grouped = op_year_all.groupby(["Year", "Group"])["Share End"].sum().reset_index()
pivot = grouped.pivot(index="Year", columns="Group", values="Share End").fillna(0)
col_order = [c for c in top_ops if c in pivot.columns] + (
    ["Others"] if "Others" in pivot.columns else []
)
pivot = pivot[col_order]
pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

# ── Financial data ────────────────────────────────────────────────────────────
df_finance = None
try:
    df_finance_raw = pd.read_csv("rekstur_data.csv")
    metric_map = {
        "1. Tekjur alls": "Revenue",
        "2  Gjöld alls": "Expenses",
        "Hreinn hagnaður (EBT)": "NetProfit",
    }
    _df = df_finance_raw[
        (df_finance_raw["Tekju- og gjaldaliðir"].isin(metric_map.keys()))
        & (df_finance_raw["Tegund skipa"] == "Samtals")
    ].copy()
    _df["Metric"] = _df["Tekju- og gjaldaliðir"].map(metric_map)
    _df.rename(columns={
        "Ár": "Year",
        "Rekstraryfirlit fiskveiða 1997-2024": "Amount",
    }, inplace=True)
    _df["Amount"] = pd.to_numeric(_df["Amount"], errors="coerce")
    df_finance = (
        _df.pivot_table(index="Year", columns="Metric", values="Amount", aggfunc="first")
        .reset_index()
    )
    df_finance.columns.name = None
    print("  Using rekstur_data.csv for profit chart")
except Exception:
    print("  rekstur_data.csv not found — profit chart will be skipped")


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def window_years(center, all_years):
    """Return the rolling-window slice of years centred on `center`."""
    half = ROLLING_WINDOW // 2
    lo = center - half
    hi = center + half - 1
    return [y for y in all_years if lo <= y <= hi]


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 1 — Species lines (catch OR value)
# ══════════════════════════════════════════════════════════════════════════════
def make_species_chart(center_year, metric, out_path):
    """metric: 'Quantity' or 'Value'"""
    wyears = window_years(center_year, ALL_YEARS)
    if len(wyears) < 2:
        return

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, 3.6))
    apply_dark(ax)

    unit = "tonnes" if metric == "Quantity" else "th. ISK"

    for i, sp in enumerate(top_species):
        sub = species_year[
            (species_year["Year"].isin(wyears)) & (species_year["Species"] == sp)
        ].sort_values("Year")
        if sub.empty:
            continue
        ax.plot(
            sub["Year"], sub[metric],
            linewidth=2.2, color=SPECIES_COLORS[i % len(SPECIES_COLORS)],
            label=sp, marker="o", markersize=4,
        )

    ax.set_ylabel(unit, fontsize=12, color=FG)
    ax.set_xlim(wyears[0] - 0.3, wyears[-1] + 0.3)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True, nbins=6))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{x/1000:.0f}k" if abs(x) >= 1000 else f"{x:.0f}"
    ))
    ax.legend(
        fontsize=9, loc="upper left", ncol=2,
        frameon=True, facecolor=BG, edgecolor=GRID_CLR,
        labelcolor=FG,
    )
    fig.tight_layout(pad=0.6)
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=BG)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 2 — Concentration stackplot
# ══════════════════════════════════════════════════════════════════════════════
def make_concentration_chart(center_year, out_path):
    wyears = window_years(center_year, sorted(pivot_pct.index.tolist()))
    if len(wyears) < 2:
        return

    sub = pivot_pct.loc[pivot_pct.index.isin(wyears)].sort_index()

    colors = []
    for i, c in enumerate(sub.columns):
        if c == "Others":
            colors.append(OTHERS_COLOR)
        else:
            colors.append(STACK_COLORS[i % len(STACK_COLORS)])

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, 3.6))
    apply_dark(ax)

    ax.stackplot(
        sub.index.values, sub.values.T,
        labels=sub.columns.tolist(), colors=colors, alpha=0.85,
    )
    ax.set_ylim(0, 100)
    ax.set_xlim(wyears[0] - 0.3, wyears[-1] + 0.3)
    ax.set_ylabel("Share (%)", fontsize=12, color=FG)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True, nbins=6))
    ax.legend(
        fontsize=8, loc="upper left", ncol=2,
        frameon=True, facecolor=BG, edgecolor=GRID_CLR,
        labelcolor=FG,
    )
    fig.tight_layout(pad=0.6)
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=BG)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
#  CHART 3 — Net profit bars
# ══════════════════════════════════════════════════════════════════════════════
def make_profit_chart(center_year, out_path):
    if df_finance is None:
        return

    wyears = window_years(center_year, sorted(df_finance["Year"].tolist()))
    if len(wyears) < 2:
        return

    sub = df_finance[df_finance["Year"].isin(wyears)].sort_values("Year")
    if "NetProfit" not in sub.columns or sub["NetProfit"].isna().all():
        return

    vals = sub["NetProfit"].fillna(0).values
    bar_colors = ["#34d399" if v >= 0 else "#f85149" for v in vals]

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, 2.8))
    apply_dark(ax)

    ax.bar(sub["Year"], vals, color=bar_colors, edgecolor="none", width=0.75)
    ax.axhline(0, color="#6b7a8d", linewidth=0.8)
    ax.set_xlim(wyears[0] - 0.6, wyears[-1] + 0.6)
    ax.set_ylabel("Net Profit (M ISK)", fontsize=12, color=FG)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True, nbins=6))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{x/1000:.0f}k" if abs(x) >= 1000 else f"{x:.0f}"
    ))
    fig.tight_layout(pad=0.6)
    fig.savefig(out_path, dpi=FIG_DPI, facecolor=BG)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATE ALL
# ══════════════════════════════════════════════════════════════════════════════
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Generating charts for {len(ALL_YEARS)} years (window={ROLLING_WINDOW}) …")

for i, yr in enumerate(ALL_YEARS):
    make_species_chart(yr, "Quantity", os.path.join(OUTPUT_DIR, f"species_catch_{yr}.png"))
    make_species_chart(yr, "Value",    os.path.join(OUTPUT_DIR, f"species_value_{yr}.png"))
    make_concentration_chart(yr,       os.path.join(OUTPUT_DIR, f"concentration_{yr}.png"))
    make_profit_chart(yr,              os.path.join(OUTPUT_DIR, f"profit_{yr}.png"))

    if (i + 1) % 10 == 0 or i == len(ALL_YEARS) - 1:
        print(f"  {i + 1}/{len(ALL_YEARS)} years done")

print(f"✓ Charts saved to {OUTPUT_DIR}/")