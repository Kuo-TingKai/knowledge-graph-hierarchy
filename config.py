from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"

# Create cache directory if not exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API endpoints
DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

# Cache settings
CACHE_EXPIRY = 86400  # 24 hours in seconds