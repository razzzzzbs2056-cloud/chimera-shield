"""
Himalayan Glacier Intelligence & Early-Warning Platform -- API entrypoint.

A continuously-updated cryosphere intelligence system. The design promise:
every observation displays source + acquisition time + processing time +
spatial resolution + confidence + age, and the platform NEVER pretends delayed
satellite data is live, nor fabricates any measurement.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router

app = FastAPI(
    title="Himalayan Glacier Intelligence & Early-Warning Platform",
    version="0.1.0",
    description=(
        "Continuous glacier monitoring for the Nepal-Tibet border and beyond. "
        "Detects conditions that may increase the probability of rapid melt, "
        "glacial-lake expansion, GLOF, ice/rock-ice avalanche, landslide, river "
        "blockage, dam formation/failure, debris flow and downstream flooding. "
        "All outputs are experimental hazard indicators, not official warnings."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["meta"])
async def root():
    return {
        "service": "himalayan-glacier-intelligence",
        "version": "0.1.0",
        "principles": [
            "Never present delayed satellite data as live.",
            "Every observation carries source, times, resolution, confidence, age.",
            "Missing data is UNKNOWN, never invented.",
            "Air temperature != surface temperature; model != measurement; "
            "forecast != observation; correlation != causation.",
            "Risk scores are experimental indicators, not evacuation warnings.",
        ],
        "docs": "/docs",
    }


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}
