"""
main.py — F1 Race Strategy Simulation Engine
=============================================
FastAPI application entry point.

Configures:
  - CORS middleware (reads allowed origins from ALLOWED_ORIGINS env var,
    defaults to React dev server localhost addresses)
  - API router mounting under /api prefix
  - Startup lifespan: precomputes degradation lookups and logs readiness
  - Shutdown lifespan: shuts down the thread-pool executor in api.py

Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router, executor

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("f1_engine")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: warm up on start, clean up on shutdown."""
    logger.info("🏎️  F1 Race Strategy Engine starting up...")
    try:
        # Warm up degradation lookup cache for the most common compounds
        from monte_carlo import get_degradation_lookup, TIRE_COMPOUNDS
        from models import WeatherCondition, TireCompoundName
        dummy_weather = WeatherCondition()
        for compound in TireCompoundName:
            get_degradation_lookup(compound, dummy_weather)
        logger.info("✅  Degradation lookups precomputed. All 24 F1 2026 tracks loaded.")
    except Exception:
        logger.exception("⚠️  Startup warmup failed — continuing anyway")

    logger.info("🚀  API online at http://localhost:8000")
    yield

    logger.info("🏁  Shutting down F1 Race Strategy Engine.")
    executor.shutdown(wait=True)
    logger.info("✅  Thread pool executor shut down cleanly.")


app = FastAPI(
    title="F1 Race Strategy & Telemetry Simulation Engine",
    description=(
        "Monte Carlo simulation engine for F1 race strategy prediction. "
        "Implements analytical polynomial-exponential tire degradation modelling, "
        "SLSQP optimisation with g(x) constraints, and dynamic weather re-optimisation. "
        "Supports all 24 circuits on the 2026 F1 calendar."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — read from environment, default to React dev server ───────────────
_default_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
_env_origins = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins = (
    [o.strip() for o in _env_origins.split(",") if o.strip()]
    if _env_origins
    else _default_origins
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount API router ────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")
