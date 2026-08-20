"""
Crop yields in Argentina: historical analysis of soy, corn and wheat over the
official Crop Estimates dataset (1969 to today).

Covers national production, yield trends, provincial concentration and the
yield gap between departments.

Usage:
    python src/analysis.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"

CROPS = {"soja total": "Soja", "maíz": "Maíz", "trigo total": "Trigo"}
CROP_ORDER = ("Soja", "Maíz", "Trigo")
CROP_COLORS = {"Soja": BLUE, "Maíz": ORANGE, "Trigo": AQUA}
MIN_HARVESTED_HA = 1000
NUMERIC_COLUMNS = ("superficie_sembrada_ha", "superficie_cosechada_ha",
                   "produccion_tm", "rendimiento_kgxha")

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "Segoe UI",
    "text.color": INK,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "figure.dpi": 150,
})


def load_data() -> pd.DataFrame:
    """
    Load the three main crops, one row per crop, season and department.

    Only the "total" categories are kept: the dataset also splits soy into
    first and second plantings, and adding those to the total would count
    the same hectares twice.
    """
    df = pd.read_csv("data/crop_estimates.csv")
    df = df[df["cultivo"].isin(CROPS)].copy()
    df["cultivo"] = df["cultivo"].map(CROPS)
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def plot_national_production(df: pd.DataFrame) -> None:
    series = (df.groupby(["anio", "cultivo"])["produccion_tm"].sum()
              .div(1e6).unstack())

    fig, ax = plt.subplots(figsize=(10, 4.6))
    for crop in CROP_ORDER:
        ax.plot(series.index, series[crop], color=CROP_COLORS[crop],
                linewidth=2, label=crop)

    ax.set_title("Producción nacional por campaña (1969 → hoy)", loc="left", pad=12)
    ax.set_ylabel("millones de toneladas")
    ax.set_ylim(bottom=0)
    ax.set_xlim(series.index.min(), series.index.max() + 1)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_2, loc="upper left")

    fig.tight_layout()
    fig.savefig("figures/01_produccion_nacional.png", bbox_inches="tight")
    plt.close(fig)


def plot_yield(df: pd.DataFrame) -> None:
    """
    National yield per season, weighted rather than averaged.

    Dividing total production by total harvested area answers the right
    question: how many tonnes came out per hectare harvested in the country.
    A plain average of department yields would give a marginal department
    with 500 ha the same weight as a core one with 200,000.
    """
    grouped = df.groupby(["anio", "cultivo"]).agg(
        production=("produccion_tm", "sum"),
        area=("superficie_cosechada_ha", "sum"))
    grouped["yield"] = grouped["production"] / grouped["area"]
    series = grouped["yield"].unstack()

    fig, ax = plt.subplots(figsize=(10, 4.6))
    for crop in CROP_ORDER:
        ax.plot(series.index, series[crop], color=CROP_COLORS[crop],
                linewidth=2, label=crop)

    ax.set_title("Rendimiento nacional promedio por campaña", loc="left", pad=12)
    ax.set_ylabel("toneladas por hectárea")
    ax.set_ylim(bottom=0)
    ax.set_xlim(series.index.min(), series.index.max() + 1)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_2, loc="upper left")

    fig.tight_layout()
    fig.savefig("figures/02_rendimiento.png", bbox_inches="tight")
    plt.close(fig)


def plot_provinces(df: pd.DataFrame, season: str) -> None:
    """Production by province and crop in the latest season."""
    latest = df[df["campania"] == season]
    table = (latest.groupby(["provincia", "cultivo"])["produccion_tm"].sum()
             .div(1e6).unstack(fill_value=0))
    table["total"] = table.sum(axis=1)
    table = table.sort_values("total").tail(10)

    fig, ax = plt.subplots(figsize=(9.5, 5))
    left = pd.Series(0.0, index=table.index)
    for crop in CROP_ORDER:
        ax.barh(table.index, table[crop], left=left, height=0.62,
                color=CROP_COLORS[crop], label=crop,
                edgecolor=SURFACE, linewidth=1.2)
        left += table[crop]
    for row, total in enumerate(table["total"]):
        ax.annotate(f"{total:,.1f}", (total, row), textcoords="offset points",
                    xytext=(5, 0), va="center", fontsize=8.5, color=INK_2)

    ax.set_title(f"Producción por provincia — campaña {season}",
                 loc="left", pad=14)
    ax.set_xlabel("millones de toneladas (soja + maíz + trigo)")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, table["total"].max() * 1.12)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_2, loc="lower right")

    fig.tight_layout()
    fig.savefig("figures/03_provincias.png", bbox_inches="tight")
    plt.close(fig)


def plot_yield_gap(df: pd.DataFrame, season: str) -> None:
    """
    Distribution of soy yield across departments in the latest season.

    Departments below the area threshold are excluded: a handful of hectares
    produces extreme ratios that blur the distribution.
    """
    soy = df[(df["campania"] == season) & (df["cultivo"] == "Soja")
             & (df["superficie_cosechada_ha"] > MIN_HARVESTED_HA)].copy()
    soy["yield"] = soy["produccion_tm"] / soy["superficie_cosechada_ha"]
    national = soy["produccion_tm"].sum() / soy["superficie_cosechada_ha"].sum()

    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ax.hist(soy["yield"], bins=32, color=BLUE, edgecolor=SURFACE, linewidth=0.8)
    ax.axvline(national, color=INK, linewidth=1.2, linestyle="--")
    ax.annotate(f"promedio nacional: {national:.2f} tn/ha",
                (national, ax.get_ylim()[1] * 0.95),
                textcoords="offset points", xytext=(8, 0),
                fontsize=9, color=INK)

    ax.set_title(f"Brecha de rindes en soja por departamento — campaña {season}",
                 loc="left", pad=12)
    ax.set_xlabel("toneladas por hectárea (departamentos con +1.000 ha cosechadas)")
    ax.set_ylabel("departamentos")
    ax.grid(axis="x", visible=False)

    fig.tight_layout()
    fig.savefig("figures/04_brecha_rindes.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    Path("figures").mkdir(exist_ok=True)
    df = load_data()
    season = df["campania"].max()
    print(f"Records (soy/corn/wheat): {len(df):,} | "
          f"seasons: {df['campania'].min()} to {season}")

    plot_national_production(df)
    plot_yield(df)
    plot_provinces(df, season)
    plot_yield_gap(df, season)
    print("Figures written to figures/")


if __name__ == "__main__":
    main()
