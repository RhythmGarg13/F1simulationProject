"""
visualizations.py — F1 Race Strategy Simulation Engine
========================================================
Seaborn and Matplotlib visualization generation.

Generates server-side comparative charts and returns them as base64-encoded
PNG strings embedded in the API response. The frontend renders these in
<img> tags — no additional chart library needed for static analyses.

Charts generated:
  1. Tire Degradation Curves — all compounds overlaid (Seaborn lineplot)
  2. Monte Carlo Lap Time Distribution — histogram of simulated race times
  3. Strategy Comparison — bar chart comparing 1-stop vs 2-stop strategies

Each function is independently testable and produces figures with
consistent F1-themed styling (dark background, compound colour palette).

Libraries: seaborn, matplotlib.
"""

from __future__ import annotations

import io
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # Non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from monte_carlo import TIRE_COMPOUNDS
from models import TireCompoundName


# ─────────────────────────────────────────────────────────────────────────────
# Shared Styling
# ─────────────────────────────────────────────────────────────────────────────

_F1_STYLE = {
    "axes.facecolor":      "#f8f9ff",
    "figure.facecolor":    "#ffffff",
    "axes.edgecolor":      "#d0d5e8",
    "axes.labelcolor":     "#1a1f3a",
    "xtick.color":         "#4a5568",
    "ytick.color":         "#4a5568",
    "text.color":          "#1a1f3a",
    "axes.spines.top":     False,
    "axes.spines.right":   False,
    "axes.grid":           True,
    "grid.color":          "#e8ecf5",
    "grid.linestyle":      "--",
    "grid.alpha":          0.7,
    "font.family":         "DejaVu Sans",
}


