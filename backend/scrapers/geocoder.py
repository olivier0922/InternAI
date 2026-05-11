"""
Batch Geocoder for Job Locations
Uses OpenStreetMap Nominatim (free, no API key) to convert location strings to lat/lng.
Rate-limited to 1 request/second per Nominatim usage policy.
"""
import time
import json
import os
import sys
from pathlib import Path
import httpx
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))
load_dotenv(Path(__file__).parent.parent / ".env")

from supabase import create_client

CACHE_FILE = Path(__file__).parent / ".geocache.json"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "InternAI-Geocoder/1.0 (student project)"}

# Load cache
_cache: dict = {}
if CACHE_FILE.exists():
    try:
        _cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        _cache = {}


def _save_cache():
    CACHE_FILE.write_text(json.dumps(_cache, ensure_ascii=False, indent=2), encoding="utf-8")


def geocode(location: str) -> tuple[float, float] | None:
    """Geocode a location string to (lat, lng). Returns None on failure."""
    if not location or location.lower() in ("remote", "worldwide", "anywhere", "global", "unknown", "usa", "europe"):
        return None

    # Check cache
    key = location.strip().lower()
    if key in _cache:
        val = _cache[key]
        if val is None:
            return None
        return (val[0], val[1])

    # Rate limit
    time.sleep(1.1)

    try:
        resp = httpx.get(
            NOMINATIM_URL,
            params={"q": location, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()

        if results:
            lat = float(results[0]["lat"])
            lng = float(results[0]["lon"])
            _cache[key] = [lat, lng]
            _save_cache()
            return (lat, lng)
        else:
            _cache[key] = None
            _save_cache()
            return None
    except Exception as e:
        print(f"  [GEOCODE ERROR] {location}: {e}")
        return None


def run_geocoder():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_KEY")
        return

    sb = create_client(url, key)

    # Fetch jobs missing coordinates
    result = sb.table("jobs").select("id, location, latitude, longitude").execute()
    all_jobs = result.data or []

    needs_geocoding = [j for j in all_jobs if j.get("location") and j.get("latitude") is None]
    already_done = len(all_jobs) - len(needs_geocoding)

    print(f"Total jobs: {len(all_jobs)}")
    print(f"Already geocoded: {already_done}")
    print(f"Need geocoding: {len(needs_geocoding)}")
    print(f"Cache entries: {len(_cache)}")
    print()

    geocoded = 0
    failed = 0

    for i, job in enumerate(needs_geocoding):
        loc = job["location"]
        progress = f"[{i+1}/{len(needs_geocoding)}]"

        coords = geocode(loc)
        if coords:
            lat, lng = coords
            sb.table("jobs").update({"latitude": lat, "longitude": lng}).eq("id", job["id"]).execute()
            print(f"  {progress} OK: {loc} -> ({lat:.4f}, {lng:.4f})")
            geocoded += 1
        else:
            print(f"  {progress} FAIL: {loc} -> no result")
            failed += 1

    print(f"\nDone: {geocoded} geocoded, {failed} failed")


if __name__ == "__main__":
    run_geocoder()
