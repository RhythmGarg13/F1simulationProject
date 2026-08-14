"""
optimizer.py — F1 Race Strategy Simulation Engine
==================================================
Race time optimization engine using scipy.optimize.

Core objective: Find the optimal pit-stop schedule that minimises total race
time subject to F1 sporting regulations and tire physics constraints.

Mathematical framework:
  Minimise: f(x) = sum(lap_times(x)) + sum(pit_time_losses(x))

  Subject to constraint functions g(x):
    g1(x): Tire age <= compound cliff threshold    [hard constraint]
    g2(x): Must use >= 2 different compounds       [sporting regulation]
    g3(x): Pit window validity                     [race strategy bounds]
    g4(x): Monotonicity (pit laps must increase)   [logical constraint]

Optimisation method: SLSQP (Sequential Least-Squares Programming)
  - Handles non-linear objectives + constraints
  - Gradient-based: exploits the smooth nature of tire degradation curves
  - Industry-standard for this class of race strategy problem

Performance notes:
  - Degradation offsets are precomputed per compound/weather before the
    optimisation loop runs, giving O(1) per-lap cost inside _total_race_time.
  - Candidate SLSQP runs are executed in parallel via ThreadPoolExecutor.
  - Candidate count is capped at ~15-20 per weather type to bound runtime.

Libraries: scipy.optimize, numpy, concurrent.futures.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import numpy as np
from scipy.linalg import norm
from scipy.optimize import minimize

from models import (
    CarState, TireCompoundName, WeatherCondition, WeatherType, Track
)
from monte_carlo import (
    TIRE_COMPOUNDS, calculate_tire_degradation, generate_race_lap_data,
    simulate_race, get_degradation_lookup,
)

logger = logging.getLogger("f1_engine.optimizer")

# Maximum number of candidate strategies evaluated per weather type.
# Prevents the search space from growing unboundedly with wide pit windows.
_MAX_CANDIDATES = 18


# ─────────────────────────────────────────────────────────────────────────────
# Strategy Candidate Generator
# ─────────────────────────────────────────────────────────────────────────────

def _get_candidate_strategies(
    track: Track,
    weather: WeatherCondition,
) -> list[dict]:
    """
    Generate a bounded set of candidate strategies based on track
    characteristics and weather conditions (capped at _MAX_CANDIDATES).

    In dry conditions: 1-stop and 2-stop strategies with Soft/Medium/Hard.
    In light rain: strategies incorporating Intermediate compound.
    In heavy rain: Wet-tire strategies.

    Returns a list of dicts, each with 'pit_laps' and 'compounds'.
    """
    total = track.total_laps
    candidates: list[dict] = []

    if weather.weather_type == WeatherType.DRY:
        pit_min = track.pit_entry_lap_min
        pit_max = track.pit_entry_lap_max
        pit_range = pit_max - pit_min

        # Adaptive step size so 1-stop candidates stay within _MAX_CANDIDATES // 2
        step_1stop = max(3, pit_range // 6)

        # ── 1-Stop Strategies ─────────────────────────────────────────────
        for pit1 in range(pit_min, pit_max, step_1stop):
            candidates.append({
                "pit_laps": [pit1],
                "compounds": [TireCompoundName.MEDIUM, TireCompoundName.HARD],
            })
            candidates.append({
                "pit_laps": [pit1],
                "compounds": [TireCompoundName.SOFT, TireCompoundName.MEDIUM],
            })
            candidates.append({
                "pit_laps": [pit1],
                "compounds": [TireCompoundName.SOFT, TireCompoundName.HARD],
            })

        # ── 2-Stop Strategies — at most 3 combinations ────────────────────
        mid = total // 3
        for pit1 in range(pit_min, mid, max(5, (mid - pit_min) // 2)):
            for pit2 in range(pit1 + 10, pit_max, max(6, (pit_max - pit1 - 10) // 2)):
                candidates.append({
                    "pit_laps": [pit1, pit2],
                    "compounds": [TireCompoundName.SOFT, TireCompoundName.MEDIUM, TireCompoundName.HARD],
                })
                candidates.append({
                    "pit_laps": [pit1, pit2],
                    "compounds": [TireCompoundName.SOFT, TireCompoundName.SOFT, TireCompoundName.MEDIUM],
                })

    elif weather.weather_type == WeatherType.LIGHT_RAIN:
        step = max(5, (total // 2 - 10) // 4)
        for pit1 in range(10, total // 2, step):
            candidates.append({
                "pit_laps": [pit1],
                "compounds": [TireCompoundName.INTER, TireCompoundName.MEDIUM],
            })
            candidates.append({
                "pit_laps": [pit1],
                "compounds": [TireCompoundName.INTER, TireCompoundName.HARD],
            })
        candidates.append({
            "pit_laps": [total // 2],
            "compounds": [TireCompoundName.INTER, TireCompoundName.INTER],
        })

    else:  # HEAVY_RAIN
        step = max(6, (total // 2 - 15) // 3)
        for pit1 in range(15, total // 2, step):
            candidates.append({
                "pit_laps": [pit1],
                "compounds": [TireCompoundName.WET, TireCompoundName.INTER],
            })
        candidates.append({
            "pit_laps": [total // 2],
            "compounds": [TireCompoundName.WET, TireCompoundName.WET],
        })

    # Hard cap — take the first _MAX_CANDIDATES to bound worst-case runtime
    return candidates[:_MAX_CANDIDATES]


# ─────────────────────────────────────────────────────────────────────────────
# Objective Function
# ─────────────────────────────────────────────────────────────────────────────

def _total_race_time(
    pit_laps_continuous: np.ndarray,
    track: Track,
    compound_sequence: list[TireCompoundName],
    weather: WeatherCondition,
    lookups: dict[TireCompoundName, np.ndarray],
) -> float:
    """
    Objective function f(x) = sum(lap_times) + sum(pit_time_losses)

    Takes continuous pit lap values (for gradient computation by SLSQP),
    rounds to nearest integer for simulation, and returns scalar total time.

    Uses precomputed degradation lookups for O(1) per-lap cost.
    """
    pit_laps = sorted(set(
        int(round(p)) for p in np.clip(pit_laps_continuous, 1, track.total_laps - 1)
    ))

    result = simulate_race(
        track, pit_laps, compound_sequence, weather,
        rng=None, noise_scale=0.0,
    )
    return result["total_time_s"]


# ─────────────────────────────────────────────────────────────────────────────
# Constraint Functions g(x)
# ─────────────────────────────────────────────────────────────────────────────

def _constraint_tire_life_g1(
    pit_laps: np.ndarray,
    track: Track,
    compound_sequence: list[TireCompoundName],
) -> np.ndarray:
    """
    g1(x): Tire age constraint — each stint must not exceed compound's max_laps.

    g1_i(x) = max_laps_i - stint_length_i >= 0  (feasibility requires g >= 0)

    Prevents tire catastrophic failure ('going off the cliff').
    """
    pit_laps_int = sorted(set(int(round(p)) for p in pit_laps))
    stints: list[int] = []

    prev = 0
    for p in pit_laps_int:
        stints.append(p - prev)
        prev = p
    stints.append(track.total_laps - prev)

    values = []
    for i, (stint_len, compound) in enumerate(zip(stints, compound_sequence)):
        max_laps = TIRE_COMPOUNDS[compound].max_laps
        values.append(float(max_laps - stint_len))

    return np.array(values)


def _constraint_min_gap_g3(pit_laps: np.ndarray) -> float:
    """
    g3(x): Minimum gap between pit stops >= 5 laps.

    g3(x) = min_i(x_{i+1} - x_i) - 5 >= 0

    Prevents physically impossible back-to-back pit stops.
    """
    if len(pit_laps) < 2:
        return 1.0
    sorted_pits = np.sort(pit_laps)
    gaps = np.diff(sorted_pits)
    return float(np.min(gaps) - 5.0)


def _constraint_pit_window_g4(
    pit_laps: np.ndarray,
    track: Track,
) -> float:
    """
    g4(x): All pit laps must be within valid pit window [min, max].

    g4(x) = (x_i - pit_min) * (pit_max - x_i) >= 0 for all i
    """
    pit_min = track.pit_entry_lap_min
    pit_max = track.pit_entry_lap_max
    return float(np.min(
        (pit_laps - pit_min) * (pit_max - pit_laps)
    ))


def _compute_constraint_gradient_norm(
    x: np.ndarray,
    track: Track,
    compound_sequence: list[TireCompoundName],
    eps: float = 0.5,
) -> float:
    """
    Compute the Euclidean norm ||grad g(x)||_2 of the combined constraint
    gradient evaluated at the solution point x.

    This is a post-hoc diagnostic of constraint sensitivity at the solution —
    it describes how quickly the constraint functions change near the optimum.
    It is NOT the convergence criterion used by SLSQP; scipy's internal ftol
    parameter drives convergence during the optimisation.

    Uses finite-difference approximation of the constraint gradient.
    """
    g1 = _constraint_tire_life_g1(x, track, compound_sequence)
    g3 = _constraint_min_gap_g3(x)
    g4 = _constraint_pit_window_g4(x, track)
    g_combined = np.concatenate([g1, [g3, g4]])

    grad = np.zeros(len(x))
    for i in range(len(x)):
        x_plus = x.copy(); x_plus[i] += eps
        g_plus = np.concatenate([
            _constraint_tire_life_g1(x_plus, track, compound_sequence),
            [_constraint_min_gap_g3(x_plus), _constraint_pit_window_g4(x_plus, track)]
        ])
        x_minus = x.copy(); x_minus[i] -= eps
        g_minus = np.concatenate([
            _constraint_tire_life_g1(x_minus, track, compound_sequence),
            [_constraint_min_gap_g3(x_minus), _constraint_pit_window_g4(x_minus, track)]
        ])
        grad[i] = np.sum(np.abs(g_plus - g_minus)) / (2 * eps)

    return float(norm(grad, ord=2))


# ─────────────────────────────────────────────────────────────────────────────
# Per-candidate SLSQP worker (runs in thread pool)
# ─────────────────────────────────────────────────────────────────────────────

def _optimise_candidate(
    candidate: dict,
    track: Track,
    weather: WeatherCondition,
    lookups: dict[TireCompoundName, np.ndarray],
) -> tuple[float, object, dict]:
    """
    Run SLSQP for a single candidate strategy.

    Returns (best_time, scipy_result, candidate).
    Designed to be called in a thread pool; each candidate is independent.
    """
    pit_laps = candidate["pit_laps"]
    compounds = candidate["compounds"]

    if not pit_laps:
        return (float("inf"), None, candidate)

    x0 = np.array(pit_laps, dtype=float)

    constraints = [
        {
            "type": "ineq",
            "fun": lambda x, t=track, c=compounds: _constraint_tire_life_g1(x, t, c),
        },
        {
            "type": "ineq",
            "fun": lambda x: _constraint_min_gap_g3(x),
        },
        {
            "type": "ineq",
            "fun": lambda x, t=track: _constraint_pit_window_g4(x, t),
        },
    ]

    bounds = [(track.pit_entry_lap_min, track.pit_entry_lap_max)] * len(pit_laps)

    result = minimize(
        fun=_total_race_time,
        x0=x0,
        args=(track, compounds, weather, lookups),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-6, "maxiter": 150, "disp": False},
    )

    time = result.fun if result.success else float("inf")
    return (time, result, candidate)


# ─────────────────────────────────────────────────────────────────────────────
# Main Optimisation Function
# ─────────────────────────────────────────────────────────────────────────────

def optimize_race_time(
    track: Track,
    weather: WeatherCondition,
    n_simulations: int = 5000,
) -> dict:
    """
    Find the optimal pit-stop strategy minimising total race time.

    Algorithm:
    1. Generate candidate strategies (warm-start for SLSQP)
    2. Precompute degradation lookups for all compounds
    3. Run all candidate SLSQP optimisations in parallel (ThreadPoolExecutor)
    4. Select best converged solution
    5. Evaluate ||grad g(x)||_2 at solution as a constraint-sensitivity diagnostic
    6. Run Monte Carlo around the optimal strategy for confidence intervals

    Parameters
    ----------
    track : Track
    weather : WeatherCondition
        Changing weather triggers full re-optimisation
    n_simulations : int
        Monte Carlo iterations for confidence interval calculation

    Returns
    -------
    dict with optimal_pit_laps, optimal_compounds, optimal_time_s,
    converged, n_iterations, constraint_norm, monte_carlo_result
    """
    from monte_carlo import run_monte_carlo

    candidates = _get_candidate_strategies(track, weather)
    if not candidates:
        raise ValueError(f"No viable candidates for track {track.track_id!r}")

    # Precompute degradation lookups once — shared by all parallel workers
    all_compounds = set()
    for c in candidates:
        all_compounds.update(c["compounds"])
    lookups = {
        comp: get_degradation_lookup(comp, weather, max_lap=track.total_laps + 5)
        for comp in all_compounds
    }

    best_time = float("inf")
    best_result = None
    best_candidate: Optional[dict] = None
    total_iterations = 0

    # Run candidate optimisations in parallel — each is independent
    with ThreadPoolExecutor(max_workers=min(4, len(candidates))) as pool:
        futures = {
            pool.submit(_optimise_candidate, cand, track, weather, lookups): cand
            for cand in candidates
        }
        for future in as_completed(futures):
            try:
                time, result, candidate = future.result()
            except Exception as exc:
                logger.warning("Candidate optimisation failed: %s", exc)
                continue

            if result is not None:
                total_iterations += result.nit

            if result is not None and result.success and time < best_time:
                best_time = time
                best_result = result
                best_candidate = candidate

    # Fallback: if SLSQP failed for all candidates, score analytically
    if best_candidate is None:
        logger.warning("SLSQP failed for all candidates — falling back to analytical scoring")
        scored = []
        for c in candidates:
            t = _total_race_time(
                np.array(c["pit_laps"], dtype=float),
                track, c["compounds"], weather, lookups,
            )
            scored.append((t, c))
        scored.sort(key=lambda x: x[0])
        best_time, best_candidate = scored[0]
        best_result = None

    optimal_pit_laps = [
        int(round(p)) for p in
        (best_result.x if best_result is not None else best_candidate["pit_laps"])
    ]
    optimal_compounds = best_candidate["compounds"]

    # Constraint sensitivity diagnostic at the solution
    x_opt = np.array(optimal_pit_laps, dtype=float)
    constraint_norm = _compute_constraint_gradient_norm(x_opt, track, optimal_compounds)

    # Monte Carlo simulation around the optimal strategy
    mc_result = run_monte_carlo(
        track, optimal_pit_laps, optimal_compounds, weather, n_simulations
    )

    lap_df = generate_race_lap_data(track, optimal_pit_laps, optimal_compounds, weather)

    return {
        "optimal_pit_laps": optimal_pit_laps,
        "optimal_compounds": optimal_compounds,
        "optimal_time_s": best_time,
        "converged": bool(best_result.success) if best_result else False,
        "n_iterations": total_iterations,
        "constraint_norm": constraint_norm,
        "monte_carlo": mc_result,
        "lap_df": lap_df,
    }
