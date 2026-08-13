# F1 Race Strategy & Telemetry Simulation Engine
## 2026 Season

A full-stack F1 race strategy simulation platform combining Monte Carlo methods, an analytical tire degradation model, scipy SLSQP optimization, and a premium React dashboard.

---

## 🏎️ Features

### Backend (Python FastAPI)
- **Monte Carlo Engine** — Configurable simulation iterations with stochastic per-lap noise + safety car events
- **Analytical Tire Degradation** — Dual-term polynomial-exponential model: `deg(lap) = α·lapᵝ + γ·exp(δ·lap)`, precomputed per-compound lookup tables for O(1) per-lap cost
- **Scipy SLSQP Optimizer** — Minimises total race time with explicit `g(x)` constraint functions, parallelised across candidate strategies via `ThreadPoolExecutor`
- **Constraint Sensitivity Diagnostic** — `||∇g(x)||₂` Euclidean norm at the solution describes how quickly constraints change near the optimum (post-hoc diagnostic, not convergence criterion)
- **Dynamic Weather** — Full re-optimisation triggered on weather change; compound selection adapts automatically
- **Seaborn/Matplotlib visualizations** — Server-side comparative charts (degradation curves, MC distribution, lap strategy)
- **All 24 F1 2026 circuits** — Complete track definitions with sectors and key points

### Frontend (React + Vite)
- **Glassmorphism design** — Medium-to-light colour palette, Inter + JetBrains Mono fonts
- **D3.js circuit visualization** — SVG track layouts with data-mapped key points
- **Animated F1 car** — Compound-coloured car follows track path via `getTotalLength` / `getPointAtLength`; respects `prefers-reduced-motion`
- **Dynamic weather toggle** — ☀️ Dry / 🌦 Light Rain / 🌧 Heavy Rain with instant re-optimisation
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

### 3. Docker Compose (both services)
```bash
docker compose up --build
```

---

## 📁 Project Structure

```
F1simulationProject/
├── .github/
│   └── workflows/ci.yml    # GitHub Actions: pytest + vitest on every push
├── backend/
│   ├── main.py             # FastAPI app + CORS (env-configurable) + lifespan hooks
│   ├── api.py              # Route definitions (sanitised error handling)
│   ├── models.py           # Pydantic schemas + dataclasses
│   ├── monte_carlo.py      # MC engine + analytical tire degradation + shared simulate_race()
│   ├── optimizer.py        # SLSQP + parallel candidate evaluation + g(x) constraints
│   ├── track_data.py       # All 24 F1 2026 tracks
│   ├── weather.py          # Dynamic weather logic
│   ├── visualizations.py   # Seaborn/Matplotlib charts
│   ├── requirements.txt    # Production dependencies
│   ├── requirements-dev.txt# Test dependencies (pytest, httpx)
│   ├── Dockerfile
│   ├── .env.example
│   ├── scripts/
│   │   └── benchmark.py    # Performance validation script
│   └── tests/
│       ├── test_api.py
│       ├── test_monte_carlo.py
│       └── test_optimizer.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx      # Main multi-card layout (split into sub-components)
│   │   │   ├── Header.jsx         # Logo, track selector, controls
│   │   │   ├── ErrorBanner.jsx    # Animated error alert (ARIA live region)
│   │   │   ├── StatsRow.jsx       # Race overview stats strip
│   │   │   ├── Footer.jsx         # Tech stack info
│   │   │   ├── CircuitMap.jsx     # D3.js SVG track + animated car
│   │   │   ├── LapTimeChart.jsx   # Recharts lap time visualization
│   │   │   ├── PitStrategy.jsx    # Pitstop timeline
│   │   │   ├── TireStrategy.jsx   # Compound donut chart
│   │   │   ├── TelemetryCard.jsx  # Live telemetry numbers
│   │   │   └── WeatherToggle.jsx  # Weather panel
│   │   ├── api/strategyApi.js     # Axios client (error interceptor, 20s timeout)
│   │   ├── data/trackPaths.js     # SVG paths for all 24 circuits
│   │   └── styles/global.css      # Design system + component CSS classes
│   ├── Dockerfile
│   └── vite.config.js             # Proxy to :8000 + Vitest config
│
└── docker-compose.yml
```

---

## 🔬 Mathematical Foundation

### Tire Degradation Model
```
deg(lap) = α · lap^β + γ · exp(δ · lap)
```
- **Polynomial term** `α · lap^β` — moderate early wear phase (linear-ish growth)
- **Exponential term** `γ · exp(δ · lap)` — cliff emergence at high lap counts
- Parameters are compound-specific (Soft/Medium/Hard/Inter/Wet)
- Precomputed as a lookup table per (compound, weather, track temp) for O(1) per-lap cost in the simulation loop

### Optimization Problem
```
Minimise: f(x) = Σ lap_times(x) + Σ pit_time_losses(x)

Subject to:
  g₁(x): max_laps_i − stint_length_i ≥ 0    [tire life]
  g₂(x): ≥ 2 different compounds used         [F1 regulation]
  g₃(x): min gap between stops ≥ 5 laps       [physical constraint]
  g₄(x): pit laps within valid window          [strategic constraint]

Post-hoc diagnostic: ||∇g(x)||₂  (constraint sensitivity at the solution)
```

---

## 🧪 Tests

### Backend
```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm test
```

### Performance benchmark
```bash
cd backend
python scripts/benchmark.py
# All 5 configurations should complete in < 5s each
```

---

## 🛠️ Technologies

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, Uvicorn |
| Simulation | NumPy, Pandas, Monte Carlo |
| Optimization | Scipy.optimize (SLSQP), ThreadPoolExecutor |
| Visualization | Seaborn, Matplotlib |
| Frontend | React 18, Vite |
| Charts | Recharts, D3.js |
| Animation | Framer Motion |
| Fonts | Inter, JetBrains Mono |
| CI | GitHub Actions |
| Containers | Docker, Docker Compose |
