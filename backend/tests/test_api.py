"""
test_api.py — FastAPI endpoint tests.

Tests all public API routes using FastAPI's TestClient (synchronous wrapper
around HTTPX). Each test is independent and uses a small n_simulations (200)
for speed.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "track_id": "suzuka",
    "driver_name": "VER",
    "team_name": "Red Bull Racing",
    "initial_fuel_kg": 110.0,
    "starting_compound": "MEDIUM",
    "starting_position": 1,
    "n_simulations": 200,
    "weather": {
        "weather_type": "DRY",
        "air_temp_c": 24.0,
        "track_temp_c": 38.0,
        "rain_intensity": 0.0,
        "wind_speed_kph": 10.0,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────────────────────

def test_health_check():
    resp = client.get("/api/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert "service" in data


# ─────────────────────────────────────────────────────────────────────────────
# Tracks
# ─────────────────────────────────────────────────────────────────────────────

def test_list_tracks_returns_24():
    resp = client.get("/api/tracks")
    assert resp.status_code == 200
    data = resp.json()
    assert "tracks" in data
    assert isinstance(data["tracks"], list)
    assert len(data["tracks"]) == 24


def test_get_valid_track():
    resp = client.get("/api/tracks/suzuka")
    assert resp.status_code == 200
    data = resp.json()
    assert data["track_id"] == "suzuka"
    assert "name" in data
    assert "total_laps" in data
    assert "key_points" in data
    assert isinstance(data["key_points"], list)


def test_get_invalid_track_returns_404():
    resp = client.get("/api/tracks/nonexistent_track_xyz")
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# calculate_strategy
# ─────────────────────────────────────────────────────────────────────────────

def test_calculate_strategy_valid():
    resp = client.post("/api/calculate_strategy", json=VALID_PAYLOAD)
    assert resp.status_code == 200, f"Got {resp.status_code}: {resp.text[:300]}"
    data = resp.json()

    # Shape assertions
    assert isinstance(data["optimizer_converged"], bool)
    assert isinstance(data["pit_stops"], list)
    assert len(data["pit_stops"]) > 0
    assert len(data["lap_data"]) == data["total_laps"]

    # Phase 1 regression: pit_window_distribution must contain dicts with lap+probability
    pwd = data["monte_carlo_stats"]["pit_window_distribution"]
    assert isinstance(pwd, dict)
    assert len(pwd) > 0
    for key, points in pwd.items():
        assert isinstance(points, list)
        assert len(points) > 0
        for pt in points:
            assert "lap" in pt, f"Missing 'lap' key in {pt}"
            assert "probability" in pt, f"Missing 'probability' key in {pt}"
            assert isinstance(pt["lap"], int)
            assert 0.0 <= pt["probability"] <= 1.0


def test_calculate_strategy_invalid_track_returns_404():
    bad_payload = {**VALID_PAYLOAD, "track_id": "no_such_track"}
    resp = client.post("/api/calculate_strategy", json=bad_payload)
    assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# update_weather
# ─────────────────────────────────────────────────────────────────────────────

def test_update_weather_returns_strategy_delta():
    payload = {
        "track_id": "suzuka",
        "driver_name": "VER",
        "team_name": "Red Bull Racing",
        "prev_weather_type": "DRY",
        "weather": {
            "weather_type": "HEAVY_RAIN",
            "air_temp_c": 14.0,
            "track_temp_c": 16.0,
            "rain_intensity": 0.85,
            "wind_speed_kph": 30.0,
        },
    }
    resp = client.post("/api/update_weather", json=payload)
    assert resp.status_code == 200, f"Got {resp.status_code}: {resp.text[:300]}"
    data = resp.json()
    assert "strategy_delta" in data
    assert data["strategy_delta"] is not None
    assert "DRY" in data["strategy_delta"] or "HEAVY_RAIN" in data["strategy_delta"]
