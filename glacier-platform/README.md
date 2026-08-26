# 🏔️ Himalayan Cryosphere Intelligence & Early-Warning Platform

A continuously-updated glacier monitoring and early-warning system for the
**Nepal–Tibet Himalayan border** (Purepu Glacier / Lhende Khola / Bhote Koshi /
Rasuwagadhi / Timure / Syabrubesi / Gyirong), expandable to any glacier globally.

It fuses satellite, meteorological, seismic and hydrological data into
**evidence-grounded hazard indicators** for rapid melt, glacial-lake expansion,
GLOF, ice / rock-ice avalanche, landslide, river blockage, natural-dam
formation/failure, debris flow and downstream flooding.

> **The core promise:** the platform never pretends delayed satellite data is
> live and never fabricates a measurement. Every observation displays its
> **source + acquisition time + processing time + spatial resolution +
> confidence + age of data**, and anything unknown is shown as `UNKNOWN` — not
> replaced with an invented number.

---

## What runs today (no credentials required)

The backend and frontend run out of the box against **public, no-auth**
scientific sources:

| Capability | Source | Status |
|---|---|---|
| Earthquakes (near-real-time) | USGS FDSN event service | ✅ live |
| Weather (hourly, recent) | Open-Meteo multi-model | ✅ live (model) |
| Forecast (to 10 days) | Open-Meteo | ✅ live (forecast) |
| Climatology / normals | Open-Meteo ERA5 archive | ✅ live (reanalysis) |
| Glacier elevation (DEM) | Copernicus DEM via Open-Meteo | ✅ live |
| Temperature intelligence, anomaly, trend | computed | ✅ |
| Elevation (lapse-rate) correction | computed | ✅ |
| Positive Degree Days (PDD) | computed | ✅ |
| Freeze–thaw cycles | computed | ✅ |
| Freezing-level analysis | Open-Meteo + computed | ✅ |
| Precipitation / snow (rain-snow split) | Open-Meteo + computed | ✅ |
| **Transparent weighted risk engine** | computed | ✅ |
| **AI evidence-fusion analyst** | computed | ✅ |
| Alert engine | computed | ✅ |
| Command-center dashboard | Next.js | ✅ |

### Scaffolded — honest `UNKNOWN` until credentials/workers are wired

These are implemented as real connectors/contracts that return `UNKNOWN`
(never fake data) until configured:

| Capability | Needs |
|---|---|
| Sentinel-1 SAR + Sentinel-2 optical scene metadata | `COPERNICUS_CLIENT_ID/SECRET` |
| Satellite surface (skin) temperature (VIIRS/MODIS) | `NASA_EARTHDATA_TOKEN` |
| Pixel-level change detection, lake delineation, glacier velocity | Celery worker + GDAL/rasterio stack |
| PostGIS persistence & history | Postgres (schema included) |
| 3D CesiumJS Earth + Time Machine | `CESIUM_ION_TOKEN` + tile store |

See `docs/ROADMAP.md` for the sequencing.

---

## Quick start

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt        # ~5 light deps for the API
uvicorn app.main:app --reload --port 8000
```

Open <http://localhost:8000/docs> for the interactive API.
`GET /config` shows exactly which connectors are live vs. UNKNOWN-only.

### Frontend (Next.js command center)

```bash
cd frontend
npm install
npm run dev            # http://localhost:3001
```

### Full stack (Postgres + PostGIS + Redis + API + web)

```bash
cp .env.example .env   # add credentials to enable scaffolded connectors
docker compose up --build
```

### Tests

```bash
cd backend && python -m pytest tests/ -q
```

The suite validates the maths **and** the integrity guarantees (no fabrication,
correct model/forecast/measured labelling, confidence propagation, UNKNOWN ≠ 0).

---

## API

```
GET  /glaciers                       list monitored glaciers
POST /glaciers                       admin: add a glacier (lat/lon/polygon/elev/radius)
GET  /glaciers/{id}                  full fused report (all cards + risk + analyst)
GET  /glaciers/{id}/temperature      temp intelligence, PDD, freeze-thaw, freezing level
GET  /glaciers/{id}/weather          precipitation + temperature
GET  /glaciers/{id}/satellite        Sentinel-1/-2 coverage (metadata)
GET  /glaciers/{id}/lake             glacial-lake state
GET  /glaciers/{id}/velocity         surface velocity
GET  /glaciers/{id}/earthquakes      nearby seismicity + association class
GET  /glaciers/{id}/risk             transparent risk breakdown + analyst
GET  /glaciers/{id}/timeline         time-machine scene catalogue
GET  /glaciers/{id}/alerts           alerts for one glacier
GET  /alerts                         all active alerts
GET  /events                         recent observation events
GET  /config                         connector live/unknown transparency
```

---

## Architecture

```
Satellite ─┐
Weather  ──┤
Temp/DEM ──┤
Seismic  ──┼─► Connectors (provenance-wrapped Observations, or UNKNOWN)
Hydrology ─┘
                │
                ▼
        Engines (elevation/lapse-rate, temperature intelligence, PDD,
        freeze-thaw, freezing level, precipitation, change detection)
                │
                ▼
        Risk engine (transparent weighted components)  ──►  AI analyst
                │                                              │
                ▼                                              ▼
            Alert engine  ───────────────►  API  ───────►  Command-center UI
```

Every value flows as an `Observation[T]` carrying a `Provenance`
(source, kinds, times, resolution) plus `Confidence` and freshness. See
`backend/app/core/` — the integrity core — and `docs/ARCHITECTURE.md`.

---

## Scientific rules enforced in code

- `may_call_live()` returns `LIVE` only for near-real-time sources within minutes.
- Air (2 m) temperature and satellite **surface/skin** temperature are separate types and cards.
- Model (ERA5/NWP), forecast, measured, derived and **elevation-adjusted** are distinct `ValueKind`s.
- Lapse-rate corrections are labelled *estimated, not measured*, with the assumption shown; large corrections downgrade confidence.
- QC **rejects** impossible values (never clamps or invents); missing → `UNKNOWN`.
- Earthquakes are reported as temporal/spatial **association**, never as a stated cause.
- Risk is a **transparent weighted blend** (each factor: value, source, weight, contribution, confidence, age), never a blind average; missing factors renormalise rather than count as zero risk.
- Risk output is labelled **“Experimental hazard indicator — not an official evacuation warning.”**

---

## License

MIT. Built as a scientific-integrity-first reference implementation; not an
operational warning system on its own.
