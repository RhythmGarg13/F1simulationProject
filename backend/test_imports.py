from models import TireCompound, CarState, Track
from track_data import TRACKS, list_tracks
tracks = list_tracks()
print(f"Loaded {len(TRACKS)} tracks")
print("First 5:", [t["name"] for t in tracks[:5]])

from monte_carlo import TIRE_COMPOUNDS
print(f"Tire compounds: {list(TIRE_COMPOUNDS.keys())}")

from weather import build_weather_condition
from models import WeatherRequest
w = build_weather_condition(WeatherRequest())
print(f"Weather: {w}")

print("All module imports OK!")
