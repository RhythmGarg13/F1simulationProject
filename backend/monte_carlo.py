"""
monte_carlo.py — F1 Race Strategy Simulation Engine
=====================================================
Monte Carlo simulation engine for F1 race strategy prediction.

Core responsibilities:
  1. Implement the non-linear tire degradation model:
       deg(lap) = alpha * lap^beta + gamma * exp(delta * lap)
     This polynomial-exponential blend captures both the gradual wear phase
     and the exponential 'cliff' when a tire rapidly degrades.
  2. Precompute per-lap degradation offsets in a single vectorised call
     (one NumPy operation per stint, not one call per lap) for performance.
  3. Run N Monte Carlo simulations with randomised perturbations to generate
     a distribution of optimal race strategies and pit-stop windows.
  4. Provide a single shared simulate_race() function used by all callers
     (Monte Carlo engine, lap-data generator, and SLSQP objective) so the
     per-lap physics logic has exactly one implementation.

Libraries: numpy, pandas.
"""

from __future__ import annotations

import warnings
from typing import Optional
import numpy as np
import pandas as pd

from models import (
    CarState, TireCompound, TireCompoundName, WeatherCondition,
    WeatherType, Track
)
from weather import compute_weather_lap_time_penalty

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# Tire Compound Catalog
# ─────────────────────────────────────────────────────────────────────────────

