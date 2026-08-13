"""
api.py — F1 Race Strategy Simulation Engine
============================================
FastAPI route definitions.

Routes:
  GET  /                        -> Health check
  GET  /tracks                  -> List all F1 2026 tracks
  GET  /tracks/{track_id}       -> Track metadata + key points
  POST /calculate_strategy      -> Full race strategy calculation (main endpoint)
  POST /update_weather          -> Weather-only re-optimisation (fast path)

All routes are async and non-blocking. Heavy computation (Monte Carlo +
SLSQP optimisation) is offloaded to a ThreadPoolExecutor to keep the event
loop free for concurrent requests.

Error handling: exceptions are logged server-side with full tracebacks;
clients receive a sanitised message that does not leak internal details.
"""

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models import (
    RaceRequest, StrategyResponse, WeatherRequest,
    LapDataPoint, PitStop, TireStint, TrackKeyPointResponse,
    MonteCarloStats, PitWindowPoint, VisualizationData, WeatherType, TireCompoundName,
    WeatherCondition,
)
from track_data import get_track, list_tracks, TRACKS
from monte_carlo import TIRE_COMPOUNDS
from optimizer import optimize_race_time
from weather import build_weather_condition, select_starting_compound, get_weather_note
from visualizations import generate_all_visualizations

from pydantic import BaseModel

logger = logging.getLogger("f1_engine.api")

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic request model for /update_weather
# ─────────────────────────────────────────────────────────────────────────────

class WeatherUpdateRequest(BaseModel):
    """Request body for the weather update endpoint."""
    track_id: str
    driver_name: str = "VER"
    team_name: str = "Red Bull Racing"
    prev_weather_type: str = "DRY"
    weather: WeatherRequest = WeatherRequest()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _format_time(total_seconds: float) -> str:
    """Format seconds as H:MM:SS.ss"""
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    secs = total_seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:05.2f}"
    return f"{minutes}:{secs:05.2f}"


