"""Runtime configuration. Secrets are read from the environment; nothing is
hard-coded. Connectors that require credentials degrade to UNKNOWN (no data)
when their credentials are absent -- they never fabricate."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


@dataclass
class Settings:
    # --- Public, no-auth connectors (work out of the box) ------------------
    open_meteo_forecast_url: str = _get(
        "OPEN_METEO_FORECAST_URL", "https://api.open-meteo.com/v1/forecast"
    )
    open_meteo_archive_url: str = _get(
        "OPEN_METEO_ARCHIVE_URL", "https://archive-api.open-meteo.com/v1/archive"
    )
    open_meteo_elevation_url: str = _get(
        "OPEN_METEO_ELEVATION_URL", "https://api.open-meteo.com/v1/elevation"
    )
    usgs_earthquake_url: str = _get(
        "USGS_EARTHQUAKE_URL",
        "https://earthquake.usgs.gov/fdsnws/event/1/query",
    )

    # --- Auth-gated connectors (structured stubs until configured) ---------
    copernicus_client_id: str = _get("COPERNICUS_CLIENT_ID")
    copernicus_client_secret: str = _get("COPERNICUS_CLIENT_SECRET")
    copernicus_token_url: str = _get(
        "COPERNICUS_TOKEN_URL",
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    )
    copernicus_catalog_url: str = _get(
        "COPERNICUS_CATALOG_URL",
        "https://catalogue.dataspace.copernicus.eu/stac/search",
    )
    nasa_earthdata_token: str = _get("NASA_EARTHDATA_TOKEN")
    cesium_ion_token: str = _get("CESIUM_ION_TOKEN")

    # --- Infrastructure ----------------------------------------------------
    database_url: str = _get(
        "DATABASE_URL", "postgresql+psycopg://glacier:glacier@localhost:5432/glacier"
    )
    redis_url: str = _get("REDIS_URL", "redis://localhost:6379/0")

    # --- Behaviour ---------------------------------------------------------
    http_timeout_s: float = float(_get("HTTP_TIMEOUT_S", "30"))
    default_monitor_radius_km: float = float(_get("DEFAULT_MONITOR_RADIUS_KM", "100"))

    def copernicus_configured(self) -> bool:
        return bool(self.copernicus_client_id and self.copernicus_client_secret)

    def nasa_configured(self) -> bool:
        return bool(self.nasa_earthdata_token)


settings = Settings()
