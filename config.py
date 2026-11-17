import os

def _load_env_file():
    """Lightweight built-in .env parser to avoid requiring external packages."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
        except Exception:
            pass

_load_env_file()

class Config:
    """Application configuration loaded from environment variables with sensible defaults."""
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "0.0.0.0")

    # OSRM routing endpoints. The public FOSSGIS service exposes separate
    # profile-specific instances; the URL prefix selects the actual graph.
    # OSRM_BASE_URL remains as a backward-compatible car endpoint override.
    OSRM_BASE_URL = os.environ.get(
        "OSRM_BASE_URL", "https://routing.openstreetmap.de/routed-car"
    ).rstrip("/")
    OSRM_CAR_BASE_URL = os.environ.get("OSRM_CAR_BASE_URL", OSRM_BASE_URL).rstrip("/")
    OSRM_FOOT_BASE_URL = os.environ.get(
        "OSRM_FOOT_BASE_URL", "https://routing.openstreetmap.de/routed-foot"
    ).rstrip("/")
    OSRM_BIKE_BASE_URL = os.environ.get(
        "OSRM_BIKE_BASE_URL", "https://routing.openstreetmap.de/routed-bike"
    ).rstrip("/")

    # Photon Geocoding API URL (Search & Reverse Geocoding)
    PHOTON_URL = os.environ.get("PHOTON_URL", "https://photon.komoot.io")

    # OpenRouteService API Key (Optional legacy support)
    ORS_API_KEY = os.environ.get("ORS_API_KEY", "")
    ORS_BASE_URL = os.environ.get("ORS_BASE_URL", "https://api.openrouteservice.org")

    # Overpass API (Public Read-Only OSM Endpoint)
    OVERPASS_URL = os.environ.get(
        "OVERPASS_URL", "https://overpass.private.coffee/api/interpreter"
    )
    OVERPASS_BACKUP_URL = os.environ.get(
        "OVERPASS_BACKUP_URL", "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
    )
    OVERPASS_FALLBACK_URL = os.environ.get(
        "OVERPASS_FALLBACK_URL", "https://overpass-api.de/api/interpreter"
    )

    # Cache TTL in seconds for Overpass queries
    CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", 1800))  # 30 minutes

    # Campus Data File Path
    CAMPUS_DATA_FILE = os.path.join(os.path.dirname(__file__), "campus_data.json")
    HISTORY_DATA_FILE = os.path.join(os.path.dirname(__file__), "history_data.json")