def _build_strategy_response(
    request: RaceRequest,
    opt_result: dict,
    weather_note: str,
    strategy_delta: str | None = None,
) -> StrategyResponse:
    """
    Transform optimizer output into a fully structured StrategyResponse
    ready for JSON serialisation and consumption by the frontend.
    """
    track = get_track(request.track_id)
    weather = build_weather_condition(request.weather)

    optimal_pit_laps = opt_result["optimal_pit_laps"]
    optimal_compounds = opt_result["optimal_compounds"]
    lap_df = opt_result["lap_df"]
    mc = opt_result["monte_carlo"]

    # ── Per-lap data ───────────────────────────────────────────────────────
    lap_data = [
        LapDataPoint(
            lap=int(row["lap"]),
            lap_time_s=float(row["lap_time_s"]),
            tire_compound=TireCompoundName(row["tire_compound"]),
            tire_age=int(row["tire_age"]),
            fuel_load_kg=float(row["fuel_load_kg"]),
            tire_wear_pct=float(row["tire_wear_pct"]),
            lap_time_delta_s=float(row["lap_time_delta_s"]),
        )
        for _, row in lap_df.iterrows()
    ]

    # ── Pit stops ──────────────────────────────────────────────────────────
    pit_stops = []
    for i, pit_lap in enumerate(optimal_pit_laps):
        in_compound  = optimal_compounds[i]
        out_compound = optimal_compounds[min(i + 1, len(optimal_compounds) - 1)]

        tire_age_at_pit = pit_lap - (optimal_pit_laps[i-1] if i > 0 else 0)
        compound_obj = TIRE_COMPOUNDS[in_compound]
        wear_at_pit = (tire_age_at_pit / compound_obj.max_laps) * 100
        cliff_warning = tire_age_at_pit >= compound_obj.cliff_lap * 0.85

        reason = f"Tire wear: {wear_at_pit:.0f}%"
        if cliff_warning:
            reason += " — approaching degradation cliff"
        if weather.weather_type != WeatherType.DRY:
            reason += f" | Weather: {weather.weather_type.value}"

        pit_stops.append(PitStop(
            pit_lap=pit_lap,
            inbound_compound=in_compound,
            outbound_compound=out_compound,
            time_loss_s=track.pit_loss_time_s,
            strategic_reason=reason,
        ))

    # ── Stints ─────────────────────────────────────────────────────────────
    stints = []
    stint_boundaries = [0] + optimal_pit_laps + [track.total_laps]

    for i in range(len(stint_boundaries) - 1):
        start_lap  = stint_boundaries[i] + 1
        end_lap    = stint_boundaries[i + 1]
        compound   = optimal_compounds[min(i, len(optimal_compounds) - 1)]
        compound_obj = TIRE_COMPOUNDS[compound]

        stint_laps = lap_df[
            (lap_df["lap"] >= start_lap) & (lap_df["lap"] <= end_lap)
        ]
        avg_time  = float(stint_laps["lap_time_s"].mean()) if not stint_laps.empty else 0.0
        total_deg = float(stint_laps["lap_time_delta_s"].sum()) if not stint_laps.empty else 0.0

        stints.append(TireStint(
            stint_number=i + 1,
            compound=compound,
            start_lap=start_lap,
            end_lap=end_lap,
            laps_on_tire=end_lap - start_lap + 1,
            avg_lap_time_s=round(avg_time, 3),
            total_degradation_s=round(total_deg, 3),
            color_hex=compound_obj.color_hex,
        ))

    # ── Track key points with simulation data ──────────────────────────────
    track_key_points = []
    pit_window_str = f"L{optimal_pit_laps[0]}–L{optimal_pit_laps[-1]}" if optimal_pit_laps else "N/A"

    for kp in track.key_points:
        sim_data: dict = {}
        if kp.event_type.value == "PIT_WINDOW":
            sim_data = {
                "pit_window": pit_window_str,
                "pit_laps": optimal_pit_laps,
                "pit_loss_s": track.pit_loss_time_s,
            }
        elif kp.event_type.value in ("HIGH_G", "TIRE_STRESS"):
            mid_lap = track.total_laps // 2
            mid_row = lap_df[lap_df["lap"] == mid_lap]
            if not mid_row.empty:
                sim_data = {
                    "avg_wear_pct": float(mid_row["tire_wear_pct"].values[0]),
                    "compound": mid_row["tire_compound"].values[0],
                }
        elif kp.event_type.value in ("DRS_ZONE", "OVERTAKE_ZONE", "BRAKING_ZONE"):
            sim_data = {
                "strategy_note": "High-importance zone for position management",
                "weather": weather.weather_type.value,
            }

        track_key_points.append(TrackKeyPointResponse(
            name=kp.name,
            svg_x_pct=kp.svg_x_pct,
            svg_y_pct=kp.svg_y_pct,
            event_type=kp.event_type.value,
            description=kp.description,
            simulation_data=sim_data,
        ))

    # ── Monte Carlo stats ──────────────────────────────────────────────────
    pit_window_dist = {
        key: [PitWindowPoint(lap=int(item["lap"]), probability=float(item["probability"]))
              for item in val]
        for key, val in mc["pit_window_distribution"].items()
    }

    mc_stats = MonteCarloStats(
        n_simulations=mc["n_simulations"],
        mean_race_time_s=mc["mean_race_time_s"],
        std_race_time_s=mc["std_race_time_s"],
        confidence_interval_95_low=mc["confidence_interval_95_low"],
        confidence_interval_95_high=mc["confidence_interval_95_high"],
        optimal_strategy_probability=mc["optimal_strategy_probability"],
        pit_window_distribution=pit_window_dist,
    )

    # ── Visualisations ─────────────────────────────────────────────────────
    mc_times = mc.get("all_times", None)
    viz = None
    if mc_times is not None:
        viz_data = generate_all_visualizations(
            lap_df=lap_df,
            pit_laps=optimal_pit_laps,
            mc_times=mc_times,
            optimal_time=opt_result["optimal_time_s"],
            track_name=track.name,
        )
        viz = VisualizationData(**viz_data)

    return StrategyResponse(
        track_name=track.name,
        track_id=track.track_id,
        driver_name=request.driver_name,
        team_name=request.team_name,
        total_laps=track.total_laps,
        weather_type=weather.weather_type,
        optimal_total_time_s=round(opt_result["optimal_time_s"], 3),
        optimal_total_time_formatted=_format_time(opt_result["optimal_time_s"]),
        pit_stops=pit_stops,
        stints=stints,
        lap_data=lap_data,
        track_key_points=track_key_points,
        monte_carlo_stats=mc_stats,
        strategy_delta=strategy_delta,
        weather_note=weather_note,
        visualizations=viz,
        optimizer_converged=opt_result["converged"],
        optimizer_iterations=opt_result["n_iterations"],
        constraint_norm=round(opt_result["constraint_norm"], 8),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "online", "service": "F1 Race Strategy & Telemetry Simulation Engine"}


