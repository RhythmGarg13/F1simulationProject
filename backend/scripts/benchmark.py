"""
benchmark.py — F1 Race Strategy Engine performance benchmark.

Measures the wall-clock time of the full optimize_race_time() pipeline
across multiple tracks and weather conditions. Run this script to validate
that Phase 2 performance targets are met.

Usage:
    cd backend
    python scripts/benchmark.py

Performance target: < 5 seconds per optimization call.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import WeatherCondition, WeatherType
from track_data import get_track, list_tracks
from optimizer import optimize_race_time

BENCHMARK_CONFIGS = [
    ("suzuka",       WeatherType.DRY,        "Suzuka — DRY"),
    ("monza",        WeatherType.DRY,        "Monza — DRY"),
    ("albert_park",  WeatherType.LIGHT_RAIN, "Albert Park — LIGHT_RAIN"),
    ("suzuka",       WeatherType.HEAVY_RAIN, "Suzuka — HEAVY_RAIN"),
    ("monaco",       WeatherType.DRY,        "Monaco — DRY"),
]

N_SIMULATIONS = 500


def run_benchmark():
    print("=" * 60)
    print("F1 Race Strategy Engine — Performance Benchmark")
    print(f"n_simulations={N_SIMULATIONS}  Target: <5s per run")
    print("=" * 60)

    results = []
    all_pass = True

    for track_id, weather_type, label in BENCHMARK_CONFIGS:
        track = get_track(track_id)
        weather = WeatherCondition(weather_type=weather_type)

        # Warm up the lookup cache
        t0 = time.perf_counter()
        result = optimize_race_time(track, weather, n_simulations=N_SIMULATIONS)
        elapsed = time.perf_counter() - t0

        passed = elapsed < 5.0
        if not passed:
            all_pass = False

        status = "[PASS]" if passed else "[FAIL]"
        results.append((label, elapsed, result["converged"], passed))

        print(
            f"{status}  {label:<30s}  "
            f"{elapsed:5.2f}s  "
            f"pits={result['optimal_pit_laps']}  "
            f"converged={result['converged']}"
        )

    print("=" * 60)
    total = sum(r[1] for r in results)
    print(f"Total: {total:.2f}s  |  {'ALL PASS' if all_pass else 'SOME FAILURES'}")

    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    run_benchmark()
