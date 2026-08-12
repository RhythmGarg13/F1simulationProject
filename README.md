# F1 Race Strategy & Telemetry Simulation Engine
## November 2025

A full-stack F1 race strategy simulation platform combining Monte Carlo methods, ML-driven tire degradation, scipy optimization, and a premium React dashboard.

---

## 🏎️ Features

### Backend (Python FastAPI)
- **Monte Carlo Engine** — 10,000 simulation iterations with randomized perturbations
- **Scikit-learn GradientBoostingRegressor** — Predicts non-linear tire degradation & lap-time offsets
- **Scipy SLSQP Optimizer** — Minimizes total race time with explicit `g(x)` constraint functions
- **Mathematical convergence** — `||∇g(x)||₂` Euclidean norm evaluated at each SLSQP iteration
- **Dynamic Weather** — Full re-optimization triggered on weather change
- **Seaborn/Matplotlib visualizations** — Server-side comparative charts (degradation curves, MC distribution)
- **All 24 F1 2026 circuits** — Complete track definitions with sectors and key points

### Frontend (React + Vite)
- **Glassmorphism design** — Medium-to-light color palette, Inter + JetBrains Mono fonts
- **D3.js circuit visualization** — SVG track layouts with data-mapped key points
- **Animated F1 car** — Compound-colored car follows track path via `getTotalLength` / `getPointAtLength`
- **Dynamic weather toggle** — ☀️ Dry / 🌦 Light Rain / 🌧 Heavy Rain with instant re-optimization
- **Multi-card dashboard** — Race overview, lap times, pitstop strategy, tire compounds
- **Live telemetry** — `||∇g(x)||₂` norm, SLSQP convergence, MC confidence intervals

---

## 🚀 Quick Start

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
Dashboard: http://localhost:5173

---

## 📁 Project Structure

```
F1simulationProject/
├── backend/
│   ├── main.py           # FastAPI app + CORS + lifespan startup
│   ├── api.py            # Route definitions
│   ├── models.py         # Pydantic schemas + dataclasses
│   ├── monte_carlo.py    # MC engine + sklearn GBR model
│   ├── optimizer.py      # scipy SLSQP + g(x) constraints
│   ├── track_data.py     # All 24 F1 2026 tracks
│   ├── weather.py        # Dynamic weather logic
│   ├── visualizations.py # Seaborn/Matplotlib charts
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Dashboard.jsx      # Main multi-card layout
    │   │   ├── CircuitMap.jsx     # D3.js SVG track + animated car
    │   │   ├── LapTimeChart.jsx   # Recharts lap time visualization
    │   │   ├── PitStrategy.jsx    # Pitstop timeline
    │   │   ├── TireStrategy.jsx   # Compound donut chart
    │   │   ├── TelemetryCard.jsx  # Live telemetry numbers
    │   │   └── WeatherToggle.jsx  # Weather panel
    │   ├── api/strategyApi.js     # Axios API client
    │   ├── data/trackPaths.js     # SVG paths for all 24 circuits
    │   └── styles/global.css      # Design system
    └── vite.config.js             # Proxy to :8000
```

---

## 🔬 Mathematical Foundation

### Tire Degradation Model
```
deg(lap) = α * lap^β + γ * exp(δ * lap)
```
- Polynomial term `α * lap^β` — moderate early wear phase
- Exponential term `γ * exp(δ * lap)` — cliff emergence at high lap counts
- ML correction via GradientBoostingRegressor trained on 10,000 synthetic telemetry samples

### Optimization Problem
```
Minimize: f(x) = Σ lap_times(x) + Σ pit_time_losses(x)

Subject to:
  g₁(x): max_laps_i - stint_length_i ≥ 0    [tire life]
  g₂(x): ≥ 2 different compounds used        [F1 regulation]
  g₃(x): min gap between stops ≥ 5 laps      [physical constraint]
  g₄(x): pit laps within valid window        [strategic constraint]

Convergence: ||∇g(x)||₂ < ε  (Euclidean norm of constraint gradient)
```

---

## 🛠️ Technologies

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| Simulation | NumPy, Pandas, Monte Carlo |
| ML | Scikit-learn (GradientBoostingRegressor) |
| Optimization | Scipy.optimize (SLSQP) |
| Visualization | Seaborn, Matplotlib |
| Frontend | React 18, Vite |
| Charts | Recharts, D3.js |
| Animation | Framer Motion |
| Fonts | Inter, JetBrains Mono |
