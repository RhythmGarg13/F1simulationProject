"""
track_data.py — F1 Race Strategy Simulation Engine
====================================================
Complete track definitions for all 24 circuits on the 2026 F1 calendar.

Each track includes:
  - Circuit metadata (laps, length, pit loss time)
  - Sector speed profiles (used in tire wear calculations)
  - Key points (mapped to SVG coordinates for frontend data binding)
  - Base lap time (for Monte Carlo baseline)

SVG coordinate system: (0.0, 0.0) = top-left, (1.0, 1.0) = bottom-right
of the circuit's SVG viewBox.

AI-assisted development: Modular registry pattern — tracks are stored
in a dictionary indexed by track_id for O(1) lookup by the API layer.
"""

from models import Track, Sector, KeyPoint, EventType


def _s(sid, name, length, speed, wear, overtake):
    return Sector(sector_id=sid, name=name, length_m=length,
                  avg_speed_kph=speed, tire_wear_factor=wear,
                  overtake_potential=overtake)


def _kp(name, x, y, event, desc=""):
    return KeyPoint(name=name, svg_x_pct=x, svg_y_pct=y,
                    event_type=event, description=desc)


# ─────────────────────────────────────────────────────────────────────────────
# Track Registry — All 24 F1 2026 circuits
# ─────────────────────────────────────────────────────────────────────────────

