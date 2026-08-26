-- Himalayan Glacier Intelligence Platform -- PostgreSQL + PostGIS schema
--
-- Design rules encoded here:
--   * Raw source values and processed values are stored SEPARATELY.
--   * Every observation row carries source, acquisition_time, processing_time,
--     spatial_resolution, confidence, and (derived) age.
--   * Value kind (measured/model/forecast/derived/elevation_adjusted) is a
--     column so a model or forecast can never be mistaken for a measurement.
--   * NULL means UNKNOWN. We never write invented substitutes.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- gen_random_uuid()

-- ---------------------------------------------------------------------------
-- Enumerations
-- ---------------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE confidence_level AS ENUM ('UNKNOWN','LOW','MEDIUM','HIGH');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE value_kind AS ENUM
      ('measured','model','forecast','derived',
       'elevation_adjusted','elevation_adjusted_forecast');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE freshness_status AS ENUM ('FRESH','DELAYED','STALE','UNKNOWN');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---------------------------------------------------------------------------
-- Reference / provenance
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS data_sources (
    id            TEXT PRIMARY KEY,             -- slug, e.g. 'usgs_earthquakes'
    name          TEXT NOT NULL,
    provider      TEXT NOT NULL,
    authoritative BOOLEAN NOT NULL DEFAULT TRUE, -- FALSE for social/unofficial
    near_real_time BOOLEAN NOT NULL DEFAULT FALSE,
    url           TEXT,
    license       TEXT
);

