"""
Cream Beans — Campus Lost & Found Intelligence System
FastAPI backend entrypoint.

Run locally:
    uvicorn backend.main:app --reload

This file only wires routers together. All business logic lives in
backend/services/, all DB access in backend/database/, and the AI
integration is isolated to backend/services/match_service.py.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import auth_routes, claims, health, items
from backend.config import settings

app = FastAPI(
    title="Cream Beans — Lost & Found Intelligence API",
    description=(
        "Bridges the frontend, Supabase, and the existing AI matching "
        "engine for the SIH 2026 campus lost & found system."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth_routes.router)
app.include_router(items.router)
app.include_router(claims.router)
