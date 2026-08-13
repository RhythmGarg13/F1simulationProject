"""
test_optimizer.py — Direct optimizer unit tests.

Tests optimize_race_time() directly (not through the API) for multiple
tracks and weather conditions, asserting constraint satisfaction and
performance bounds.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import time
import pytest
from models import WeatherCondition, WeatherType
from track_data import get_track
from optimizer import optimize_race_time
from monte_carlo import TIRE_COMPOUNDS


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _assert_strategy_valid(result: dict, track):
    """Assert all constraint conditions on an optimizer result."""
    pit_laps = result["optimal_pit_laps"]
    compounds = result["optimal_compounds"]

    # Non-empty pit schedule
    assert len(pit_laps) > 0, "Expected at least one pit stop"
    assert len(compounds) >= 2, "Expected at least two compounds"

    # Positive race time
    assert result["optimal_time_s"] > 0

    # g1: All pit laps within track's valid pit window
    for lap in pit_laps:
        assert track.pit_entry_lap_min <= lap <= track.pit_entry_lap_max, (
            f"Pit lap {lap} outside window [{track.pit_entry_lap_min}, {track.pit_entry_lap_max}]"
        )

    # g2: At least 2 distinct compounds (F1 sporting regulation for DRY/mixed conditions)
    # In heavy rain, WET+WET is a valid strategy — regulation only mandates 2 compounds in dry
    from models import WeatherType
    distinct = set(compounds)
    # Only enforce 2 compounds when we're not in a pure wet-tire scenario
    all_wet = all(c.value in ("WET", "INTERMEDIATE") for c in distinct)
    if not all_wet:
        assert len(distinct) >= 2, f"Only one compound used in non-rain condition: {distinct}"

    # g1 (tire life): No stint exceeds its compound's max_laps
    stints = []
    prev = 0
    for p in pit_laps:
        stints.append(p - prev)
        prev = p
    stints.append(track.total_laps - prev)

    for stint_len, compound in zip(stints, compounds):
        max_laps = TIRE_COMPOUNDS[compound].max_laps
        assert stint_len <= max_laps, (
            f"Stint of {stint_len} laps on {compound.value} exceeds max {max_laps}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_optimizer_suzuka_dry():
    track = get_track("suzuka")
    weather = WeatherCondition(weather_type=WeatherType.DRY)
    result = optimize_race_time(track, weather, n_simulations=200)
    _assert_strategy_valid(result, track)


def test_optimizer_monza_dry():
    track = get_track("monza")
    weather = WeatherCondition(weather_type=WeatherType.DRY)
    result = optimize_race_time(track, weather, n_simulations=200)
    _assert_strategy_valid(result, track)


def test_optimizer_suzuka_heavy_rain():
    track = get_track("suzuka")
    weather = WeatherCondition(
        weather_type=WeatherType.HEAVY_RAIN,
        rain_intensity=0.85,
        wind_speed_kph=30,
        air_temp_c=14,
        track_temp_c=16,
    )
    result = optimize_race_time(track, weather, n_simulations=200)
    _assert_strategy_valid(result, track)


def test_optimizer_light_rain():
    track = get_track("albert_park")
    weather = WeatherCondition(
        weather_type=WeatherType.LIGHT_RAIN,
        rain_intensity=0.35,
        wind_speed_kph=18,
    )
    result = optimize_race_time(track, weather, n_simulations=200)
    _assert_strategy_valid(result, track)


def test_optimizer_performance_under_5s():
    """Phase 2 regression guard: full optimization must complete in under 5 seconds."""
    track = get_track("suzuka")
    weather = WeatherCondition(weather_type=WeatherType.DRY)

    t0 = time.time()
    optimize_race_time(track, weather, n_simulations=200)
    elapsed = time.time() - t0

    assert elapsed < 5.0, f"Optimizer took {elapsed:.1f}s — exceeds 5s budget"


def test_optimizer_converged():
    track = get_track("suzuka")
    weather = WeatherCondition()
    result = optimize_race_time(track, weather, n_simulations=200)
    assert result["converged"] is True
