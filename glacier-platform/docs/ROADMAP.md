# Roadmap

The current build delivers the integrity core, the public-source connectors,
the full compute/risk/analyst/alert stack, the API, and the command-center
frontend. The following extend it toward the full operational vision. Each item
preserves the non-negotiable rule: **no fabricated data; UNKNOWN when unknown.**

## 1. Imagery workers (Celery + GDAL/rasterio/xarray)
- Sentinel-2 L2A download → cloud mask (SCL) → NDSI/NDWI → snow/glacier/water/
  lake extent → lake-area change time series.
- Sentinel-1 GRD → speckle filter → change detection between consecutive passes
  → flooded-terrain / wet-snow / avalanche-scar candidates (flagged, unverified).
- Feature-tracking (e.g. autoRIFT-style) for surface velocity.
- Optional InSAR coherence + displacement time series.

## 2. PostGIS persistence + history
- Wire SQLAlchemy/GeoAlchemy2 sessions; write every `Observation` to the raw +
  processed columns already defined in `schema.sql`.
- Serve the Time Machine and temperature graphs from stored history.

## 3. Change-detection product
- Before / after / difference tiles per glacier, with cloud-validity flags.
- Persist `change_events` and surface them in `/events`.

## 4. 3D Earth (CesiumJS) + Time Machine
- Cesium globe with layers: glacier polygons, lakes, rivers, watersheds, DEM,
  imagery, SAR change, surface temperature, anomaly, precipitation, snowfall,
  earthquakes, slope movement, flood corridors, settlements, bridges, roads,
  hydropower.
- Timeline slider (2015→present) + before/after comparison.
- Optional Google Photorealistic 3D Tiles where API access is configured.

## 5. River & blockage detection
- Ingest river-gauge feeds where available (level, discharge, rate-of-rise,
  percentile). Cross-reference with SAR/optical to raise
  `POSSIBLE RIVER BLOCKAGE — REQUIRES VERIFICATION` (never a confirmed dam).

## 6. Ingestion scheduling
- Weather hourly; earthquakes near-real-time polling; river gauges at best
  reliable cadence; satellite catalogue polled for new scenes with scene-id +
  hash deduplication; risk recomputed after any material new observation.

## 7. Alerting delivery
- Persist alerts, add acknowledgement workflow, and optional push/webhook
  delivery with downstream-catchment routing traced on the DEM flow network.