def _to_base64(fig: plt.Figure) -> str:
    """Convert a Matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


# ─────────────────────────────────────────────────────────────────────────────
# 1. Tire Degradation Curves (Seaborn)
# ─────────────────────────────────────────────────────────────────────────────

def plot_degradation_curves(max_laps: int = 50) -> str:
    """
    Generate a Seaborn lineplot showing the non-linear degradation curves
    for all tire compounds up to max_laps.

    This is the 'comparative visualization' from the resume:
      'Accurately predicted non-linear tire degradation curves and lap-time offsets'
      'designed comparative visualizations'
    """
    plt.rcParams.update(_F1_STYLE)

    laps = np.arange(0, max_laps + 1)
    records = []

    for compound_name, compound in TIRE_COMPOUNDS.items():
        deg = (
            compound.alpha * (laps ** compound.beta) +
            compound.gamma * np.exp(compound.delta * np.clip(laps, 0, compound.cliff_lap * 1.2))
        )
        for lap, d in zip(laps, deg):
            records.append({
                "Lap": lap,
                "Lap Time Delta (s)": d + compound.base_pace_delta,
                "Compound": compound_name.value,
            })

    df = pd.DataFrame(records)

    compound_colors = {
        "SOFT":         "#FF1801",
        "MEDIUM":       "#D4AF00",
        "HARD":         "#888888",
        "INTERMEDIATE": "#39B54A",
        "WET":          "#0067FF",
    }

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.lineplot(
        data=df, x="Lap", y="Lap Time Delta (s)",
        hue="Compound", palette=compound_colors,
        linewidth=2.5, ax=ax
    )

    # Highlight cliff zones with vertical shading
    for compound_name, compound in TIRE_COMPOUNDS.items():
        ax.axvline(x=compound.cliff_lap, color=compound_colors[compound_name.value],
                   linestyle=":", alpha=0.4, linewidth=1)

    ax.set_title("Tire Degradation Curves — All Compounds", fontsize=13,
                 fontweight="bold", pad=15, color="#1a1f3a")
    ax.set_xlabel("Tire Age (Laps)", fontsize=11)
    ax.set_ylabel("Lap Time Delta (s)", fontsize=11)
    ax.legend(title="Compound", bbox_to_anchor=(1.02, 1), loc="upper left",
              frameon=True, framealpha=0.9)

    # Add annotation for cliff zones
    ax.text(0.98, 0.98, "Dotted lines = Degradation cliff threshold",
            transform=ax.transAxes, fontsize=8, ha="right", va="top",
            color="#6b7280", style="italic")

    fig.tight_layout()
    return _to_base64(fig)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Monte Carlo Lap Time Distribution (Seaborn)
# ─────────────────────────────────────────────────────────────────────────────

def plot_monte_carlo_distribution(
    race_times: np.ndarray,
    optimal_time: float,
    track_name: str,
) -> str:
    """
    Generate a Seaborn histogram showing the distribution of simulated
    total race times from the Monte Carlo engine.

    Annotates the optimal strategy time and 95% confidence interval.
    """
    plt.rcParams.update(_F1_STYLE)

    fig, ax = plt.subplots(figsize=(9, 4.5))

    sns.histplot(
        race_times / 60,   # Convert to minutes
        bins=60,
        color="#4F7FFF",
        alpha=0.75,
        kde=True,
        line_kws={"linewidth": 2, "color": "#1a1f3a"},
        ax=ax,
    )

    # Optimal time line
    ax.axvline(x=optimal_time / 60, color="#e10600", linewidth=2.5,
               linestyle="-", label=f"Optimal: {optimal_time/60:.1f} min")

    # 95% CI lines
    ci_low  = np.percentile(race_times, 2.5)  / 60
    ci_high = np.percentile(race_times, 97.5) / 60
    ax.axvline(x=ci_low,  color="#FF8C00", linewidth=1.5, linestyle="--",
               alpha=0.8, label=f"95% CI: [{ci_low:.1f}, {ci_high:.1f}] min")
    ax.axvline(x=ci_high, color="#FF8C00", linewidth=1.5, linestyle="--", alpha=0.8)

    # Shade CI region
    ax.axvspan(ci_low, ci_high, alpha=0.08, color="#FF8C00")

    ax.set_title(f"Monte Carlo Race Time Distribution — {track_name}\n"
                 f"N = {len(race_times):,} simulations", fontsize=12,
                 fontweight="bold", pad=12, color="#1a1f3a")
    ax.set_xlabel("Total Race Time (minutes)", fontsize=11)
    ax.set_ylabel("Simulation Count", fontsize=11)
    ax.legend(frameon=True, framealpha=0.9, fontsize=9)

    fig.tight_layout()
    return _to_base64(fig)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Lap Time Strategy Comparison (Matplotlib)
# ─────────────────────────────────────────────────────────────────────────────

def plot_strategy_comparison(
    lap_df: pd.DataFrame,
    pit_laps: list[int],
    track_name: str,
) -> str:
    """
    Generate a colored line chart showing per-lap times colored by tire compound.

    This is the 'Expected Lap Times' visualization showing how lap time
    evolves through the race with compound changes and pit stops.
    """
    plt.rcParams.update(_F1_STYLE)

    compound_colors = {
        "SOFT":         "#FF1801",
        "MEDIUM":       "#D4AF00",
        "HARD":         "#888888",
        "INTERMEDIATE": "#39B54A",
        "WET":          "#0067FF",
    }

    fig, ax = plt.subplots(figsize=(11, 5))

    # Plot line segments colored by compound
    compounds_seen = set()
    for compound_name, group in lap_df.groupby("tire_compound", sort=False):
        color = compound_colors.get(compound_name, "#888888")
        label = compound_name if compound_name not in compounds_seen else "_nolegend_"
        ax.plot(group["lap"], group["lap_time_s"],
                color=color, linewidth=2.2, label=label, alpha=0.9)
        compounds_seen.add(compound_name)

    # Pit stop markers
    for pit_lap in pit_laps:
        ax.axvline(x=pit_lap, color="#1a1f3a", linewidth=1.5,
                   linestyle="--", alpha=0.5)
        ax.text(pit_lap + 0.3,
                ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05,
                f"PIT L{pit_lap}", fontsize=7.5, color="#1a1f3a",
                rotation=90, va="bottom", alpha=0.8)

    # Legend patches for compounds
    patches = [
        mpatches.Patch(color=compound_colors.get(c, "#888"), label=c)
        for c in lap_df["tire_compound"].unique()
    ]
    ax.legend(handles=patches, title="Compound", frameon=True, framealpha=0.9,
              loc="upper right", fontsize=9)

    ax.set_title(f"Expected Lap Times by Compound — {track_name}",
                 fontsize=13, fontweight="bold", pad=12, color="#1a1f3a")
    ax.set_xlabel("Lap Number", fontsize=11)
    ax.set_ylabel("Lap Time (s)", fontsize=11)
    ax.margins(x=0.02)

    fig.tight_layout()
    return _to_base64(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Bundled Generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_all_visualizations(
    lap_df: pd.DataFrame,
    pit_laps: list[int],
    mc_times: np.ndarray,
    optimal_time: float,
    track_name: str,
    max_tire_laps: int = 50,
) -> dict[str, str]:
    """
    Generate all three Seaborn/Matplotlib charts and return as base64 PNGs.
    Called by the API endpoint to populate VisualizationData.
    """
    return {
        "degradation_curves_b64": plot_degradation_curves(max_tire_laps),
        "lap_time_distribution_b64": plot_monte_carlo_distribution(
            mc_times, optimal_time, track_name
        ),
        "strategy_comparison_b64": plot_strategy_comparison(
            lap_df, pit_laps, track_name
        ),
    }