-- ---------------------------------------------------------------------------
-- Core targets
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS glaciers (
    id                   TEXT PRIMARY KEY,
    name                 TEXT NOT NULL,
    location             GEOGRAPHY(Point,4326) NOT NULL,
    polygon              GEOGRAPHY(Polygon,4326),        -- optional glacier outline
    catchment_polygon    GEOGRAPHY(Polygon,4326),
    terminus_elevation_m DOUBLE PRECISION,
    median_elevation_m   DOUBLE PRECISION,
    headwall_elevation_m DOUBLE PRECISION,
    country              TEXT,
    catchment            TEXT,
    river_system         TEXT,
    monitor_radius_km    DOUBLE PRECISION NOT NULL DEFAULT 100,
    elevation_source     TEXT,                            -- provenance of geometry
    external_ids         JSONB,                           -- e.g. GLIMS/RGI ids
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS glaciers_gix ON glaciers USING GIST (location);

CREATE TABLE IF NOT EXISTS glacier_polygons (
    id           BIGSERIAL PRIMARY KEY,
    glacier_id   TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    outline      GEOGRAPHY(Polygon,4326) NOT NULL,
    area_km2     DOUBLE PRECISION,                -- processed
    raw_area_px  DOUBLE PRECISION,                -- raw (pixel count) if any
    debris_fraction DOUBLE PRECISION,
    snow_fraction   DOUBLE PRECISION,
    source_id    TEXT REFERENCES data_sources(id),
    value_kind   value_kind NOT NULL DEFAULT 'derived',
    acquisition_time TIMESTAMPTZ,
    processing_time  TIMESTAMPTZ NOT NULL DEFAULT now(),
    spatial_resolution_m DOUBLE PRECISION,
    confidence   confidence_level NOT NULL DEFAULT 'UNKNOWN'
);

CREATE TABLE IF NOT EXISTS infrastructure (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    kind         TEXT NOT NULL,                   -- settlement|bridge|road|hydropower|border
    location     GEOGRAPHY(Point,4326) NOT NULL,
    elevation_m  DOUBLE PRECISION,
    river_system TEXT
);
CREATE INDEX IF NOT EXISTS infra_gix ON infrastructure USING GIST (location);

-- ---------------------------------------------------------------------------
-- Observations (raw + processed side by side)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weather_observations (
    id            BIGSERIAL PRIMARY KEY,
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    source_id     TEXT REFERENCES data_sources(id),
    value_kind    value_kind NOT NULL,            -- model | forecast
    acquisition_time TIMESTAMPTZ NOT NULL,        -- the hour represented
    processing_time  TIMESTAMPTZ NOT NULL DEFAULT now(),
    model_grid_elevation_m DOUBLE PRECISION,
    -- raw source values
    raw_air_temp_c        DOUBLE PRECISION,
    raw_dewpoint_c        DOUBLE PRECISION,
    -- processed / adjusted
    air_temp_c            DOUBLE PRECISION,        -- may equal raw if no adj
    adjusted_glacier_temp_c DOUBLE PRECISION,      -- elevation-adjusted estimate
    lapse_rate_c_per_m    DOUBLE PRECISION,
    relative_humidity_pct DOUBLE PRECISION,
    surface_pressure_hpa  DOUBLE PRECISION,
    wind_speed_ms         DOUBLE PRECISION,
    wind_direction_deg    DOUBLE PRECISION,
    solar_radiation_wm2   DOUBLE PRECISION,
    cloud_cover_pct       DOUBLE PRECISION,
    precipitation_mm      DOUBLE PRECISION,
    rain_mm               DOUBLE PRECISION,
    snowfall_cm           DOUBLE PRECISION,
    snow_depth_m          DOUBLE PRECISION,
    freezing_level_m      DOUBLE PRECISION,
    confidence            confidence_level NOT NULL DEFAULT 'UNKNOWN',
    UNIQUE (glacier_id, source_id, value_kind, acquisition_time)
);
CREATE INDEX IF NOT EXISTS wx_glacier_time ON weather_observations (glacier_id, acquisition_time DESC);

-- Satellite surface (skin) temperature -- STORED SEPARATELY from air temp.
CREATE TABLE IF NOT EXISTS surface_temperature (
    id            BIGSERIAL PRIMARY KEY,
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    source_id     TEXT REFERENCES data_sources(id),
    acquisition_time TIMESTAMPTZ NOT NULL,
    processing_time  TIMESTAMPTZ NOT NULL DEFAULT now(),
    daytime       BOOLEAN,
    raw_value_k   DOUBLE PRECISION,               -- raw Kelvin
    surface_temp_c DOUBLE PRECISION,              -- processed Celsius
    quality_flag  TEXT,
    cloud_flag    TEXT,
    spatial_resolution_m DOUBLE PRECISION,
    confidence    confidence_level NOT NULL DEFAULT 'UNKNOWN'
);

CREATE TABLE IF NOT EXISTS satellite_scenes (
    id            BIGSERIAL PRIMARY KEY,
    scene_id      TEXT UNIQUE NOT NULL,           -- provider scene id (dedup key)
    scene_hash    TEXT,                           -- content hash (dedup)
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    source_id     TEXT REFERENCES data_sources(id),
    modality      TEXT NOT NULL,                  -- optical | sar | thermal
    acquisition_time TIMESTAMPTZ NOT NULL,
    ingest_time   TIMESTAMPTZ NOT NULL DEFAULT now(),
    cloud_cover_pct DOUBLE PRECISION,
    orbit_direction TEXT,
    incidence_angle_deg DOUBLE PRECISION,
    polarizations TEXT,
    spatial_resolution_m DOUBLE PRECISION,
    footprint     GEOGRAPHY(Polygon,4326),
    metadata      JSONB
);
CREATE INDEX IF NOT EXISTS scenes_glacier_time ON satellite_scenes (glacier_id, acquisition_time DESC);

CREATE TABLE IF NOT EXISTS snow_extent (
    id            BIGSERIAL PRIMARY KEY,
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    source_id     TEXT REFERENCES data_sources(id),
    acquisition_time TIMESTAMPTZ NOT NULL,
    processing_time  TIMESTAMPTZ NOT NULL DEFAULT now(),
    snow_covered_area_km2 DOUBLE PRECISION,
    snowline_altitude_m   DOUBLE PRECISION,
    wet_snow_flag BOOLEAN,
    cloud_cover_pct DOUBLE PRECISION,
    spatial_resolution_m DOUBLE PRECISION,
    value_kind    value_kind NOT NULL DEFAULT 'derived',
    confidence    confidence_level NOT NULL DEFAULT 'UNKNOWN'
);

CREATE TABLE IF NOT EXISTS glacial_lakes (
    id            TEXT PRIMARY KEY,
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE SET NULL,
    name          TEXT,
    outline       GEOGRAPHY(Polygon,4326),
    elevation_m   DOUBLE PRECISION,
    distance_from_glacier_km DOUBLE PRECISION,
    downstream_outlet GEOGRAPHY(Point,4326),
    historical_max_area_km2 DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS lake_measurements (
    id            BIGSERIAL PRIMARY KEY,
    lake_id       TEXT REFERENCES glacial_lakes(id) ON DELETE CASCADE,
    source_id     TEXT REFERENCES data_sources(id),
    acquisition_time TIMESTAMPTZ NOT NULL,
    processing_time  TIMESTAMPTZ NOT NULL DEFAULT now(),
    area_km2      DOUBLE PRECISION,
    perimeter_km  DOUBLE PRECISION,
    outline       GEOGRAPHY(Polygon,4326),
    cloud_cover_pct DOUBLE PRECISION,
    spatial_resolution_m DOUBLE PRECISION,
    value_kind    value_kind NOT NULL DEFAULT 'derived',
    confidence    confidence_level NOT NULL DEFAULT 'UNKNOWN'
);
CREATE INDEX IF NOT EXISTS lake_meas_time ON lake_measurements (lake_id, acquisition_time DESC);

CREATE TABLE IF NOT EXISTS glacier_velocity (
    id            BIGSERIAL PRIMARY KEY,
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    source_id     TEXT REFERENCES data_sources(id),
    period_start  TIMESTAMPTZ NOT NULL,
    period_end    TIMESTAMPTZ NOT NULL,
    processing_time TIMESTAMPTZ NOT NULL DEFAULT now(),
    velocity_m_per_day DOUBLE PRECISION,
    method        TEXT,                           -- feature-tracking | product
    spatial_resolution_m DOUBLE PRECISION,
    confidence    confidence_level NOT NULL DEFAULT 'UNKNOWN'
);

CREATE TABLE IF NOT EXISTS earthquakes (
    event_id      TEXT PRIMARY KEY,               -- USGS id (dedup)
    magnitude     DOUBLE PRECISION,
    location      GEOGRAPHY(Point,4326),
    depth_km      DOUBLE PRECISION,
    origin_time   TIMESTAMPTZ,
    update_time   TIMESTAMPTZ,
    place         TEXT,
    source_id     TEXT REFERENCES data_sources(id),
    ingest_time   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS eq_gix ON earthquakes USING GIST (location);
CREATE INDEX IF NOT EXISTS eq_time ON earthquakes (origin_time DESC);

CREATE TABLE IF NOT EXISTS river_observations (
    id            BIGSERIAL PRIMARY KEY,
    station_id    TEXT NOT NULL,
    location      GEOGRAPHY(Point,4326),
    source_id     TEXT REFERENCES data_sources(id),
    acquisition_time TIMESTAMPTZ NOT NULL,
    processing_time  TIMESTAMPTZ NOT NULL DEFAULT now(),
    water_level_m DOUBLE PRECISION,
    discharge_m3s DOUBLE PRECISION,
    rate_of_rise_m_per_h DOUBLE PRECISION,
    historical_percentile DOUBLE PRECISION,
    confidence    confidence_level NOT NULL DEFAULT 'UNKNOWN'
);
CREATE INDEX IF NOT EXISTS river_time ON river_observations (station_id, acquisition_time DESC);

CREATE TABLE IF NOT EXISTS terrain_features (
    id            BIGSERIAL PRIMARY KEY,
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    dem_source_id TEXT REFERENCES data_sources(id),
    slope_deg     DOUBLE PRECISION,
    aspect_deg    DOUBLE PRECISION,
    curvature     DOUBLE PRECISION,
    flow_accumulation DOUBLE PRECISION,
    avalanche_path GEOGRAPHY(LineString,4326),
    debris_flow_path GEOGRAPHY(LineString,4326),
    spatial_resolution_m DOUBLE PRECISION,
    computed_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Analytics
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS change_events (
    id            BIGSERIAL PRIMARY KEY,
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    modality      TEXT NOT NULL,                  -- optical | sar
    before_scene_id TEXT,
    after_scene_id  TEXT,
    detected_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    change_type   TEXT,                           -- avalanche_scar|flood|new_lake|...
    magnitude     DOUBLE PRECISION,
    geom          GEOGRAPHY(Polygon,4326),
    valid_for_change BOOLEAN NOT NULL DEFAULT TRUE, -- FALSE if cloudy/unverified
    confidence    confidence_level NOT NULL DEFAULT 'UNKNOWN',
    evidence      JSONB
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id            BIGSERIAL PRIMARY KEY,
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    computed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    score_0_100   DOUBLE PRECISION,               -- NULL => UNKNOWN
    level         TEXT,
    confidence    confidence_level NOT NULL DEFAULT 'UNKNOWN',
    components    JSONB NOT NULL,                 -- full transparent breakdown
    weights       JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS risk_time ON risk_scores (glacier_id, computed_at DESC);

CREATE TABLE IF NOT EXISTS alerts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    glacier_id    TEXT REFERENCES glaciers(id) ON DELETE CASCADE,
    condition     TEXT NOT NULL,
    severity      TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    location      GEOGRAPHY(Point,4326),
    evidence      JSONB,
    confidence    confidence_level NOT NULL DEFAULT 'UNKNOWN',
    recommended_investigation TEXT,
    affected_downstream JSONB,
    acknowledged  BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS alerts_time ON alerts (created_at DESC);

-- Seed the known authoritative sources.
INSERT INTO data_sources (id,name,provider,authoritative,near_real_time,url,license) VALUES
 ('usgs_earthquakes','USGS Earthquake Catalog','USGS',TRUE,TRUE,'https://earthquake.usgs.gov/','public domain'),
 ('open_meteo_forecast','Open-Meteo Forecast','Open-Meteo',TRUE,FALSE,'https://open-meteo.com/','CC-BY 4.0'),
 ('open_meteo_era5','Open-Meteo ERA5 archive','ECMWF/Copernicus',TRUE,FALSE,'https://open-meteo.com/','CC-BY 4.0'),
 ('open_meteo_elevation','Open-Meteo Elevation (Copernicus DEM)','ESA/Copernicus',TRUE,FALSE,'https://open-meteo.com/','CC-BY 4.0'),
 ('sentinel1_grd','Sentinel-1 GRD','ESA/Copernicus',TRUE,FALSE,'https://dataspace.copernicus.eu/','Copernicus open data'),
 ('sentinel2_l2a','Sentinel-2 L2A','ESA/Copernicus',TRUE,FALSE,'https://dataspace.copernicus.eu/','Copernicus open data'),
 ('viirs_lst','VIIRS Land Surface Temperature','NASA',TRUE,FALSE,'https://www.earthdata.nasa.gov/','NASA open data')
ON CONFLICT (id) DO NOTHING;
