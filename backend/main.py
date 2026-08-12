"""
main.py — F1 Race Strategy Simulation Engine
=============================================
FastAPI application entry point.

Configures:
  - CORS middleware (allows React dev server at localhost:5173 and 3000)
  - API router mounting
  - Startup event: pre-trains the Scikit-learn model at server start
    so the first API call is not slow due to model training

Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from monte_carlo import _get_model   # Pre-train model at startup

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("f1_engine")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-train the sklearn model on application startup."""
    logger.info("🏎️  F1 Race Strategy Engine starting up...")
    logger.info("🔧  Pre-training Scikit-learn GradientBoostingRegressor...")
    _get_model()
    logger.info("✅  Model ready. All 24 F1 2026 tracks loaded.")
    logger.info("🚀  API online at http://localhost:8000")
    yield
    logger.info("🏁  Shutting down F1 Race Strategy Engine.")


app = FastAPI(
    title="F1 Race Strategy & Telemetry Simulation Engine",
    description=(
        "Monte Carlo simulation engine for F1 race strategy prediction. "
        "Implements non-linear tire degradation modeling (Scikit-learn GBR), "
        "SLSQP optimization with g(x) constraints, and dynamic weather re-optimization. "
        "Supports all 24 circuits on the 2026 F1 calendar."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — Allow React dev server ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount API router ───────────────────────────────────────────────────────
app.include_router(router, prefix="/api")
