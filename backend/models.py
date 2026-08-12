"""
models.py — F1 Race Strategy Simulation Engine
================================================
Data classes and Pydantic schemas for the simulation engine.
Defines the core domain objects: TireCompound, CarState, Track,
WeatherCondition, and all API request/response schemas.

AI-assisted development: modular design with clear separation of concerns.
Each class is self-documenting with type hints and docstrings.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class TireCompoundName(str, Enum):
    SOFT       = "SOFT"
    MEDIUM     = "MEDIUM"
    HARD       = "HARD"
    INTER      = "INTERMEDIATE"
    WET        = "WET"


class WeatherType(str, Enum):
    DRY        = "DRY"
    LIGHT_RAIN = "LIGHT_RAIN"
    HEAVY_RAIN = "HEAVY_RAIN"


class EventType(str, Enum):
    HIGH_G       = "HIGH_G"
    TIRE_STRESS  = "TIRE_STRESS"
    PIT_WINDOW   = "PIT_WINDOW"
    OVERTAKE     = "OVERTAKE_ZONE"
    DRS_ZONE     = "DRS_ZONE"
    BRAKING_ZONE = "BRAKING_ZONE"


# ─────────────────────────────────────────────────────────────────────────────
# Core Domain Dataclasses (used internally by simulation engine)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TireCompound:
    """
    Represents an F1 tire compound with its performance characteristics.
    
    Degradation model: deg(lap) = alpha * lap^beta + gamma * exp(delta * lap)
    This polynomial-exponential blend captures both the linear wear phase
    and the exponential 'cliff' when the tire rapidly degrades.
    """
    name: TireCompoundName
    # Base pace advantage/disadvantage in seconds vs median
    base_pace_delta: float          # negative = faster (e.g., Soft = -0.8s)
    # Degradation model coefficients
    alpha: float                    # polynomial coefficient
    beta: float                     # polynomial exponent
    gamma: float                    # exponential coefficient
    delta: float                    # exponential growth rate
    # Cliff threshold — after this lap, exponential degradation dominates
    cliff_lap: int
    # Maximum laps before catastrophic failure
    max_laps: int
    # Wet weather performance factor (1.0 = neutral, <1 = better in wet)
    wet_performance_factor: float
    # Color for visualization
    color_hex: str


@dataclass
class CarState:
    """
    Represents the dynamic state of an F1 car at any given lap.
    
    Fuel load decreases ~1.85 kg per lap, affecting lap time by ~0.035s/kg.
    """
    current_lap: int = 0
    fuel_load_kg: float = 110.0         # Full fuel at race start
    tire_compound: TireCompoundName = TireCompoundName.MEDIUM
    tire_age_laps: int = 0              # How many laps on current set
    position: int = 1
    cumulative_time_s: float = 0.0
    pit_count: int = 0
    # Per-lap telemetry history (populated during simulation)
    lap_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class KeyPoint:
    """
    A geographically-significant point on the circuit that maps
    simulation data to a specific location on the SVG track layout.
    """
    name: str
    svg_x_pct: float    # X position as percentage of SVG viewBox width
    svg_y_pct: float    # Y position as percentage of SVG viewBox height
    event_type: EventType
    description: str = ""


@dataclass
class Sector:
    """Defines a track sector with its speed profile characteristics."""
    sector_id: int
    name: str
    length_m: float
    avg_speed_kph: float
    tire_wear_factor: float     # 1.0 = baseline, >1 = high wear
    overtake_potential: float   # 0–1 scale


@dataclass
class Track:
    """
    Complete circuit definition for an F1 2026 track.
    
    Includes sector definitions, key points for data mapping,
    and pit-lane-specific data for strategy optimization.
    """
    track_id: str
    name: str
    country: str
    city: str
    total_laps: int
    circuit_length_km: float
    pit_loss_time_s: float          # Time lost during a pit stop
    pit_entry_lap_min: int          # Earliest viable pit lap
    pit_entry_lap_max: int          # Latest viable pit lap before danger
    sectors: List[Sector]
    key_points: List[KeyPoint]
    base_lap_time_s: float          # Representative fastest lap
    fuel_consumption_kg_per_lap: float = 1.85
    safety_car_probability: float = 0.35


@dataclass
class WeatherCondition:
    """
    Dynamic weather state that triggers full strategy re-optimization.
    
    Temperature differentials significantly affect tire compound selection
    and degradation rates — a core feature of the dynamic strategy system.
    """
    weather_type: WeatherType = WeatherType.DRY
    air_temp_c: float = 24.0
    track_temp_c: float = 38.0
    rain_intensity: float = 0.0     # 0.0 = dry, 1.0 = heavy rain
    wind_speed_kph: float = 10.0


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic API Schemas (Request / Response)
# ─────────────────────────────────────────────────────────────────────────────

class WeatherRequest(BaseModel):
    """Weather condition submitted by the frontend weather toggle."""
    weather_type: WeatherType = WeatherType.DRY
    air_temp_c: float = Field(default=24.0, ge=-10, le=50)
    track_temp_c: float = Field(default=38.0, ge=0, le=70)
    rain_intensity: float = Field(default=0.0, ge=0.0, le=1.0)
    wind_speed_kph: float = Field(default=10.0, ge=0, le=100)


class RaceRequest(BaseModel):
    """
    Full race strategy request from the frontend.
    Sent on initial load and whenever weather/track changes.
    """
    track_id: str = Field(default="suzuka", description="F1 2026 track identifier")
    driver_name: str = Field(default="VER", max_length=20)
    team_name: str = Field(default="Red Bull Racing", max_length=50)
    initial_fuel_kg: float = Field(default=110.0, ge=80.0, le=120.0)
    starting_compound: TireCompoundName = TireCompoundName.MEDIUM
    starting_position: int = Field(default=1, ge=1, le=20)
    n_simulations: int = Field(default=5000, ge=100, le=20000,
                               description="Monte Carlo iterations (more = slower but more accurate)")
    weather: WeatherRequest = Field(default_factory=WeatherRequest)


class LapDataPoint(BaseModel):
    """Single lap telemetry data point returned in strategy response."""
    lap: int
    lap_time_s: float
    tire_compound: TireCompoundName
    tire_age: int
    fuel_load_kg: float
    tire_wear_pct: float
    lap_time_delta_s: float     # vs optimal


class PitStop(BaseModel):
    """A single pit stop event in the optimal strategy."""
    pit_lap: int
    inbound_compound: TireCompoundName
    outbound_compound: TireCompoundName
    time_loss_s: float
    strategic_reason: str


class TireStint(BaseModel):
    """A continuous stint on one tire compound."""
    stint_number: int
    compound: TireCompoundName
    start_lap: int
    end_lap: int
    laps_on_tire: int
    avg_lap_time_s: float
    total_degradation_s: float
    color_hex: str


class TrackKeyPointResponse(BaseModel):
    """Track key point with simulation data bound to it — sent to frontend for D3 mapping."""
    name: str
    svg_x_pct: float
    svg_y_pct: float
    event_type: str
    description: str
    simulation_data: Dict[str, Any] = {}


class MonteCarloStats(BaseModel):
    """Statistical summary of the Monte Carlo simulation run."""
    n_simulations: int
    mean_race_time_s: float
    std_race_time_s: float
    confidence_interval_95_low: float
    confidence_interval_95_high: float
    optimal_strategy_probability: float
    pit_window_distribution: Dict[str, List[float]]


class VisualizationData(BaseModel):
    """Base64-encoded Seaborn/Matplotlib charts generated server-side."""
    degradation_curves_b64: str     # Tire degradation overlay chart
    lap_time_distribution_b64: str  # Monte Carlo lap time histogram
    strategy_comparison_b64: str    # Strategy comparison bar chart


class StrategyResponse(BaseModel):
    """
    Complete strategy response returned to the frontend.
    Contains all data needed to render the full dashboard.
    """
    # Race metadata
    track_name: str
    track_id: str
    driver_name: str
    team_name: str
    total_laps: int
    weather_type: WeatherType

    # Core strategy outputs
    optimal_total_time_s: float
    optimal_total_time_formatted: str   # "1:28:32.4"
    pit_stops: List[PitStop]
    stints: List[TireStint]
    lap_data: List[LapDataPoint]

    # Track data with simulation data bound to key points
    track_key_points: List[TrackKeyPointResponse]

    # Monte Carlo statistics
    monte_carlo_stats: MonteCarloStats

    # Dynamic strategy adjustments (populated on weather change)
    strategy_delta: Optional[str] = None
    weather_note: str = ""

    # Seaborn/Matplotlib visualizations
    visualizations: Optional[VisualizationData] = None

    # Optimization convergence info
    optimizer_converged: bool = True
    optimizer_iterations: int = 0
    constraint_norm: float = 0.0    # ||∇g(x)||₂ at convergence