TIRE_COMPOUNDS: dict[TireCompoundName, TireCompound] = {
    TireCompoundName.SOFT: TireCompound(
        name=TireCompoundName.SOFT,
        base_pace_delta=-0.85,          # 0.85 s faster than median
        alpha=0.008, beta=2.1,          # polynomial: moderate initial wear
        gamma=0.002, delta=0.22,        # exponential: steep cliff after lap 18
        cliff_lap=18, max_laps=25,
        wet_performance_factor=1.35,    # Soft is poor in wet
        color_hex="#FF1801"
    ),
    TireCompoundName.MEDIUM: TireCompound(
        name=TireCompoundName.MEDIUM,
        base_pace_delta=0.0,            # Baseline pace
        alpha=0.004, beta=1.85,
        gamma=0.0008, delta=0.16,
        cliff_lap=28, max_laps=40,
        wet_performance_factor=1.15,
        color_hex="#FFF200"
    ),
    TireCompoundName.HARD: TireCompound(
        name=TireCompoundName.HARD,
        base_pace_delta=0.60,           # 0.6 s slower than median
        alpha=0.002, beta=1.65,
        gamma=0.0003, delta=0.10,
        cliff_lap=42, max_laps=60,
        wet_performance_factor=1.20,
        color_hex="#FFFFFF"
    ),
    TireCompoundName.INTER: TireCompound(
        name=TireCompoundName.INTER,
        base_pace_delta=1.20,           # Slower in dry, optimal in light rain
        alpha=0.006, beta=1.90,
        gamma=0.001, delta=0.18,
        cliff_lap=30, max_laps=45,
        wet_performance_factor=0.65,    # Significantly better in wet
        color_hex="#39B54A"
    ),
    TireCompoundName.WET: TireCompound(
        name=TireCompoundName.WET,
        base_pace_delta=3.50,           # Much slower in dry conditions
        alpha=0.003, beta=1.70,
        gamma=0.0005, delta=0.12,
        cliff_lap=35, max_laps=50,
        wet_performance_factor=0.40,    # Designed for heavy rain
        color_hex="#0067FF"
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Precomputed Degradation Lookup
# ─────────────────────────────────────────────────────────────────────────────

def _build_degradation_lookup(
    compound: TireCompound,
    weather: WeatherCondition,
    max_lap: int = 70,
) -> np.ndarray:
    """
    Precompute lap-time offsets for laps 0..max_lap in a single vectorised
    NumPy call.  Returns an array where index i is the offset at tire age i.

    Analytical model:
        deg(lap) = alpha * lap^beta + gamma * exp(delta * lap)

    Weather multiplier adjusts for compound performance in rain:
        offset = deg * wet_performance_factor   (if not DRY)

    This avoids per-lap model calls inside tight simulation loops.
    """
    laps = np.arange(0, max_lap + 1, dtype=float)

    # Polynomial + exponential degradation
    analytical = (
        compound.alpha * (laps ** compound.beta)
        + compound.gamma * np.exp(compound.delta * np.clip(laps, 0, compound.cliff_lap * 1.3))
    )

    # Weather multiplier — wet compounds improve in rain, dry compounds suffer
    if weather.weather_type != WeatherType.DRY:
        analytical = analytical * compound.wet_performance_factor

    return analytical  # shape: (max_lap + 1,)


# Cache keyed by (compound_name, weather_type, track_temp_bucket) so the same
# lookup is reused across all laps of the same stint within one request.
_LOOKUP_CACHE: dict[tuple, np.ndarray] = {}


def get_degradation_lookup(
    compound_name: TireCompoundName,
    weather: WeatherCondition,
    max_lap: int = 70,
) -> np.ndarray:
    """Return (or build and cache) the precomputed degradation offset array."""
    # Bucket track temp to nearest 5°C so minor float variation doesn't bust cache
    temp_bucket = round(weather.track_temp_c / 5) * 5
    key = (compound_name, weather.weather_type, temp_bucket)
    if key not in _LOOKUP_CACHE:
        compound = TIRE_COMPOUNDS[compound_name]
        _LOOKUP_CACHE[key] = _build_degradation_lookup(compound, weather, max_lap)
    return _LOOKUP_CACHE[key]


def clear_lookup_cache() -> None:
    """Clear the precomputed lookup cache (call between requests if needed)."""
    _LOOKUP_CACHE.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Core Degradation Function
# ─────────────────────────────────────────────────────────────────────────────

def calculate_tire_degradation(
    car_state: CarState,
    weather: WeatherCondition,
    laps_ahead: int = 1,
) -> dict:
    """
    Calculate non-linear tire degradation and lap-time offset for the given car
    state and weather conditions.

    Mathematical model:
        deg(lap) = alpha * lap^beta + gamma * exp(delta * lap)

    Where:
        alpha, beta = polynomial coefficients (moderate-wear phase)
        gamma, delta = exponential coefficients (cliff / rapid-wear phase)

    This dual-term formulation captures:
      - Early laps: polynomial growth (alpha * lap^beta dominates)
      - Late laps: exponential growth (gamma * exp(delta * lap) dominates)
      - The 'cliff' emerges naturally from the exponential term

    Parameters
    ----------
    car_state : CarState
        Current state of the car (compound, tire age, fuel load)
    weather : WeatherCondition
        Current weather (temperature, rain intensity)
    laps_ahead : int
        How many laps ahead to project degradation

    Returns
    -------
    dict with keys:
        degradation_rate   — fraction of tire life consumed per lap
        lap_time_offset_s  — extra seconds added to lap time
        wear_pct           — cumulative tire wear percentage
        cliff_warning      — bool: approaching degradation cliff
        projected_df       — pandas DataFrame of per-lap projections
    """
    compound = TIRE_COMPOUNDS[car_state.tire_compound]
    current_age = car_state.tire_age_laps

    laps = np.arange(current_age, current_age + laps_ahead + 1)

    # Use precomputed lookup — O(1) per lap instead of a predict() call
    lookup = get_degradation_lookup(car_state.tire_compound, weather)
    # Clamp indices to lookup bounds
    clamped = np.clip(laps, 0, len(lookup) - 1).astype(int)
    offsets = lookup[clamped]

    # Degradation rate (fraction of max tire life consumed per lap)
    analytical_deg = (
        compound.alpha * (laps ** compound.beta)
        + compound.gamma * np.exp(compound.delta * np.clip(laps, 0, compound.cliff_lap * 1.3))
    )
    deg_rate = analytical_deg / compound.max_laps

    # Wear percentage
    wear_pct = np.clip((laps / compound.max_laps) * 100.0, 0, 100)

    projected_df = pd.DataFrame({
        "lap": laps,
        "tire_age": laps,
        "degradation_value": analytical_deg,
        "degradation_rate": deg_rate,
        "combined_lap_time_offset_s": offsets,
        "wear_pct": wear_pct,
    })

    cliff_warning = bool(current_age >= compound.cliff_lap * 0.85)

    return {
        "degradation_rate": float(deg_rate[0]),
        "lap_time_offset_s": float(offsets[0]),
        "wear_pct": float(wear_pct[0]),
        "cliff_warning": cliff_warning,
        "projected_df": projected_df,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Shared Race Simulation — Single Source of Truth
# ─────────────────────────────────────────────────────────────────────────────

def simulate_race(
    track: Track,
    pit_laps: list[int],
    compound_sequence: list[TireCompoundName],
    weather: WeatherCondition,
    rng: Optional[np.random.Generator] = None,
    noise_scale: float = 0.0,
) -> dict:
    """
    Single source of truth for simulating one race.

    Used by:
      - _simulate_single_race()    — Monte Carlo iterations (with noise)
      - generate_race_lap_data()   — Deterministic per-lap telemetry for charts
      - optimizer._total_race_time() — SLSQP objective function (deterministic)

    Parameters
    ----------
    track : Track
    pit_laps : list[int]
        Lap numbers at which pit stops occur (sorted ascending)
    compound_sequence : list[TireCompoundName]
        Tire compound for each stint (len = len(pit_laps) + 1)
    weather : WeatherCondition
    rng : np.random.Generator | None
        If None, no random noise is applied (deterministic mode).
    noise_scale : float
        Standard deviation of per-lap Gaussian noise (0 = deterministic).

    Returns
    -------
    dict with:
        total_time_s, lap_times, lap_records (list of per-lap dicts),
        pit_laps_applied, compound_sequence
    """
    # Build precomputed degradation lookups for each compound in this race
    lookups: dict[TireCompoundName, np.ndarray] = {
        c: get_degradation_lookup(c, weather, max_lap=track.total_laps + 5)
        for c in set(compound_sequence)
    }

    # Weather lap-time penalty — standing water, aquaplaning, wind effect
    weather_penalty = compute_weather_lap_time_penalty(weather)

    total_time = 0.0
    lap_times: list[float] = []
    lap_records: list[dict] = []

    current_compound = compound_sequence[0]
    compound_idx = 0
    tire_age = 0
    fuel_load = track.fuel_consumption_kg_per_lap * track.total_laps
    pit_set = set(pit_laps)
    pit_idx = 0

    for lap in range(1, track.total_laps + 1):
        # Pit stop on this lap?
        if pit_idx < len(pit_laps) and lap == pit_laps[pit_idx]:
            total_time += track.pit_loss_time_s
            compound_idx = min(compound_idx + 1, len(compound_sequence) - 1)
            current_compound = compound_sequence[compound_idx]
            tire_age = 0
            pit_idx += 1

        # Fuel decreases per lap
        fuel_load = max(0.0, fuel_load - track.fuel_consumption_kg_per_lap)

        # Tire degradation offset — O(1) lookup
        lookup = lookups[current_compound]
        clamped_age = min(tire_age, len(lookup) - 1)
        deg_offset = float(lookup[clamped_age])

        # Fuel load effect: ~0.035 s/kg above minimum
        fuel_delta = fuel_load * 0.035

        # Wear percentage for telemetry
        compound_obj = TIRE_COMPOUNDS[current_compound]
        wear_pct = min(100.0, (tire_age / compound_obj.max_laps) * 100.0)

        # Total lap time
        lap_time = (
            track.base_lap_time_s
            + deg_offset
            + fuel_delta
            + weather_penalty          # rain/wind penalty (0 if DRY)
        )

        # Stochastic perturbations (Monte Carlo mode only)
        if rng is not None and noise_scale > 0:
            lap_time += rng.normal(0, noise_scale)
            # Safety car event — ~20–35 s added
            if rng.random() < (track.safety_car_probability / track.total_laps):
                lap_time += rng.uniform(20, 35)

        total_time += lap_time
        lap_times.append(lap_time)

        lap_records.append({
            "lap": lap,
            "lap_time_s": round(lap_time - weather_penalty, 3),  # chart shows without weather penalty for clarity
            "tire_compound": current_compound.value,
            "tire_age": tire_age,
            "fuel_load_kg": round(fuel_load, 2),
            "tire_wear_pct": round(wear_pct, 1),
            "lap_time_delta_s": round(deg_offset, 3),
        })

        tire_age += 1

    return {
        "total_time_s": total_time,
        "lap_times": lap_times,
        "lap_records": lap_records,
        "pit_laps_applied": pit_laps,
        "compound_sequence": compound_sequence,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Single Race Simulation (Monte Carlo helper)
# ─────────────────────────────────────────────────────────────────────────────

def _simulate_single_race(
    track: Track,
    pit_laps: list[int],
    compound_sequence: list[TireCompoundName],
    weather: WeatherCondition,
    rng: np.random.Generator,
    noise_scale: float = 0.18,
) -> dict:
    """
    Simulate a single stochastic race.

    Perturbations per lap:
      - Gaussian lap-time noise (driver variation, traffic, micro-incidents)
      - Safety car probability events
    """
    # Vary pit windows ±2 laps around proposed schedule
    perturbed_pits = [
        max(1, min(track.total_laps - 1, lap + int(rng.integers(-2, 3))))
        for lap in pit_laps
    ]
    return simulate_race(
        track, perturbed_pits, compound_sequence, weather,
        rng=rng, noise_scale=noise_scale,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Monte Carlo Engine — Main Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def run_monte_carlo(
    track: Track,
    pit_schedule: list[int],
    compound_sequence: list[TireCompoundName],
    weather: WeatherCondition,
    n_simulations: int = 5000,
) -> dict:
    """
    Run N Monte Carlo simulations to generate a statistical distribution
    of race outcomes for a given pit stop strategy.

    Each simulation introduces randomised perturbations:
      - Per-lap Gaussian noise (driver variation, traffic)
      - Safety car probability events
      - ±2-lap jitter on pit window timings

    Parameters
    ----------
    track : Track
    pit_schedule : list[int]
        Lap numbers for each pit stop
    compound_sequence : list[TireCompoundName]
        Tire compound for each stint (len = len(pit_schedule) + 1)
    weather : WeatherCondition
    n_simulations : int
        Number of Monte Carlo iterations

    Returns
    -------
    dict with statistical summary and pit window distribution
    """
    rng = np.random.default_rng(seed=None)  # Non-deterministic across runs
    results: list[float] = []

    for _ in range(n_simulations):
        sim_result = _simulate_single_race(
            track, pit_schedule, compound_sequence, weather, rng
        )
        results.append(sim_result["total_time_s"])

    results_array = np.array(results)

    mean_time   = float(np.mean(results_array))
    std_time    = float(np.std(results_array))
    ci_low      = float(np.percentile(results_array, 2.5))
    ci_high     = float(np.percentile(results_array, 97.5))

    # Probability that the nominal strategy is within 5 s of optimal
    optimal_prob = float(np.mean(results_array < (np.min(results_array) + 5.0)))

    # Pit window distribution: Gaussian probability weights around each nominal pit lap
    pit_window_distribution: dict[str, list[dict]] = {}
    for i, nominal_lap in enumerate(pit_schedule):
        window_center = nominal_lap
        window = list(range(max(1, window_center - 5), min(track.total_laps, window_center + 6)))
        weights = np.exp(-0.5 * ((np.array(window) - nominal_lap) / 2.0) ** 2)
        weights = (weights / weights.sum()).tolist()
        pit_window_distribution[f"pit_{i+1}"] = [
            {"lap": lap, "probability": float(w)}
            for lap, w in zip(window, weights)
        ]

    return {
        "n_simulations": n_simulations,
        "mean_race_time_s": mean_time,
        "std_race_time_s": std_time,
        "confidence_interval_95_low": ci_low,
        "confidence_interval_95_high": ci_high,
        "optimal_strategy_probability": optimal_prob,
        "pit_window_distribution": pit_window_distribution,
        "all_times": results_array,   # Used for visualization
    }


# ─────────────────────────────────────────────────────────────────────────────
# Per-Lap Race Data Generation (for frontend charts)
# ─────────────────────────────────────────────────────────────────────────────

def generate_race_lap_data(
    track: Track,
    pit_laps: list[int],
    compound_sequence: list[TireCompoundName],
    weather: WeatherCondition,
) -> pd.DataFrame:
    """
    Generate deterministic per-lap telemetry data for the optimal strategy.

    Returns a Pandas DataFrame with one row per lap containing:
      lap, lap_time_s, tire_compound, tire_age, fuel_load_kg,
      tire_wear_pct, lap_time_delta_s

    Sent to the frontend for the 'Expected Lap Times' chart.
    """
    result = simulate_race(track, pit_laps, compound_sequence, weather,
                           rng=None, noise_scale=0.0)
    return pd.DataFrame(result["lap_records"])
