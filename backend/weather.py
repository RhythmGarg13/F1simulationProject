"""
weather.py — F1 Race Strategy Simulation Engine
================================================
Dynamic weather logic module.

When weather conditions change via the frontend toggle, this module:
  1. Validates and normalizes the incoming WeatherRequest
  2. Adjusts track-specific parameters (e.g., slippery surface = longer lap times)
  3. Selects the most appropriate starting tire compound for the new conditions
  4. Generates a human-readable strategy note explaining the weather impact

The returned WeatherCondition object is passed to the full re-optimization
pipeline (optimize_race_time), which recalculates the entire race strategy.

All functions are pure (no side effects) and independently testable.
"""

from __future__ import annotations

from models import WeatherCondition, WeatherType, TireCompoundName, WeatherRequest


def build_weather_condition(req: WeatherRequest) -> WeatherCondition:
    """Convert a frontend WeatherRequest into the internal WeatherCondition dataclass."""
    return WeatherCondition(
        weather_type=req.weather_type,
        air_temp_c=req.air_temp_c,
        track_temp_c=req.track_temp_c,
        rain_intensity=req.rain_intensity,
        wind_speed_kph=req.wind_speed_kph,
    )


def select_starting_compound(weather: WeatherCondition) -> TireCompoundName:
    """
    Determine the optimal starting tire compound based on weather conditions.

    Decision logic:
    - Heavy rain (intensity > 0.7)    → WET
    - Light rain (intensity 0.2–0.7)  → INTERMEDIATE
    - Cool dry track (< 30°C)         → MEDIUM (cold track = less thermal load, soft risky)
    - Hot dry track (≥ 30°C)          → SOFT (maximize early pace)
    
    This is the 'Dynamic Weather' requirement: compound selection must update
    instantly when the weather panel changes.
    """
    if weather.weather_type == WeatherType.HEAVY_RAIN or weather.rain_intensity > 0.7:
        return TireCompoundName.WET

    if weather.weather_type == WeatherType.LIGHT_RAIN or weather.rain_intensity > 0.2:
        return TireCompoundName.INTER

    # Dry conditions — temperature-based compound selection
    if weather.track_temp_c < 30:
        return TireCompoundName.MEDIUM   # Cold track → grip from Medium, Soft may blister

    return TireCompoundName.SOFT  # Hot dry → maximize early pace on Softs


def get_weather_note(weather: WeatherCondition, prev_weather: WeatherCondition | None = None) -> str:
    """
    Generate a human-readable strategic note about the weather conditions.

    If prev_weather is provided, the note describes what changed and why the
    strategy updated — shown in the 'Dynamic Strategy Adjustments' card.
    """
    type_map = {
        WeatherType.DRY: "Dry",
        WeatherType.LIGHT_RAIN: "Light Rain",
        WeatherType.HEAVY_RAIN: "Heavy Rain",
    }
    current_desc = type_map[weather.weather_type]

    base_notes = {
        WeatherType.DRY: (
            f"Track temp: {weather.track_temp_c:.0f}°C — "
            f"Dry conditions favor aggressive Soft-tire strategy. "
            f"Tire thermal management is critical above {weather.track_temp_c:.0f}°C."
        ),
        WeatherType.LIGHT_RAIN: (
            f"Track temp: {weather.track_temp_c:.0f}°C — "
            f"Light rain detected (intensity: {weather.rain_intensity:.0%}). "
            f"Intermediate tires recommended. Strategy window is compressed — "
            f"track conditions may dry, forcing an early switch decision."
        ),
        WeatherType.HEAVY_RAIN: (
            f"Track temp: {weather.track_temp_c:.0f}°C — "
            f"Heavy rain (intensity: {weather.rain_intensity:.0%}). "
            f"Full Wet tires mandatory. Race distance may be shortened. "
            f"Safety car deployment probability significantly elevated."
        ),
    }

    note = base_notes[weather.weather_type]

    if prev_weather and prev_weather.weather_type != weather.weather_type:
        prev_desc = type_map[prev_weather.weather_type]
        note = (
            f"⚡ Weather change: {prev_desc} → {current_desc}. "
            f"Full strategy re-optimization triggered. " + note
        )

    return note


def compute_weather_lap_time_penalty(weather: WeatherCondition) -> float:
    """
    Compute the additional lap time (seconds) added by current weather
    to the base lap time — beyond what tire compound selection handles.

    This models: standing water, aquaplaning risk, reduced visibility.
    """
    if weather.weather_type == WeatherType.DRY:
        return 0.0

    # Base penalty from rain intensity (exponential: light rain has small effect,
    # heavy rain has massive effect on lap times)
    rain_penalty = weather.rain_intensity ** 1.6 * 8.5  # up to ~8.5s in monsoon

    # Wind penalty (crosswinds destabilize car — especially on high-speed corners)
    wind_penalty = max(0, (weather.wind_speed_kph - 20) * 0.04)

    return round(rain_penalty + wind_penalty, 3)
