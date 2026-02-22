from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import urlopen

PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


@dataclass
class PlacesSearchConfig:
    query: str
    api_key: str
    max_results: int = 60


def _normalize_result(raw: dict) -> dict[str, str | float | int | None]:
    location = raw.get("geometry", {}).get("location", {})
    return {
        "place_id": raw.get("place_id", ""),
        "name": raw.get("name", ""),
        "formatted_address": raw.get("formatted_address", ""),
        "rating": raw.get("rating", 0.0),
        "user_ratings_total": raw.get("user_ratings_total", 0),
        "business_status": raw.get("business_status", ""),
        "types": ",".join(raw.get("types", [])),
        "lat": location.get("lat"),
        "lng": location.get("lng"),
    }


def _request_json(params: dict[str, str]) -> dict:
    url = f"{PLACES_TEXT_SEARCH_URL}?{urlencode(params)}"
    with urlopen(url, timeout=30) as response:  # nosec B310 - trusted Google API endpoint
        return json.loads(response.read().decode("utf-8"))


def fetch_places(config: PlacesSearchConfig) -> Iterable[dict[str, str | float | int | None]]:
    params = {"query": config.query, "key": config.api_key}
    collected: list[dict[str, str | float | int | None]] = []
    next_page_token: str | None = None

    while len(collected) < config.max_results:
        if next_page_token:
            params = {"pagetoken": next_page_token, "key": config.api_key}
            time.sleep(2)

        payload = _request_json(params)
        status = payload.get("status")
        if status not in {"OK", "ZERO_RESULTS"}:
            message = payload.get("error_message", "No additional details provided.")
            raise RuntimeError(f"Google Places API returned {status}: {message}")

        for place in payload.get("results", []):
            collected.append(_normalize_result(place))
            if len(collected) >= config.max_results:
                break

        next_page_token = payload.get("next_page_token")
        if not next_page_token:
            break

    return collected


def fetch_and_save_raw_csv(query: str, output_csv: str, max_results: int = 60) -> list[dict[str, str | float | int | None]]:
    api_key = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing GOOGLE_PLACES_API_KEY environment variable.")

    records = list(fetch_places(PlacesSearchConfig(query=query, api_key=api_key, max_results=max_results)))
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "place_id",
        "name",
        "formatted_address",
        "rating",
        "user_ratings_total",
        "business_status",
        "types",
        "lat",
        "lng",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return records
