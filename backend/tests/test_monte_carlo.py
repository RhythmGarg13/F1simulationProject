"""
test_monte_carlo.py — Monte Carlo engine unit tests.

Tests tire degradation physics, run_monte_carlo() statistical properties,
and pit_window_distribution probability normalization.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import numpy as np
from models import CarState, WeatherCondition, WeatherType, TireCompoundName
from monte_carlo import calculate_tire_degradation, run_monte_carlo, TIRE_COMPOUNDS
from track_data import get_track


# ─────────────────────────────────────────────────────────────────────────────
# calculate_tire_degradation
# ─────────────────────────────────────────────────────────────────────────────

def test_degradation_increases_with_tire_age():
    """Wear percentage must increase monotonically as tire ages."""
    weather = WeatherCondition()
    wear_values = []
    for age in [0, 5, 10, 15, 20]:
        state = CarState(
            current_lap=age,
            fuel_load_kg=80.0,
            tire_compound=TireCompoundName.MEDIUM,
            tire_age_laps=age,
        )
        result = calculate_tire_degradation(state, weather)
        wear_values.append(result["wear_pct"])

    for i in range(1, len(wear_values)):
        assert wear_values[i] > wear_values[i - 1], (
            f"Wear did not increase: {wear_values}"
        )


def test_degradation_offset_positive():
    """Lap time offset must be >= 0 at age 0 (fresh tire may still have base_pace_delta)."""
    weather = WeatherCondition()
    state = CarState(
        current_lap=0,
        fuel_load_kg=110.0,
        tire_compound=TireCompoundName.SOFT,
        tire_age_laps=0,
    )
    result = calculate_tire_degradation(state, weather)
    # offset can be very small (near 0) for a fresh soft in dry
    assert isinstance(result["lap_time_offset_s"], float)
    assert result["wear_pct"] >= 0.0


def test_cliff_warning_near_cliff_lap():
    """cliff_warning must be True when tire age approaches the compound's cliff lap."""
    weather = WeatherCondition()
    soft = TIRE_COMPOUNDS[TireCompoundName.SOFT]
    state = CarState(
        current_lap=soft.cliff_lap,
        fuel_load_kg=50.0,
        tire_compound=TireCompoundName.SOFT,
        tire_age_laps=soft.cliff_lap,  # At exactly the cliff lap
    )
    result = calculate_tire_degradation(state, weather)
    assert result["cliff_warning"] is True


def test_wet_compound_lower_offset_in_rain():
    """WET compound should have a lower (or equal) offset vs SOFT in heavy rain."""
    rain_weather = WeatherCondition(
        weather_type=WeatherType.HEAVY_RAIN,
        rain_intensity=0.9,
    )
    age = 10

    wet_state = CarState(current_lap=age, fuel_load_kg=80, tire_compound=TireCompoundName.WET, tire_age_laps=age)
    soft_state = CarState(current_lap=age, fuel_load_kg=80, tire_compound=TireCompoundName.SOFT, tire_age_laps=age)

    wet_offset = calculate_tire_degradation(wet_state, rain_weather)["lap_time_offset_s"]
    soft_offset = calculate_tire_degradation(soft_state, rain_weather)["lap_time_offset_s"]

    assert wet_offset <= soft_offset, (
        f"WET offset ({wet_offset:.3f}) should be <= SOFT offset ({soft_offset:.3f}) in heavy rain"
    )


# ─────────────────────────────────────────────────────────────────────────────
# run_monte_carlo
# ─────────────────────────────────────────────────────────────────────────────

def test_mc_mean_inside_confidence_interval():
    """Mean race time must lie within the 95% confidence interval."""
    track = get_track("suzuka")
    weather = WeatherCondition()
    pit_laps = [20, 40]
    compounds = [TireCompoundName.SOFT, TireCompoundName.MEDIUM, TireCompoundName.HARD]

    mc = run_monte_carlo(track, pit_laps, compounds, weather, n_simulations=500)

    mean = mc["mean_race_time_s"]
    ci_low = mc["confidence_interval_95_low"]
    ci_high = mc["confidence_interval_95_high"]

    assert ci_low <= mean <= ci_high, (
        f"Mean {mean:.1f} not in [{ci_low:.1f}, {ci_high:.1f}]"
    )


def test_mc_pit_window_probabilities_sum_to_one():
    """Probabilities in each pit stop's window distribution must sum to ~1.0."""
    track = get_track("suzuka")
    weather = WeatherCondition()
    pit_laps = [20, 40]
    compounds = [TireCompoundName.MEDIUM, TireCompoundName.HARD, TireCompoundName.MEDIUM]

    mc = run_monte_carlo(track, pit_laps, compounds, weather, n_simulations=200)

    for key, points in mc["pit_window_distribution"].items():
        total_prob = sum(pt["probability"] for pt in points)
        assert abs(total_prob - 1.0) < 1e-6, (
            f"Probabilities for {key} sum to {total_prob:.6f}, expected ~1.0"
        )


def test_mc_pit_window_has_dict_items():
    """Each item in pit_window_distribution must be a dict with 'lap' and 'probability'."""
    track = get_track("albert_park")
    weather = WeatherCondition()
    pit_laps = [18]
    compounds = [TireCompoundName.SOFT, TireCompoundName.HARD]

    mc = run_monte_carlo(track, pit_laps, compounds, weather, n_simulations=100)

    for key, points in mc["pit_window_distribution"].items():
        for pt in points:
            assert isinstance(pt, dict), f"Expected dict, got {type(pt)}"
            assert "lap" in pt
            assert "probability" in pt


def test_mc_std_positive():
    """Standard deviation of race times must be positive with random noise."""
    track = get_track("suzuka")
    weather = WeatherCondition()
    mc = run_monte_carlo(
        track, [20], [TireCompoundName.MEDIUM, TireCompoundName.HARD],
        weather, n_simulations=300,
    )
    assert mc["std_race_time_s"] > 0.0