TRACKS: dict[str, Track] = {

    # ── 1. Albert Park, Melbourne ─────────────────────────────────────────
    "albert_park": Track(
        track_id="albert_park", name="Albert Park Circuit",
        country="Australia", city="Melbourne",
        total_laps=58, circuit_length_km=5.278,
        pit_loss_time_s=23.9, pit_entry_lap_min=14, pit_entry_lap_max=42,
        base_lap_time_s=87.5, fuel_consumption_kg_per_lap=1.72,
        safety_car_probability=0.40,
        sectors=[
            _s(1, "Turn 1–3 Medium Speed", 1200, 195, 0.9, 0.5),
            _s(2, "Lakeside Sweep S2", 2100, 230, 0.85, 0.3),
            _s(3, "Chicane–Hairpin S3", 1978, 185, 1.1, 0.6),
        ],
        key_points=[
            _kp("Turn 1 Braking Zone", 0.22, 0.18, EventType.BRAKING_ZONE, "Heavy braking — 300→80 km/h"),
            _kp("Lakeside Complex", 0.55, 0.28, EventType.HIGH_G, "High-G sweeping left — tire lateral load peak"),
            _kp("Turn 13 DRS Zone", 0.78, 0.65, EventType.DRS_ZONE, "Main straight DRS activation point"),
            _kp("Pit Lane Entry", 0.85, 0.82, EventType.PIT_WINDOW, "Pit window opens L14–L42"),
            _kp("Turn 15 Overtake Zone", 0.90, 0.55, EventType.OVERTAKE, "Highest overtaking probability"),
        ]
    ),

    # ── 2. Shanghai International Circuit ────────────────────────────────
    "shanghai": Track(
        track_id="shanghai", name="Shanghai International Circuit",
        country="China", city="Shanghai",
        total_laps=56, circuit_length_km=5.451,
        pit_loss_time_s=24.5, pit_entry_lap_min=15, pit_entry_lap_max=41,
        base_lap_time_s=93.2, fuel_consumption_kg_per_lap=1.80,
        safety_car_probability=0.30,
        sectors=[
            _s(1, "Long Right Hairpin S1", 1680, 175, 1.15, 0.45),
            _s(2, "High-Speed Sweeps S2", 2100, 245, 0.80, 0.20),
            _s(3, "Stadium Section S3", 1671, 200, 1.05, 0.55),
        ],
        key_points=[
            _kp("Turn 6–7 Esses", 0.38, 0.22, EventType.HIGH_G, "Combined G-load peak — front tire stress"),
            _kp("Back Straight DRS", 0.65, 0.48, EventType.DRS_ZONE, "Highest top speed zone — 330+ km/h"),
            _kp("Turn 14 Hairpin", 0.72, 0.75, EventType.BRAKING_ZONE, "Overtaking hotspot — heavy braking"),
            _kp("Pit Lane Entry", 0.12, 0.60, EventType.PIT_WINDOW, "Pit window L15–L41"),
            _kp("Turn 16 Tire Stress", 0.88, 0.35, EventType.TIRE_STRESS, "Rear tire degradation peak"),
        ]
    ),

    # ── 3. Suzuka Circuit ────────────────────────────────────────────────
    "suzuka": Track(
        track_id="suzuka", name="Suzuka Circuit",
        country="Japan", city="Suzuka",
        total_laps=53, circuit_length_km=5.807,
        pit_loss_time_s=22.4, pit_entry_lap_min=16, pit_entry_lap_max=39,
        base_lap_time_s=91.5, fuel_consumption_kg_per_lap=1.89,
        safety_car_probability=0.38,
        sectors=[
            _s(1, "S-Curves & Degner", 1975, 195, 1.25, 0.15),
            _s(2, "Hairpin to Spoon", 1950, 215, 1.20, 0.25),
            _s(3, "130R to Chicane", 1882, 255, 0.90, 0.50),
        ],
        key_points=[
            _kp("S-Curves (T1–T2)", 0.28, 0.18, EventType.HIGH_G, "Iconic S-Curves — peak lateral G: ~4.5G"),
            _kp("Degner Curve", 0.55, 0.30, EventType.TIRE_STRESS, "Right-rear tire degradation hotspot"),
            _kp("Hairpin", 0.68, 0.60, EventType.BRAKING_ZONE, "Best overtaking spot — 250→70 km/h"),
            _kp("Spoon Curve", 0.38, 0.72, EventType.HIGH_G, "High-speed right — tire lateral stress"),
            _kp("130R", 0.22, 0.55, EventType.HIGH_G, "Taken flat — ~5G corner at 300 km/h"),
            _kp("Pit Lane Entry", 0.88, 0.45, EventType.PIT_WINDOW, "Pit window L16–L39"),
        ]
    ),

    # ── 4. Bahrain International Circuit ─────────────────────────────────
    "bahrain": Track(
        track_id="bahrain", name="Bahrain International Circuit",
        country="Bahrain", city="Sakhir",
        total_laps=57, circuit_length_km=5.412,
        pit_loss_time_s=23.0, pit_entry_lap_min=14, pit_entry_lap_max=43,
        base_lap_time_s=91.0, fuel_consumption_kg_per_lap=1.78,
        safety_car_probability=0.25,
        sectors=[
            _s(1, "Power Section S1", 1870, 220, 0.95, 0.55),
            _s(2, "Technical Middle S2", 1680, 180, 1.20, 0.35),
            _s(3, "Back Straight S3", 1862, 240, 0.80, 0.45),
        ],
        key_points=[
            _kp("Turn 1 Braking", 0.20, 0.25, EventType.BRAKING_ZONE, "High degradation entry — rear lockup risk"),
            _kp("Turn 4 Hairpin", 0.45, 0.45, EventType.OVERTAKE, "Primary overtaking zone — DRS activation"),
            _kp("Turn 10–11 Chicane", 0.60, 0.68, EventType.TIRE_STRESS, "Rear tire wear zone — abrasive tarmac"),
            _kp("Pit Lane Entry", 0.15, 0.65, EventType.PIT_WINDOW, "Pit window L14–L43"),
            _kp("Turn 15 DRS Zone", 0.82, 0.38, EventType.DRS_ZONE, "Second DRS — rear-wing stall zone"),
        ]
    ),

    # ── 5. Jeddah Corniche Circuit ────────────────────────────────────────
    "jeddah": Track(
        track_id="jeddah", name="Jeddah Corniche Circuit",
        country="Saudi Arabia", city="Jeddah",
        total_laps=50, circuit_length_km=6.174,
        pit_loss_time_s=24.8, pit_entry_lap_min=14, pit_entry_lap_max=37,
        base_lap_time_s=89.8, fuel_consumption_kg_per_lap=1.92,
        safety_car_probability=0.55,
        sectors=[
            _s(1, "Long Back Straight S1", 2500, 280, 0.65, 0.40),
            _s(2, "Tight Wall Section S2", 1880, 185, 1.05, 0.30),
            _s(3, "Sweeping Curves S3", 1794, 250, 0.85, 0.30),
        ],
        key_points=[
            _kp("Turn 1 High-Speed Entry", 0.18, 0.20, EventType.BRAKING_ZONE, "320 km/h braking — wall proximity"),
            _kp("Turn 13 Chicane", 0.52, 0.50, EventType.OVERTAKE, "Best overtaking spot on the circuit"),
            _kp("Back Straight DRS", 0.75, 0.30, EventType.DRS_ZONE, "Top speed: 340+ km/h"),
            _kp("Pit Lane Entry", 0.88, 0.72, EventType.PIT_WINDOW, "Pit window L14–L37 — high pit-loss"),
        ]
    ),

    # ── 6. Miami International Autodrome ─────────────────────────────────
    "miami": Track(
        track_id="miami", name="Miami International Autodrome",
        country="USA", city="Miami",
        total_laps=57, circuit_length_km=5.412,
        pit_loss_time_s=22.0, pit_entry_lap_min=16, pit_entry_lap_max=42,
        base_lap_time_s=90.6, fuel_consumption_kg_per_lap=1.76,
        safety_car_probability=0.42,
        sectors=[
            _s(1, "Long Straight S1", 2100, 265, 0.72, 0.50),
            _s(2, "Infield Technical S2", 1780, 185, 1.18, 0.35),
            _s(3, "Marina Section S3", 1532, 210, 0.95, 0.45),
        ],
        key_points=[
            _kp("Turn 1 Entry", 0.15, 0.22, EventType.BRAKING_ZONE, "310 km/h approach — heavy braking"),
            _kp("Turn 11 Hairpin", 0.55, 0.58, EventType.OVERTAKE, "Prime overtaking zone"),
            _kp("Marina Complex T14-16", 0.70, 0.35, EventType.HIGH_G, "Sequential corners — compound stress"),
            _kp("Pit Lane Entry", 0.88, 0.78, EventType.PIT_WINDOW, "Pit window L16–L42"),
        ]
    ),

    # ── 7. Circuit Gilles Villeneuve ──────────────────────────────────────
    "montreal": Track(
        track_id="montreal", name="Circuit Gilles Villeneuve",
        country="Canada", city="Montreal",
        total_laps=70, circuit_length_km=4.361,
        pit_loss_time_s=21.8, pit_entry_lap_min=20, pit_entry_lap_max=52,
        base_lap_time_s=75.2, fuel_consumption_kg_per_lap=1.55,
        safety_car_probability=0.48,
        sectors=[
            _s(1, "Casino Hairpin S1", 1450, 185, 0.90, 0.60),
            _s(2, "Wall of Champions S2", 1620, 255, 0.75, 0.25),
            _s(3, "Island Chicane S3", 1291, 195, 1.05, 0.50),
        ],
        key_points=[
            _kp("Turn 1–3 Chicane", 0.20, 0.30, EventType.BRAKING_ZONE, "Multiple direction changes — wear spike"),
            _kp("Wall of Champions", 0.62, 0.40, EventType.TIRE_STRESS, "High-speed exit — wall on limit"),
            _kp("Hairpin", 0.40, 0.70, EventType.OVERTAKE, "Best overtaking spot — low-speed hairpin"),
            _kp("Pit Lane Entry", 0.88, 0.55, EventType.PIT_WINDOW, "Pit window L20–L52"),
        ]
    ),

    # ── 8. Circuit de Monaco ──────────────────────────────────────────────
    "monaco": Track(
        track_id="monaco", name="Circuit de Monaco",
        country="Monaco", city="Monte Carlo",
        total_laps=78, circuit_length_km=3.337,
        pit_loss_time_s=31.5, pit_entry_lap_min=20, pit_entry_lap_max=58,
        base_lap_time_s=72.5, fuel_consumption_kg_per_lap=1.35,
        safety_car_probability=0.60,
        sectors=[
            _s(1, "Sainte Devote–Massenet S1", 1100, 130, 0.85, 0.10),
            _s(2, "Casino–Mirabeau S2", 1080, 125, 0.88, 0.08),
            _s(3, "Swimming Pool–Rascasse S3", 1157, 120, 0.90, 0.15),
        ],
        key_points=[
            _kp("Sainte Devote", 0.18, 0.25, EventType.BRAKING_ZONE, "First braking zone — wall risk"),
            _kp("Casino Square", 0.42, 0.18, EventType.HIGH_G, "Blind left — lateral load through bump"),
            _kp("Fairmont Hairpin", 0.55, 0.55, EventType.OVERTAKE, "Slowest F1 corner — ~45 km/h"),
            _kp("Swimming Pool", 0.68, 0.78, EventType.TIRE_STRESS, "Chicane — tire sidewall stress"),
            _kp("Pit Lane Entry", 0.85, 0.45, EventType.PIT_WINDOW, "Long pit stop — track position key"),
        ]
    ),

    # ── 9. Circuit de Barcelona-Catalunya ────────────────────────────────
    "barcelona": Track(
        track_id="barcelona", name="Circuit de Barcelona-Catalunya",
        country="Spain", city="Barcelona",
        total_laps=66, circuit_length_km=4.657,
        pit_loss_time_s=23.1, pit_entry_lap_min=18, pit_entry_lap_max=49,
        base_lap_time_s=80.8, fuel_consumption_kg_per_lap=1.65,
        safety_car_probability=0.22,
        sectors=[
            _s(1, "Turn 1–5 S1", 1555, 195, 1.10, 0.40),
            _s(2, "High-Speed S2", 1700, 250, 0.82, 0.15),
            _s(3, "Technical Infield S3", 1402, 185, 1.15, 0.35),
        ],
        key_points=[
            _kp("Turn 1 Braking", 0.20, 0.22, EventType.BRAKING_ZONE, "Classic overtaking spot"),
            _kp("Turn 3 High-Speed", 0.40, 0.38, EventType.HIGH_G, "Long right — front tire peak load"),
            _kp("Turn 9 Compound Wear", 0.60, 0.65, EventType.TIRE_STRESS, "Highest wear per lap on circuit"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L18–L49"),
        ]
    ),

    # ── 10. Red Bull Ring ─────────────────────────────────────────────────
    "red_bull_ring": Track(
        track_id="red_bull_ring", name="Red Bull Ring",
        country="Austria", city="Spielberg",
        total_laps=71, circuit_length_km=4.318,
        pit_loss_time_s=21.5, pit_entry_lap_min=22, pit_entry_lap_max=53,
        base_lap_time_s=66.5, fuel_consumption_kg_per_lap=1.48,
        safety_car_probability=0.28,
        sectors=[
            _s(1, "Uphill S1", 1210, 210, 0.88, 0.50),
            _s(2, "Fast Middle S2", 1575, 245, 0.72, 0.30),
            _s(3, "Technical S3", 1533, 200, 1.05, 0.40),
        ],
        key_points=[
            _kp("Turn 1 Uphill Braking", 0.28, 0.18, EventType.BRAKING_ZONE, "Blind uphill braking — DRS zone end"),
            _kp("Turn 3 Hairpin", 0.50, 0.38, EventType.OVERTAKE, "Best overtaking — Turn 4 exit"),
            _kp("Turn 9 Compound Stress", 0.65, 0.72, EventType.TIRE_STRESS, "Exit understeer — rear wear"),
            _kp("Pit Lane Entry", 0.88, 0.55, EventType.PIT_WINDOW, "Pit window L22–L53"),
        ]
    ),

    # ── 11. Silverstone Circuit ───────────────────────────────────────────
    "silverstone": Track(
        track_id="silverstone", name="Silverstone Circuit",
        country="UK", city="Silverstone",
        total_laps=52, circuit_length_km=5.891,
        pit_loss_time_s=23.7, pit_entry_lap_min=16, pit_entry_lap_max=39,
        base_lap_time_s=88.0, fuel_consumption_kg_per_lap=1.90,
        safety_car_probability=0.30,
        sectors=[
            _s(1, "Copse–Maggots S1", 2100, 245, 1.15, 0.20),
            _s(2, "Stowe–Becketts S2", 2000, 260, 0.90, 0.15),
            _s(3, "Vale–Club–Hangar S3", 1791, 240, 0.95, 0.45),
        ],
        key_points=[
            _kp("Copse Corner", 0.25, 0.20, EventType.HIGH_G, "Flat-out at 290 km/h — 4G+ corner"),
            _kp("Maggotts–Becketts", 0.45, 0.35, EventType.HIGH_G, "Iconic sequence — peak lateral G"),
            _kp("Stowe Braking", 0.68, 0.55, EventType.BRAKING_ZONE, "260→80 km/h — prime overtake zone"),
            _kp("Vale Corner", 0.50, 0.72, EventType.TIRE_STRESS, "Tire rear-left thermal stress"),
            _kp("Pit Lane Entry", 0.88, 0.45, EventType.PIT_WINDOW, "Pit window L16–L39"),
        ]
    ),

    # ── 12. Circuit de Spa-Francorchamps ──────────────────────────────────
    "spa": Track(
        track_id="spa", name="Circuit de Spa-Francorchamps",
        country="Belgium", city="Stavelot",
        total_laps=44, circuit_length_km=7.004,
        pit_loss_time_s=25.0, pit_entry_lap_min=12, pit_entry_lap_max=33,
        base_lap_time_s=105.5, fuel_consumption_kg_per_lap=1.98,
        safety_car_probability=0.42,
        sectors=[
            _s(1, "Eau Rouge–Raidillon S1", 2400, 255, 1.20, 0.25),
            _s(2, "Pouhon–Stavelot S2", 2800, 270, 0.88, 0.20),
            _s(3, "Bus Stop Chicane S3", 1804, 220, 1.05, 0.50),
        ],
        key_points=[
            _kp("Eau Rouge / Raidillon", 0.22, 0.30, EventType.HIGH_G, "Iconic uphill flat-out — 5G+ through valley"),
            _kp("Pouhon Corner", 0.50, 0.58, EventType.HIGH_G, "Long left — sustained 3.5G — tire stress"),
            _kp("Bus Stop Chicane", 0.78, 0.28, EventType.BRAKING_ZONE, "Prime overtaking zone into final chicane"),
            _kp("La Source Hairpin", 0.88, 0.18, EventType.OVERTAKE, "Turn 1 — DRS + KERS deployment"),
            _kp("Pit Lane Entry", 0.92, 0.48, EventType.PIT_WINDOW, "Pit window L12–L33"),
        ]
    ),

    # ── 13. Hungaroring ───────────────────────────────────────────────────
    "hungaroring": Track(
        track_id="hungaroring", name="Hungaroring",
        country="Hungary", city="Budapest",
        total_laps=70, circuit_length_km=4.381,
        pit_loss_time_s=22.5, pit_entry_lap_min=20, pit_entry_lap_max=52,
        base_lap_time_s=79.5, fuel_consumption_kg_per_lap=1.62,
        safety_car_probability=0.28,
        sectors=[
            _s(1, "Turn 1–4 S1", 1380, 175, 1.15, 0.35),
            _s(2, "Technical Middle S2", 1650, 190, 1.20, 0.20),
            _s(3, "Back Straight S3", 1351, 225, 0.88, 0.45),
        ],
        key_points=[
            _kp("Turn 1 Braking", 0.20, 0.25, EventType.BRAKING_ZONE, "Heavy braking — bumpy surface"),
            _kp("Turn 4 High Wear", 0.38, 0.45, EventType.TIRE_STRESS, "Downforce-dependent corner — compound sensitive"),
            _kp("Turn 11 Hairpin", 0.62, 0.70, EventType.OVERTAKE, "Longest braking zone — overtake window"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L20–L52"),
        ]
    ),

    # ── 14. Circuit Zandvoort ─────────────────────────────────────────────
    "zandvoort": Track(
        track_id="zandvoort", name="Circuit Zandvoort",
        country="Netherlands", city="Zandvoort",
        total_laps=72, circuit_length_km=4.259,
        pit_loss_time_s=22.2, pit_entry_lap_min=22, pit_entry_lap_max=54,
        base_lap_time_s=72.0, fuel_consumption_kg_per_lap=1.55,
        safety_car_probability=0.35,
        sectors=[
            _s(1, "Tarzanbocht S1", 1400, 215, 1.05, 0.50),
            _s(2, "Hugenholtz S2", 1500, 240, 0.88, 0.20),
            _s(3, "Banked Assen S3", 1359, 220, 0.95, 0.35),
        ],
        key_points=[
            _kp("Tarzanbocht (T1)", 0.18, 0.25, EventType.BRAKING_ZONE, "Best overtaking — 290→80 km/h"),
            _kp("Hugenholtz Banked T3", 0.45, 0.35, EventType.HIGH_G, "Banked turn — 4G sustained"),
            _kp("Final Banked Turn", 0.72, 0.68, EventType.HIGH_G, "5G banked corner — tire vertical load peak"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L22–L54"),
        ]
    ),

    # ── 15. Autodromo Nazionale di Monza ──────────────────────────────────
    "monza": Track(
        track_id="monza", name="Autodromo Nazionale di Monza",
        country="Italy", city="Monza",
        total_laps=53, circuit_length_km=5.793,
        pit_loss_time_s=25.5, pit_entry_lap_min=15, pit_entry_lap_max=39,
        base_lap_time_s=82.2, fuel_consumption_kg_per_lap=1.88,
        safety_car_probability=0.32,
        sectors=[
            _s(1, "Rettifilo–Curva Grande S1", 2200, 295, 0.68, 0.50),
            _s(2, "Lesmos–Ascari S2", 2050, 270, 0.75, 0.35),
            _s(3, "Parabolica S3", 1543, 310, 0.60, 0.55),
        ],
        key_points=[
            _kp("Curva Grande", 0.28, 0.22, EventType.HIGH_G, "Flat-out at 310 km/h"),
            _kp("Variante del Rettifilo", 0.18, 0.45, EventType.BRAKING_ZONE, "Turn 1 braking — 330→80 km/h"),
            _kp("Lesmo 1 Tire Stress", 0.52, 0.38, EventType.TIRE_STRESS, "Rear tire thermal — low downforce"),
            _kp("Parabolica", 0.70, 0.68, EventType.HIGH_G, "Final corner — exit critical for lap time"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L15–L39"),
        ]
    ),

    # ── 16. IFEMA Madrid ──────────────────────────────────────────────────
    "madrid": Track(
        track_id="madrid", name="IFEMA Madrid Circuit",
        country="Spain", city="Madrid",
        total_laps=55, circuit_length_km=5.470,
        pit_loss_time_s=23.5, pit_entry_lap_min=16, pit_entry_lap_max=41,
        base_lap_time_s=91.5, fuel_consumption_kg_per_lap=1.80,
        safety_car_probability=0.30,
        sectors=[
            _s(1, "Exhibition Park S1", 1850, 225, 0.95, 0.45),
            _s(2, "Outer Circuit S2", 2000, 250, 0.82, 0.30),
            _s(3, "Inner Hairpin Section S3", 1620, 185, 1.15, 0.55),
        ],
        key_points=[
            _kp("Turn 1 Entry", 0.20, 0.22, EventType.BRAKING_ZONE, "New circuit — high-speed brake zone"),
            _kp("High-Speed S-Curves", 0.45, 0.35, EventType.HIGH_G, "Sustained lateral load sequence"),
            _kp("Inner Hairpin", 0.65, 0.65, EventType.OVERTAKE, "Primary overtaking opportunity"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L16–L41"),
        ]
    ),

    # ── 17. Baku City Circuit ─────────────────────────────────────────────
    "baku": Track(
        track_id="baku", name="Baku City Circuit",
        country="Azerbaijan", city="Baku",
        total_laps=51, circuit_length_km=6.003,
        pit_loss_time_s=24.3, pit_entry_lap_min=15, pit_entry_lap_max=38,
        base_lap_time_s=103.0, fuel_consumption_kg_per_lap=1.95,
        safety_car_probability=0.60,
        sectors=[
            _s(1, "Castle Section S1", 2050, 165, 0.95, 0.35),
            _s(2, "Old Town S2", 1820, 175, 0.90, 0.25),
            _s(3, "Main Straight S3", 2133, 330, 0.60, 0.60),
        ],
        key_points=[
            _kp("Castle Section T8", 0.30, 0.30, EventType.BRAKING_ZONE, "Tightest corner on any F1 street circuit"),
            _kp("Main Straight DRS", 0.75, 0.55, EventType.DRS_ZONE, "Longest DRS zone — 335+ km/h"),
            _kp("Turn 1 Braking", 0.88, 0.22, EventType.OVERTAKE, "Prime overtaking — safety car restarts"),
            _kp("Pit Lane Entry", 0.92, 0.65, EventType.PIT_WINDOW, "Pit window L15–L38"),
        ]
    ),

    # ── 18. Marina Bay Street Circuit ────────────────────────────────────
    "singapore": Track(
        track_id="singapore", name="Marina Bay Street Circuit",
        country="Singapore", city="Singapore",
        total_laps=62, circuit_length_km=4.940,
        pit_loss_time_s=28.0, pit_entry_lap_min=18, pit_entry_lap_max=46,
        base_lap_time_s=102.5, fuel_consumption_kg_per_lap=1.72,
        safety_car_probability=0.65,
        sectors=[
            _s(1, "Bay Section S1", 1650, 155, 1.05, 0.40),
            _s(2, "Civic District S2", 1680, 160, 1.00, 0.30),
            _s(3, "Marina South S3", 1610, 175, 1.02, 0.35),
        ],
        key_points=[
            _kp("Turn 1–3 Chicane", 0.18, 0.28, EventType.BRAKING_ZONE, "Tight entry — wall proximity risk"),
            _kp("Anderson Bridge", 0.42, 0.18, EventType.TIRE_STRESS, "Bump-stressed compound — sidewall wear"),
            _kp("Turn 18 Hairpin", 0.65, 0.70, EventType.OVERTAKE, "Only real overtaking opportunity"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L18–L46 — undercut key"),
        ]
    ),

    # ── 19. Circuit of the Americas (COTA) ────────────────────────────────
    "cota": Track(
        track_id="cota", name="Circuit of the Americas",
        country="USA", city="Austin, Texas",
        total_laps=56, circuit_length_km=5.513,
        pit_loss_time_s=23.4, pit_entry_lap_min=16, pit_entry_lap_max=42,
        base_lap_time_s=94.5, fuel_consumption_kg_per_lap=1.85,
        safety_car_probability=0.32,
        sectors=[
            _s(1, "Uphill T1 Section S1", 2000, 200, 1.10, 0.45),
            _s(2, "Esses & Back S2", 2200, 235, 0.95, 0.25),
            _s(3, "Stadium Section S3", 1313, 210, 1.05, 0.55),
        ],
        key_points=[
            _kp("Turn 1 Uphill", 0.22, 0.20, EventType.BRAKING_ZONE, "Blind uphill braking — 320 km/h entry"),
            _kp("Turn 12–15 Esses", 0.48, 0.35, EventType.HIGH_G, "High-speed esses — peak G sequence"),
            _kp("Turn 19 Hairpin", 0.65, 0.72, EventType.OVERTAKE, "Main overtaking zone — stadium section"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L16–L42"),
        ]
    ),

    # ── 20. Autódromo Hermanos Rodríguez ──────────────────────────────────
    "mexico_city": Track(
        track_id="mexico_city", name="Autódromo Hermanos Rodríguez",
        country="Mexico", city="Mexico City",
        total_laps=71, circuit_length_km=4.304,
        pit_loss_time_s=22.3, pit_entry_lap_min=21, pit_entry_lap_max=53,
        base_lap_time_s=79.8, fuel_consumption_kg_per_lap=1.62,
        safety_car_probability=0.28,
        sectors=[
            _s(1, "Stadium & Esses S1", 1400, 230, 0.88, 0.45),
            _s(2, "Peraltada S2", 1650, 265, 0.72, 0.20),
            _s(3, "Hairpins S3", 1254, 185, 1.10, 0.55),
        ],
        key_points=[
            _kp("Turn 1–3 Stadium", 0.25, 0.25, EventType.BRAKING_ZONE, "High-altitude braking — longer stops"),
            _kp("Peraltada", 0.55, 0.55, EventType.HIGH_G, "Banked sweeper — 310 km/h at altitude"),
            _kp("Turn 13 Hairpin", 0.72, 0.72, EventType.OVERTAKE, "Best overtaking on circuit"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L21–L53 — thin-air fuel correction"),
        ]
    ),

    # ── 21. Interlagos Circuit ────────────────────────────────────────────
    "interlagos": Track(
        track_id="interlagos", name="Autódromo José Carlos Pace (Interlagos)",
        country="Brazil", city="São Paulo",
        total_laps=71, circuit_length_km=4.309,
        pit_loss_time_s=22.5, pit_entry_lap_min=21, pit_entry_lap_max=53,
        base_lap_time_s=72.9, fuel_consumption_kg_per_lap=1.55,
        safety_car_probability=0.45,
        sectors=[
            _s(1, "Senna S S1", 1350, 195, 1.05, 0.35),
            _s(2, "Descida do Lago S2", 1550, 250, 0.82, 0.25),
            _s(3, "Junção Reta S3", 1409, 220, 0.95, 0.50),
        ],
        key_points=[
            _kp("Senna S (T1)", 0.22, 0.22, EventType.BRAKING_ZONE, "Classic entry — anti-clockwise circuit"),
            _kp("Curva do Lago", 0.45, 0.42, EventType.HIGH_G, "High-speed right — tire lateral peak"),
            _kp("Junção", 0.62, 0.72, EventType.OVERTAKE, "Best overtaking — DRS activation"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L21–L53"),
        ]
    ),

    # ── 22. Las Vegas Strip Circuit ───────────────────────────────────────
    "las_vegas": Track(
        track_id="las_vegas", name="Las Vegas Strip Circuit",
        country="USA", city="Las Vegas",
        total_laps=50, circuit_length_km=6.201,
        pit_loss_time_s=23.8, pit_entry_lap_min=14, pit_entry_lap_max=37,
        base_lap_time_s=92.5, fuel_consumption_kg_per_lap=1.95,
        safety_car_probability=0.40,
        sectors=[
            _s(1, "Strip Straight S1", 2400, 335, 0.60, 0.50),
            _s(2, "Casino District S2", 2000, 200, 1.02, 0.30),
            _s(3, "Return Straight S3", 1801, 290, 0.70, 0.40),
        ],
        key_points=[
            _kp("Las Vegas Strip Straight", 0.30, 0.18, EventType.DRS_ZONE, "Top speed: 340+ km/h — night race"),
            _kp("Turn 12 Chicane", 0.55, 0.55, EventType.BRAKING_ZONE, "Only real braking zone — prime overtake"),
            _kp("Casino Corner", 0.72, 0.35, EventType.TIRE_STRESS, "Cold-tire risk — night temps <15°C"),
            _kp("Pit Lane Entry", 0.88, 0.70, EventType.PIT_WINDOW, "Pit window L14–L37"),
        ]
    ),

    # ── 23. Lusail International Circuit ─────────────────────────────────
    "lusail": Track(
        track_id="lusail", name="Lusail International Circuit",
        country="Qatar", city="Lusail",
        total_laps=57, circuit_length_km=5.380,
        pit_loss_time_s=23.6, pit_entry_lap_min=16, pit_entry_lap_max=43,
        base_lap_time_s=83.8, fuel_consumption_kg_per_lap=1.78,
        safety_car_probability=0.28,
        sectors=[
            _s(1, "Turn 1–6 Fast S1", 1900, 250, 1.00, 0.35),
            _s(2, "Technical Middle S2", 1800, 215, 1.12, 0.30),
            _s(3, "Back Straight S3", 1680, 275, 0.75, 0.50),
        ],
        key_points=[
            _kp("Turn 1–4 Sequence", 0.28, 0.25, EventType.HIGH_G, "High-speed sequence — front tire peak"),
            _kp("Turn 14 Hairpin", 0.55, 0.65, EventType.OVERTAKE, "Main overtaking zone at hairpin"),
            _kp("Back Straight DRS", 0.72, 0.38, EventType.DRS_ZONE, "275+ km/h — rear thermal peak"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L16–L43"),
        ]
    ),

    # ── 24. Yas Marina Circuit ────────────────────────────────────────────
    "yas_marina": Track(
        track_id="yas_marina", name="Yas Marina Circuit",
        country="UAE", city="Abu Dhabi",
        total_laps=58, circuit_length_km=5.281,
        pit_loss_time_s=24.0, pit_entry_lap_min=16, pit_entry_lap_max=43,
        base_lap_time_s=84.5, fuel_consumption_kg_per_lap=1.75,
        safety_car_probability=0.22,
        sectors=[
            _s(1, "Marina Turn S1", 1800, 215, 0.95, 0.40),
            _s(2, "Hotel Section S2", 1900, 240, 0.85, 0.30),
            _s(3, "Hairpin Section S3", 1581, 195, 1.08, 0.50),
        ],
        key_points=[
            _kp("Turn 1–2 Marina", 0.20, 0.28, EventType.BRAKING_ZONE, "Opening chicane — overtaking spot"),
            _kp("Hotel Tunnel Section", 0.50, 0.45, EventType.HIGH_G, "Under Yas Viceroy Hotel — unique corner"),
            _kp("Turn 11 Hairpin", 0.65, 0.72, EventType.OVERTAKE, "Best overtaking — DRS zone entry"),
            _kp("Pit Lane Entry", 0.88, 0.50, EventType.PIT_WINDOW, "Pit window L16–L43 — season finale track"),
        ]
    ),
}


def get_track(track_id: str) -> Track:
    """Retrieve a Track by its ID. Raises ValueError if not found."""
    if track_id not in TRACKS:
        available = ", ".join(TRACKS.keys())
        raise ValueError(f"Unknown track_id '{track_id}'. Available: {available}")
    return TRACKS[track_id]


def list_tracks() -> list[dict]:
    """Return a summary list of all tracks for the frontend selector."""
    return [
        {
            "track_id": t.track_id,
            "name": t.name,
            "country": t.country,
            "city": t.city,
            "laps": t.total_laps,
            "circuit_length_km": t.circuit_length_km,
        }
        for t in TRACKS.values()
    ]