@router.get("/tracks")
async def get_all_tracks():
    """Return a list of all supported F1 2026 tracks."""
    return {"tracks": list_tracks()}


@router.get("/tracks/{track_id}")
async def get_track_info(track_id: str):
    """Return metadata and key points for a specific track."""
    try:
        track = get_track(track_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Track '{track_id}' not found")

    return {
        "track_id": track.track_id,
        "name": track.name,
        "country": track.country,
        "city": track.city,
        "total_laps": track.total_laps,
        "circuit_length_km": track.circuit_length_km,
        "pit_loss_time_s": track.pit_loss_time_s,
        "base_lap_time_s": track.base_lap_time_s,
        "safety_car_probability": track.safety_car_probability,
        "key_points": [
            {
                "name": kp.name,
                "svg_x_pct": kp.svg_x_pct,
                "svg_y_pct": kp.svg_y_pct,
                "event_type": kp.event_type.value,
                "description": kp.description,
            }
            for kp in track.key_points
        ],
    }


@router.post("/calculate_strategy", response_model=StrategyResponse)
async def calculate_strategy(request: RaceRequest):
    """
    Main endpoint: Calculate the complete race strategy.

    Runs the full pipeline:
      1. Build weather condition from request
      2. Run SLSQP optimisation (finds optimal pit laps + compounds)
      3. Run Monte Carlo simulation (configurable iterations)
      4. Generate Seaborn/Matplotlib visualisations
      5. Return complete StrategyResponse JSON

    Heavy computation runs in a thread pool to keep the event loop free.
    """
    try:
        track = get_track(request.track_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Track '{request.track_id}' not found")

    weather = build_weather_condition(request.weather)
    weather_note = get_weather_note(weather)

    loop = asyncio.get_event_loop()
    opt_fn = partial(
        optimize_race_time,
        track=track,
        weather=weather,
        n_simulations=request.n_simulations,
    )

    try:
        opt_result = await loop.run_in_executor(executor, opt_fn)
    except Exception:
        logger.exception("Optimisation failed for track=%s", request.track_id)
        raise HTTPException(status_code=500, detail="Strategy optimisation failed. Check server logs.")

    try:
        response = _build_strategy_response(request, opt_result, weather_note)
    except Exception:
        logger.exception("Response assembly failed for track=%s", request.track_id)
        raise HTTPException(status_code=500, detail="Failed to assemble strategy response. Check server logs.")

    return response


@router.post("/update_weather", response_model=StrategyResponse)
async def update_weather(body: WeatherUpdateRequest):
    """
    Fast-path endpoint: Re-optimise strategy when weather changes.

    Called by the frontend WeatherToggle — triggers full re-optimisation.
    Returns a new StrategyResponse with strategy_delta highlighting changes.
    Accepts a single JSON body for consistency with /calculate_strategy.
    """
    try:
        track = get_track(body.track_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Track '{body.track_id}' not found")

    new_weather = build_weather_condition(body.weather)
    prev_weather_obj = WeatherCondition(weather_type=WeatherType(body.prev_weather_type))
    weather_note = get_weather_note(new_weather, prev_weather_obj)

    new_starting_compound = select_starting_compound(new_weather)

    request = RaceRequest(
        track_id=body.track_id,
        driver_name=body.driver_name,
        team_name=body.team_name,
        starting_compound=new_starting_compound,
        weather=body.weather,
    )

    loop = asyncio.get_event_loop()
    opt_fn = partial(
        optimize_race_time,
        track=track,
        weather=new_weather,
        n_simulations=3000,
    )

    try:
        opt_result = await loop.run_in_executor(executor, opt_fn)
    except Exception:
        logger.exception("Weather re-optimisation failed for track=%s", body.track_id)
        raise HTTPException(status_code=500, detail="Weather re-optimisation failed. Check server logs.")

    strategy_delta = (
        f"Strategy updated: {body.prev_weather_type} → {body.weather.weather_type.value}. "
        f"Starting compound changed to {new_starting_compound.value}."
    )

    response = _build_strategy_response(request, opt_result, weather_note, strategy_delta)
    return response
