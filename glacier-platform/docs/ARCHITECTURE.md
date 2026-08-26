# Architecture

## Layers

1. **Integrity core** (`backend/app/core/`)
   - `provenance.py` — `Observation[T]`, `Provenance`, `Confidence`, `ValueKind`,
     `DataSource`. Nothing leaves a connector without this wrapper.
   - `freshness.py` — age → human string + FRESH/DELAYED/STALE, and the strict
     `may_call_live()` gate. Per-source cadence profiles.
   - `units.py` — Kelvin↔Celsius, physical plausibility bounds, QC that rejects
     (never clamps/invents) impossible values.

2. **Connectors** (`backend/app/connectors/`) — fetch real data or return
   `UNKNOWN`.
   - `usgs_earthquakes.py` — public, near-real-time (may be LIVE).
   - `open_meteo.py` — public: recent weather (model), forecast, ERA5 archive
     (climatology), Copernicus DEM elevation.
   - `copernicus_sentinel.py` — Sentinel-1/-2 STAC search (auth-gated).
   - `nasa_lst.py` — VIIRS/MODIS surface temperature (auth-gated).

3. **Engines** (`backend/app/engines/`) — pure computation, fully unit-tested.
   - `elevation.py` (lapse-rate), `temperature.py` (intelligence + anomaly),
     `pdd.py`, `freeze_thaw.py`, `freezing_level.py`, `precipitation.py`,
     `change_detection.py` (contract), `risk.py` (transparent weighted model),
     `ai_analyst.py`, `alerts.py`.

4. **Domain** (`backend/app/domain/`)
   - `glaciers.py` — seed reference geometry (approximate, labelled non-measured).
   - `assemble.py` — the fusion pipeline.
   - `registry.py` — glacier registry + short TTL report cache (freshness
     recomputed on read, never misrepresented as newer than the data).

5. **API** (`backend/app/api/`) — FastAPI routes; `main.py` app.

6. **Persistence** (`backend/app/db/schema.sql`) — PostgreSQL + PostGIS. Raw
   source values and processed values are stored in separate columns; every
   observation row carries source, times, resolution, confidence, value-kind.

7. **Frontend** (`frontend/`) — Next.js App Router command center. Every card
   renders provenance + freshness + confidence badges; `LIVE` is shown only when
   the backend confirms it.

## The fusion pipeline (`assemble.py`)

```
reference glacier
  → DEM/model elevation
  → recent weather (model)  ─┐
  → ERA5 climatology         │→ elevation-adjust series → temperature intelligence
                             │                          → PDD
                             │                          → freeze-thaw
                             │                          → freezing level
                             │                          → precipitation
  → surface temperature (LST, separate)
  → earthquakes (association only)
  → Sentinel-1/-2 scene metadata → change-pair validity
  → lake / velocity (UNKNOWN until worker)
  → downstream exposure
  → risk engine (transparent weighted components)
  → AI analyst (evidence-grounded, non-predictive)
  → alerts
```

## Missing-data policy

A missing input is `UNKNOWN`, propagates as such, and is **excluded** from any
derived score (weights renormalise). It is never treated as `0`. A component or
the overall risk becomes `UNKNOWN` when it has no available factors — the UI
shows `UNKNOWN`, not a falsely reassuring low score.

## Extending

- **Workers**: add a Celery app (`redis` broker) for scene download, cloud
  masking, NDSI/NDWI, lake delineation, SAR change, InSAR coherence/displacement,
  and feature-tracked velocity. Write results into the `*_measurements` /
  `change_events` / `glacier_velocity` tables and the risk engine picks them up.
- **New glacier**: `POST /glaciers` with lat/lon (+ optional polygon, elevations,
  radius). Everything else is derived from real connectors at runtime.
