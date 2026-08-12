"""
Quick end-to-end smoke test for the F1 Strategy API.
Tests /calculate_strategy with Suzuka + Dry weather.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import urllib.request
import json

BASE = "http://localhost:8000/api"

# 1. Health check
r = urllib.request.urlopen(f"{BASE}/")
health = json.loads(r.read())
print("[OK] Health:", health)

# 2. Tracks list
r = urllib.request.urlopen(f"{BASE}/tracks")
tracks = json.loads(r.read())
print(f"[OK] Tracks: {len(tracks['tracks'])} tracks loaded")
print("   First 3:", [t["name"] for t in tracks["tracks"][:3]])

# 3. Single track
r = urllib.request.urlopen(f"{BASE}/tracks/suzuka")
track = json.loads(r.read())
print(f"[OK] Suzuka: {track['total_laps']} laps, {track['circuit_length_km']} km")
print(f"   Key points: {len(track['key_points'])}")

# 4. Full strategy calculation
payload = json.dumps({
    "track_id": "suzuka",
    "driver_name": "VER",
    "team_name": "Red Bull Racing",
    "initial_fuel_kg": 110.0,
    "starting_compound": "MEDIUM",
    "starting_position": 1,
    "n_simulations": 500,   # Small for quick test
    "weather": {
        "weather_type": "DRY",
        "air_temp_c": 26.0,
        "track_temp_c": 42.0,
        "rain_intensity": 0.0,
        "wind_speed_kph": 8.0
    }
}).encode()

req = urllib.request.Request(
    f"{BASE}/calculate_strategy",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)
print("\n[...] Calling /calculate_strategy (500 MC sims)...")
r = urllib.request.urlopen(req, timeout=120)
result = json.loads(r.read())

print(f"[OK] Strategy calculated!")
print(f"   Track: {result['track_name']}")
print(f"   Optimal time: {result['optimal_total_time_formatted']}")
print(f"   Pit stops: {len(result['pit_stops'])}")
print(f"   Stints: {len(result['stints'])}")
print(f"   Lap data points: {len(result['lap_data'])}")
print(f"   SLSQP converged: {result['optimizer_converged']}")
print(f"   Constraint norm ||∇g(x)||₂: {result['constraint_norm']}")
print(f"   MC simulations: {result['monte_carlo_stats']['n_simulations']}")
print(f"   MC 95% CI: [{result['monte_carlo_stats']['confidence_interval_95_low']:.1f}, {result['monte_carlo_stats']['confidence_interval_95_high']:.1f}]s")
print(f"   Track key points: {len(result['track_key_points'])}")
print(f"   Visualizations: {'YES' if result['visualizations'] else 'NO'}")

print("\n[PIT] Pit strategy:")
for pit in result["pit_stops"]:
    print(f"   L{pit['pit_lap']}: {pit['inbound_compound']} → {pit['outbound_compound']} (+{pit['time_loss_s']:.1f}s)")

print("\n[STINTS]")
for stint in result["stints"]:
    print(f"   Stint {stint['stint_number']}: {stint['compound']} L{stint['start_lap']}-L{stint['end_lap']} ({stint['laps_on_tire']} laps, avg {stint['avg_lap_time_s']:.3f}s)")

print("\n[ALL TESTS PASSED] F1 Strategy Engine is operational!")
