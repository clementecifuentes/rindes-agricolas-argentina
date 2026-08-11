"""
Rindes agrícolas en Argentina: análisis histórico de soja, maíz y trigo
sobre las Estimaciones Agrícolas oficiales (1969 → hoy).

Producción nacional, evolución del rendimiento, ranking provincial y
brecha de rindes entre departamentos.

Uso:
    python src/analisis.py
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

# ── Estilo (paleta validada para accesibilidad) ──────────────────────────────
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"

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

CULTIVOS = {"soja total": "Soja", "maíz": "Maíz", "trigo total": "Trigo"}
COLORES = {"Soja": BLUE, "Maíz": ORANGE, "Trigo": AQUA}


def cargar_datos() -> pd.DataFrame:
    df = pd.read_csv("data/estimaciones.csv")
    df = df[df["cultivo"].isin(CULTIVOS)].copy()
    df["cultivo"] = df["cultivo"].map(CULTIVOS)
    for col in ("superficie_sembrada_ha", "superficie_cosechada_ha",
                "produccion_tm", "rendimiento_kgxha"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def fig_produccion_nacional(df: pd.DataFrame) -> None:
    serie = (df.groupby(["anio", "cultivo"])["produccion_tm"].sum()
             .div(1e6).unstack())

    fig, ax = plt.subplots(figsize=(10, 4.6))
    for cultivo in ("Soja", "Maíz", "Trigo"):
        ax.plot(serie.index, serie[cultivo], color=COLORES[cultivo],
                linewidth=2, label=cultivo)

    ax.set_title("Producción nacional por campaña (1969 → hoy)", loc="left", pad=12)
    ax.set_ylabel("millones de toneladas")
    ax.set_ylim(bottom=0)
    ax.set_xlim(serie.index.min(), serie.index.max() + 1)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_2, loc="upper left")

    fig.tight_layout()
    fig.savefig("figures/01_produccion_nacional.png", bbox_inches="tight")
    plt.close(fig)


def fig_rendimiento(df: pd.DataFrame) -> None:
    """Rendimiento nacional ponderado: producción total / superficie cosechada."""
    agg = df.groupby(["anio", "cultivo"]).agg(
        prod=("produccion_tm", "sum"), sup=("superficie_cosechada_ha", "sum"))
    agg["rinde"] = agg["prod"] / agg["sup"]  # tn/ha
    serie = agg["rinde"].unstack()

    fig, ax = plt.subplots(figsize=(10, 4.6))
    for cultivo in ("Soja", "Maíz", "Trigo"):
        ax.plot(serie.index, serie[cultivo], color=COLORES[cultivo],
                linewidth=2, label=cultivo)

    ax.set_title("Rendimiento nacional promedio por campaña", loc="left", pad=12)
    ax.set_ylabel("toneladas por hectárea")
    ax.set_ylim(bottom=0)
    ax.set_xlim(serie.index.min(), serie.index.max() + 1)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_2, loc="upper left")

    fig.tight_layout()
    fig.savefig("figures/02_rendimiento.png", bbox_inches="tight")
    plt.close(fig)


def fig_provincias(df: pd.DataFrame, campania: str) -> None:
    """Producción por provincia y cultivo en la última campaña completa."""
    ult = df[df["campania"] == campania]
    tabla = (ult.groupby(["provincia", "cultivo"])["produccion_tm"].sum()
             .div(1e6).unstack(fill_value=0))
    tabla["total"] = tabla.sum(axis=1)
    tabla = tabla.sort_values("total").tail(10)

    fig, ax = plt.subplots(figsize=(9.5, 5))
    base = pd.Series(0.0, index=tabla.index)
    for cultivo in ("Soja", "Maíz", "Trigo"):
        ax.barh(tabla.index, tabla[cultivo], left=base, height=0.62,
                color=COLORES[cultivo], label=cultivo,
                edgecolor=SURFACE, linewidth=1.2)
        base += tabla[cultivo]
    for y, total in enumerate(tabla["total"]):
        ax.annotate(f"{total:,.1f}", (total, y), textcoords="offset points",
                    xytext=(5, 0), va="center", fontsize=8.5, color=INK_2)

    ax.set_title(f"Producción por provincia — campaña {campania}",
                 loc="left", pad=14)
    ax.set_xlabel("millones de toneladas (soja + maíz + trigo)")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, tabla["total"].max() * 1.12)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK_2, loc="lower right")

    fig.tight_layout()
    fig.savefig("figures/03_provincias.png", bbox_inches="tight")
    plt.close(fig)


def fig_brecha_rindes(df: pd.DataFrame, campania: str) -> None:
    """Distribución del rinde de soja por departamento en la última campaña."""
    soja = df[(df["campania"] == campania) & (df["cultivo"] == "Soja")
              & (df["superficie_cosechada_ha"] > 1000)].copy()
    soja["rinde"] = soja["produccion_tm"] / soja["superficie_cosechada_ha"]
    nacional = soja["produccion_tm"].sum() / soja["superficie_cosechada_ha"].sum()

    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ax.hist(soja["rinde"], bins=32, color=BLUE, edgecolor=SURFACE, linewidth=0.8)
    ax.axvline(nacional, color=INK, linewidth=1.2, linestyle="--")
    ax.annotate(f"promedio nacional: {nacional:.2f} tn/ha",
                (nacional, ax.get_ylim()[1] * 0.95),
                textcoords="offset points", xytext=(8, 0),
                fontsize=9, color=INK)

    ax.set_title(f"Brecha de rindes en soja por departamento — campaña {campania}",
                 loc="left", pad=12)
    ax.set_xlabel("toneladas por hectárea (departamentos con +1.000 ha cosechadas)")
    ax.set_ylabel("departamentos")
    ax.grid(axis="x", visible=False)

    fig.tight_layout()
    fig.savefig("figures/04_brecha_rindes.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = cargar_datos()
    campania = df["campania"].max()
    print(f"Registros (soja/maíz/trigo): {len(df):,} | "
          f"campañas: {df['campania'].min()} → {campania}")

    fig_produccion_nacional(df)
    fig_rendimiento(df)
    fig_provincias(df, campania)
    fig_brecha_rindes(df, campania)
    print("Figuras generadas en figures/")


if __name__ == "__main__":
    main()
